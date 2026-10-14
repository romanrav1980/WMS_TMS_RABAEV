from pathlib import Path
import json,hashlib
read=lambda p:Path(p).read_text(encoding="utf-8")
folder="db/migrations/2026-10-13_ni072_case_wait/"
files={}
def before(name,prefix="949",body="package_body"):
 p=f"tmp/{prefix}_{name.lower()}_{body}.sql"
 raw=read(p);files[folder+"000_before_"+name.lower()+".sql"]=raw
 return "\n".join(x for x in raw.splitlines()if x.strip())+"\n"
physical=before("RRL_ST_DEFER_PHYSICAL","948")
needle="  select count(*),sum(case"
assert physical.count(needle)==1
physical=physical.replace(needle,"""  select count(*)into bad from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS p on p.ID=c.LEGACY_SBORKA_PALLET_ID
   where p.ST_NUMBER=p_st and exists(select 1 from RRL_CASE_CARRIER_LOT l join RRL_REMAINS r on r.UID_POLETA=l.LOT_UID where l.CASE_PICK_TASK_ID=c.CASE_PICK_TASK_ID and(r.REMAIN>0 or r.HARD_RESERVED_BASE>0));
  if bad>0 then return RRL_ST_DEFER_CASE_WAIT.snapshot(p_st,p_ware,p_ignore_plan);end if;
"""+needle)
files[folder+"003_physical.sql"]=physical
defer=before("RRL_ST_DEFER_API")
needle="   or exists(select 1 from RRL_CASE_PICK_TASK c where c.LEGACY_SBORKA_PALLET_ID=p.ID)\n   or exists(select 1 from RRL_CUSTOMER_ORDER_FULFILLMENT f where f.LEGACY_SBORKA_PALLET_ID=p.ID and f.PICKED_CASE_TASK_ID is not null)"
assert defer.count(needle)==1
# Only remove CASE guards after the complete prepared physical snapshot has passed.
defer=defer.replace(needle,"")
needle="  if n>0 then raise_application_error(-20886,'ST_DEFER_UNLOADED_SUPPORTED_PHYSICAL_SOURCE_ONLY');end if;"
assert defer.count(needle)==1
defer=defer.replace(needle,needle+"""
  select count(*)into n from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS p on p.ID=c.LEGACY_SBORKA_PALLET_ID where p.ST_NUMBER=v_st;
  if n>0 then
   declare prep json_object_t:=json_object_t.parse(src).get_object('physical_preparation');begin
    if prep is null or nvl(prep.get_string('state'),'NONE')!='PREPARED_CASE'then raise_application_error(-20886,'ST_DEFER_PREPARED_CASE_REQUIRED');end if;
   end;
  end if;""")
