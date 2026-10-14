from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-11_ni072_st_defer/002_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace(" procedure context(p_st", " procedure history(p_st varchar2,p_actor varchar2,p_after number,p_result out clob);\n procedure context(p_st",1)
needle=" procedure apply_decision(p_operation"
at=s.index(needle,s.index("create or replace package body"))
s=s[:at]+""" procedure history(p_st varchar2,p_actor varchar2,p_after number,p_result out clob)is
  ware number;a json_array_t:=json_array_t();b json_object_t:=json_object_t();item json_object_t;n number:=0;last_version number;more boolean:=false;
 begin
  access_st(p_st,p_actor,'transport_dispatch_view',ware);
  if p_after is null or p_after<0 or trunc(p_after)!=p_after then raise_application_error(-20886,'ST_DEFER_HISTORY_CURSOR_REQUIRED');end if;
  for x in(select VERSION_NO,RESULT_JSON from RRL_ST_DEFER_DECISION where ST_NUMBER=p_st and WARE_ID=ware and VERSION_NO>p_after order by VERSION_NO fetch first 51 rows only)loop
   n:=n+1;if n>50 then more:=true;exit;end if;
   item:=json_object_t.parse(x.RESULT_JSON);a.append(item);last_version:=x.VERSION_NO;
  end loop;
  b.put('st_number',p_st);b.put('warehouse_id',ware);b.put('rows',a);b.put('has_more',more);
  if more then b.put('next_after_version',last_version);else b.put_null('next_after_version');end if;
  b.put('stock_changed',false);p_result:=b.to_clob;
 end;
"""+s[at:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/st_deferral.py");s=p.read_text(encoding="utf-8")
s+="""    def history(self,st: str,after: int,actor: str) -> dict:
        try:
            with self.gateway.transaction("ST deferral journal READ ONLY")as cur:
                cur.execute("set transaction read only");out=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_ST_DEFER_API.history",[st,actor,after,out]);return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:raise trip_error(exc)from exc
""";out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/contracts_st_deferral.py");s=p.read_text(encoding="utf-8").replace("    def context", "    def history(self,st: str,after: int,actor: str) -> dict: ...\n    def context");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/api/st_deferral_routes.py");s=p.read_text(encoding="utf-8")
s+="""
@router.get("/history")
def history(st_number: str=Query(min_length=1,max_length=100),after_version: int=Query(default=0,ge=0),
            user: AdminUser=Depends(require_permission("transport_dispatch_view")),
            service: StDeferralPort=Depends(st_deferral_service)) -> dict:
    try:return service.history(st_number,after_version,user.username)
    except TransportPlanError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc
""";out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
