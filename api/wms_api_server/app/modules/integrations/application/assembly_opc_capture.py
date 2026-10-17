"""Continuous assembly Gross windows; never tare/zero a loaded container."""
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import time
from typing import Any
from ..contracts_scale_opc import OpcWeightReader, ScaleDeviceLease, ScaleBundleJournal
from ..contracts_scales import ScaleGatewayError
from .scale_opc_window import collect_opc_window


class OpcAssemblyCapture:
    def __init__(self, reader: OpcWeightReader, lease: ScaleDeviceLease,
                 profile: dict[str,Any], profile_digest: str, bundle: ScaleBundleJournal | None = None) -> None:
        self.bundle = bundle
        self.reader,self.lease,self.profile,self.profile_digest = reader,lease,profile,profile_digest

    async def capture(self, request: dict[str,Any], timeout: float = 10) -> tuple[bytes,bytes]:
        device = self.profile["device_id"]
        if request["device_id"] != device or request["phase"] not in {"BEFORE","AFTER","RECONCILE"}:
            raise ScaleGatewayError("ASSEMBLY_REQUEST_DEVICE_OR_PHASE_INVALID")
        expiry = datetime.fromisoformat(request["expires_at"])
        if expiry.tzinfo is None or expiry <= datetime.now(timezone.utc):
            raise ScaleGatewayError("ASSEMBLY_REQUEST_EXPIRED")
        before = Decimal(request["expected_before_kg"]) if request["phase"] == "AFTER" else None
        minimum = Decimal(request["min_delta_kg"]) if before is not None else None
        token = self.lease.acquire(device,time.time(),10)
        try:
            if self.bundle is not None:
                saved = self.bundle.get("WAREHOUSE_ASSEMBLY_RECON" if request["phase"] == "RECONCILE" else "WAREHOUSE_ASSEMBLY", device, request["capture_id"])
                if saved is not None:
                    return saved
            def renew() -> None:
                self.lease.renew(device,token,time.time(),10)
            observations,offsets = await collect_opc_window(self.reader,renew,timeout,before,minimum)
            if expiry <= datetime.now(timezone.utc):
                raise ScaleGatewayError("ASSEMBLY_REQUEST_EXPIRED")
            packet = {key:request[key] for key in ("session_id","step_id","capture_id","phase","device_id","device_policy_version","calibration_ref")}
            if request["phase"] == "RECONCILE":
                packet["reconciliation_id"] = request["reconciliation_id"]
            quality = all(value["status_code"] == 0 for obs in observations for value in obs.evidence["values"].values())
            tare_clear = all(obs.tare == 0 and obs.evidence["values"]["tare_mode"]["value"] == self.profile["no_tare_mode"] for obs in observations)
            if not quality or not tare_clear:
                raise ScaleGatewayError("ASSEMBLY_OBSERVATION_NOT_ADMISSIBLE")
            packet.update(unit="KG",basis="GROSS",preset_tare_kg="0",tare_mode_clear=tare_clear,quality_confirmed=quality,
                measured_at=observations[-1].evidence["values"]["current_weight"]["server_timestamp"],
                samples=[dict(offset_ms=offset,weight_kg=format(obs.gross,"f")) for obs,offset in zip(observations,offsets,strict=True)])
            body = json.dumps(packet,ensure_ascii=True,sort_keys=True,separators=(",", ":")).encode()
            raw = self._raw(request,body,observations,offsets)
            if self.bundle is not None:
                renew()
                self.bundle.stage(body,raw)
                renew()
            return body,raw
        finally:
            self.lease.release(device,token)

    def _raw(self, request: dict[str,Any], body: bytes, observations: list[Any], offsets: list[int]) -> bytes:
        raw = dict(protocol_version="1.1",capture_kind="WAREHOUSE_ASSEMBLY",device_id=request["device_id"],capture_id=request["capture_id"],
            capture_sha256=hashlib.sha256(body).hexdigest().upper(),profile_sha256=self.profile_digest.upper(),
            station_id=self.profile["station_id"],model_namespace_uri=self.profile["model_namespace_uri"],
            nodes={key:dict(namespace_uri=value["namespace_uri"],identifier_type="String" if value["identifier_type"]=="s" else "Numeric",
                            identifier=str(value["identifier"])) for key,value in self.profile["nodes"].items()},
            opc_server=dict(application_uri=self.profile["server_application_uri"],certificate_sha256=self.profile["security"]["server_sha256"].upper()),
            zero_reference={key:request[key] for key in ("session_id","step_id","phase","tare_capture_key")},
            observations=[dict(offset_ms=offset,**obs.evidence) for obs,offset in zip(observations,offsets,strict=True)])
        if request["phase"] == "RECONCILE":
            raw.update(protocol_version="1.2",capture_kind="WAREHOUSE_ASSEMBLY_RECON")
            raw["zero_reference"]["reconciliation_id"] = request["reconciliation_id"]
        return json.dumps(raw,ensure_ascii=True,sort_keys=True,separators=(",", ":")).encode()
