from pathlib import Path
import json,hashlib,re
files={};folder="db/migrations/2026-10-13_ni072_place_selection/";mid="2026-10-13-012-ni072-place-selection"
def read(p):return Path(p).read_text(encoding="utf-8")
def captured(n,kind="package_body"):
 # Undo capture's Windows newline conversion without removing intentional blank source lines.
 return Path("tmp/1075_"+n.lower()+"_"+kind+".sql").read_bytes().decode("utf-8").replace("\r\r\n","\n").replace("\r\n","\n")
for name in("RRL_ST_DEFER_HU_WAIT","RRL_ST_DEFER_WAIT_API","RRL_ST_DEFER_PHYSICAL","RRL_ST_DEFER_API"):
 for kind in("package","package_body"):files[folder+"000_before_"+name.lower()+"_"+kind+".sql"]=captured(name,kind)
spec=captured("RRL_ST_DEFER_HU_WAIT","package")
spec=spec.replace("package RRL_STOCK_HU_TASK)as","package RRL_STOCK_HU_TASK,package RRL_ST_DEFER_PLACE_READ)as")
needle=" function snapshot(";pos=spec.index(needle)
spec=spec[:pos]+" function snapshot_root(p_st varchar2,p_ware number,p_root varchar2,p_ignore_plan varchar2 default null)return clob;\n"+spec[pos:]
spec=spec.replace("p_request out clob);","p_request out clob,p_root varchar2 default null);",1)
files[folder+"001_hu_scope_spec.sql"]=spec
place=r"""create or replace package RRL_ST_DEFER_PLACE_READ authid definer
 accessible by(package RRL_ST_DEFER_HU_WAIT,package RRL_ST_DEFER_WAIT_API)as
 function collect(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null,p_display boolean default false)return clob;
 function selected(p_st varchar2,p_ware number,p_root varchar2,p_ignore_plan varchar2 default null)return clob;
 function manifest(p_st varchar2)return json_array_t;
end;
/
create or replace package body RRL_ST_DEFER_PLACE_READ as
 function roots(p_st varchar2)return json_array_t is
  output json_array_t:=json_array_t();item json_object_t;v_case number;v_n number;v_parent varchar2(200);v_next varchar2(200);v_root varchar2(200);
  v_kind varchar2(20);v_steps number;v_members number:=0;
  type kind_map is table of varchar2(20)index by varchar2(200);seen kind_map;
 begin
  for member in(select ID from RRL_SBORKA_PALLETS where ST_NUMBER=p_st order by ID fetch first 201 rows only)loop
   v_members:=v_members+1;if v_members>200 then raise_application_error(-20881,'DEFER_PLACE_ST_MEMBER_BOUND_200');end if;
   select count(*),min(CASE_PICK_TASK_ID)into v_n,v_case from RRL_CASE_PICK_TASK where LEGACY_SBORKA_PALLET_ID=member.ID;
   if v_n!=1 then raise_application_error(-20886,'DEFER_PLACE_COMPLETED_CASE_MEMBERS_REQUIRED');end if;
   select count(*),min(PARENT_UID)into v_n,v_parent from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=v_case and ACTIVE_FLAG=1;
   if v_n>1 then raise_application_error(-20886,'DEFER_PLACE_ONE_PARENT_REQUIRED');end if;
   if v_n=0 then v_root:='CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(v_case);v_kind:='CASE';
   else
    v_kind:='HU';v_steps:=0;
    loop
     v_steps:=v_steps+1;if v_steps>200 then raise_application_error(-20886,'DEFER_PLACE_PARENT_BOUND_200');end if;
     select count(*),min(PARENT_UID)into v_n,v_next from RRL_WMS_HU_LINK where CHILD_PALLET_UID=v_parent and ACTIVE_FLAG=1;
     exit when v_n=0;
     if v_n!=1 then raise_application_error(-20886,'DEFER_PLACE_ONE_TOP_PARENT_REQUIRED');end if;v_parent:=v_next;
    end loop;
    v_root:=v_parent;
   end if;
   if seen.exists(v_root)then
    if seen(v_root)!=v_kind then raise_application_error(-20886,'DEFER_PLACE_ROOT_IDENTIFIER_AMBIGUOUS');end if;
   else
    seen(v_root):=v_kind;item:=json_object_t();item.put('root_identifier',v_root);item.put('place_kind',v_kind);
    if v_kind='CASE'then item.put('case_task_id',v_case);end if;output.append(item);
   end if;
  end loop;
  if v_members=0 then raise_application_error(-20886,'DEFER_PLACE_REGISTERED_ST_REQUIRED');end if;
  return output;
 end;

 function source_for(p_st varchar2,p_ware number,p_root json_object_t,p_ignore varchar2)return clob is
 begin
  if p_root.get_string('place_kind')='CASE'then
   return RRL_ST_DEFER_CASE_WAIT.snapshot(p_st,p_ware,p_ignore,p_root.get_number('case_task_id'));
  end if;
  return RRL_ST_DEFER_HU_WAIT.snapshot_root(p_st,p_ware,p_root.get_string('root_identifier'),p_ignore);
 end;

 function selected(p_st varchar2,p_ware number,p_root varchar2,p_ignore_plan varchar2 default null)return clob is
  items json_array_t:=roots(p_st);item json_object_t;
 begin
  if p_root is null or trim(p_root)!=p_root or length(p_root)>200 then raise_application_error(-20886,'DEFER_PLACE_ROOT_REQUIRED');end if;
  for i in 0..items.get_size-1 loop
   item:=treat(items.get(i)as json_object_t);
   if item.get_string('root_identifier')=p_root then return source_for(p_st,p_ware,item,p_ignore_plan);end if;
  end loop;
  raise_application_error(-20886,'DEFER_PLACE_ROOT_OUTSIDE_CURRENT_ST');
 end;

 function collect(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null,p_display boolean default false)return clob is
  items json_array_t;item json_object_t;source json_object_t;outcome json_object_t:=json_object_t();v_nested number;
  v_cases number:=0;v_lots number:=0;v_members number;v_ignore varchar2(100);v_uid varchar2(200);v_case number;v_task number;v_count number;
  v_plan_source clob;v_target varchar2(50);v_open boolean;v_move boolean:=false;
 begin
  if not p_display then
   select count(*)into v_nested from RRL_WMS_HU_LINK h join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=h.CHILD_CASE_TASK_ID
    join RRL_SBORKA_PALLETS st on st.ID=ct.LEGACY_SBORKA_PALLET_ID where st.ST_NUMBER=p_st and h.ACTIVE_FLAG=1;
   if v_nested=0 then return null;end if;
  end if;
  items:=roots(p_st);
  for i in 0..items.get_size-1 loop
   item:=treat(items.get(i)as json_object_t);v_uid:=item.get_string('root_identifier');v_case:=item.get_number('case_task_id');
   v_ignore:=p_ignore_plan;v_task:=null;v_open:=false;
   if p_display then
    select count(*),min(p.PLAN_OPERATION_ID),min(p.TASK_ID)into v_count,v_ignore,v_task
     from RRL_ST_DEFER_WAIT_PLAN p join RRL_ST_DEFER_WAIT_RUN wr on wr.OPERATION_ID=p.PLAN_OPERATION_ID
     join RRL_ST_DEFER_DECISION d on d.OPERATION_ID=wr.DECISION_OPERATION_ID join RRL_WAREHOUSE_TASK t on t.TASK_ID=p.TASK_ID
     join RRL_RECEIPT_WARE_SETTINGS cfg on cfg.WARE_ID=d.WARE_ID
     where d.ST_NUMBER=p_st and d.VERSION_NO=(select max(VERSION_NO)from RRL_ST_DEFER_DECISION where ST_NUMBER=p_st)
      and t.STATUS not in('DONE','CANCELLED')and p.TARGET_CELL=cfg.DEFER_WAIT_CELL
      and((v_case is not null and p.CASE_TASK_ID=v_case)or(v_case is null and p.UID_PALLET=v_uid and p.BASE_UOM='HU'));
    if v_count>1 then v_ignore:=null;v_task:=null;end if;
   end if;
   begin
    source:=json_object_t.parse(source_for(p_st,p_ware,item,v_ignore));
    item.put('source',source);
    if p_display and v_task is not null then
     select SOURCE_MEMBERS_JSON into v_plan_source from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=v_task;
     if dbms_lob.compare(v_plan_source,source.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: current planned place');end if;
     item.put('planned_task_id',v_task);
    end if;
    if source.get_string('state')='PREPARED_CASE'then v_cases:=v_cases+1;v_lots:=v_lots+source.get_array('stocks').get_size;
    else v_cases:=v_cases+source.get_number('case_count');v_lots:=v_lots+source.get_number('lot_count');end if;
    if v_lots>200 then raise_application_error(-20881,'DEFER_PLACE_TOTAL_LOT_BOUND_200');end if;
    if source.get_boolean('physical_move_required')then v_move:=true;end if;
   exception when others then
    if not p_display then raise;end if;
    item.remove('source');item.put('blocked',true);item.put('reason_code',sqlcode);
   end;
   items.put(i,item);
  end loop;
  select count(*)into v_members from RRL_SBORKA_PALLETS where ST_NUMBER=p_st;
  if not p_display and v_cases!=v_members then raise_application_error(-20886,'DEFER_PLACE_EXACT_ST_COVERAGE_REQUIRED');end if;
  if not p_display and items.get_size=1 then return treat(items.get(0)as json_object_t).get_object('source').to_clob;end if;
  outcome.put('state','PREPARED_PLACES');outcome.put('places',items);outcome.put('case_count',v_cases);outcome.put('lot_count',v_lots);
  outcome.put('physical_move_required',v_move);outcome.put('stock_changed',false);return outcome.to_clob;
 end;

 function manifest(p_st varchar2)return json_array_t is
  values_json json_array_t:=json_array_t();item json_object_t;v_count number:=0;v_rows number:=0;cargo json_array_t;line json_object_t;
 begin
  for member in(select ID,PALLET_UID,WARE_ID,TRANSTASK_ID,CONDITION from RRL_SBORKA_PALLETS where ST_NUMBER=p_st order by ID fetch first 201 rows only)loop
   v_count:=v_count+1;if v_count>200 then raise_application_error(-20881,'DEFER_PLACE_MANIFEST_BOUND_200');end if;
   item:=json_object_t();item.put('id',member.ID);item.put('identifier',member.PALLET_UID);item.put('warehouse',member.WARE_ID);
   item.put('trip',member.TRANSTASK_ID);item.put('condition',member.CONDITION);cargo:=json_array_t();
   for row_item in(select ID,ARTICUL,EI,QUANTITY,PACK_COUNT,ORDER_WEIGHT from RRL_SBORKA_PALLET_ROWS where PALLET_UID=member.PALLET_UID order by ID fetch first 1001 rows only)loop
    v_rows:=v_rows+1;if v_rows>1000 then raise_application_error(-20881,'DEFER_PLACE_MANIFEST_CARGO_BOUND_1000');end if;
    line:=json_object_t();line.put('id',row_item.ID);line.put('article',row_item.ARTICUL);line.put('unit',row_item.EI);
    line.put('quantity',row_item.QUANTITY);line.put('packs',row_item.PACK_COUNT);line.put('weight',row_item.ORDER_WEIGHT);cargo.append(line);
   end loop;
   item.put('cargo',cargo);values_json.append(item);
  end loop;
  return values_json;
 end;
end;
/
"""
files[folder+"002_place_read.sql"]=place
helper=captured("RRL_ST_DEFER_HU_WAIT")
helper=helper.replace(" function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null)return clob is",
 " function snapshot_root(p_st varchar2,p_ware number,p_root varchar2,p_ignore_plan varchar2 default null)return clob is",1)
