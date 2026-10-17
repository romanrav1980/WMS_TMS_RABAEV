"""Native claimed warehouse GROSS evidence, actual empty zero, immutable local bundle."""
import asyncio
from datetime import datetime
import hashlib
import json
import time
from typing import Any, Callable, Protocol
from ..contracts_scale_opc import OpcWeightObservation, OpcWeightReader, ScaleDeviceLease, ScaleBundleJournal
from ..contracts_scales import ScaleGatewayError
from ..contracts_warehouse_gateway import WarehouseGatewayProfile
from .scale_opc_window import collect_opc_window
from .warehouse_scale_claim import validate_claim
from .warehouse_scale_ack import warehouse_packet
from .warehouse_zero_progress import zero_event, restore_zero, validate_zero_ack


class WarehouseClaimJournal(Protocol):
    def prepare(self, request_id: str, device_id: str) -> bytes: ...
    def terminal(self, request_id: str, error: str) -> None: ...
    def zero(self, claim_id: str) -> bytes | None: ...
    def stage_zero(self, request_id: str, claim_id: str, body: bytes) -> None: ...


class WarehouseClaimApi(Protocol):
    def claim_request(self, request_id: str, body: bytes) -> bytes: ...
    def confirm_zero(self, request_id: str, body: bytes) -> bytes: ...


