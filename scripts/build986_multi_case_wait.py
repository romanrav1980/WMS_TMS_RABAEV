from pathlib import Path
import json,hashlib
read=lambda p:Path(p).read_text(encoding="utf-8");d="db/migrations/2026-10-13_ni072_multi_case_wait/";files={}
def captured(n,typ="package_body"):
 raw=read("tmp/985_"+n.lower()+"_"+typ+".sql");files[d+"000_before_"+n.lower()+"_"+typ+".sql"]=raw
 return "\n".join(x for x in raw.splitlines()if x.strip())+"\n"
spec=captured("RRL_ST_DEFER_CASE_WAIT","package");needle="p_ignore_plan varchar2 default null)return clob;";assert spec.count(needle)==1
files[d+"001_spec.sql"]=spec.replace(needle,"p_ignore_plan varchar2 default null,p_case_id number default null)return clob;")
body=captured("RRL_ST_DEFER_CASE_WAIT")
needle="function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null)return clob is";assert body.count(needle)==1
body=body.replace(needle,"function single_snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2,p_case_id number)return clob is")
needle="select count(*)into n from RRL_SBORKA_PALLETS where ST_NUMBER=p_st;";assert body.count(needle)==1
body=body.replace(needle,"select count(*)into n from RRL_SBORKA_PALLETS where ST_NUMBER=p_st and ID=(select LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_case_id);")
needle="where p.ST_NUMBER=p_st;";assert body.count(needle)==1
body=body.replace(needle,"where p.ST_NUMBER=p_st and c.CASE_PICK_TASK_ID=p_case_id;")
needle=" procedure assert_command(";pos=body.index(needle)
aggregate=""" function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null,p_case_id number default null)return clob is
  n number;case_id number;case_count number;total_lots number:=0;need_move boolean:=false;
  cases json_array_t:=json_array_t();child json_object_t;result json_object_t:=json_object_t();uid varchar2(200);
  type identifiers is table of pls_integer index by varchar2(200);seen identifiers;
 begin
  if p_case_id is not null then return single_snapshot(p_st,p_ware,p_ignore_plan,p_case_id);end if;
  select count(*)into n from RRL_SBORKA_PALLETS where ST_NUMBER=p_st;
  if n<1 or n>200 then raise_application_error(-20881,'DEFER_CASE_ST_MEMBER_BOUND_200');end if;
  for member in(select ID from RRL_SBORKA_PALLETS where ST_NUMBER=p_st order by ID)loop
   select count(*),min(CASE_PICK_TASK_ID)into case_count,case_id from RRL_CASE_PICK_TASK where LEGACY_SBORKA_PALLET_ID=member.ID;
   if case_count!=1 then raise_application_error(-20886,'DEFER_CASE_ALL_ST_MEMBERS_SINGLE_CASE_REQUIRED');end if;
   child:=json_object_t.parse(single_snapshot(p_st,p_ware,p_ignore_plan,case_id));
   total_lots:=total_lots+child.get_array('stocks').get_size;
   if total_lots>200 then raise_application_error(-20881,'DEFER_CASE_ST_TOTAL_LOT_BOUND_200');end if;
   uid:=child.get_string('pallet_identifier');if seen.exists(uid)then raise_application_error(-20886,'DEFER_CASE_DISTINCT_CARRIER_IDENTIFIERS_REQUIRED');end if;seen(uid):=1;
   if child.get_boolean('physical_move_required')then need_move:=true;end if;cases.append(child);
  end loop;
  if cases.get_size=1 then return treat(cases.get(0)as json_object_t).to_clob;end if;
  result.put('state','PREPARED_CASES');result.put('cases',cases);result.put('case_count',cases.get_size);result.put('lot_count',total_lots);
  result.put('physical_move_required',need_move);result.put('stock_changed',false);return result.to_clob;
 end;
"""
body=body[:pos]+aggregate+body[pos:]
needle="src:=snapshot(dec.ST_NUMBER,dec.WARE_ID,p.PLAN_OPERATION_ID);";assert body.count(needle)==1
body=body.replace(needle,"src:=snapshot(dec.ST_NUMBER,dec.WARE_ID,p.PLAN_OPERATION_ID,p.CASE_TASK_ID);")
needle="select count(*)into n from RRL_SBORKA_PALLETS where ST_NUMBER=dec.ST_NUMBER and(nvl(TRANSTASK_ID,-1)!=dec.TARGET_TT_ID or nvl(CONDITION,0)=2);";assert body.count(needle)==1
body=body.replace(needle,"""select count(*)into n from RRL_SBORKA_PALLETS s where s.ST_NUMBER=dec.ST_NUMBER and(nvl(s.TRANSTASK_ID,-1)!=dec.TARGET_TT_ID or nvl(s.CONDITION,0)=2
   or exists(select 1 from RRL_TT_HU_LOAD_ST ls join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID
    where ls.SBORKA_PALLET_ID=s.ID and ls.ACTIVE_FLAG=1 and l.STATUS in('LOADED','DEPARTED')));""")
