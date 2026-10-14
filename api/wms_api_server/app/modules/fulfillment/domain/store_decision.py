"""Assumed normalized ERP gateway decision; never labelled a standard SAP IDoc."""
from hashlib import sha256
import re
import xml.etree.ElementTree as ET
from .store_order import scalar


def read_store_decision(raw: bytes) -> dict[str, object]:
    if not raw or len(raw) > 4 * 1024 * 1024:
        raise ValueError("Decision XML exceeds 4 MiB")
    text = raw.decode("utf-8-sig")
    if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper():
        raise ValueError("DTD/entities forbidden")
    root = ET.fromstring(text)
    names = {"Sender", "MessageId", "DecisionId", "OrderNumber", "OriginalContentHash",
             "ExpectedVersion", "Decision", "Reason", "Reference"}
    if root.tag.split("}")[-1] != "WarehouseCustomerOrderDecision" or root.get("version") != "1":
        raise ValueError("Expected WarehouseCustomerOrderDecision version=1")
    if any(node.tag.split("}")[-1] not in names for node in root):
        raise ValueError("Unknown decision field")
    fields = {name: scalar(root, name, 500 if name in {"Reason", "Reference"} else 100) for name in names}
    if not re.fullmatch("[a-f0-9]{64}", fields["OriginalContentHash"]):
        raise ValueError("OriginalContentHash must match immutable imported source")
    version = fields["ExpectedVersion"]
    if not version.isascii() or not version.isdigit() or len(version) > 9:
        raise ValueError("ExpectedVersion must be a nonnegative bounded integer")
    if fields["Decision"] not in {"ACCEPT", "REJECT"} or min(len(fields["Reason"]), len(fields["Reference"])) < 8:
        raise ValueError("Explicit ACCEPT/REJECT, reason and reference required")
    return {"sender": fields["Sender"], "message_id": fields["MessageId"], "decision_id": fields["DecisionId"],
            "order_number": fields["OrderNumber"], "original_content_hash": fields["OriginalContentHash"],
            "expected_version": int(version), "decision": fields["Decision"],
            "reason": fields["Reason"], "reference": fields["Reference"],
            "payload_hash": sha256(raw).hexdigest(), "raw_xml": text}
