"""Vendor integration utility. No simulated scale values or credential logging."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.wms_api_server.app.modules.integrations.public import (
    HttpScaleGateway, ScaleGatewayError, ScaleGatewayWorker, SqliteScaleOutbox,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Poll scale requests and deliver a vendor-produced capture packet")
    parser.add_argument("--once", action="store_true", required=True)
    parser.add_argument("--packet-file", type=Path, help="Actual measured packet exported by supplier API/SDK")
    parser.add_argument("--outbox", type=Path, default=Path("runtime/store-scale-gateway.sqlite"))
    parser.add_argument("--allow-loopback-http", action="store_true", help="Local development only")
    args = parser.parse_args()
    try:
        api = HttpScaleGateway(os.environ["STORE_SCALE_API_ORIGIN"], os.environ["STORE_SCALE_SENDER"],
                               os.environ["STORE_SCALE_PASSWORD"], allow_loopback_http=args.allow_loopback_http)
        device = os.environ["STORE_SCALE_DEVICE_ID"]
        if not device or len(device) > 100:
            raise ValueError()
        args.outbox.parent.mkdir(parents=True, exist_ok=True)
        packet = None
        if args.packet_file:
            with args.packet_file.open("rb") as stream:
                packet = stream.read(65537)
            if len(packet) > 65536:
                raise ValueError()
        worker = ScaleGatewayWorker(api, SqliteScaleOutbox(args.outbox), device, time.time)
        result = worker.cycle(packet)
        print(json.dumps(result))
        return 0 if result["status"] in {"ARCHIVED", "WAITING_FOR_VENDOR_PACKET"} else 2
    except ScaleGatewayError as exc:
        print(json.dumps({"status": "UNAVAILABLE", "error": exc.code}))
        return 2
    except (KeyError, ValueError, OSError):
        print(json.dumps({"status": "CONFIGURATION_REQUIRED"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
