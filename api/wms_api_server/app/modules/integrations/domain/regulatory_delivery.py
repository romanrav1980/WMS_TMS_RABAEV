"""Transmission outcome is distinct from verified government acceptance."""
from dataclasses import dataclass
@dataclass(frozen=True)
class RegulatoryResponse:
    status: str
    external_status: str
    external_request_id: str|None
    external_document_id: str|None
    http_status: int|None
    response_json: str
    real_external_ack: bool=False

@dataclass(frozen=True)
class RegulatoryDeliveryDecision:
    delivered: bool
    request_status: str
    error_code: str|None=None
    error_text: str|None=None

def regulatory_delivery_decision(response: RegulatoryResponse) -> RegulatoryDeliveryDecision:
    code=response.http_status
    http_ok=code is None or isinstance(code,int)and not isinstance(code,bool)and 200<=code<300
    if isinstance(response.status,str)and response.status.strip().upper()=="DONE"and http_ok:
        return RegulatoryDeliveryDecision(True,"DONE")
    text=f"ADAPTER_RESPONSE_NOT_DELIVERED: status={response.status}; HTTP={code}; external={response.external_status}"
    return RegulatoryDeliveryDecision(False,"ERROR","ADAPTER_RESPONSE_NOT_DELIVERED",text)