start=helper.index("  select count(*),min(h.PARENT_UID)");end=helper.index("  if p_ignore_plan is not null then",start)
helper=helper[:start]+"  root_uid:=p_root;\n"+helper[end:]
helper=helper.replace("if case_count!=members then","if case_count<1 or case_count>members then",1)
needle=" procedure describe(";pos=helper.index(needle)
wrapper=""" function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null)return clob is begin
  return RRL_ST_DEFER_PLACE_READ.collect(p_st,p_ware,p_ignore_plan);
 end;
"""
helper=helper[:pos]+wrapper+helper[pos:]
helper=helper.replace("p_task number,p_value out json_object_t)is","p_task number,p_value out json_object_t,p_root varchar2 default null,p_manifest boolean default true)is",1)
helper=helper.replace("ignore_plan varchar2(100);own number;admin_flag number;","ignore_plan varchar2(100);own number;admin_flag number;v_root varchar2(200):=p_root;",1)
helper=helper.replace("   ignore_plan:=plan.PLAN_OPERATION_ID;", "   ignore_plan:=plan.PLAN_OPERATION_ID;v_root:=plan.UID_PALLET;",1)
helper=helper.replace("  source:=snapshot(dec.ST_NUMBER,dec.WARE_ID,ignore_plan);","""  if v_root is null then source:=snapshot(dec.ST_NUMBER,dec.WARE_ID,ignore_plan);
  else source:=RRL_ST_DEFER_PLACE_READ.selected(dec.ST_NUMBER,dec.WARE_ID,v_root,ignore_plan);end if;""",1)
