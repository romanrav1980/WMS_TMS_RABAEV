"""Persist original warehouse samples before POST; no polling contract is invented."""
from collections.abc import Callable
from datetime import datetime
from ..contracts_scales import ScaleOutbox, ScaleTransport, ScaleGatewayError
from ..contracts_warehouse_gateway import WarehouseGatewayProfile
from .warehouse_scale_ack import validate_warehouse_ack, warehouse_packet


class WarehouseScaleGatewayWorker:
    def __init__(self, api: ScaleTransport, outbox: ScaleOutbox, profile: WarehouseGatewayProfile,
                 clock: Callable[[], float]) -> None:
        self.api, self.outbox, self.profile, self.clock = api, outbox, profile, clock

    def cycle(self, packet: bytes | None = None) -> dict[str, str]:
        if packet is not None:
            source = warehouse_packet(packet)
            retained_capture = self.outbox.has_capture(source["device_id"], source["capture_id"])
            fields = ("device_id", "post_cell", "basis") if retained_capture else (
                "device_id", "post_cell", "device_policy_version", "calibration_ref", "basis")
            for field in fields:
                if source[field] != getattr(self.profile, field):
                    raise ScaleGatewayError("WAREHOUSE_CAPTURE_PROFILE_MISMATCH")
            if not retained_capture:
                try:
                    measured = datetime.fromisoformat(source["measured_at"]).timestamp()
                except ValueError:
                    raise ScaleGatewayError("WAREHOUSE_CAPTURE_PACKET_INVALID") from None
                age = self.clock() - measured
                if age < -2 or age > 30:
                    raise ScaleGatewayError("WAREHOUSE_CAPTURE_EXPIRED")
            self.outbox.stage(packet)
        delivery = self.outbox.claim(self.clock(), lease_seconds=30)
        if delivery is None:
            return {"status": "WAITING_FOR_VENDOR_PACKET"}
        try:
            retained = warehouse_packet(delivery.body)
            # An original archived retry keeps its original policy/calibration; API resolves replay first.
            for field in ("device_id", "post_cell", "basis"):
                if retained[field] != getattr(self.profile, field):
                    raise ScaleGatewayError("WAREHOUSE_CAPTURE_PROFILE_MISMATCH")
            response = self.api.post_capture(delivery.body)
            validate_warehouse_ack(delivery.body, response, self.profile)
            self.outbox.acknowledge(delivery, response)
            return {"status": "ARCHIVED"}
        except ScaleGatewayError as exc:
            if exc.retryable:
                self.outbox.defer(delivery, self.clock() + min(300, 2 ** min(delivery.attempts, 8)), exc.code)
            else:
                self.outbox.suspend(delivery, exc.code)
            return {"status": "RETRY_PENDING" if exc.retryable else "SUSPENDED", "error": exc.code}