class OpcWarehouseCapture:
    def __init__(self, reader: OpcWeightReader, lease: ScaleDeviceLease, profile: dict[str, Any],
                 profile_digest: str, station: WarehouseGatewayProfile, bundle: ScaleBundleJournal,
                 claims: WarehouseClaimJournal, api: WarehouseClaimApi,
                 pending: Callable[[], bool]) -> None:
        self.reader, self.lease, self.profile, self.profile_digest = reader, lease, profile, profile_digest
        self.station, self.bundle, self.claims, self.api, self.pending = station, bundle, claims, api, pending

    async def capture(self, request: dict[str, Any]) -> tuple[bytes, bytes]:
        device = self.station.device_id
        if request.get('device_id') != device or self.profile['device_id'] != device:
            raise ScaleGatewayError('WAREHOUSE_REQUEST_DEVICE_MISMATCH')
        if self.station.basis != 'GROSS':
            raise ScaleGatewayError('WAREHOUSE_OPC_NET_PROFILE_UNSUPPORTED')
        if request.get('purpose') == 'PICK' and self.profile.get('warehouse_pick_mode') != 'SEALED_WEIGHT_BOX':
            raise ScaleGatewayError('WAREHOUSE_OPC_PICK_COMMISSIONING_REQUIRED')
        token = self.lease.acquire(device, time.time(), 15)
        try:
            body = self.claims.prepare(request['request_id'], device)
            claim_id = json.loads(body)['claim_id']
            kind = 'WAREHOUSE_PICK' if request['purpose'] == 'PICK' else 'WAREHOUSE_FINAL'
            saved = self.bundle.get(kind, device, claim_id)
            if saved is not None:
                return saved
            if self.pending():
                raise ScaleGatewayError('WAREHOUSE_ORIGINAL_OUTBOX_DRAIN_REQUIRED', True)
            response = await asyncio.to_thread(self.api.claim_request, request['request_id'], body)
            self.lease.renew(device, token, time.time(), 15)
            try:
                claim = validate_claim(request, body, response, self.station)
            except ScaleGatewayError as exc:
                if exc.code == 'WAREHOUSE_CLAIM_EXPIRED_OR_CAPTURED':
                    self.claims.terminal(request['request_id'], exc.code)
                raise
            try:
                packet, raw = await self._measure(claim, token)
            except ScaleGatewayError as exc:
                if exc.code in {'WAREHOUSE_ACTUAL_EMPTY_PLATFORM_ZERO_REQUIRED', 'WAREHOUSE_CLAIM_WINDOW_TOO_SHORT'}:
                    self.claims.terminal(request['request_id'], exc.code)
                raise
            self.lease.renew(device, token, time.time(), 15)
            self.bundle.stage(packet, raw)
            return packet, raw
        finally:
            self.lease.release(device, token)

    async def _measure(self, claim: dict[str, Any], token: str) -> tuple[bytes, bytes]:
        expiry = datetime.fromisoformat(claim['claim_expires_at']).timestamp()
        # No claimed_at is supplied. All reads start after the authenticated claim ACK.
        lower = time.time()
        def renew() -> None:
            if time.time() >= expiry - 6:
                self.claims.terminal(claim['request_id'], 'WAREHOUSE_CLAIM_LEASE_EXPIRED')
                raise ScaleGatewayError('WAREHOUSE_CLAIM_LEASE_EXPIRED')
            self.lease.renew(self.station.device_id, token, time.time(), 15)
        zero = await self._reported_zero(claim, renew, expiry)
        if claim.get('zero_progress_required') is True:
            while time.time() < expiry - 9:
                renew()
                loaded = await self.reader.read()
                if loaded.gross > 0:
                    break
                await asyncio.sleep(.25)
            else:
                raise ScaleGatewayError('WAREHOUSE_CLAIM_WINDOW_TOO_SHORT')
        remaining = min(10.0, expiry-time.time()-6)
        if remaining < 2.5:
            renew()
            raise ScaleGatewayError('WAREHOUSE_CLAIM_WINDOW_TOO_SHORT')
        observations, offsets = await collect_opc_window(self.reader, renew, remaining)
        renew()
        for observation in [zero, *observations]:
            stamp = datetime.fromisoformat(observation.evidence['values']['current_weight']['server_timestamp']).timestamp()
            earliest = datetime.fromisoformat(claim['claim_created_at']).timestamp() if observation is zero and claim.get('zero_progress_required') is True else lower
            if stamp < earliest or stamp >= expiry:
                raise ScaleGatewayError('WAREHOUSE_OBSERVATION_OUTSIDE_LOCAL_CLAIM')
        source = dict(claim['capture_context'])
        source.update(zero_confirmed=True, zero_check_kg=format(zero.gross, 'f'),
            zero_check_at=zero.evidence['values']['current_weight']['server_timestamp'],
            measured_at=observations[-1].evidence['values']['current_weight']['server_timestamp'],
            samples=[dict(offset_ms=offset, weight_kg=format(obs.gross, 'f'))
                     for obs, offset in zip(observations, offsets, strict=True)])
        body = json.dumps(source, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode()
        warehouse_packet(body)  # Existing exact DTO, including final exclude-none convention.
        return body, self._evidence(body, zero, observations, offsets)

    async def _reported_zero(self, claim: dict[str, Any], renew: Callable[[], None],
                             expiry: float) -> OpcWeightObservation:
        if claim.get('zero_progress_required') is not True:
            return await self._zero(renew, expiry)
        saved = self.claims.zero(claim['claim_id'])
        if saved is None:
            zero = await self._zero(renew, expiry, datetime.fromisoformat(claim['claim_created_at']).timestamp())
            saved = zero_event(claim, zero, self.profile, self.profile_digest)
            self.claims.stage_zero(claim['request_id'], claim['claim_id'], saved)
        zero = restore_zero(saved, claim, self.profile_digest)
        renew()
        response = await asyncio.to_thread(self.api.confirm_zero, claim['request_id'], saved)
        validate_zero_ack(saved, response, claim)
        renew()
        return zero

    async def _zero(self, renew: Callable[[], None], expiry: float,
                    claim_start: float | None = None) -> OpcWeightObservation:
        while time.time() < expiry - 9:
            renew()
            observation = await self.reader.read()
            renew()
            if observation.center_zero and observation.stable and observation.gross == 0:
                # Instrument clocks/last values can precede the server claim ACK. Wait for
                # genuinely fresh DataValues; never restamp or durably stage an old zero.
                stamps = [datetime.fromisoformat(observation.evidence['observed_at']).timestamp(),
                          *[datetime.fromisoformat(value['server_timestamp']).timestamp()
                            for value in observation.evidence['values'].values()]] if claim_start is not None else []
                if all((claim_start is None or stamp >= claim_start) and stamp <= expiry for stamp in stamps):
                    return observation
            await asyncio.sleep(.5)
        raise ScaleGatewayError('WAREHOUSE_ACTUAL_EMPTY_PLATFORM_ZERO_REQUIRED')

    def _evidence(self, body: bytes, zero: OpcWeightObservation,
                  observations: list[OpcWeightObservation], offsets: list[int]) -> bytes:
        source = json.loads(body)
        raw = dict(protocol_version='1.0', device_id=source['device_id'], capture_id=source['capture_id'],
            capture_kind='WAREHOUSE_FINAL' if 'purpose' in source else 'WAREHOUSE_PICK',
            capture_sha256=hashlib.sha256(body).hexdigest().upper(), profile_sha256=self.profile_digest.upper(),
            station_id=self.profile['station_id'], model_namespace_uri=self.profile['model_namespace_uri'],
            nodes={field: dict(namespace_uri=node['namespace_uri'],
                identifier_type='String' if node['identifier_type']=='s' else 'Numeric', identifier=str(node['identifier']))
                for field, node in self.profile['nodes'].items()},
            opc_server=dict(application_uri=self.profile['server_application_uri'],
                certificate_sha256=self.profile['security']['server_sha256'].upper()),
            zero_observation=zero.evidence,
            observations=[dict(offset_ms=offset, **obs.evidence) for obs, offset in zip(observations, offsets, strict=True)])
        return json.dumps(raw, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode()