helper=helper.replace("  p_value:=json_object_t.parse(source);", "  p_value:=json_object_t.parse(source);\n  if p_manifest then p_value.put('cohort_manifest',RRL_ST_DEFER_PLACE_READ.manifest(dec.ST_NUMBER));end if;",1)
helper=helper.replace("p_request out clob)is","p_request out clob,p_root varchar2 default null)is",1)
old="  raw_source:=snapshot(dec.ST_NUMBER,dec.WARE_ID);if raw_source is null then return;end if;\n  describe(p_decision,p_actor,null,value);"
assert old in helper
helper=helper.replace(old,"""  if p_root is null then raw_source:=snapshot(dec.ST_NUMBER,dec.WARE_ID);
  else raw_source:=RRL_ST_DEFER_PLACE_READ.selected(dec.ST_NUMBER,dec.WARE_ID,p_root);end if;
  if raw_source is null then return;end if;value:=json_object_t.parse(raw_source);
  if value.get_string('state')='PREPARED_PLACES'then raise_application_error(-20886,'DEFER_WAIT_ROOT_SELECTION_REQUIRED');end if;
  if value.get_string('state')='PREPARED_CASE'then return;end if;
  describe(p_decision,p_actor,null,value,p_root);""")
helper=helper.replace("  meta.put('defer_decision_operation_id',p_decision);", "  if p_root is not null then meta.put('defer_requested_root',p_root);end if;\n  meta.put('defer_decision_operation_id',p_decision);",1)
helper=helper.replace("   describe(decision,d.get_string('actor'),null,value);","""   describe(decision,d.get_string('actor'),null,value,meta.get_string('defer_requested_root'));
   if value.get_string('state')='PREPARED_PLACES'then raise_application_error(-20886,'DEFER_WAIT_ROOT_SELECTION_REQUIRED');end if;""",1)
