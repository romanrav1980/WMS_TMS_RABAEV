"""Local durable exact-body retry journal for a dedicated equipment gateway.

SQLite owns only delivery state, never warehouse quantities or accepted receipts.
Lease clocks are UTC epoch seconds supplied by the gateway, not device timestamps.
"""
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import sqlite3
from typing import Iterator
from uuid import uuid4

from ..contracts_scales import ScaleDelivery


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("SCALE_JSON_DUPLICATE_KEY")
        result[key] = value
    return result


def _check_clock(value: float) -> None:
    if isinstance(value, bool) or not math.isfinite(value) or value < 0:
        raise ValueError("SCALE_CLOCK_INVALID")


class SqliteScaleOutbox:
    def __init__(self, path: Path, max_packet_bytes: int = 65536) -> None:
        if type(max_packet_bytes) is not int or not 1 <= max_packet_bytes <= 131072:
            raise ValueError("SCALE_PACKET_BOUND_INVALID")
        self.max_packet_bytes = max_packet_bytes
        self.path = path
        with self._connection() as db:
            db.execute("""create table if not exists scale_outbox(
                capture_key text primary key, body blob not null, state text not null,
                lease_token text, available_at real not null default 0,
                attempts integer not null default 0, response blob, last_error text)""")

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, timeout=5)
        try:
            db.execute("pragma synchronous=FULL")
            with db:
                yield db
        finally:
            db.close()

    def stage(self, body: bytes) -> str:
        """Persist before sending; same device/capture may never change payload."""
        if not isinstance(body, bytes) or len(body) > self.max_packet_bytes:
            raise ValueError("SCALE_PACKET_SIZE_INVALID")
        packet = json.loads(body.decode("utf-8"), object_pairs_hook=_unique_object)
        if not isinstance(packet, dict):
            raise ValueError("SCALE_PACKET_OBJECT_REQUIRED")
        identity = []
        for field in ("device_id", "capture_id"):
            value = packet.get(field)
            if not isinstance(value, str) or not 1 <= len(value) <= 100:
                raise ValueError("SCALE_PACKET_ID_INVALID")
            identity.append(value)
        # Length-prefix-free JSON tuple avoids ambiguous device/capture concatenation.
        key = hashlib.sha256(json.dumps(identity, ensure_ascii=True).encode()).hexdigest()
        with self._connection() as db:
            db.execute("begin immediate")
            existing = db.execute("select body from scale_outbox where capture_key=?", (key,)).fetchone()
            if existing and existing[0] != body:
                raise ValueError("SCALE_CAPTURE_PAYLOAD_CONFLICT")
            db.execute("insert or ignore into scale_outbox(capture_key,body,state) values(?,?,'PENDING')", (key, body))
        return key

    def has_capture(self, device_id: str, capture_id: str) -> bool:
        key = hashlib.sha256(json.dumps([device_id, capture_id], ensure_ascii=True).encode()).hexdigest()
        with self._connection() as db:
            return db.execute("select 1 from scale_outbox where capture_key=?", (key,)).fetchone() is not None

    def pending_count(self) -> int:
        """Delivery still in flight/backoff; suspended historical facts need explicit investigation."""
        with self._connection() as db:
            return db.execute("select count(*) from scale_outbox where state in ('PENDING','SENDING')").fetchone()[0]

    def suspended_count(self) -> int:
        with self._connection() as db:
            return db.execute("select count(*) from scale_outbox where state='SUSPENDED'").fetchone()[0]

    def suspended_count(self) -> int:
        with self._connection() as db:
            return db.execute("select count(*) from scale_outbox where state='SUSPENDED'").fetchone()[0]

    def bodies(self) -> Iterator[bytes]:
        for _, body in self.entries(0):
            yield body

    def entries(self, after_rowid: int) -> Iterator[tuple[int, bytes]]:
        """Append watermark includes ACK history once; subsequent scans visit new rows only."""
        with self._connection() as db:
            cursor = db.execute("select rowid,body from scale_outbox where rowid>? order by rowid", (after_rowid,))
            while rows := cursor.fetchmany(100):
                for row in rows:
                    yield row[0], row[1]

    def claim(self, now: float, lease_seconds: int = 30) -> ScaleDelivery | None:
        _check_clock(now)
        if not 1 <= lease_seconds <= 300:
            raise ValueError("SCALE_LEASE_INVALID")
        with self._connection() as db:
            db.execute("begin immediate")
            row = db.execute("""select capture_key,body,attempts from scale_outbox
                where state in ('PENDING','SENDING') and available_at<=?
                order by available_at,capture_key limit 1""", (now,)).fetchone()
            if not row:
                return None
            token = uuid4().hex
            db.execute("""update scale_outbox set state='SENDING',lease_token=?,available_at=?,
                attempts=attempts+1 where capture_key=?""", (token, now + lease_seconds, row[0]))
            return ScaleDelivery(row[0], row[1], token, row[2] + 1)

    def acknowledge(self, delivery: ScaleDelivery, response: bytes) -> None:
        with self._connection() as db:
            changed = db.execute("""update scale_outbox set state='ACKNOWLEDGED',response=?,
                lease_token=null,last_error=null where capture_key=? and lease_token=? and state='SENDING'""",
                (response, delivery.key, delivery.lease_token)).rowcount
            if changed != 1:
                raise ValueError("SCALE_LEASE_LOST")

    def defer(self, delivery: ScaleDelivery, retry_at: float, error: str) -> None:
        _check_clock(retry_at)
        with self._connection() as db:
            changed = db.execute("""update scale_outbox set state='PENDING',available_at=?,
                lease_token=null,last_error=? where capture_key=? and lease_token=? and state='SENDING'""",
                (retry_at, error[:200], delivery.key, delivery.lease_token)).rowcount
            if changed != 1:
                raise ValueError("SCALE_LEASE_LOST")

    def suspend(self, delivery: ScaleDelivery, error: str) -> None:
        """Permanent API rejection needs operator investigation, never a new capture ID."""
        with self._connection() as db:
            changed = db.execute("""update scale_outbox set state='SUSPENDED',lease_token=null,last_error=?
                where capture_key=? and lease_token=? and state='SENDING'""",
                (error[:200], delivery.key, delivery.lease_token)).rowcount
            if changed != 1:
                raise ValueError("SCALE_LEASE_LOST")


