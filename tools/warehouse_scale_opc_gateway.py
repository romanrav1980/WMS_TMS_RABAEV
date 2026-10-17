"""Claimed GROSS warehouse OPC gateway; no stock command is sent."""
import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
import sys
import time
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_profile import OpcScaleProfile
from api.wms_api_server.app.modules.integrations.infrastructure.scale_device_lease import SqliteScaleDeviceLease
from api.wms_api_server.app.modules.integrations.infrastructure.scale_bundle_journal import SqliteScaleBundleJournal
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox
from api.wms_api_server.app.modules.integrations.infrastructure.warehouse_scale_claims import SqliteWarehouseScaleClaims
from api.wms_api_server.app.modules.integrations.infrastructure.warehouse_scale_request_http import HttpWarehouseScaleRequests
from api.wms_api_server.app.modules.integrations.application.warehouse_scale_gateway import WarehouseScaleGatewayWorker
from api.wms_api_server.app.modules.integrations.application.warehouse_opc_capture import OpcWarehouseCapture
from api.wms_api_server.app.modules.integrations.application.scale_evidence_delivery import deliver_evidence
from api.wms_api_server.app.modules.integrations.contracts_warehouse_gateway import WarehouseGatewayProfile
from api.wms_api_server.app.modules.integrations.contracts_scales import ScaleGatewayError


def output(value: dict[str, Any]) -> None:
    print(json.dumps(value), flush=True)


def drain(api: HttpWarehouseScaleRequests, worker: WarehouseScaleGatewayWorker,
          rawbox: SqliteScaleOutbox, bundle: SqliteScaleBundleJournal) -> bool:
    bundle.reconcile(worker.outbox, rawbox)
    output(worker.cycle())
    output(deliver_evidence(api.post_evidence, rawbox, time.time()))
    suspended = worker.outbox.suspended_count() + rawbox.suspended_count()
    if suspended:
        output({'status': 'SUSPENDED_ARCHIVES_REVIEW_REQUIRED', 'count': suspended})
    return worker.outbox.pending_count() == 0 and rawbox.pending_count() == 0


async def cycle(api: HttpWarehouseScaleRequests, capture: OpcWarehouseCapture,
                worker: WarehouseScaleGatewayWorker, rawbox: SqliteScaleOutbox,
                bundle: SqliteScaleBundleJournal) -> None:
    if not await asyncio.to_thread(drain, api, worker, rawbox, bundle):
        output({'status': 'ORIGINAL_OUTBOX_DRAIN_REQUIRED'})
        return
    requests = await asyncio.to_thread(api.requests, capture.station.device_id)
    for request in requests:
        try:
            await capture.capture(request)
            await asyncio.to_thread(drain, api, worker, rawbox, bundle)
            return
        except ScaleGatewayError as exc:
            output({'status': 'BLOCKED', 'request_id': request['request_id'], 'error': exc.code})
            if exc.code != 'WAREHOUSE_CLAIM_TERMINAL_REVIEW_REQUIRED':
                raise
    if not requests:
        output({'status': 'NO_PENDING_WAREHOUSE_REQUEST'})


async def serve(args: argparse.Namespace) -> int:
    from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_client import Opc40200Client
    profile = OpcScaleProfile.load(args.profile)
    station = WarehouseGatewayProfile.model_validate(json.loads(args.station_profile.read_bytes()))
    if station.basis != 'GROSS' or station.device_id != profile.data['device_id']:
        raise ValueError('WAREHOUSE_OPC_GROSS_PROFILE_REQUIRED')
    args.runtime.mkdir(parents=True, exist_ok=True)
    args.lease_db.parent.mkdir(parents=True, exist_ok=True)
    api = HttpWarehouseScaleRequests(os.environ['STORE_SCALE_API_ORIGIN'], os.environ['STORE_SCALE_SENDER'],
        os.environ['STORE_SCALE_PASSWORD'], allow_loopback_http=args.allow_loopback_http)
    box = SqliteScaleOutbox(args.runtime/'captures.sqlite')
    rawbox = SqliteScaleOutbox(args.runtime/'evidence.sqlite', max_packet_bytes=131072)
    bundle = SqliteScaleBundleJournal(args.runtime/'bundles.sqlite')
    claims = SqliteWarehouseScaleClaims(args.runtime/'claims.sqlite')
    lease = SqliteScaleDeviceLease(args.lease_db)
    worker = WarehouseScaleGatewayWorker(api, box, station, time.time)
    while True:
        reader = Opc40200Client(profile)
        capture = OpcWarehouseCapture(reader, lease, profile.data, profile.digest, station, bundle, claims, api,
                                     lambda: box.pending_count() > 0 or rawbox.pending_count() > 0)
        try:
            if not await asyncio.to_thread(drain, api, worker, rawbox, bundle):
                output({'status': 'ORIGINAL_OUTBOX_DRAIN_REQUIRED'})
                if args.once:
                    return 2
                await asyncio.sleep(1)
                continue
            await reader.connect()
            while True:
                await cycle(api, capture, worker, rawbox, bundle)
                if args.once:
                    return 0
                await asyncio.sleep(1)
        except ScaleGatewayError as exc:
            output({'status': 'BLOCKED', 'error': exc.code})
            if args.once:
                return 2
        except Exception:
            output({'status': 'DISCONNECTED', 'error': 'OPC_CONNECTION_OR_PROFILE_REJECTED'})
            if args.once:
                return 2
        finally:
            await reader.disconnect()
        await asyncio.sleep(2)


def main() -> int:
    parser = argparse.ArgumentParser(description='OPC40200 claimed warehouse GROSS gateway')
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--station-profile', type=Path, required=True)
    parser.add_argument('--runtime', type=Path, default=Path('runtime/warehouse-scale-opc'))
    parser.add_argument('--lease-db', type=Path, default=Path(__file__).resolve().parents[1]/'runtime/opc-device-leases.sqlite')
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--allow-loopback-http', action='store_true')
    logging.basicConfig(level=logging.CRITICAL)
    try:
        return asyncio.run(serve(parser.parse_args()))
    except ModuleNotFoundError:
        output({'status': 'CONFIGURATION_REQUIRED', 'error': 'SCALE_GATEWAY_TOOL_DEPENDENCIES_REQUIRED'})
        return 2
    except (KeyError, ValueError, OSError):
        output({'status': 'CONFIGURATION_REQUIRED'})
        return 2
    except KeyboardInterrupt:
        return 0


if __name__ == '__main__':
    raise SystemExit(main())


