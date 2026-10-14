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
  v_plan_source clob;v_saved json_object_t;v_target varchar2(50);v_open boolean;v_move boolean:=false;
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
     v_saved:=json_object_t.parse(v_plan_source);v_saved.remove('cohort_manifest');v_plan_source:=v_saved.to_clob;
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
   items.put(i,item,true);
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