# Current helper gets a selected root from the task, while default planning still checks the complete single-root source.
helper=helper.replace("describe(p_frozen.get_string('decision_operation_id'),p_actor,p_task,current_value);",
 "describe(p_frozen.get_string('decision_operation_id'),p_actor,p_task,current_value,p_frozen.get_string('root'),p_frozen.has('cohort_manifest'));",1)
# Row-lock only the actual member rows participating in this root, already declared by its CASE bindings.
old="  cases:=p_frozen.get_array('cases');v_st_number:=p_frozen.get_string('st_number');\n  for x in(select s.ID from RRL_SBORKA_PALLETS s where s.ST_NUMBER=v_st_number order by s.ID)loop"
new="""  cases:=p_frozen.get_array('cases');v_st_number:=p_frozen.get_string('st_number');v_case_json:=cases.to_clob;
  for x in(select s.ID from RRL_SBORKA_PALLETS s join json_table(v_case_json,'$[*]'columns(st_member_id number path '$.st_member_id'))j on j.st_member_id=s.ID
    where s.ST_NUMBER=v_st_number order by s.ID)loop"""
assert old in helper;helper=helper.replace(old,new)
helper=helper.replace("v_st_number varchar2(100);row_busy", "v_st_number varchar2(100);v_case_json clob;row_busy",1)
files[folder+"003_hu_scope.sql"]=helper
spec=captured("RRL_ST_DEFER_WAIT_API","package")
spec=spec.replace("p_result out clob);", "p_result out clob,p_root varchar2 default null);",1)
pos=spec.rfind("end;")
spec=spec[:pos]+" procedure read_places(p_decision varchar2,p_actor varchar2,p_result out clob);\n"+spec[pos:]
files[folder+"004_wait_spec.sql"]=spec
api=captured("RRL_ST_DEFER_WAIT_API")
api=api.replace("p_result out clob)is","p_result out clob,p_root varchar2 default null)is",1)
api=api.replace("request.put('actor',p_actor);request_body:=", "request.put('actor',p_actor);if p_root is not null then request.put('root_identifier',p_root);end if;request_body:=",1)
api=api.replace("request_plan(p_operation,p_decision,p_actor,hu_request);","request_plan(p_operation,p_decision,p_actor,hu_request,p_root);",1)
needle="  source:=RRL_ST_DEFER_PHYSICAL.snapshot(decision.ST_NUMBER,decision.WARE_ID);";assert api.count(needle)==1
api=api.replace(needle,"""  if p_root is null then source:=RRL_ST_DEFER_PHYSICAL.snapshot(decision.ST_NUMBER,decision.WARE_ID);
  else source:=RRL_ST_DEFER_PLACE_READ.selected(decision.ST_NUMBER,decision.WARE_ID,p_root);end if;
  if p_root is not null then result.put('root_identifier',p_root);end if;""")
