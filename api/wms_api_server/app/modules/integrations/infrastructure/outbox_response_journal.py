"""Local response recovery, sharded OS ownership, no repeated provider call."""
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4
from .file_gateway import directory_owner
from .outbox_delivery import OutboxDelivery

class OutboxResponseJournal:
    MAX_BYTES = 8 * 1024 * 1024
    MAX_PENDING = 500

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(os.getenv("WMS_OUTBOX_RESPONSE_DIR",
            str(Path(__file__).resolve().parents[4] / "runtime" / "outbox_responses")))
        if self.root.is_symlink():
            raise ValueError("Response journal root must not be a symbolic link")
        self.root = self.root.resolve()
        self.pending = self.root / "pending"
        self.locks = self.root / "locks"

    def ready(self) -> None:
        for path in (self.root, self.pending, self.locks):
            if path.is_symlink():
                raise ValueError("Response journal directory must not be a symbolic link")
            path.mkdir(parents=True, exist_ok=True)
        count = 0
        with os.scandir(self.pending) as entries:
            for entry in entries:
                if entry.name.endswith(".json"):
                    count += 1
                    if count >= self.MAX_PENDING:
                        raise RuntimeError("OUTBOX_RESPONSE_JOURNAL_BACKPRESSURE")
        # Prove writable storage before claiming/sending; no response content in this probe.
        probe = self.pending / (uuid4().hex + ".probe")
        with probe.open("xb") as handle:
            handle.write(b"0"); handle.flush(); os.fsync(handle.fileno())
        linked = probe.with_suffix(".probe-link")
        try:
            os.link(probe, linked)
        finally:
            if linked.exists():
                linked.unlink()
            probe.unlink()

    def _owner(self, key: str) -> Path:
        directory = self.locks / key[:2]
        if directory.is_symlink():
            raise ValueError("Response journal lock must not be a symbolic link")
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def save(self, claim: dict[str, Any], request_id: int, target: str,
             body: dict[str, Any], simulation: bool, real_ack: bool) -> str:
        key = sha256(f'{claim["event_outbox_id"]}:{claim["claim_version"]}:{request_id}'.encode()).hexdigest()
        record = {"version": 1, "claim": claim, "request_id": request_id, "target_system": target,
                  "body": body, "simulation": simulation, "real_external_ack": real_ack}
        raw = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
        if len(raw) > self.MAX_BYTES:
            raise RuntimeError("OUTBOX_RESPONSE_JOURNAL_BODY_BOUND")
        path = self.pending / (key + ".json")
        if path.is_symlink():
            raise ValueError("Response journal entry must not be a symbolic link")
        temporary = self.pending / (key + ".writing-" + uuid4().hex)
        try:
            with temporary.open("xb") as handle:
                handle.write(raw); handle.flush(); os.fsync(handle.fileno())
            # Atomic create-if-absent publication on local NTFS/POSIX; immutable payload.
            # A recovery may remove an already finalized record between attempts.
            for _ in range(3):
                try:
                    os.link(temporary, path)
                    break
                except FileExistsError:
                    try:
                        existing = path.read_bytes()
                    except FileNotFoundError:
                        continue
                    if existing != raw:
                        raise RuntimeError("OUTBOX_RESPONSE_JOURNAL_CONTENT_CONFLICT")
                    break
            else:
                raise RuntimeError("OUTBOX_RESPONSE_JOURNAL_PUBLICATION_UNCONFIRMED")
        finally:
            if temporary.exists():
                temporary.unlink()
        return key

    def finalize(self, key: str, delivery: OutboxDelivery) -> dict[str, Any] | None:
        if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
            raise ValueError("Response journal key required")
        path = self.pending / (key + ".json")
        with directory_owner(self._owner(key)) as owned:
            if not owned or not path.exists():
                return None
            if path.is_symlink():
                raise ValueError("Response journal entry must not be a symbolic link")
            with path.open("rb") as handle:
                raw = handle.read(self.MAX_BYTES + 1)
            if len(raw) > self.MAX_BYTES:
                raise RuntimeError("OUTBOX_RESPONSE_JOURNAL_BODY_BOUND")
            record = json.loads(raw)
            claim = record["claim"]
            expected = sha256(f'{claim["event_outbox_id"]}:{claim["claim_version"]}:{record["request_id"]}'.encode()).hexdigest()
            if record["version"] != 1 or expected != key:
                raise RuntimeError("OUTBOX_RESPONSE_JOURNAL_IDENTITY_CONFLICT")
            result = delivery.finish(claim, record["request_id"], record["body"])
            # Keep on any unconfirmed commit. Exact response hash makes recovery repeat safe.
            path.unlink()
            return {**result, "claim_version": claim["claim_version"], "error": record["body"].get("error_text"),
                    "external_status": record["body"].get("external_status"), "simulation": record["simulation"],
                    "real_external_ack": record["real_external_ack"] is True and record["simulation"] is False
                        and result["status"] == "DONE", "response_recovered": True}

    def recover_one(self, delivery: OutboxDelivery, target: str | None) -> dict[str, Any] | None:
        if not self.pending.exists():
            return None
        checked = 0
        with os.scandir(self.pending) as entries:
            for entry in entries:
                if not entry.name.endswith(".json"):
                    continue
                checked += 1
                if checked > self.MAX_PENDING:
                    raise RuntimeError("OUTBOX_RESPONSE_JOURNAL_BACKPRESSURE")
                if entry.is_symlink():
                    raise ValueError("Response journal entry must not be a symbolic link")
                path = Path(entry.path)
                try:
                    with path.open("rb") as handle:
                        raw = handle.read(self.MAX_BYTES + 1)
                except FileNotFoundError:
                    continue
                if len(raw) > self.MAX_BYTES:
                    raise RuntimeError("OUTBOX_RESPONSE_JOURNAL_BODY_BOUND")
                record = json.loads(raw)
                if target and record["target_system"].upper() != target.upper():
                    continue
                result = self.finalize(path.stem, delivery)
                if result is not None:
                    return result
        return None
