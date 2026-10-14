from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-11_ni022_source_scope/001_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace('procedure begin_source(p_actor varchar2,p_permission varchar2,p_ware number);','procedure begin_source(p_actor varchar2,p_permission varchar2,p_ware number,p_order number default null);')
s=s.replace('procedure begin_source(p_actor varchar2,p_permission varchar2,p_ware number)is\n  f json_array_t:=json_array_t();','procedure begin_source(p_actor varchar2,p_permission varchar2,p_ware number,p_order number default null)is\n  f json_array_t:=json_array_t();r json_array_t:=json_array_t();')
s=s.replace('RRL_STOCK_LOCK_API.begin_plan;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);','''RRL_STOCK_LOCK_API.begin_plan;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);
  if p_order is not null then
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(p_order));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SAP_STORE_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(p_order));
  end if;
  RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);''')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/store_source_scope.py");s=p.read_text(encoding="utf-8").replace('[actor, permission, warehouse])\n                opened = True','[actor, permission, warehouse, order])\n                opened = True');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py");s=p.read_text(encoding="utf-8").replace("lock table RRL_SAP_STORE_ORDER in share row exclusive mode'","lock table RRL_SAP_STORE_ORDER in share row exclusive mode wait 3'");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py");s=p.read_text(encoding="utf-8").replace('for update of s.PREPARATION_HASH','for update of s.PREPARATION_HASH wait 3');out[str(p)]=s
p=Path("scripts/case265_source_scope.py");s=p.read_text(encoding="utf-8").replace(' finally:meta("update RUSERS set DELETED=1 where ID=:actor",actor=actor)',''' finally:
  q.callproc("RRL_STORE_ORDER_SCOPE.end_source");c.rollback()
  meta("update RUSERS set DELETED=1 where ID=:actor",actor=actor)''');out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
