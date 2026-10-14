import json
from pathlib import Path
out={}
p=Path("db/migrations/2026-10-12_ni072_shipping_inspection/002_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace(" procedure append_inspection(p_actor", " procedure resolve(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob);\n procedure append_inspection(p_actor",1)
pos=s.index(" procedure append_inspection(",s.index("create or replace package body"))
proc=""" procedure resolve(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob)is
  b json_object_t;parent RRL_DAY_REVIEW%rowtype;v_review varchar2(100);v_role varchar2(30);
  f json_array_t:=json_array_t();resources json_array_t:=json_array_t();result json_object_t:=json_object_t();v_lock boolean:=false;
 begin
  lookup(p_actor,p_operation,p_body,p_result);if p_result is not null then return;end if;
  b:=json_object_t.parse(p_body);v_review:=b.get_string('review_operation_id');v_role:=b.get_string('inspection_role');
  select *into parent from RRL_DAY_REVIEW where OPERATION_ID=v_review;access(parent.WARE_ID,p_actor,v_role);
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.row_key(resources,'RRL_DAY_REVIEW',to_char(parent.WARE_ID,'TM9')||':'||to_char(parent.BUSINESS_DATE,'YYYY-MM-DD')||':'||parent.TIMEZONE_REGION);
  RRL_STOCK_PLAN_HELPER.row_key(resources,'RRL_DAY_INSPECTION',v_review);
  RRL_STOCK_PLAN_HELPER.anchor(resources,70,'UNIQUE','DAY.INSPECTION:'||p_operation);
  RRL_STOCK_LOCK_API.begin_plan;v_lock:=true;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(resources.to_clob);
  access(parent.WARE_ID,p_actor,v_role);lookup(p_actor,p_operation,p_body,p_result);
  if p_result is null then result.put('operation_id',p_operation);result.put('state','NOT_RECORDED');result.put('day_closed',false);p_result:=result.to_clob;end if;
  RRL_STOCK_LOCK_API.clear_plan;
 exception when others then if v_lock then RRL_STOCK_LOCK_API.clear_plan;end if;raise;
 end;
"""
s=s[:pos]+proc+s[pos:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/day_inspections.py");s=p.read_text(encoding="utf-8")
pos=s.index("    def record(")
s=s[:pos]+"""    def resolve(self,operation: str,body: dict,actor: str) -> dict:
        try:
            with self.gateway.transaction("Resolve original shipping inspection operation") as cur:
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_DAY_INSPECT_API.resolve",[actor,operation,canonical(body),result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code in(20882,20886,20863):
                raise LogisticsCostError("DAY_INSPECTION_RESOLVE_REJECTED",str(exc.args[0]).split("\\n",1)[0],403 if code==20882 else 409)from exc
            raise

"""+s[pos:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/contracts_day_reviews.py");s=p.read_text(encoding="utf-8").replace("    def inspection(", "    def resolve_inspection(self,operation: str,body: dict,actor: str) -> dict: ...\n    def inspection(",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py");s=p.read_text(encoding="utf-8").replace("    def inspection(", """    def resolve_inspection(self,operation: str,body: dict,actor: str) -> dict:
        from .day_inspections import DayInspections
        return DayInspections(self.gateway).resolve(operation,body,actor)

    def inspection(""",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/api/day_review_routes.py");s=p.read_text(encoding="utf-8")
s+="""

@router.post("/shipping-inspections/resolve")
def resolve_inspection(body: InspectionBody,user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                       service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.resolve_inspection(body.operation_id,body.model_dump(exclude={"operation_id"}),user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id})from exc
"""
out[str(p)]=s
out["db/migrations/2026-10-12_ni072_shipping_inspection/apply_resolve696.sql"]="@002_api.sql\n"
print(json.dumps(out))
