from __future__ import annotations

import argparse
import dataclasses
import socket
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..services.production_exchange_service import ProductionExchangeService


def process_batch(
    worker_id: str,
    root_dir: str | None,
    limit: int,
    sleep_seconds: float,
    loop: bool,
) -> None:
    service = ProductionExchangeService(root_dir=Path(root_dir) if root_dir else None)
    while True:
        results = service.process_once(limit=limit)
        if not results:
            print_status({"status": "idle", "worker_id": worker_id, "root_dir": str(service.root_dir)})
            if not loop:
                return
            time.sleep(sleep_seconds)
            continue

        for result in results:
            print_status({"worker_id": worker_id, **dataclasses.asdict(result)})

        if not loop:
            return


def print_status(payload: dict[str, Any]) -> None:
    payload = {"at": datetime.now(UTC).isoformat(), **payload}
    print(payload, flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WMS production-release file exchange worker")
    parser.add_argument("--worker-id", default=f"production-exchange-worker-{socket.gethostname()}")
    parser.add_argument("--root-dir", default=None)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--sleep-seconds", type=float, default=5.0)
    parser.add_argument("--loop", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    process_batch(
        worker_id=args.worker_id,
        root_dir=args.root_dir,
        limit=max(1, args.limit),
        sleep_seconds=max(0.5, args.sleep_seconds),
        loop=args.loop,
    )


if __name__ == "__main__":
    main()