# Root's immutable plan receipt must preserve the optional selection in the original command contract.
needle="  req.put('decision_operation_id',decision);req.put('actor',d.get_string('actor'));";assert api.count(needle)==1
api=api.replace(needle,needle+"""
  if d.get_object('metadata').get_string('defer_requested_root')is not null then
   req.put('root_identifier',d.get_object('metadata').get_string('defer_requested_root'));
   result.put('root_identifier',d.get_object('metadata').get_string('defer_requested_root'));
  end if;""")
api=api.replace("value.remove('decision_version');value.remove('target_trip');value.remove('target_cell');source:=",
 "value.remove('decision_version');value.remove('target_trip');value.remove('target_cell');value.remove('cohort_manifest');source:=",1)
reader=r"""
 procedure read_places(p_decision varchar2,p_actor varchar2,p_result out clob)is
  dec RRL_ST_DEFER_DECISION%rowtype;v_n number;full_value json_object_t;items json_array_t;out_items json_array_t:=json_array_t();
  item json_object_t;value json_object_t;out_item json_object_t;summary json_object_t:=json_object_t();need_choice boolean:=false;has_hu boolean:=false;has_planned boolean:=false;
 begin
  select *into dec from RRL_ST_DEFER_DECISION where OPERATION_ID=p_decision;
  select count(*)into v_n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'warehouse_task_view')=1
   and(u.WARE_ID=dec.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if v_n!=1 then raise_application_error(-20882,'DEFER_PLACE_CURRENT_WARE_VIEW_REQUIRED');end if;
  select count(*)into v_n from RRL_ST_DEFER_DECISION where ST_NUMBER=dec.ST_NUMBER and VERSION_NO>dec.VERSION_NO;
  if v_n>0 then summary.put('places',out_items);summary.put('selection_required',false);summary.put('unavailable_reason','DECISION_SUPERSEDED');p_result:=summary.to_clob;return;end if;
  begin
   full_value:=json_object_t.parse(RRL_ST_DEFER_PLACE_READ.collect(dec.ST_NUMBER,dec.WARE_ID,null,true));items:=full_value.get_array('places');
   for i in 0..items.get_size-1 loop
    item:=treat(items.get(i)as json_object_t);out_item:=json_object_t();
    out_item.put('root_identifier',item.get_string('root_identifier'));out_item.put('place_kind',item.get_string('place_kind'));
    if item.get_string('place_kind')='HU'then has_hu:=true;end if;
    if item.has('blocked')then out_item.put('available',false);out_item.put('reason','CURRENT_SOURCE_OR_OPEN_TASK_REQUIRES_REVIEW');
    else
     value:=item.get_object('source');out_item.put('cell',value.get_string('cell'));out_item.put('content_version',value.get_number('content_version'));
     out_item.put('move_required',value.get_boolean('physical_move_required'));out_item.put('available',true);
     if item.get_number('planned_task_id')is not null then
      out_item.put('planned_task_id',item.get_number('planned_task_id'));out_item.put('available',false);has_planned:=true;
     end if;
    end if;
    out_items.append(out_item);
   end loop;
   need_choice:=out_items.get_size>1 and(has_hu or has_planned);
  exception when others then
   if sqlcode not between -20999 and -20800 then raise;end if;
   summary.put('unavailable_reason','CURRENT_PREPARED_SOURCE_REQUIRES_REVIEW');
  end;
  summary.put('places',out_items);summary.put('selection_required',need_choice);p_result:=summary.to_clob;
 end;
"""
pos=api.rfind("end;");api=api[:pos]+reader+api[pos:]
files[folder+"005_wait_api.sql"]=api
defer=captured("RRL_ST_DEFER_API")
needle="not in('PREPARED_CASE','PREPARED_CASES','PREPARED_HU')";assert defer.count(needle)==1
files[folder+"006_deferral.sql"]=defer.replace(needle,"not in('PREPARED_CASE','PREPARED_CASES','PREPARED_HU','PREPARED_PLACES')")
files[folder+"007_compile.sql"]=read("db/migrations/2026-10-13_ni072_nested_hu_wait/009_compile.sql")
files[folder+"008_ledger.sql"]=f"""merge into RRL_SCHEMA_MIGRATIONS t using(select '{mid}'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Select one whole top HU or standalone CASE from the same prepared ST; existing one-root atomic planning/movement and per-place frozen sources preserved',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
files[folder+"apply.sql"]="".join("@@"+p.split("/")[-1]+"\n"for p in list(files)if p.startswith(folder)and p.split("/")[-1][0].isdigit()and not p.split("/")[-1].startswith("000"))
files[folder+"009_rollback_preflight.sql"]="""declare n number;begin
 select count(*)into n from RRL_ST_DEFER_WAIT_PLAN p join RRL_WAREHOUSE_TASK t on t.TASK_ID=p.TASK_ID
 where t.STATUS not in('DONE','CANCELLED');
 if n>0 then raise_application_error(-20886,'ROLLBACK_REQUIRES_RECOVERY_OF_OPEN_WAIT_TASKS');end if;
