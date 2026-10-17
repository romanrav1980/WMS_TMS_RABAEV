"""Real OPC40200 store gateway service. No hardware simulation or auto-trust."""
import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_client import Opc40200Client
from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_profile import OpcScaleProfile
from api.wms_api_server.app.modules.integrations.infrastructure.scale_device_lease import SqliteScaleDeviceLease
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox
from api.wms_api_server.app.modules.integrations.infrastructure.scale_bundle_journal import SqliteScaleBundleJournal
from api.wms_api_server.app.modules.integrations.infrastructure.scale_evidence_http import HttpScaleEvidenceGateway
from api.wms_api_server.app.modules.integrations.application.scale_opc_capture import OpcStoreCapture
from api.wms_api_server.app.modules.integrations.application.scale_gateway import ScaleGatewayWorker
from api.wms_api_server.app.modules.integrations.application.scale_evidence_delivery import deliver_evidence
from api.wms_api_server.app.modules.integrations.contracts_scales import ScaleGatewayError


def output(value: dict) -> None:
    print(json.dumps(value), flush=True)


async def cycle(api, worker, capture, raw_outbox, bundle) -> None:
    await asyncio.to_thread(bundle.reconcile, worker.outbox, raw_outbox)
    # Recover original commands before considering a new physical measurement.
    result = await asyncio.to_thread(worker.cycle)
    if result["status"] not in {"WAITING_FOR_VENDOR_PACKET", "ARCHIVED"}:
        output(result)
    output(await asyncio.to_thread(deliver_evidence, api.post_evidence, raw_outbox, time.time()))
    requests = await asyncio.to_thread(api.requests, capture.profile["device_id"])
    await capture.observe_zero()
    for request in requests:
        if worker.outbox.has_capture(request["device_id"], request["request_id"]):
            continue
        body, raw = await capture.capture(request)
        await asyncio.to_thread(bundle.reconcile, worker.outbox, raw_outbox)
        output(await asyncio.to_thread(worker.cycle, body))
        break
    output(await asyncio.to_thread(deliver_evidence, api.post_evidence, raw_outbox, time.time()))
    if not requests:
        output({"status": "WAITING_FOR_REQUEST", "zero_observed": capture.zero is not None})


async def serve(args: argparse.Namespace) -> int:
    profile = OpcScaleProfile.load(args.profile)
    args.runtime.mkdir(parents=True, exist_ok=True)
    api = HttpScaleEvidenceGateway(os.environ["STORE_SCALE_API_ORIGIN"], os.environ["STORE_SCALE_SENDER"],
        os.environ["STORE_SCALE_PASSWORD"], allow_loopback_http=args.allow_loopback_http)
    outbox = SqliteScaleOutbox(args.runtime/"captures.sqlite")
    raw_outbox = SqliteScaleOutbox(args.runtime/"evidence.sqlite", max_packet_bytes=131072)
    args.lease_db.parent.mkdir(parents=True, exist_ok=True)
    lease = SqliteScaleDeviceLease(args.lease_db)
    bundle = SqliteScaleBundleJournal(args.runtime/"bundles.sqlite")
    worker = ScaleGatewayWorker(api, outbox, profile.data["device_id"], time.time)
    while True:
        reader = Opc40200Client(profile)
        capture = OpcStoreCapture(reader, lease, profile.data, profile.digest, bundle)
        try:
            await asyncio.to_thread(bundle.reconcile, outbox, raw_outbox)
            output(await asyncio.to_thread(worker.cycle))
            output(await asyncio.to_thread(deliver_evidence, api.post_evidence, raw_outbox, time.time()))
            await reader.connect()
            while True:
                try:
                    await cycle(api, worker, capture, raw_outbox, bundle)
                except ScaleGatewayError as exc:
                    output({"status": "BLOCKED", "error": exc.code})
                    if exc.code not in {"OPC_EMPTY_PLATFORM_ZERO_REQUIRED", "OPC_STABLE_WINDOW_TIMEOUT"}:
                        capture.reset_connection()
                    if exc.code in {"OPC_READ_UNAVAILABLE", "OPC_NOT_CONNECTED"}:
                        raise
                    if args.once:
                        return 2
                if args.once:
                    return 0
                await asyncio.sleep(1)
        except ScaleGatewayError as exc:
            output({"status": "DISCONNECTED", "error": exc.code})
            if args.once:
                return 2
        except Exception:
            output({"status": "DISCONNECTED", "error": "OPC_CONNECTION_OR_PROFILE_REJECTED"})
            if args.once:
                return 2
        finally:
            capture.reset_connection()
            await reader.disconnect()
        await asyncio.sleep(3)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only OPC40200 store scale gateway")
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, default=Path("runtime/store-scale-opc"))
    parser.add_argument("--lease-db", type=Path, default=Path(__file__).resolve().parents[1]/"runtime/opc-device-leases.sqlite")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--allow-loopback-http", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.CRITICAL)
    try:
        return asyncio.run(serve(args))
    except (KeyError, ValueError, OSError):
        output({"status": "CONFIGURATION_REQUIRED"})
        return 2
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
