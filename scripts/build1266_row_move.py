import json
from pathlib import Path
root="db/migrations/2026-10-14_ni022_prepared_row_move/"
files={root+"001_read.sql":Path("tmp/1266_read.sql").read_text(encoding="utf-8"),root+"003_command.sql":Path("tmp/1266_command.sql").read_text(encoding="utf-8")}
s=Path(root+"000_rrl_update_sborka_pallet_rows2.sql").read_text(encoding="utf-8")
point="BEGIN\n"
assert s.count(point)==1
branch="""BEGIN
 declare release_state varchar2(20);op varchar2(100);kind varchar2(80);request clob;d json_object_t;src json_object_t;
  source_row RRL_SBORKA_PALLET_ROWS%rowtype;target_row RRL_SBORKA_PALLET_ROWS%rowtype;target_id number;source_id number;n number;
 begin
  select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if release_state='ACTIVE'then
   op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
   if op is null then raise_application_error(-20863,'ST_ROW_MOVE_EXPLICIT_ROOT_REQUIRED');end if;
   select COMMAND_TYPE,CANONICAL_REQUEST into kind,request from RRL_STOCK_OPERATION where OPERATION_ID=op and STATE='IN_FLIGHT';
   d:=json_object_t.parse(request);src:=d.get_object('source');
   if kind!='ST_PREPARED_ROW_MOVE'or src.get_number('row_id')!=row_id_from then raise_application_error(-20863,'ST_ROW_MOVE_ROOT_SCOPE_REQUIRED');end if;
   select ID into target_id from RRL_SBORKA_PALLETS where PALLET_UID=PALLET_UID_to;
   if target_id!=src.get_number('target_shipment_id')then raise_application_error(-20863,'ST_ROW_MOVE_TARGET_SCOPE_REQUIRED');end if;
   select *into source_row from RRL_SBORKA_PALLET_ROWS where ID=row_id_from;
   select ID into source_id from RRL_SBORKA_PALLETS where PALLET_UID=source_row.PALLET_UID;
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(source_id)));
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(target_id)));
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLET_ROWS',RRL_STOCK_PLAN_HELPER.decimal_text(row_id_from)));
   select count(*)into n from RRL_SBORKA_PALLET_ROWS where PALLET_UID=PALLET_UID_to and ARTICUL=source_row.ARTICUL;
   if n=0 then
    update RRL_SBORKA_PALLET_ROWS set PALLET_UID=PALLET_UID_to,SELECTED=1 where ID=row_id_from;
    tmpVar:=row_id_from;
   elsif n=1 then
    select *into target_row from RRL_SBORKA_PALLET_ROWS where PALLET_UID=PALLET_UID_to and ARTICUL=source_row.ARTICUL;
    RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLET_ROWS',RRL_STOCK_PLAN_HELPER.decimal_text(target_row.ID)));
    update RRL_SBORKA_PALLET_ROWS set QUANTITY=QUANTITY+source_row.QUANTITY,ORDER_WEIGHT=ORDER_WEIGHT+source_row.ORDER_WEIGHT,
     PACK_COUNT=PACK_COUNT+source_row.PACK_COUNT,ORIGINAL_QUANTITY=nvl(ORIGINAL_QUANTITY,0)+nvl(source_row.ORIGINAL_QUANTITY,0),
     ORIGINAL_ORDER_WEIGHT=nvl(ORIGINAL_ORDER_WEIGHT,0)+nvl(source_row.ORIGINAL_ORDER_WEIGHT,0),SELECTED=1
     where ID=target_row.ID;
    delete from RRL_SBORKA_PALLET_ROWS where ID=row_id_from;tmpVar:=target_row.ID;
   else raise_application_error(-20887,'ST_ROW_MOVE_AMBIGUOUS_TARGET');end if;
   update RRL_SBORKA_PALLETS set PROOVED_BY_SCAN=0,PROOVED=0,KLADOVSHIK=d.get_string('actor') where ID in(source_id,target_id);
   return tmpVar;
  elsif release_state!='PREPARED'then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 end;
"""
# JSON object method must be assigned before SQL on Oracle19c.
branch=branch.replace("target_id number;source_id number;n number;","target_id number;source_id number;n number;actor_value varchar2(50);")
branch=branch.replace("update RRL_SBORKA_PALLETS set PROOVED_BY_SCAN=0,PROOVED=0,KLADOVSHIK=d.get_string('actor')","actor_value:=d.get_string('actor');\n   update RRL_SBORKA_PALLETS set PROOVED_BY_SCAN=0,PROOVED=0,KLADOVSHIK=actor_value")
files[root+"002_existing_writer.sql"]=s.replace(point,branch,1)
s=Path(root+"000_rrl_stock_posting_api.sql").read_text(encoding="utf-8")
point="  -- Immutable committed replay is considered"
assert point in s;s=s.replace(point,"  if g_kind='ST_PREPARED_ROW_MOVE'then declare doc json_object_t:=json_object_t.parse(p_request);w number;begin w:=RRL_ST_LAYOUT_READ.scope_order(doc.get_object('source').get_number('order_id'),p_actor,'outgoing_pallet_edit');end;end if;\n"+point,1)
point="   if g_kind='"
at=s.index(point);s=s[:at]+"   if g_kind='ST_PREPARED_ROW_MOVE'then RRL_STOCK_ST_ROW_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   els"+s[at+3:]
point="  if g_kind='"
at=s.index(point,s.index("procedure execute_prepared")) if "procedure execute_prepared" in s else -1
# Find the command-specific execution dispatch, never the earlier scope guard.
marker="RRL_STOCK_CASE_TYPE_CMD.execute_command"
line_start=s.rfind("\n",0,s.index(marker))+1
assert s[line_start:].startswith("  if ")
s=s[:line_start]+"  if g_kind='ST_PREPARED_ROW_MOVE'then RRL_STOCK_ST_ROW_CMD.execute_command(g_request,g_actor,p_result);\n  els"+s[line_start+2:]
files[root+"004_root.sql"]=s
files[root+"005_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1265-prepared-row-move' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit conserved prepared ST row transfer through existing writer and zero-stock Root journal',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
files[root+"apply.sql"]="@@001_read.sql\n@@002_existing_writer.sql\n@@003_command.sql\n@@004_root.sql\n@@005_ledger.sql\n"
files[root+"rollback.sql"]="""declare n number;begin
 select count(*)into n from RRL_STOCK_OPERATION where COMMAND_TYPE='ST_PREPARED_ROW_MOVE'and STATE='APPLIED';
 if n>0 then raise_application_error(-20863,'ST_LAYOUT_HISTORY_RETAIN_FORWARD_REPAIR_REQUIRED');end if;
end;
/
@@000_rrl_stock_posting_api.sql
@@000_rrl_update_sborka_pallet_rows2.sql
"""
files[root+"verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_ST_LAYOUT_READ','RRL_STOCK_ST_ROW_CMD','RRL_UPDATE_SBORKA_PALLET_ROWS2','RRL_STOCK_POSTING_API');\n"
print(json.dumps(files))