end;
/
"""
files[folder+"rollback.sql"]="@@009_rollback_preflight.sql\n"+"".join("@@000_before_"+name.lower()+"_package.sql\n@@000_before_"+name.lower()+"_package_body.sql\n"for name in("RRL_ST_DEFER_HU_WAIT","RRL_ST_DEFER_WAIT_API","RRL_ST_DEFER_PHYSICAL","RRL_ST_DEFER_API"))+"drop package RRL_ST_DEFER_PLACE_READ;\n/\n@@007_compile.sql\n"
files[folder+"verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%';\nselect OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%';\n"
files[folder+"checkpoint.json"]=json.dumps({"migration_id":mid,"state":"PREPARED","target":"RABAEV/orcl","capture":1075,"recovery":"original spec/bodies/pairedrollback; preflight refuses open waitingtasks; no dbcopy or goods deletion","sha256":{p:hashlib.sha256(t.encode()).hexdigest()for p,t in files.items()}},indent=2)
page="""# NI07.2 — выбор верхнего места одной подготовленной СТ
1076 PREPARED, migration2026-10-13-012-ni072-place-selection; freshcapture1075/invalid0/checksum/pairedrollback beforeapply.

Existing allCASE-oneHU/full standaloneCASE defaults preserved. НесколькоHU илиHU+standaloneCASE требуют конкретного root_identifier. Классификация/whole-own-leaf proof — RRL_ST_DEFER_PLACE_READ +existingHU/CASEsnapshot. Per-place планирование атомарно впрежнемRootHU илиCASEmetadata; не запускаются несколькоRoot вгрязнойтранзакции. Source однойпартии сохраняется отдельно отверсийсоседнегоRoot; globalSTmembership/cargo manifest guards logicaldrift while siblingphysicalversions maychange.

RootHU waiting declare usesexactmember resources andlocks; currentrole/WARE/decision/trip/config/source guards remain. Availableplaces currentscopednative read handles relatedalreadyplanned tasks onlyfor display; actualselectedsource stillrejectsotheropen task. Existingstrict wholeSTdeferral context doesn'tsilentlyignore pending tasks.

MixedFULLPAL/newinterWARErevision/slotcapacity awaiting remainoutsideincrement. Pythoncontract/UIselection and actualretained source test next; nofullsprint closure. Rollback untested, openwaitingtaskpreflight blocks restoring older selectors.
"""
files["wiki/database/nicora_ni072_place_selection_20261013.md"]=page
for p,note in [
("wiki/index.md","- [Place selection1076](database/nicora_ni072_place_selection_20261013.md): prepared sameST multiTOP/HU+CASE/atomicperplace/currentmanifest; capture1075/livepending.\n"),
("wiki/log.md","\n- checkpoint1076 PREPARED: native top-place selection, strictglobalproof/perRoot frozen source/currentSTmanifest, no dirty batchRoot; originalspecs/bodies/capture1075/checksum/rollback preflight. API/UI/actualapply pending.\n")]:
 t=read(p);files[p]=note+t if p.endswith("index.md")else t+note
print(json.dumps(files,ensure_ascii=True))
