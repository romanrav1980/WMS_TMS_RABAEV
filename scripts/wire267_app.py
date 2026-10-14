from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py");s=p.read_text(encoding="utf-8")
a=s.index('        cur.execute("""select cal.UTC_OFFSET_MINUTES,cal.DELIVERY_WEEKDAYS,');b=s.index('        local_day =',a)
s=s[:a]+'''        from .store_calendar_rule import delivery_rule
        proof=delivery_rule(cur,int(data['WarehouseId']),store[0],datetime.fromisoformat(data['DeliveryDate']))
        settings=(proof["utc_offset_minutes"],proof["delivery_weekdays"],proof["allow_same_day"])
        times=calendar(data,settings[0],settings[1],bool(settings[2]),received,proof["allowed"])
        times['calendar_basis']=proof["calendar_basis"]
        times['calendar_exception']=proof if proof.get("exception_state") else None
'''+s[b:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py");s=p.read_text(encoding="utf-8").replace("            if not row[4]:", "            from .store_calendar_rule import assert_current_order_calendar\n            assert_current_order_calendar(cur,order_id)\n            if not row[4]:",1)
s=s.replace("lock table RRL_ORDERS in share row exclusive mode'","lock table RRL_ORDERS in share row exclusive mode wait 3'");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/store_order_reads.py");s=p.read_text(encoding="utf-8").replace('        result["consistent_snapshot"] = True','        from .store_admission import read_admission\n        result["admission_decision"] = read_admission(cur, order, actor)\n        result["consistent_snapshot"] = True');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/public.py");s=p.read_text(encoding="utf-8")+'''
from .api.store_decision_routes import router as store_decision_router, store_admission_service
from .infrastructure.store_admission import StoreAdmission


def build_store_admission_service() -> StoreAdmission:
    return StoreAdmission(OracleGateway())
''';out[str(p)]=s
p=Path("api/wms_api_server/app/main.py");s=p.read_text(encoding="utf-8")
# Separate module router, composition only.
s+='''

from .modules.fulfillment.public import store_decision_router, store_admission_service, build_store_admission_service
app.include_router(store_decision_router)
app.dependency_overrides[store_admission_service] = build_store_admission_service
''';out[str(p)]=s
p=Path("api/wms_api_server/app/workers/sap_artmas_worker.py");s=p.read_text(encoding="utf-8").replace('from ..modules.fulfillment.public import build_store_order_service','from ..modules.fulfillment.public import build_store_order_service, build_store_admission_service')
s=s.replace("receiver = build_store_order_service() if kind == 'store' else","receiver = build_store_admission_service() if kind == 'store-decision' else build_store_order_service() if kind == 'store' else")
s=s.replace("('artmas', 'supply', 'ack', 'store')","('artmas', 'supply', 'ack', 'store', 'store-decision')")
s=s.replace("'store': DEFAULT_ROOT.parent/'sap_store_orders'","'store': DEFAULT_ROOT.parent/'sap_store_orders', 'store-decision': DEFAULT_ROOT.parent/'sap_store_decisions'");out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