files[folder+"004_deferral.sql"]=defer
api=before("RRL_ST_DEFER_WAIT_API")
needle="  arr:=json_object_t.parse(source).get_array('members');"
assert api.count(needle)==1
api=api.replace(needle,"""  declare prep json_object_t:=json_object_t.parse(source);src_case number;
  begin
   if prep.get_string('state')='PREPARED_CASE'then
    src_case:=prep.get_number('case_task_id');from_cell:=prep.get_string('cell');
    result.put('operation_id',p_operation);result.put('decision_operation_id',p_decision);result.put('st_number',decision.ST_NUMBER);
    result.put('warehouse_id',decision.WARE_ID);result.put('waiting_cell',target);
    if from_cell=target then skips.append(prep.get_string('pallet_identifier'));
    else
     select RRL_WAREHOUSE_TASK_SQ.nextval into task_id from dual;
     v:=json_object_t();v.put('task_id',task_id);v.put('pallet_identifier',prep.get_string('pallet_identifier'));v.put('case_pick_task_id',src_case);targets.append(v);
    end if;
    result.put('tasks',targets);result.put('already_waiting',skips);result.put('stock_changed',false);result.put('physical_move_completed',false);p_result:=result.to_clob;
    g_tx:=dbms_transaction.local_transaction_id(true);
    insert into RRL_ST_DEFER_WAIT_RUN(OPERATION_ID,DECISION_OPERATION_ID,ACTOR,REQUEST_JSON,RESULT_JSON)values(p_operation,p_decision,p_actor,request_body,p_result);
    if from_cell!=target then
     insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,
      FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY)
      values(task_id,'PUTAWAY','MANUAL',src_case,'ST_DEFER_CASE',decision.VERSION_NO,prep.get_string('pallet_identifier'),from_cell,target,decision.WARE_ID,decision.WARE_ID,1,'CASE','PALLET','PLANNED',p_actor);
     insert into RRL_ST_DEFER_WAIT_PLAN(TASK_ID,PLAN_OPERATION_ID,UID_PALLET,FROM_CELL,TARGET_CELL,BASE_QTY,BASE_UOM,STOCK_VERSION,SOURCE_MEMBERS_JSON,CASE_TASK_ID)
      values(task_id,p_operation,prep.get_string('pallet_identifier'),from_cell,target,1,'CASE',prep.get_number('content_version'),source,src_case);
    end if;
    g_tx:=null;RRL_STOCK_METADATA_TX.end_change;return;
   end if;
  end;
"""+needle)
files[folder+"005_wait_api.sql"]=api
move=before("RRL_STOCK_CASE_MOVE_CMD")
needle="  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;"
assert move.count(needle)==1
move=move.replace(needle,"  RRL_ST_DEFER_CASE_WAIT.plan_move(p_request,d.get_string('actor'),r,v);\n"+needle)
needle="  if system_flag is null or system_flag!=1 then raise_application_error(-20886,'CASE_CARRIER_CONTROL_OR_STAGING_ZONE_REQUIRED');end if;"
assert move.count(needle)==1
move=move.replace(needle,"""  if m.get_number('physical_task_id')is not null then
   RRL_ST_DEFER_CASE_WAIT.validate_move(p_request,p_actor,v.get_object('deferred_case_waiting'));
   if system_flag is null or system_flag!=0 then raise_application_error(-20886,'DEFER_CASE_ORDINARY_WAITING_CELL_REQUIRED');end if;
  elsif system_flag is null or system_flag!=1 then raise_application_error(-20886,'CASE_CARRIER_CONTROL_OR_STAGING_ZONE_REQUIRED');end if;""")
