"""Fresh real read windows projected into the existing store contract.

No quantity, sample-spread, weight tolerance or stock effect is decided here.
"""
import hashlib
import json
import time
from typing import Any

from ..contracts_scale_opc import OpcWeightObservation, OpcWeightReader, ScaleDeviceLease, ScaleBundleJournal
from ..contracts_scales import ScaleGatewayError
from .scale_opc_window import collect_opc_window


class OpcStoreCapture:
    def __init__(self, reader: OpcWeightReader, lease: ScaleDeviceLease, profile: dict[str, Any],
                 profile_digest: str, bundle: ScaleBundleJournal | None = None) -> None:
        self.bundle = bundle
        self.reader, self.lease, self.profile, self.profile_digest = reader, lease, profile, profile_digest
        self.zero: OpcWeightObservation | None = None

    def reset_connection(self) -> None:
        self.zero = None

    async def observe_zero(self) -> bool:
        device = self.profile["device_id"]
        token = self.lease.acquire(device, time.time(), 10)
        try:
            observation = await self.reader.read()
            self.lease.renew(device, token, time.time(), 10)
            if observation.center_zero and observation.stable and observation.gross == 0:
                self.zero = observation
                return True
            return False
        finally:
            self.lease.release(device, token)

    async def capture(self, request: dict[str, Any], timeout: float = 10) -> tuple[bytes, bytes]:
        device = self.profile["device_id"]
        if request["device_id"] != device or request["state"] != "REQUESTED":
            raise ScaleGatewayError("OPC_REQUEST_DEVICE_MISMATCH")
        token = self.lease.acquire(device, time.time(), 10)
        try:
            if self.bundle is not None:
                saved = self.bundle.get("STORE_RECEIPT", device, request["request_id"])
                if saved is not None:
                    return saved
            if self.zero is None or not 0 <= time.time()-self.zero.observed_at.timestamp() <= 590:
                raise ScaleGatewayError("OPC_EMPTY_PLATFORM_ZERO_REQUIRED", True)
            observations, offsets = await self._window(device, token, timeout)
            body = self._packet(request, observations, offsets)
            raw = self._evidence(body, observations, offsets)
            if self.bundle is not None:
                self.lease.renew(device, token, time.time(), 10)
                self.bundle.stage(body, raw)
                self.lease.renew(device, token, time.time(), 10)
            self.zero = None
            return body, raw
        finally:
            self.lease.release(device, token)

    async def _window(self, device: str, token: str, timeout: float) -> tuple[list[OpcWeightObservation], list[int]]:
        def renew() -> None:
            self.lease.renew(device, token, time.time(), 10)
        return await collect_opc_window(self.reader, renew, timeout)

    def _packet(self, request: dict[str, Any], observations: list[OpcWeightObservation], offsets: list[int]) -> bytes:
        packet = {key: request[key] for key in ("device_id", "load_operation_id", "store_address",
                                               "device_policy_version", "calibration_ref")}
        packet.update(capture_id=request["request_id"], unit="KG", basis="GROSS", preset_tare_kg="0",
                      zero_confirmed=True, zero_check_kg="0",
                      zero_check_at=self.zero.evidence["values"]["current_weight"]["server_timestamp"],
                      measured_at=observations[-1].evidence["values"]["current_weight"]["server_timestamp"],
                      samples=[dict(offset_ms=offset, gross_weight_kg=format(obs.gross, "f"))
                               for obs, offset in zip(observations, offsets, strict=True)])
        return json.dumps(packet, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()

    def _evidence(self, packet: bytes, observations: list[OpcWeightObservation], offsets: list[int]) -> bytes:
        source = json.loads(packet)
        raw = dict(protocol_version="1.0", device_id=source["device_id"], capture_id=source["capture_id"],
                   capture_kind="STORE_RECEIPT", capture_sha256=hashlib.sha256(packet).hexdigest().upper(),
                   profile_sha256=self.profile_digest.upper(), station_id=self.profile["station_id"],
                   model_namespace_uri=self.profile["model_namespace_uri"],
                   nodes={field: dict(namespace_uri=node["namespace_uri"],
                                      identifier_type="String" if node["identifier_type"] == "s" else "Numeric",
                                      identifier=str(node["identifier"])) for field, node in self.profile["nodes"].items()},
                   opc_server=dict(application_uri=self.profile["server_application_uri"],
                                   certificate_sha256=self.profile["security"]["server_sha256"].upper()),
                   zero_observation=self.zero.evidence,
                   observations=[dict(offset_ms=offset, **obs.evidence) for obs, offset in zip(observations, offsets, strict=True)])
        return json.dumps(raw, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
