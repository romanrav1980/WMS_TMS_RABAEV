"""Deliver actual warehouse packet-file measurements; never manufacture sample values."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.wms_api_server.app.modules.integrations.public import (
    HttpWarehouseScaleGateway, WarehouseGatewayProfile, WarehouseScaleGatewayWorker,
    SqliteScaleOutbox, ScaleGatewayError,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Deliver measured warehouse PICK/EMPTY_TARE/FINAL_GROSS evidence")
    parser.add_argument("--once", action="store_true", required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--packet-file", type=Path)
    parser.add_argument("--outbox", type=Path, required=True, help="Dedicated warehouse station delivery journal")
    parser.add_argument("--allow-loopback-http", action="store_true", help="Local development only")
    args = parser.parse_args()
    try:
        with args.profile.open("rb") as stream:
            profile_bytes = stream.read(8193)
        if len(profile_bytes) > 8192:
            raise ValueError("WAREHOUSE_PROFILE_SIZE_INVALID")
        profile = WarehouseGatewayProfile.model_validate_json(profile_bytes)
        api = HttpWarehouseScaleGateway(os.environ["WAREHOUSE_SCALE_API_ORIGIN"],
            os.environ["WAREHOUSE_SCALE_SENDER"], os.environ["WAREHOUSE_SCALE_PASSWORD"],
            allow_loopback_http=args.allow_loopback_http)
        packet = None
        if args.packet_file:
            with args.packet_file.open("rb") as stream:
                packet = stream.read(32001)
        args.outbox.parent.mkdir(parents=True, exist_ok=True)
        result = WarehouseScaleGatewayWorker(api, SqliteScaleOutbox(args.outbox), profile, time.time).cycle(packet)
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
