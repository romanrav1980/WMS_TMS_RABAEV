"""Vendor API bridge: no browser mass and no invented device measurements."""
from collections.abc import Callable
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from typing import Any

from ..contracts_scales import ScaleGatewayApi, ScaleGatewayError, ScaleOutbox


def validate_scale_ack(body: bytes, response: bytes) -> None:
    try:
        source, result = json.loads(body), json.loads(response)
        for field in ("device_id", "capture_id", "load_operation_id", "store_address"):
            if result[field] != source[field]:
                raise ValueError()
        identity = json.dumps([source["device_id"], source["capture_id"]], ensure_ascii=False, separators=(",", ":"))
        expected_key = hashlib.sha256(identity.encode("utf-8")).hexdigest().upper()
        if result["capture_key"] != expected_key or result["status"] != "ARCHIVED" or result["receipt_confirmed"] is not False:
            raise ValueError()
        if not re.fullmatch(r"[0-9A-F]{64}", result["capture_key"]):
            raise ValueError()
        canonical = json.dumps(source, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        if result["source_sha256"] != hashlib.sha256(canonical.encode("utf-8")).hexdigest().upper():
            raise ValueError()
        for field in ("device_policy_version", "calibration_ref", "measured_at"):
            if result[field] != source[field]:
                raise ValueError()
        expected_mass = Decimal(source["samples"][-1]["gross_weight_kg"])
        if Decimal(result["gross_weight_kg"]) != expected_mass:
            raise ValueError()
    except (ValueError, KeyError, TypeError, IndexError, InvalidOperation):
        raise ScaleGatewayError("SCALE_CAPTURE_ACK_INVALID", True) from None


def _validate_request_packet(request: dict[str, Any], packet: dict[str, Any], now: float) -> None:
    try:
        if request["state"] != "REQUESTED" or request["request_id"] != packet["capture_id"]:
            raise ValueError()
        for field in ("device_id", "load_operation_id", "store_address", "device_policy_version", "calibration_ref"):
            if request[field] != packet[field]:
                raise ValueError()
        expires = datetime.fromisoformat(request["expires_at"])
        if expires.tzinfo is None or expires <= datetime.fromtimestamp(now, timezone.utc):
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise ScaleGatewayError("SCALE_REQUEST_PACKET_MISMATCH") from None


class ScaleGatewayWorker:
    def __init__(self, api: ScaleGatewayApi, outbox: ScaleOutbox, device_id: str,
                 clock: Callable[[], float]) -> None:
        self.api, self.outbox, self.device_id, self.clock = api, outbox, device_id, clock

    def cycle(self, packet: bytes | None = None) -> dict[str, Any]:
        """Optional packet comes from vendor's actual API/SDK, never generated here."""
        requests = self.api.requests(self.device_id)
        if any(item.get("device_id") != self.device_id for item in requests):
            raise ScaleGatewayError("SCALE_POLL_DEVICE_MISMATCH")
        if packet is not None:
            try:
                source = json.loads(packet)
                if source["device_id"] != self.device_id:
                    raise ValueError()
                if not self.outbox.has_capture(source["device_id"], source["capture_id"]):
                    request = next(item for item in requests if item.get("request_id") == source["capture_id"])
                    _validate_request_packet(request, source, self.clock())
            except (ValueError, KeyError, TypeError, StopIteration):
                raise ScaleGatewayError("SCALE_ACTIVE_REQUEST_REQUIRED") from None
            self.outbox.stage(packet)
        delivery = self.outbox.claim(self.clock(), lease_seconds=30)
        if delivery is None:
            return {"status": "WAITING_FOR_VENDOR_PACKET", "pending_requests": len(requests)}
        try:
            response = self.api.post_capture(delivery.body)
            validate_scale_ack(delivery.body, response)
            self.outbox.acknowledge(delivery, response)
            return {"status": "ARCHIVED", "pending_requests": len(requests)}
        except ScaleGatewayError as exc:
            if exc.retryable:
                delay = min(300, 2 ** min(delivery.attempts, 8))
                self.outbox.defer(delivery, self.clock() + delay, exc.code)
            else:
                self.outbox.suspend(delivery, exc.code)
            return {"status": "RETRY_PENDING" if exc.retryable else "SUSPENDED", "error": exc.code}
