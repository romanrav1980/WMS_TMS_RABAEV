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
    def __init__(self, requested_mode: str="DISABLED") -> None:
        self.requested_mode=requested_mode
        self.requested_mode_supported=requested_mode in {"DISABLED","MOCK","REAL"}
        self.implementation_available=requested_mode in {"DISABLED","MOCK"}
        self.reason_code,self.next_action={
            "DISABLED":("REGULATORY_DISABLED","Обмен отключён. Реальная отправка будет доступна после реализации интеграционного шлюза."),
            "REAL":("PRODUCTION_CONNECTOR_NOT_IMPLEMENTED","Настроить интеграционный шлюз после его реализации. По решению владельца шлюз реализуется отдельно позже; одного URL или сертификата сейчас недостаточно."),
            "MOCK":("MOCK_NOT_ALLOWED","Имитация не разрешена. Только для тестового стенда требуются RETAILCASE_REGULATORY_MODE=MOCK и RETAILCASE_ALLOW_REGULATORY_MOCK=1.")
        }.get(requested_mode,("UNSUPPORTED_MODE","Исправьте RETAILCASE_REGULATORY_MODE: допустимы DISABLED, MOCK или REAL; интеграционный шлюз для REAL пока отсутствует."))
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
    mode=os.environ.get("RETAILCASE_REGULATORY_MODE","DISABLED").strip().upper()
    if mode=="MOCK"and os.environ.get("RETAILCASE_ALLOW_REGULATORY_MOCK")=="1":
        return MockRegulatoryAdapter()
    return DisabledRegulatoryAdapter(mode)

def regulatory_runtime_status() -> dict[str,Any]:
    adapter=build_regulatory_adapter()
    requested=os.environ.get("RETAILCASE_REGULATORY_MODE","DISABLED").strip().upper()
    reason=getattr(adapter,"reason_code","SIMULATION_ONLY")
    action=getattr(adapter,"next_action","Имитация не подтверждает подключение к государственной системе.")
    return {"mode":adapter.mode,"configured":adapter.configured,"simulation":adapter.simulated,
            "real_external_ack":False,"pending_events_preserved":not adapter.configured,
            "requested_mode":requested,"requested_mode_supported":requested in {"DISABLED","MOCK","REAL"},
            "implementation_available":requested in {"DISABLED","MOCK"},"reason_code":reason,"next_action":action,
            "message":"Имитация обмена; государственной квитанции нет." if adapter.simulated else action+" Исходящие сообщения сохранены."}
