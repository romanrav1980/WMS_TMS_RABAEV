from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/integrations/public.py");s=p.read_text(encoding="utf-8");s+="""
from .contracts_regulatory import RegulatoryAdapter,RegulatoryResponse
from .infrastructure.regulatory_runtime import build_regulatory_adapter,MockRegulatoryAdapter,regulatory_runtime_status
from .api.regulatory_runtime_routes import router as regulatory_runtime_router,regulatory_runtime_service
""";out[p.as_posix()]=s
p=Path("api/wms_api_server/app/main.py");s=p.read_text(encoding="utf-8")
needle='app.include_router(sap_retail.router)'
assert needle in s
s=s.replace(needle,needle+'\napp.include_router(sap_retail.regulatory_runtime_router)\napp.dependency_overrides[sap_retail.regulatory_runtime_service]=sap_retail.regulatory_runtime_status',1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/services/outbox_service.py");s=p.read_text(encoding="utf-8")
s=s.replace('from .adapters.mock import MockRegulatoryAdapter','from ..modules.integrations.public import RegulatoryAdapter,build_regulatory_adapter')
s=s.replace('adapter: MockRegulatoryAdapter | None = None','adapter: RegulatoryAdapter | None = None')
s=s.replace('self.adapter = adapter or MockRegulatoryAdapter()','self.adapter = adapter if adapter is not None else build_regulatory_adapter()')
needle='        event_id = self.lock_next(worker_id=worker_id, target_system=target_system)'
assert needle in s
s=s.replace(needle,"""        if not self.adapter.configured:
            return {"status":"NOT_CONFIGURED","target_system":target_system,"event_outbox_id":None,"real_external_ack":False,"pending_events_preserved":True}
"""+needle,1)
s=s.replace('"external_status": response.external_status,','"external_status": response.external_status,\n                "simulation": self.adapter.simulated,\n                "real_external_ack": response.real_external_ack and not self.adapter.simulated,',1)
s=s.replace('                p_signature_status => :signature_status,','                p_cert_alias => :cert_alias,\n                p_cert_thumbprint => :cert_thumbprint,\n                p_signature_status => :signature_status,',1)
s=s.replace('"signature_status": "MOCK_NOT_SIGNED",','"signature_status": self.adapter.signature_status,\n                "cert_alias": self.adapter.cert_alias,\n                "cert_thumbprint": self.adapter.cert_thumbprint,',1)
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/workers/outbox_worker.py");s=p.read_text(encoding="utf-8")
needle='        if result is None:'
assert needle in s
s=s.replace(needle,"""        if result is not None and result.get("status")=="NOT_CONFIGURED":
            print_status(result)
            if not loop:
                return
            time.sleep(sleep_seconds)
            continue
"""+needle,1);out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
