raise SystemExit("Retired authoring generator: use final224 native/API owners/fresh checkpoint; do not overwrite capture")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni052_single_load_scope");out={}
out["wiki/database/nicora_ni052_single_scope_design_20261011.md"]="""# NI05.2: текущий склад самостоятельной погрузки
224 authoritative current active RUSERS/right/warehouse or GLOBAL_ADMIN checked against original legacy ST identifier. Existing loading read owner exposes assert_scope, used by Root LOAD_SHIPMENT before committed replay/after actual locks and by actor-aware preview. Authorization checks only original ST metadata, so old committed replay works after physical shipping; changed current warehouse/right denies saved replay. Same read-only Oracle transaction for authorized preview. Existing public port gains optional internal actor (public HTTP always authenticated actor), existing source/quantity/binding unchanged.
"""
s=(f/"000_before_rrl_stock_loading_read.sql").read_text(encoding="utf-8")
s=s.replace(" procedure describe_source"," procedure assert_scope(p_identifier varchar2,p_actor varchar2);\n procedure describe_source",1)
s=s.replace("function preview_json(p_identifier varchar2) return clob","function preview_json(p_identifier varchar2,p_actor varchar2 default null) return clob",1)
idx=s.index(" procedure describe_source",s.index("create or replace package body"))
helper=""" procedure assert_scope(p_identifier varchar2,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_SBORKA_PALLETS s join RUSERS u on u.ID=p_actor
   where s.PALLET_UID=p_identifier and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'stock_posting_shipping')=1
    and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN'or u.WARE_ID=s.WARE_ID);
  if n!=1 then raise_application_error(-20882,'SINGLE_LOAD_CURRENT_WARE_ACTOR_REQUIRED');end if;
 end;
"""
s=s[:idx]+helper+s[idx:]
s=s.replace("function preview_json(p_identifier varchar2) return clob is","function preview_json(p_identifier varchar2,p_actor varchar2 default null) return clob is",1)
anchor="  describe_source(p_identifier,'READ.LOADING'";assert anchor in s;s=s.replace(anchor,"  if p_actor is not null then assert_scope(p_identifier,p_actor);end if;\n"+anchor,1);out[str(f/"001_loading_read.sql")]=s
s=(f/"000_before_rrl_stock_posting_api.sql").read_text(encoding="utf-8");anchor="  assert_actor_active(p_actor);";assert s.count(anchor)==2;s=s.replace(anchor,anchor+"\n  if g_kind='LOAD_SHIPMENT'then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_LOADING_READ.assert_scope(doc.get_object('source').get_string('pallet_identifier'),p_actor);end;end if;");out[str(f/"002_root.sql")]=s
out[str(f/"003_recompile.sql")]="alter package RRL_STOCK_SINGLE_LOAD_CMD compile body;\nalter package RRL_STOCK_POSTING_API compile body;\n"
out[str(f/"apply.sql")]="@@001_loading_read.sql\n@@002_root.sql\n@@003_recompile.sql\n"
out[str(f/"rollback.sql")]="@@000_before_rrl_stock_loading_read.sql\n@@000_before_rrl_stock_posting_api.sql\n@@003_recompile.sql\n"
out[str(f/"verify.sql")]="select name,type,line,position,text from user_errors where name not like 'BIN$%';\nselect object_name,object_type from user_objects where status='INVALID';\n"
p=Path("api/wms_api_server/app/modules/transport/contracts.py");s=p.read_text(encoding="utf-8").replace("def preview_single(self, shipment_identifier: str)","def preview_single(self, shipment_identifier: str, actor: str | None = None)",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/api/loading_routes.py");s=p.read_text(encoding="utf-8").replace("return service.preview_single(shipment_identifier)","return service.preview_single(shipment_identifier,user.username)",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/loading.py");s=p.read_text(encoding="utf-8");s=s.replace("from ..contracts import TransportLoadingError","from ..contracts import TransportLoadingError\nfrom ...platform.public import read_oracle_json",1)
start=s.index("    def preview_single(");end=s.index("\n    def load_single(",start)
s=s[:start]+'''    def preview_single(self, shipment_identifier: str, actor: str | None = None) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Current warehouse standalone loading preview") as q:
                q.execute("set transaction read only")
                q.execute("select RRL_STOCK_LOADING_READ.preview_json(:identifier,:actor) from dual",
                          identifier=shipment_identifier,actor=actor)
                return read_oracle_json(q.fetchone()[0])
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==20882:
                raise TransportLoadingError("SINGLE_LOAD_FORBIDDEN",str(exc.args[0]).split("\\n",1)[0],status=403) from exc
            if code==1403 or 20800<=abs(code)<=20999:
                raise TransportLoadingError("SINGLE_LOAD_SOURCE_UNAVAILABLE",str(exc.args[0]).split("\\n",1)[0]) from exc
            raise
''' +s[end:];out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