files[d+"002_scope.sql"]=body
defer=captured("RRL_ST_DEFER_API");needle="nvl(prep.get_string('state'),'NONE')!='PREPARED_CASE'";assert defer.count(needle)==1
files[d+"003_deferral.sql"]=defer.replace(needle,"nvl(prep.get_string('state'),'NONE')not in('PREPARED_CASE','PREPARED_CASES')")
api=captured("RRL_ST_DEFER_WAIT_API")
start=api.index("  declare prep json_object_t:=json_object_t.parse(source);")
end=api.index("  arr:=json_object_t.parse(source).get_array('members');",start)
branch="""  declare prep json_object_t:=json_object_t.parse(source);src_case number;case_uid varchar2(200);case_version number;
   cases json_array_t:=json_array_t();child json_object_t;case_body clob;
   type origin_map is table of clob index by varchar2(100);origins origin_map;origin_key varchar2(100);
  begin
   if prep.get_string('state')in('PREPARED_CASE','PREPARED_CASES')then
    if prep.get_string('state')='PREPARED_CASE'then cases.append(prep);else cases:=prep.get_array('cases');end if;
    if cases is null or cases.get_size<1 or cases.get_size>200 then raise_application_error(-20881,'DEFER_WAIT_CASE_MEMBER_BOUND_200');end if;
    for i in 0..cases.get_size-1 loop
     child:=treat(cases.get(i)as json_object_t);src_case:=child.get_number('case_task_id');from_cell:=child.get_string('cell');case_uid:=child.get_string('pallet_identifier');
     origin_key:=RRL_STOCK_PLAN_HELPER.decimal_text(src_case);origins(origin_key):=child.to_clob;
     if from_cell=target then skips.append(case_uid);
     else
      select RRL_WAREHOUSE_TASK_SQ.nextval into task_id from dual;
      v:=json_object_t();v.put('task_id',task_id);v.put('pallet_identifier',case_uid);v.put('case_pick_task_id',src_case);targets.append(v);
     end if;
    end loop;
    result.put('operation_id',p_operation);result.put('decision_operation_id',p_decision);result.put('st_number',decision.ST_NUMBER);
    result.put('warehouse_id',decision.WARE_ID);result.put('waiting_cell',target);result.put('tasks',targets);result.put('already_waiting',skips);
    result.put('stock_changed',false);result.put('physical_move_completed',false);p_result:=result.to_clob;
    g_tx:=dbms_transaction.local_transaction_id(true);
    insert into RRL_ST_DEFER_WAIT_RUN(OPERATION_ID,DECISION_OPERATION_ID,ACTOR,REQUEST_JSON,RESULT_JSON)values(p_operation,p_decision,p_actor,request_body,p_result);
    for i in 0..targets.get_size-1 loop
     v:=treat(targets.get(i)as json_object_t);task_id:=v.get_number('task_id');src_case:=v.get_number('case_pick_task_id');
     child:=json_object_t.parse(origins(RRL_STOCK_PLAN_HELPER.decimal_text(src_case)));
     from_cell:=child.get_string('cell');case_uid:=child.get_string('pallet_identifier');case_version:=child.get_number('content_version');case_body:=child.to_clob;
     insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,
      FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY)
      values(task_id,'PUTAWAY','MANUAL',task_id,'ST_DEFER_CASE',decision.VERSION_NO,case_uid,from_cell,target,decision.WARE_ID,decision.WARE_ID,1,'CASE','PALLET','PLANNED',p_actor);
     insert into RRL_ST_DEFER_WAIT_PLAN(TASK_ID,PLAN_OPERATION_ID,UID_PALLET,FROM_CELL,TARGET_CELL,BASE_QTY,BASE_UOM,STOCK_VERSION,SOURCE_MEMBERS_JSON,CASE_TASK_ID)
      values(task_id,p_operation,case_uid,from_cell,target,1,'CASE',case_version,case_body,src_case);
    end loop;
    g_tx:=null;RRL_STOCK_METADATA_TX.end_change;return;
   end if;
  end;
"""
files[d+"004_planner.sql"]=api[:start]+branch+api[end:]
files[d+"005_compile.sql"]=read("db/migrations/2026-10-13_ni072_case_wait/008_compile.sql")
files[d+"006_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-007-ni072-multi-case-wait'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Prepared ST supports multiple standalone CASE places with bounded exact per-place frozen plans; sibling completion does not invalidate another case source',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
files[d+"apply.sql"]="@@001_spec.sql\n@@002_scope.sql\n@@003_deferral.sql\n@@004_planner.sql\n@@005_compile.sql\n@@006_ledger.sql\n"
files[d+"rollback.sql"]="@@000_before_rrl_st_defer_case_wait_package.sql\n@@000_before_rrl_st_defer_case_wait_package_body.sql\n@@000_before_rrl_st_defer_api_package_body.sql\n@@000_before_rrl_st_defer_wait_api_package_body.sql\n@@005_compile.sql\n"
files[d+"verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%';\nselect TASK_ID,CASE_TASK_ID,PLAN_OPERATION_ID from RRL_ST_DEFER_WAIT_PLAN where CASE_TASK_ID is not null order by TASK_ID;\n"
files[d+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-13-007-ni072-multi-case-wait","state":"PREPARED","target":"RABAEV/orcl","recovery":"captured current985 package spec/bodies + paired rollback; no stock history changes/copy","sha256":{p:hashlib.sha256(b.encode()).hexdigest()for p,b in files.items()}},indent=2)
page="""# NI07.2 — несколько CASE одной СТ

986 PREPARED, migration2026-10-13-007-ni072-multi-case-wait. Current985 spec/body sources captured, SHA/paired rollback/no DBcopy.

Existing ST deferral/WAIT_API/CASE mover reused. OneCASE still PREPARED_CASE with previous shape. Several fully prepared standalone CASEs produce PREPARED_CASES/cases[], each member has oneCASE and onePICKED FF/current ownWARE/complete carrier/own HARD. Up to200 members AND total200 physical lots, distinct carrier identifiers; no sum across different goods/UOM. Mixed FULLPAL/CASE, unfinished/nested/slots/capacity/resource sessions remain explicit refusals.

One plan run registers only needed movements; cases already waiting are recorded as skipped. Each WHT keeps its own immutable child source JSON/CASEID/version and self sourceTaskID; execution freezes that child and current global decision/trip/warehouse config/load state. First sibling completion changes its own CASE/FF/stock, so the second child can still execute against its unchanged source. Root keys/trip lock and current active-load check protect the source; original nativeCASE/ST/FF/lot/reserve/unit locks retained. Same existing Root movement finishes WHT/SYNC/outbox and one FF-version owner974.

No physical parent/residual is invented. Old single CASE plans/replays preserve their original body/shape. Rollback restores code but cannot erase registered multi-place history; unsupported older planner afterrollback needs explicit recovery planning. Need livecompile + private retained12/8 groupedST scenario; no fullsprint closure before actual.
"""
files["wiki/database/nicora_ni072_multi_case_wait_20261013.md"]=page
p="wiki/index.md";files[p]="- [NI07.2 multiCASE986](database/nicora_ni072_multi_case_wait_20261013.md): prepared per-place frozen source/one ST/allCASE/bounded200lots, live pending.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint986 PREPARED multiple standaloneCASE sameST; exactpermember frozenplans/current globaldecision/trip/config/load and perCASE currentstock; single shape kept, captured985/SHA/pairedrollback, no parent or quantity sum; actualapply pending.\n"
print(json.dumps(files,ensure_ascii=True))
