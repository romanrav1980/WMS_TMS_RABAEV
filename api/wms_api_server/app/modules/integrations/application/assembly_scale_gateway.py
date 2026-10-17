"""Durable assembly capture delivery; stock effects stay in native CASE posting."""
from collections.abc import Callable
from datetime import datetime, timezone
import json
from typing import Any
from ..contracts_scales import ScaleGatewayApi, ScaleOutbox, ScaleGatewayError
from .assembly_scale_ack import validate_assembly_ack


class AssemblyScaleWorker:
    def __init__(self, api: ScaleGatewayApi, outbox: ScaleOutbox, device: str, clock: Callable[[],float]) -> None:
        self.api,self.outbox,self.device,self.clock = api,outbox,device,clock

    def requests(self) -> list[dict[str,Any]]:
        items = self.api.requests(self.device)
        if len(items)>1 or any(item.get("device_id") != self.device for item in items):
            raise ScaleGatewayError("ASSEMBLY_REQUEST_DEVICE_MISMATCH")
        return items

    def cycle(self, packet: bytes | None = None) -> dict[str,Any]:
        requests = self.requests()
        if packet is not None:
            try:
                source = json.loads(packet)
                if source["device_id"] != self.device:
                    raise ValueError()
                if not self.outbox.has_capture(self.device,source["capture_id"]):
                    request = next(item for item in requests if item["capture_id"] == source["capture_id"])
                    for field in ("session_id","step_id","capture_id","phase","device_id","device_policy_version","calibration_ref"):
                        if source[field] != request[field]:
                            raise ValueError()
                    if source["phase"] == "RECONCILE" and source["reconciliation_id"] != request["reconciliation_id"]:
                        raise ValueError()
                    expiry = datetime.fromisoformat(request["expires_at"])
                    if expiry.tzinfo is None or expiry <= datetime.fromtimestamp(self.clock(),timezone.utc):
                        raise ValueError()
            except (ValueError,KeyError,TypeError,StopIteration):
                raise ScaleGatewayError("ASSEMBLY_CAPTURE_REQUEST_MISMATCH") from None
            self.outbox.stage(packet)
        delivery = self.outbox.claim(self.clock(),30)
        if delivery is None:
            return {"status":"WAITING_FOR_ASSEMBLY_REQUEST","requests":len(requests)}
        try:
            response = self.api.post_capture(delivery.body)
            validate_assembly_ack(delivery.body,response)
            self.outbox.acknowledge(delivery,response)
            return {"status":"CAPTURE_ARCHIVED","step_state":json.loads(response).get("step",{}).get("state"),
                    "stock_outcome":"NO_STOCK_EFFECT_RECONCILIATION" if json.loads(delivery.body)["phase"] == "RECONCILE" else "READ_STEP"}
        except ScaleGatewayError as exc:
            if exc.retryable:
                self.outbox.defer(delivery,self.clock()+min(300,2**min(delivery.attempts,8)),exc.code)
            else:
                self.outbox.suspend(delivery,exc.code)
            return {"status":"CAPTURE_RETRY_PENDING" if exc.retryable else "CAPTURE_SUSPENDED","error":exc.code}
