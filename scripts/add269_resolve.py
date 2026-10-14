from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-11_ni072_review/002_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace(" procedure append_review(p_actor", " procedure resolve(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob);\n procedure append_review(p_actor",1)
pos=s.index(" procedure append_review(p_actor",s.index("create or replace package body"))
resolver=""" procedure resolve(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob)is
  b json_object_t;f json_array_t:=json_array_t();resources json_array_t:=json_array_t();r json_object_t:=json_object_t();
  v_ware number;v_day date;v_zone varchar2(64);v_lock boolean:=false;
 begin
  if p_operation is null or lengthb(p_operation)>100 or p_body is null or dbms_lob.getlength(p_body)>4000 then raise_application_error(-20886,'DAY_REVIEW_RESOLVE_BOUND');end if;
  b:=json_object_t.parse(p_body);v_ware:=b.get_number('warehouse_id');v_day:=to_date(b.get_string('business_date'),'FXYYYY-MM-DD');v_zone:=b.get_string('timezone_region');
  access(v_ware,p_actor,'transport_dispatch_edit');
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.row_key(resources,'RRL_DAY_REVIEW',to_char(v_ware,'TM9')||':'||to_char(v_day,'YYYY-MM-DD')||':'||v_zone);
  RRL_STOCK_PLAN_HELPER.anchor(resources,70,'UNIQUE','DAY.REVIEW:'||p_operation);
  RRL_STOCK_LOCK_API.begin_plan;v_lock:=true;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(resources.to_clob);
  access(v_ware,p_actor,'transport_dispatch_edit');lookup(p_actor,p_operation,p_body,p_result);
  if p_result is null then r.put('operation_id',p_operation);r.put('state','NOT_RECORDED');r.put('day_closed',false);p_result:=r.to_clob;end if;
  RRL_STOCK_LOCK_API.clear_plan;
 exception when others then if v_lock then RRL_STOCK_LOCK_API.clear_plan;end if;raise;
 end;
"""
s=s[:pos]+resolver+s[pos:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/contracts_day_reviews.py");s=p.read_text(encoding="utf-8").replace("    def record(","    def resolve(self,operation: str,body: dict,actor: str) -> dict: ...\n    def record(");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py");s=p.read_text(encoding="utf-8")
pos=s.index("    def record(")
s=s[:pos]+"""    def resolve(self,operation: str,body: dict,actor: str) -> dict:
        try:
            with self.gateway.transaction("Resolve review outcome after original operation lock") as cur:
                require_warehouse(cur,body["warehouse_id"],actor,"transport_dispatch_edit")
                payload=cur.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,canonical(body))
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_DAY_REVIEW_API.resolve",[actor,operation,payload,result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code in (20882,20886):
                raise LogisticsCostError("DAY_REVIEW_RESOLVE_CONFLICT",str(exc),403 if code==20882 else 409) from exc
            raise

"""+s[pos:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/api/day_review_routes.py");s=p.read_text(encoding="utf-8");s+="""

@router.post("/reviews/resolve")
def resolve(body: ReviewBody,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
            service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.resolve(body.operation_id,body.model_dump(mode="json",exclude={"operation_id"}),user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
""";out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
