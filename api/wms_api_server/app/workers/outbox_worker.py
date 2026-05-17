from __future__ import annotations

import argparse
import socket
import time
from datetime import UTC, datetime
from typing import Any

from ..services.outbox_service import OutboxService


def process_batch(
    worker_id: str,
    target_system: str | None,
    limit: int,
    sleep_seconds: float,
    loop: bool,
) -> None:
    service = OutboxService()
    processed = 0
    while True:
        result = service.process_next(worker_id=worker_id, target_system=target_system)
        if result is None:
            print_status({"status": "idle", "worker_id": worker_id})
            if not loop:
                return
            time.sleep(sleep_seconds)
            continue

        processed += 1
        print_status(result)
        if not loop and processed >= limit:
            return


def print_status(payload: dict[str, Any]) -> None:
    payload = {"at": datetime.now(UTC).isoformat(), **payload}
    print(payload, flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WMS external outbox worker")
    parser.add_argument("--worker-id", default=f"outbox-worker-{socket.gethostname()}")
    parser.add_argument("--target-system", default=None)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--sleep-seconds", type=float, default=5.0)
    parser.add_argument("--loop", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    process_batch(
        worker_id=args.worker_id,
        target_system=args.target_system,
        limit=max(1, args.limit),
        sleep_seconds=max(0.5, args.sleep_seconds),
        loop=args.loop,
    )


if __name__ == "__main__":
    main()
