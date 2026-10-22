"""Recheck durable missing-master messages for explicitly selected warehouses."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import signal
import sys
import threading
from stock_posting_environment import load_local_oracle_environment


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--warehouse', type=int, action='append', required=True)
    parser.add_argument('--actor', required=True)
    parser.add_argument('--interval', type=int, default=30)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    warehouses = sorted(set(args.warehouse))
    if any(w < 1 for w in warehouses) or len(warehouses) > 10 or args.interval < 15:
        parser.error('Select 1..10 positive warehouses and an interval of at least 15 seconds')
    load_local_oracle_environment()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'api/wms_api_server'))
    from app.modules.integrations.public import build_trade_deferred_worker
    service = build_trade_deferred_worker()
    stopping = threading.Event()
    for name in (signal.SIGINT, signal.SIGTERM):
        signal.signal(name, lambda *_: stopping.set())
    while not stopping.is_set():
        for warehouse in warehouses:
            if stopping.is_set():
                break
            try:
                record = service.reconcile(warehouse, args.actor)
            except Exception as exc:
                record = dict(warehouse_id=warehouse, status='ERROR', error_type=type(exc).__name__,
                              code=getattr(exc, 'code', 'DEFERRED_WORKER_FAILED'))
            print(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(), **record)), flush=True)
        if args.once:
            break
        stopping.wait(args.interval)


if __name__ == '__main__':
    main()