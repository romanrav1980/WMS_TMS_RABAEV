from pathlib import Path
import json,ast
root=Path("api/wms_api_server/app");out={}
out[str(root/"modules/integrations/domain/regulatory_delivery.py")]='''"""Transmission outcome is distinct from verified government acceptance."""
from dataclasses import dataclass
from ..contracts_regulatory import RegulatoryResponse

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
'''
p=root/"modules/integrations/public.py";out[str(p)]=p.read_text(encoding="utf-8")+"\nfrom .domain.regulatory_delivery import regulatory_delivery_decision\n"
p=root/"services/outbox_service.py";text=p.read_text(encoding="utf-8")
text=text.replace("from ..modules.integrations.public import RegulatoryAdapter,build_regulatory_adapter","from ..modules.integrations.public import RegulatoryAdapter,build_regulatory_adapter,regulatory_delivery_decision")
text=text.replace("            response = self.adapter.send(event)","            response = self.adapter.send(event)\n            decision=regulatory_delivery_decision(response)")
needle="                status=response.status,"
assert text.count(needle)==1
text=text.replace(needle,"                status=decision.request_status,\n                error_code=decision.error_code,\n                error_text=decision.error_text,")
text=text.replace("            self.mark_done(event_id)","            if decision.delivered:\n                self.mark_done(event_id)\n            else:\n                self.mark_error(event_id,error_text=decision.error_text or 'ADAPTER_RESPONSE_NOT_DELIVERED')",1)
needle='                "status": "DONE",'
assert text.count(needle)==1
text=text.replace(needle,'                "status": decision.request_status,\n                "error": decision.error_text,')
text=text.replace('"real_external_ack": response.real_external_ack and not self.adapter.simulated','"real_external_ack": decision.delivered and response.real_external_ack is True and not self.adapter.simulated')
text=text.replace("                   PAYLOAD_JSON,","                   to_clob(PAYLOAD_JSON) PAYLOAD_JSON,")
out[str(p)]=text
for path,text in out.items():ast.parse(text)
print(json.dumps(out,ensure_ascii=True))
