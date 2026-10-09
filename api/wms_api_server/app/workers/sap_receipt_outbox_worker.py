"""Publish committed WMS receipt events as gateway XML files."""
import argparse
import json
from pathlib import Path
import time
from ..modules.integrations.public import build_receipt_exporter


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[4] / 'exchange' / 'sap_receipts' / 'outbox')
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--watch', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.limit <= 200:
        parser.error('limit must be 1..200')
    exporter = build_receipt_exporter()
    while True:
        try:
            print(json.dumps(exporter.export(args.root, args.limit), ensure_ascii=False), flush=True)
        except Exception as exc:
            print(json.dumps({'status': 'ERROR', 'error': str(exc)}, ensure_ascii=False), flush=True)
            if not args.watch:
                raise
        if not args.watch:
            break
        time.sleep(2)


if __name__ == '__main__':
    main()