needle="j.put('content_version',ct.CONTENT_VERSION+1);j.put('status','MOVED');j.put('lots',a);p_result:=j.to_clob;"
assert move.count(needle)==1
move=move.replace(needle,needle+"\n  RRL_ST_DEFER_CASE_WAIT.finish_move(p_request,p_actor,p_result);")
files[folder+"006_case_move.sql"]=move
root=before("RRL_STOCK_POSTING_API")
needle="if g_kind in('CASE_PICK_CONFIRM','CASE_CARRIER_MOVE','CASE_CARRIER_RETURN','CASE_SHORT_APPROVE')then RRL_CASE_TASK_ACCESS.assert_command(p_request,p_actor);end if;"
assert root.count(needle)==2
root=root.replace(needle,needle+"\n  if g_kind='CASE_CARRIER_MOVE'then RRL_ST_DEFER_CASE_WAIT.assert_command(p_request,p_actor);end if;")
files[folder+"007_root.sql"]=root
files[folder+"001_table.sql"]="""alter table RRL_ST_DEFER_WAIT_PLAN add CASE_TASK_ID number(12,0);
alter table RRL_ST_DEFER_WAIT_PLAN add constraint RRL_DWAIT_CASE_FK foreign key(CASE_TASK_ID)references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID);
alter table RRL_ST_DEFER_WAIT_PLAN add constraint RRL_DWAIT_CASE_CK check(CASE_TASK_ID is null or(BASE_QTY=1 and BASE_UOM='CASE'));
"""
# Existing append-only planner guard owns the additive column, unchanged.
helper=read(folder+"002_case_wait.sql")
helper=helper.replace(" procedure finish_move(p_request", " procedure validate_move(p_request clob,p_actor varchar2,p_frozen json_object_t);\n procedure finish_move(p_request",1)
needle=" function snapshot(p_st"
position=helper.index(needle,helper.index("create or replace package body"))
helper=helper[:position]+""" function task_signature(t RRL_WAREHOUSE_TASK%rowtype)return varchar2 is v json_object_t:=json_object_t();begin
  v.put('status',t.STATUS);v.put('assigned',t.ASSIGNED_TO);v.put('resource',t.RESOURCE_ID);v.put('session',t.RESOURCE_SESSION_ID);v.put('equipment',t.EQUIPMENT_ID);
  v.put('started',to_char(t.STARTED_AT_INSTANT,'YYYY-MM-DD HH24:MI:SS.FF6TZH:TZM'));
  return lower(rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256)));
 end;
"""+helper[position:]
helper=helper.replace("RRL_STOCK_TASK_PLAN.signature(t)","task_signature(t)")
needle=" procedure plan_move(p_request"
position=helper.index(needle,helper.index("create or replace package body"))
helper=helper[:position]+""" procedure validate_move(p_request clob,p_actor varchar2,p_frozen json_object_t)is current_src json_object_t;copy_src json_object_t;begin
  describe(p_request,p_actor,current_src);
  if p_frozen is null then raise_application_error(-20886,'DEFER_CASE_ROOT_PLAN_REQUIRED');end if;
  copy_src:=json_object_t.parse(p_frozen.to_clob);copy_src.remove('sync_id');copy_src.remove('sync_key');
  if dbms_lob.compare(current_src.to_clob,copy_src.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: deferred CASE waiting source');end if;
 end;
"""+helper[position:]
# Only admitted scalar place quantity, original carrier and both location scans.
needle="  assert_command(p_request,p_actor);\n  select *into p"
assert helper.count(needle)==1
helper=helper.replace(needle,"""  assert_command(p_request,p_actor);
  if m.get_string('scanned_pallet')is null or m.get_string('scanned_pallet')!=m.get_string('scan_container')
   or m.get_string('scanned_from_cell')is null or m.get_string('fact_qty')is null or RRL_STOCK_MATH.quantity(m.get_string('fact_qty'))!=1
   or m.get_number('resource_id')is not null or m.get_number('resource_session_id')is not null or m.get_number('equipment_id')is not null
   or m.get_string('scan_draft_id')is not null or m.get_string('scanned_to_slot_code')is not null
   then raise_application_error(-20886,'DEFER_CASE_WHOLE_PLACE_SCANS_REQUIRED');end if;
  select *into p""")
needle="  select *into t from RRL_WAREHOUSE_TASK where TASK_ID=tid;\n  select d.*into dec"
helper=helper.replace(needle,"""  select *into t from RRL_WAREHOUSE_TASK where TASK_ID=tid;
  if m.get_string('scanned_from_cell')!=p.FROM_CELL then raise_application_error(-20886,'DEFER_CASE_ORIGINAL_SOURCE_SCAN_REQUIRED');end if;
  select d.*into dec""")
