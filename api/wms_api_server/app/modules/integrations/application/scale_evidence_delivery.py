"""Durable provenance delivery is separate from capture and stock acceptance."""
from collections.abc import Callable
import hashlib
import json
from typing import Any
from ..contracts_scales import ScaleOutbox, ScaleGatewayError


def validate_evidence_ack(body: bytes, response: bytes) -> dict[str, Any]:
    try:
        source, result = json.loads(body), json.loads(response)
        canonical = json.dumps(source, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        for field in ("protocol_version", "capture_kind", "device_id", "capture_id", "capture_sha256"):
            if source[field] != result[field]:
                raise ValueError()
        if result["evidence_sha256"] != hashlib.sha256(canonical).hexdigest().upper():
            raise ValueError()
        if result["status"] != "ARCHIVED" or result["binding"] not in {"MATCHED", "PENDING"} or result["stock_posted"] is not False:
            raise ValueError()
        if result["provenance"] != "GATEWAY_REPORTED":
            raise ValueError()
        return result
    except (ValueError, TypeError, KeyError):
        raise ScaleGatewayError("OPC_EVIDENCE_ACK_INVALID", True) from None


def deliver_evidence(post: Callable[[bytes], bytes], outbox: ScaleOutbox, now: float) -> dict[str, Any]:
    delivery = outbox.claim(now, 30)
    if delivery is None:
        return {"status": "NO_PENDING_EVIDENCE"}
    try:
        response = post(delivery.body)
        result = validate_evidence_ack(delivery.body, response)
        outbox.acknowledge(delivery, response)
        return {"status": "EVIDENCE_ARCHIVED", "binding": result["binding"]}
    except ScaleGatewayError as exc:
        if exc.retryable:
            outbox.defer(delivery, now+min(300, 2**min(delivery.attempts, 8)), exc.code)
        else:
            outbox.suspend(delivery, exc.code)
        return {"status": "EVIDENCE_RETRY_PENDING" if exc.retryable else "EVIDENCE_SUSPENDED", "error": exc.code}
