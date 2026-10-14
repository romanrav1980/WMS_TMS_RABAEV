"""Missing production connector never silently becomes a successful mock delivery."""
from datetime import datetime,UTC
from typing import Any
import os,json
from ..contracts_regulatory import RegulatoryResponse,RegulatoryAdapter

class DisabledRegulatoryAdapter:
    mode="DISABLED"
    configured=False
    simulated=False
    signature_status="NOT_SIGNED"
    cert_alias=None
    cert_thumbprint=None
    def send(self,event: dict[str,Any]) -> RegulatoryResponse:
        raise RuntimeError("REGULATORY_CONNECTOR_NOT_CONFIGURED")

class MockRegulatoryAdapter:
    mode="MOCK"
    configured=True
    simulated=True
    signature_status="MOCK_NOT_SIGNED"
    cert_alias=None
    cert_thumbprint=None
    def send(self,event: dict[str,Any]) -> RegulatoryResponse:
        system=str(event.get("target_system")or"INTERNAL").upper()
        event_id=event.get("event_outbox_id")
        request=f"MOCK-{system}-REQ-{event_id}"
        document=f"MOCK-{system}-DOC-{event_id}"
        payload={"mock":True,"systemCode":system,"eventOutboxId":event_id,"eventType":event.get("event_type"),"externalRequestId":request,"externalDocumentId":document,"simulatedAt":datetime.now(UTC).isoformat(),"realExternalAck":False}
        return RegulatoryResponse("DONE","SIMULATED_ACCEPTED",request,document,200,json.dumps(payload,ensure_ascii=False),False)

def build_regulatory_adapter() -> RegulatoryAdapter:
    mode=os.environ.get("NICORA_REGULATORY_MODE","DISABLED").upper()
    if mode=="MOCK"and os.environ.get("NICORA_ALLOW_REGULATORY_MOCK")=="1":
        return MockRegulatoryAdapter()
    return DisabledRegulatoryAdapter()

def regulatory_runtime_status() -> dict[str,Any]:
    adapter=build_regulatory_adapter()
    return {"mode":adapter.mode,"configured":adapter.configured,"simulation":adapter.simulated,"real_external_ack":False,"pending_events_preserved":not adapter.configured,"requested_mode":os.environ.get("NICORA_REGULATORY_MODE","DISABLED").upper(),"message":"Имитация обмена; государственной квитанции нет." if adapter.simulated else "Реальный регуляторный адаптер не подключён. Исходящие сообщения сохранены."}