files[folder+"002_case_wait.sql"]=helper
files[folder+"apply.sql"]="\n".join("@@"+p for p in ("001_table.sql","002_case_wait.sql","003_physical.sql","004_deferral.sql","005_wait_api.sql","006_case_move.sql","007_root.sql","008_compile.sql","009_ledger.sql"))+"\n"
files[folder+"008_compile.sql"]="""begin
 for x in(select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_TYPE in('PACKAGE','PACKAGE BODY','TRIGGER','PROCEDURE','FUNCTION','VIEW')and OBJECT_NAME not like 'BIN$%')loop
  begin execute immediate 'alter '||case when x.OBJECT_TYPE='PACKAGE BODY'then'package'else lower(x.OBJECT_TYPE)end||' '||dbms_assert.simple_sql_name(x.OBJECT_NAME)||' compile'||case when x.OBJECT_TYPE='PACKAGE BODY'then' body'else''end;exception when others then null;end;
 end loop;
end;
/
"""
files[folder+"rollback.sql"]="""declare n number;begin select count(*)into n from RRL_ST_DEFER_WAIT_PLAN where CASE_TASK_ID is not null;if n>0 then raise_application_error(-20886,'CASE_WAIT_ROLLBACK_REGISTERED_TASKS_EXIST');end if;end;
/
"""+"\n".join("@@000_before_"+n.lower()+".sql"for n in ("RRL_STOCK_POSTING_API","RRL_STOCK_CASE_MOVE_CMD","RRL_ST_DEFER_WAIT_API","RRL_ST_DEFER_API","RRL_ST_DEFER_PHYSICAL"))+"""
drop package RRL_ST_DEFER_CASE_WAIT;
alter table RRL_ST_DEFER_WAIT_PLAN drop constraint RRL_DWAIT_CASE_FK;
alter table RRL_ST_DEFER_WAIT_PLAN drop constraint RRL_DWAIT_CASE_CK;
alter table RRL_ST_DEFER_WAIT_PLAN drop column CASE_TASK_ID;
@@008_compile.sql
"""
files[folder+"verify.sql"]="""select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_ST_DEFER_CASE_WAIT','RRL_ST_DEFER_PHYSICAL','RRL_ST_DEFER_API','RRL_ST_DEFER_WAIT_API','RRL_STOCK_CASE_MOVE_CMD','RRL_STOCK_POSTING_API');
select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%'order by NAME,SEQUENCE;
select TASK_ID,CASE_TASK_ID from RRL_ST_DEFER_WAIT_PLAN where CASE_TASK_ID is not null;
"""
p="api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py";body=read(p)
needle='    container = gateway.fetch_all('
assert body.count(needle)==1
body=body.replace(needle,"""    case_wait = gateway.fetch_all(
        "select p.CASE_TASK_ID,p.STOCK_VERSION,t.UID_PALLET,t.TO_CELL from RRL_ST_DEFER_WAIT_PLAN p "
        "join RRL_WAREHOUSE_TASK t on t.TASK_ID=p.TASK_ID where p.TASK_ID=:task and p.CASE_TASK_ID is not null",
        {"task": task_id})
    if case_wait:
        plan = case_wait[0]
        metadata.update({"physical_task_id": task_id, "scan_container": metadata.get("scanned_pallet"),
                         "target_cell": plan["to_cell"], "expected_content_version": int(plan["stock_version"])})
        if metadata.get("fact_qty") is None:
            metadata["fact_qty"] = "1"
        return _post_completion(StockCommand(operation_id=operation, command_type="CASE_CARRIER_MOVE",
            actor=actor, lines=(), source={"case_task_id": int(plan["case_task_id"])}, metadata=metadata))
"""+needle)
# Extract shared existing stock error mapping instead of duplicating it for new CASE branch.
start=body.index("    try:\n        return StockPosting().post(StockCommand(")
end=body.index("\n\n\ndef lock_domain",start)
old=body[start:end]
replacement="""    return _post_completion(StockCommand(
        operation_id=operation, command_type=command_type, actor=actor, lines=(),
        source={"type": "WAREHOUSE_TASK", "task_id": task_id}, metadata=metadata,
    ))


def _post_completion(command: StockCommand) -> dict[str, Any]:
    try:
        return StockPosting().post(command)
"""+old[old.index("    except StockPostingError"):].replace("exc.operation_id","exc.operation_id")
body=body[:start]+replacement+body[end:];files[p]=body
# Add source manifests and proportional recovery checkpoint before live apply.
files[folder+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-13-004-ni072-case-waiting","state":"PREPARED","recovery":"captured affected package bodies + additive column; no DB copy; rollback refuses registered CASE plans","target":"RABAEV/orcl","sha256":{p:hashlib.sha256(v.encode()).hexdigest()for p,v in files.items()}},indent=2)
print(json.dumps(files,ensure_ascii=True))
