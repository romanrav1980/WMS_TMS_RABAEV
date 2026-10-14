"""Transport success and mock acceptance do not prove a government business acknowledgment."""
from typing import Any

def adapter_request_evidence(row: dict[str,Any]) -> dict[str,Any]:
    signature=str(row.get("signature_status")or"").upper()
    identifiers=[str(row.get(key)or"").upper()for key in ("external_request_id","external_document_id")]
    simulated=signature.startswith("MOCK") or any(value.startswith("MOCK-")for value in identifiers)
    return {**row,"simulation":simulated,"external_ack_verified":False,
            "acknowledgment_kind":"SIMULATED" if simulated else "NOT_VERIFIED"}
