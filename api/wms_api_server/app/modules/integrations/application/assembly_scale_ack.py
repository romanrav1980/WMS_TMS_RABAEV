"""Archive ACK is distinct from READY/APPLIED or an uncertain stock result."""
from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any
from ..contracts_scales import ScaleGatewayError


def validate_assembly_ack(body: bytes, response: bytes) -> dict[str, Any]:
    try:
        source, response_body = json.loads(body), json.loads(response)
        archive = response_body["archive"]
        for field in ("device_id","capture_id","session_id","step_id","phase","device_policy_version","calibration_ref","measured_at"):
            if type(archive[field]) is not type(source[field]) or archive[field] != source[field]:
                raise ValueError()
        canonical = json.dumps(source,ensure_ascii=True,sort_keys=True,separators=(",", ":")).encode()
        identity = json.dumps([source["device_id"],source["capture_id"]],ensure_ascii=False,separators=(",", ":")).encode()
        if archive["source_sha256"] != hashlib.sha256(canonical).hexdigest().upper():
            raise ValueError()
        if archive["capture_key"] != hashlib.sha256(identity).hexdigest().upper():
            raise ValueError()
        if archive["status"] != "ARCHIVED" or archive["stock_posted"] is not False:
            raise ValueError()
        if not isinstance(archive["weight_kg"],str) or Decimal(archive["weight_kg"]) != Decimal(source["samples"][-1]["weight_kg"]):
            raise ValueError()
        if source["phase"] == "RECONCILE":
            if archive["reconciliation_id"] != source["reconciliation_id"] or archive["state"] not in {"COMPLETED","DISCREPANCY"}:
                raise ValueError()
            if response_body.get("posting") is not None:
                raise ValueError()
        return archive
    except (ValueError,TypeError,KeyError,IndexError,InvalidOperation):
        raise ScaleGatewayError("ASSEMBLY_CAPTURE_ACK_INVALID",True) from None
