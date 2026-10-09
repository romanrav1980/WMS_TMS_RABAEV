"""SAP XML file gateway: article master or warehouse supply order."""
import argparse
import json
from pathlib import Path
import time
from ..modules.integrations.public import build_artmas_service, build_supply_service, receive_gateway_files, build_acknowledgements
from ..modules.fulfillment.public import build_store_order_service

DEFAULT_ROOT = Path(__file__).resolve().parents[4] / 'exchange' / 'sap_retail'

def process_batch(root: Path, limit: int = 20, min_age: int = 2, kind: str = "artmas") -> list[dict]:
    receiver = build_store_order_service() if kind == 'store' else build_acknowledgements() if kind == "ack" else build_supply_service() if kind == "supply" else build_artmas_service()
    return receive_gateway_files(root, receiver, limit, min_age)


def main() -> None:
    parser = argparse.ArgumentParser(description='SAP Retail ARTMAS10 file inbox')
    parser.add_argument('--kind', choices=('artmas', 'supply', 'ack', 'store'), default='artmas')
    parser.add_argument('--root', type=Path, default=None)
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--watch', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.limit <= 200:
        parser.error('limit must be 1..200')
    roots = {'artmas': DEFAULT_ROOT, 'supply': DEFAULT_ROOT.parent/'sap_supply', 'ack': DEFAULT_ROOT.parent/'sap_receipts', 'store': DEFAULT_ROOT.parent/'sap_store_orders'}
    root = args.root or roots[args.kind]
    while True:
        try:
            result = process_batch(root, args.limit, kind=args.kind)
            if result or not args.watch:
                print(json.dumps(result, ensure_ascii=False), flush=True)
        except Exception as exc:
            print(json.dumps({'status': 'ERROR', 'error': str(exc)}, ensure_ascii=False), flush=True)
            if not args.watch:
                raise
        if not args.watch:
            break
        time.sleep(2)

if __name__ == '__main__':
    main()
