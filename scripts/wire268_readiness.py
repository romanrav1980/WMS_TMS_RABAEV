from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/preparation_readiness.py");s=p.read_text(encoding="utf-8")
s=s.replace("s.DELIVERY_DATE,s.UTC_OFFSET_MINUTES,","s.DELIVERY_DATE,s.UTC_OFFSET_MINUTES,c.CUSTOMER_STORE_MAP_ID,")
s=s.replace("prepared,day,offset,future=header","prepared,day,offset,map_id,future=header")
s=s.replace("warehouse,header and _map_id(cur,order),day","warehouse,map_id,day")
s=s[:s.index("\ndef _map_id")]
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/application/ports.py");s=p.read_text(encoding="utf-8").replace("class PreparationPort(Protocol):","class PreparationPort(Protocol):\n    def readiness(self, order_id: int, actor: str) -> dict: ...")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py");s=p.read_text(encoding="utf-8").replace("    def prepare(self,", "    def readiness(self, order_id: int, actor: str) -> dict:\n        from .preparation_readiness import preparation_readiness\n        return preparation_readiness(self.gateway, order_id, actor)\n\n    def prepare(self,",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/store_calendar_rule.py");s=p.read_text(encoding="utf-8")
s=s.replace("s.DELIVERY_DATE,s.UTC_OFFSET_MINUTES","s.DELIVERY_DATE,s.UTC_OFFSET_MINUTES,\n            case when from_tz(cast(s.PICKING_FINISH_AT as timestamp),\n                case when s.UTC_OFFSET_MINUTES<0 then '-' else '+' end||\n                lpad(trunc(abs(s.UTC_OFFSET_MINUTES)/60),2,'0')||':'||\n                lpad(mod(abs(s.UTC_OFFSET_MINUTES),60),2,'0'))>systimestamp then 1 else 0 end")
s+="\n    if row[4] != 1:\n        raise StoreOrderConflict(\"SAP order picking deadline has passed\")\n"
out[str(p)]=s
out["api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py"]="""from fastapi import APIRouter, Depends, HTTPException
from ...platform.public import AdminUser, require_permission
from ..application.ports import PreparationPort
from .store_order_routes import preparation_service

router=APIRouter(prefix="/api/integrations/sap/store-orders",tags=["sap-store-orders"])

@router.get("/{order_id}/preparation-readiness")
def readiness(order_id: int,user: AdminUser=Depends(require_permission("customer_order_view")),
              service: PreparationPort=Depends(preparation_service)) -> dict:
    try:
        return service.readiness(order_id,user.username)
    except PermissionError as exc:
        raise HTTPException(403,str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404,str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409,str(exc)) from exc
"""
p=Path("api/wms_api_server/app/modules/fulfillment/public.py");s=p.read_text(encoding="utf-8");s+="\nfrom .api.preparation_read_routes import router as preparation_read_router\n";out[str(p)]=s
p=Path("api/wms_api_server/app/main.py");s=p.read_text(encoding="utf-8");s+="\nfrom .modules.fulfillment.public import preparation_read_router\napp.include_router(preparation_read_router)\n";out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sap-store-admission.js");s=p.read_text(encoding="utf-8")
s=s.replace("      const last=value.admission_decision?.last_decision;","      const readiness=await api('/api/integrations/sap/store-orders/'+id+'/preparation-readiness');if(token!==epoch)return;\n      const last=value.admission_decision?.last_decision;")
s=s.replace("      el('sapAdmissionHash').value=value.content_hash;","      el('sapPreparationReadiness').textContent=readiness.already_prepared?'СТ уже подготовлена. Используйте сохранённый результат.':readiness.ready_for_operator_layout?'Параметры готовы к операторской укладке. При подтверждении система проверит их снова.':'Подготовка СТ требует исправления: '+[...readiness.blockers,...readiness.lines.flatMap(line=>line.blockers.map(code=>line.articul+': '+code))].join('; ');\n      el('sapAdmissionHash').value=value.content_hash;")
s=s.replace("el('sapAdmissionDemand').replaceChildren();el('sapAdmissionHash').value='';","el('sapAdmissionDemand').replaceChildren();el('sapAdmissionHash').value='';el('sapPreparationReadiness').textContent='';")
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8").replace('<p id="sapAdmissionDetail"','<p id="sapPreparationReadiness" role="status"></p><p id="sapAdmissionDetail"',1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
