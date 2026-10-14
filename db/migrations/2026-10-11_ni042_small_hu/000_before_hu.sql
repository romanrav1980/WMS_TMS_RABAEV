create or replace package RRL_STOCK_HU_CMD authid definer
 accessible by(package RRL_STOCK_HU_TASK,package RRL_STOCK_POSTING_API,package RRL_STOCK_HU_UNPACK_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD,package RRL_STOCK_HU_REPACK_CMD) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob,p_allow_slotted boolean default false);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure declare_tree(f in out nocopy json_array_t,r in out nocopy json_array_t,s clob);
end;
/

create or replace package body RRL_STOCK_HU_CMD as
 function digest(p_value clob) return varchar2 is begin return rawtohex(sys.dbms_crypto.hash(p_value,sys.dbms_crypto.hash_sh256));end;
 procedure add_tree(f in out nocopy json_array_t,r in out nocopy json_array_t,s clob) is
  j json_object_t:=json_object_t.parse(s);a json_array_t;x json_object_t;v_st number;v_case_id number;
 begin
  a:=j.get_array('nodes');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',x.get_string('uid'));
   if x.get_string('kind')='CASE' then
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('case_task_id')));
    v_case_id:=x.get_number('case_task_id');select LEGACY_SBORKA_PALLET_ID into v_st from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_case_id;
    if v_st is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(v_st));end if;
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('wave_id')));
   else RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',x.get_string('uid'));end if;
   if x.get_number('open_task_count')>0 then raise_application_error(-20886,'HU_PHYSICAL_TASK_OPEN');end if;
   if x.get_string('kind')='STOCK' then
    RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),x.get_string('article'),x.get_string('cell'),null);
   else RRL_STOCK_PLAN_HELPER.fence(f,'CELL',x.get_string('cell'));end if;
  end loop;
  a:=j.get_array('links');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   if x.get_number('id') is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('id')));end if;
  end loop;
  a:=j.get_array('ancestors');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   if x.get_number('open_task_count')>0 then raise_application_error(-20886,'HU_ANCESTOR_PHYSICAL_TASK_OPEN');end if;
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',x.get_string('uid'));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',x.get_string('uid'));
  end loop;
 end;
 procedure declare_tree(f in out nocopy json_array_t,r in out nocopy json_array_t,s clob) is begin add_tree(f,r,s);end;
 procedure assert_scan(p_uid varchar2,p_scan varchar2) is v_alias varchar2(32);
 begin
  select SSCC into v_alias from RRL_PALLETS where UID_PALLET=p_uid;
  if p_scan is null or (p_scan!=p_uid and (v_alias is null or p_scan!=v_alias)) then raise_application_error(-20886,'HU_PHYSICAL_SCAN_REQUIRED');end if;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob,p_allow_slotted boolean default false) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();s clob;t clob;ps json_object_t;cs json_object_t;a json_array_t;x json_object_t;
  v_uid varchar2(200):=d.get_object('source').get_string('uid');v_child varchar2(200):=m.get_string('child_uid');
  v_kind varchar2(80):=d.get_string('command_type');v_link number;v_count number;v_cell varchar2(60);v_ware number;v_sscc varchar2(32);v_sum number:=0;v_target varchar2(60);v_target_ware number;v_system number;v_otbor number;v_weight number;v_height number;v_ignore_task number;v_case number:=m.get_number('child_case_task_id');v_slot number;v_slot_json clob;v_claim number;
 begin
  if v_kind='HU_TASK_COMPLETE' then v_kind:='HU_MOVE';v_ignore_task:=m.get_number('physical_task_id');end if;
  if v_uid is null or length(v_uid)>200 or trim(v_uid)!=v_uid then raise_application_error(-20886,'HU_IDENTIFIER_REQUIRED');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||digest(to_clob(p_operation)));
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v_uid);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',v_uid);
  if v_kind='HU_CREATE' then
   select count(*) into v_count from RRL_PALLETS where UID_PALLET=v_uid;
   if v_count>0 then raise_application_error(-20886,'HU_IDENTIFIER_ALREADY_EXISTS');end if;
   v_cell:=m.get_string('cell');v_sscc:=m.get_string('sscc');
   select WARE_ID into v_ware from RRL_CELLS where CELL=v_cell;
   if v_ware is null or v_ware<1 or m.get_number('warehouse') is null or m.get_number('warehouse')!=v_ware
    or m.get_string('container_type') is null or m.get_string('container_type') not in('PALLET','BOX','ROLL_CAGE','BAG')
    or m.get_number('tare_weight_kg') is null or m.get_number('tare_weight_kg')<0 then raise_application_error(-20886,'HU_CREATE_LOCATION_TYPE_OR_TARE_INVALID');end if;
   if v_sscc is not null then
    if not regexp_like(v_sscc,'^[0-9]{18}$') then raise_application_error(-20886,'HU_SSCC_GS1_REQUIRED');end if;
    for i in 1..17 loop v_sum:=v_sum+to_number(substr(v_sscc,i,1))*case when mod(i,2)=1 then 3 else 1 end;end loop;
    if mod(10-mod(v_sum,10),10)!=to_number(substr(v_sscc,18,1)) then raise_application_error(-20886,'HU_SSCC_CHECK_DIGIT_INVALID');end if;
    select count(*) into v_count from RRL_PALLETS where SSCC=v_sscc;
    if v_count>0 then raise_application_error(-20886,'HU_SSCC_ALREADY_BOUND');end if;
    RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','HU.SSCC:'||v_sscc);
   end if;
   RRL_STOCK_PLAN_HELPER.fence(f,'CELL',v_cell);v.put('cell',v_cell);v.put('warehouse',v_ware);
  elsif v_kind='HU_MOVE' then
   s:=RRL_STOCK_HU_READ.snapshot_json(v_uid,v_ignore_task);ps:=json_object_t.parse(s);
   if ps.get_array('ancestors').get_size>0 then raise_application_error(-20886,'HU_TOP_LEVEL_MOVE_REQUIRED');end if;
   if treat(ps.get_array('nodes').get(0) as json_object_t).get_string('kind')!='CONTAINER' then raise_application_error(-20886,'HU_CONTAINER_WITH_STOCK_REQUIRED');end if;
   if m.get_number('expected_version') is null or m.get_number('expected_version')!=treat(ps.get_array('nodes').get(0) as json_object_t).get_number('version') then raise_application_error(-20867,'HU_CONTENT_VERSION_CONFLICT');end if;
   v_target:=m.get_string('target_cell');
   if v_target is null or v_target=ps.get_string('cell') then raise_application_error(-20886,'HU_MOVE_TARGET_REQUIRED');end if;
   select WARE_ID,nvl(IS_SYSTEM,0),nvl(OTBOR,0),nvl(LIMIT_WEIGHT,0),nvl(LIMIT_HEIGHT,0)
    into v_target_ware,v_system,v_otbor,v_weight,v_height from RRL_CELLS where CELL=v_target;
   v_slot_json:=RRL_STOCK_HU_SLOT.target_json(s,m.to_clob,v_ignore_task);
   v.put('placement',json_object_t.parse(v_slot_json));v_slot:=m.get_number('target_slot_id');
   if v_slot is not null then RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(v_slot));end if;
   for claim in(select TASK_ID,CELL_SLOT_ID from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=v_uid and STATUS='OCCUPIED') loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(claim.TASK_ID));
    RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(claim.CELL_SLOT_ID));
   end loop;
   if v_ignore_task is not null and v_slot is not null then
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(v_ignore_task));
   end if;
   select count(*) into v_count from RRL_REMAINS where CELL=v_target and (REMAIN>0 or HARD_RESERVED_BASE>0);
   if v_count>0 and v_slot is null then raise_application_error(-20886,'HU_MOVE_EMPTY_TARGET_REQUIRED');end if;
   select count(*) into v_count from RRL_PALLETS where case when HU_KIND='CONTAINER' then HU_CURRENT_CELL end=v_target;
   if v_count>0 and v_slot is null then raise_application_error(-20886,'HU_MOVE_TARGET_HAS_CONTAINER');end if;
   select count(*) into v_count from RRL_WAREHOUSE_TASK where TO_CELL=v_target and STATUS not in('DONE','CANCELLED') and (v_ignore_task is null or TASK_ID!=v_ignore_task);
   if v_count>0 and v_slot is null then raise_application_error(-20886,'HU_MOVE_TARGET_HAS_OPEN_ARRIVAL');end if;
   add_tree(f,r,s);RRL_STOCK_PLAN_HELPER.fence(f,'CELL',v_target,6);
   RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT','CELL:'||v_target);
   a:=ps.get_array('nodes');
   for i in 0..a.get_size-1 loop x:=treat(a.get(i) as json_object_t);
    if x.get_string('kind')='STOCK' then RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),x.get_string('article'),x.get_string('cell'),v_target);end if;
   end loop;
   v.put('ignored_task_id',v_ignore_task);v.put('parent_snapshot',ps);v.put('parent_signature',digest(s));v.put('target',v_target);v.put('warehouse',v_target_ware);
  elsif v_kind in('HU_ATTACH','HU_DETACH') then
   if (v_child is null and v_case is null) or(v_child is not null and v_case is not null) or v_child=v_uid then raise_application_error(-20886,'HU_CHILD_IDENTITY_REQUIRED');end if;
   s:=RRL_STOCK_HU_READ.snapshot_json(v_uid);if v_case is null then t:=RRL_STOCK_HU_READ.snapshot_json(v_child);else t:=RRL_STOCK_HU_READ.case_snapshot_json(v_case);end if;
   ps:=json_object_t.parse(s);cs:=json_object_t.parse(t);
   if treat(ps.get_array('nodes').get(0) as json_object_t).get_string('kind')!='CONTAINER' then raise_application_error(-20886,'HU_PARENT_CONTAINER_REQUIRED');end if;
   if ps.get_string('cell')!=cs.get_string('cell') or ps.get_number('warehouse')!=cs.get_number('warehouse') then raise_application_error(-20886,'HU_PACK_SAME_LOCATION_REQUIRED');end if;
   if m.get_number('expected_version') is null or m.get_number('expected_version')!=treat(ps.get_array('nodes').get(0) as json_object_t).get_number('version')
    or m.get_number('expected_child_version') is null or m.get_number('expected_child_version')!=treat(cs.get_array('nodes').get(0) as json_object_t).get_number('version') then raise_application_error(-20867,'HU_CONTENT_VERSION_CONFLICT');end if;
   v_cell:=ps.get_string('cell');
   select count(*) into v_count from RRL_RECEIPT_SLOT_CLAIM where CELL=v_cell and STATUS in('RESERVED','OCCUPIED');
   if v_count>0 and not p_allow_slotted then raise_application_error(-20886,'HU_PACK_UNPACK_REQUIRES_UNSLOTTED_WORK_AREA');end if;
   a:=cs.get_array('nodes');
   for i in 0..a.get_size-1 loop x:=treat(a.get(i) as json_object_t);
    if x.get_string('kind')!='CASE' and x.get_string('uid')=v_uid then raise_application_error(-20886,'HU_CYCLE_FORBIDDEN');end if;
   end loop;
   if v_kind='HU_ATTACH' then
    if cs.get_array('ancestors').get_size>0 then raise_application_error(-20886,'HU_CHILD_ALREADY_HAS_PARENT');end if;
    if ps.get_array('nodes').get_size+cs.get_array('nodes').get_size>200 then raise_application_error(-20881,'HU_ATTACH_NODE_BOUND_200');end if;
    select RRL_WMS_HU_LINK_SQ.nextval into v_link from dual;
   else
    if m.get_string('reason') is null then raise_application_error(-20886,'HU_UNPACK_REASON_REQUIRED');end if;
    begin select HU_LINK_ID into v_link from RRL_WMS_HU_LINK where PARENT_UID=v_uid and (CHILD_PALLET_UID=v_child or CHILD_CASE_TASK_ID=v_case) and ACTIVE_FLAG=1;
    exception when no_data_found then raise_application_error(-20886,'HU_CHILD_NOT_IN_PARENT');end;
   end if;
   if v_kind='HU_ATTACH'and m.get_string('retained_tare_booking_operation_id')is not null then
    if v_case is null then raise_application_error(-20886,'NESTED_TARE_DIRECT_CASE_REQUIRED');end if;
    declare book RRL_TARE_BOOK%rowtype;book_id varchar2(100):=m.get_string('retained_tare_booking_operation_id');begin
     select *into book from RRL_TARE_BOOK where OPERATION_ID=book_id and STATUS='HELD';
     if book.PLACE_KIND!='CASE'or book.PLACE_ID!=RRL_STOCK_PLAN_HELPER.decimal_text(v_case)or book.OWNER_WARE_ID!=ps.get_number('warehouse')then raise_application_error(-20886,'NESTED_TARE_ORIGINAL_CASE_BOOK_REQUIRED');end if;
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BOOK',book.OPERATION_ID);
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BALANCE',rawtohex(book.BALANCE_KEY));
     v.put('retained_tare_booking_operation_id',book.OPERATION_ID);
    exception when no_data_found then raise_application_error(-20886,'NESTED_TARE_ACTIVE_BOOK_REQUIRED');end;
   end if;
   add_tree(f,r,s);add_tree(f,r,t);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(v_link));
   v.put('parent_snapshot',ps);v.put('child_snapshot',cs);v.put('parent_signature',digest(s));v.put('child_signature',digest(t));v.put('link_id',v_link);
  else raise_application_error(-20888,'HU_COMMAND_SLICE_NOT_INSTALLED');end if;
  v.put('uid',v_uid);v.put('child',v_child);v.put('child_case_task_id',v_case);v.put('kind',v_kind);
  p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure bump(p_uid varchar2) is begin update RRL_PALLETS set HU_CONTENT_VERSION=HU_CONTENT_VERSION+1 where UID_PALLET=p_uid;end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;j json_object_t:=json_object_t();a json_array_t;x json_object_t;
  v_op varchar2(100):=d.get_string('operation_id');plan clob;s clob;t clob;v_uid varchar2(200);v_child varchar2(200);v_kind varchar2(80);v_link number;
  v_cell varchar2(60);v_ware number;v_sscc varchar2(32);v_type varchar2(20);v_tare number;v_count number;v_target varchar2(60);v_base varchar2(20);v_policy number;v_qty number;v_from varchar2(60);v_leaf_uid varchar2(200);v_article varchar2(160);v_ignore_task number;v_case number;v_slot number;v_slot_json clob;v_claim number;v_mode varchar2(20);v_case_sscc varchar2(64);v_parent_nodes clob;v_child_nodes clob;
 begin
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'HU_EXECUTION_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
  v:=json_object_t.parse(plan).get_object('domain');v_uid:=v.get_string('uid');v_child:=v.get_string('child');v_kind:=v.get_string('kind');v_case:=v.get_number('child_case_task_id');
  if v.has('parent_snapshot') then v_parent_nodes:=v.get_object('parent_snapshot').get_array('nodes').to_clob;end if;
  if v.has('child_snapshot') then v_child_nodes:=v.get_object('child_snapshot').get_array('nodes').to_clob;end if;
  -- Match shipping/QC actual-row order: planned ST rows before CASE rows.
  for st in(select ID from RRL_SBORKA_PALLETS where ID in(
   select LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(
    select CASE_ID from json_table(v_parent_nodes,'$[*]' columns(CASE_ID number path '$.case_task_id'))
    union select CASE_ID from json_table(v_child_nodes,'$[*]' columns(CASE_ID number path '$.case_task_id')))) order by ID) loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(st.ID)));
   select ID into v_claim from RRL_SBORKA_PALLETS where ID=st.ID for update;
  end loop;
  for locked_case in(select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(
   select CASE_ID from json_table(v_parent_nodes,'$[*]' columns(CASE_ID number path '$.case_task_id'))
   union select CASE_ID from json_table(v_child_nodes,'$[*]' columns(CASE_ID number path '$.case_task_id')))
   order by CASE_PICK_TASK_ID) loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(locked_case.CASE_PICK_TASK_ID)));
   select CASE_PICK_TASK_ID into v_claim from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=locked_case.CASE_PICK_TASK_ID for update;
  end loop;
  if v_kind='HU_CREATE' then
   v_cell:=v.get_string('cell');v_ware:=v.get_number('warehouse');v_sscc:=m.get_string('sscc');v_type:=m.get_string('container_type');v_tare:=m.get_number('tare_weight_kg');
   if m.get_string('scan_container') is null or m.get_string('scan_container')!=v_uid
    or m.get_string('scan_cell') is null or m.get_string('scan_cell')!=v_cell then raise_application_error(-20886,'HU_CREATE_SCAN_REQUIRED');end if;
   select count(*) into v_count from RRL_PALLETS where UID_PALLET=v_uid or (v_sscc is not null and SSCC=v_sscc);
   if v_count>0 then raise_application_error(-20890,'CLOSURE_CHANGED: HU alias identity');end if;
   insert into RRL_PALLETS(UID_PALLET,ARTICUL,UNIT_COUNT,PRIHOD_NAKLAD_ID,CREATION_DATE,HU_KIND,HU_TYPE,HU_CONTENT_VERSION,HU_CURRENT_CELL,HU_TARE_WEIGHT_KG,SSCC,CREATED_BY_STOCK_OP)
    values(v_uid,null,0,0,sysdate,'CONTAINER',v_type,0,v_cell,v_tare,v_sscc,v_op);
  elsif v_kind='HU_MOVE' then
   v_ignore_task:=v.get_number('ignored_task_id');s:=RRL_STOCK_HU_READ.snapshot_json(v_uid,v_ignore_task);
   if digest(s)!=v.get_string('parent_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: HU physical composition');end if;
   assert_scan(v_uid,m.get_string('scan_container'));v_target:=v.get_string('target');v_ware:=v.get_number('warehouse');
   v_from:=v.get_object('parent_snapshot').get_string('cell');
   if m.get_string('scanned_from_cell') is null or m.get_string('scanned_from_cell')!=v_from
    or m.get_string('scanned_to_cell') is null or m.get_string('scanned_to_cell')!=v_target then raise_application_error(-20886,'HU_MOVE_FROM_TO_SCAN_REQUIRED');end if;
   v_slot:=m.get_number('target_slot_id');
   select count(*) into v_count from RRL_REMAINS where CELL=v_target and (REMAIN>0 or HARD_RESERVED_BASE>0);
   if v_count>0 and v_slot is null then raise_application_error(-20890,'CLOSURE_CHANGED: HU target occupied');end if;
   select count(*) into v_count from RRL_PALLETS where case when HU_KIND='CONTAINER' then HU_CURRENT_CELL end=v_target;
   if v_count>0 and v_slot is null then raise_application_error(-20890,'CLOSURE_CHANGED: HU target container');end if;
   v_slot:=m.get_number('target_slot_id');
   v_slot_json:=RRL_STOCK_HU_SLOT.target_json(s,m.to_clob,v_ignore_task);
   if dbms_lob.compare(v_slot_json,v.get_object('placement').to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: HU slot policy');end if;
   if v_slot is not null and (m.get_string('scanned_to_slot_code') is null or m.get_string('scanned_to_slot_code')!=v.get_object('placement').get_string('slot_code')) then raise_application_error(-20886,'HU_TARGET_SLOT_SCAN_REQUIRED');end if;
   a:=v.get_object('parent_snapshot').get_array('nodes');
   for i in 0..a.get_size-1 loop x:=treat(a.get(i) as json_object_t);
    v_leaf_uid:=x.get_string('uid');
    if x.get_string('kind')='STOCK' then
     v_article:=x.get_string('article');v_base:=x.get_string('base_uom');v_qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));
     select max(POLICY_VERSION) into v_policy from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article
      and INPUT_UOM=v_base and BASE_UOM=v_base and NUMERATOR=1 and DENOMINATOR=1;
     if v_policy is null then raise_application_error(-20868,'HU_MOVE_BASE_POLICY_REQUIRED');end if;
     v_mode:=case when x.get_number('case_task_id') is not null and v_from='CPT_'||RRL_STOCK_PLAN_HELPER.decimal_text(v_ware) then 'CASE_EXIT' else 'ORDINARY' end;
     RRL_STOCK_TRANSFER_CORE.move(v_leaf_uid,v_leaf_uid,v_from,v_target,v_qty,v_base,v_policy,v_ware,p_actor,i+1,p_target_slot=>v_slot,p_location_mode=>v_mode);
     bump(v_leaf_uid);
    elsif x.get_string('kind')='CASE' then
     v_case:=x.get_number('case_task_id');
     update RRL_CASE_PICK_TASK set CURRENT_CELL=v_target,CONTENT_VERSION=CONTENT_VERSION+1,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=v_case;
     insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,PAYLOAD_JSON,CREATED_BY)
      values(RRL_CASE_PICK_EVENT_SQ.nextval,v_case,'HU_CARRIER_MOVED',p_request,p_actor);
    else
     update RRL_PALLETS set HU_CURRENT_CELL=v_target,HU_CONTENT_VERSION=HU_CONTENT_VERSION+1 where UID_PALLET=v_leaf_uid;
    end if;
   end loop;
   delete from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=v_uid and STATUS='OCCUPIED';
   if v_slot is not null then
    declare measures json_object_t:=v.get_object('placement').get_object('measurements');version_no number;mass_no number;volume_no number;begin
     mass_no:=RRL_STOCK_MATH.quantity(measures.get_string('gross_weight_kg'));volume_no:=RRL_STOCK_MATH.quantity(measures.get_string('bounding_volume_m3'));
     select HU_CONTENT_VERSION into version_no from RRL_PALLETS where UID_PALLET=v_uid;
     insert into RRL_RECEIPT_SLOT_CLAIM(TASK_ID,UID_PALLET,CELL,CELL_SLOT_ID,STATUS,HU_GROSS_WEIGHT_KG,HU_BOUNDING_VOLUME_M3,HU_COMPOSITION_VERSION)
      values(v_ignore_task,v_uid,v_target,v_slot,'OCCUPIED',mass_no,volume_no,version_no);
    end;
   end if;
  else
   s:=RRL_STOCK_HU_READ.snapshot_json(v_uid);if v_case is null then t:=RRL_STOCK_HU_READ.snapshot_json(v_child);else t:=RRL_STOCK_HU_READ.case_snapshot_json(v_case);end if;
   if digest(s)!=v.get_string('parent_signature') or digest(t)!=v.get_string('child_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: HU composition');end if;
   assert_scan(v_uid,m.get_string('scan_container'));
   if v_case is null then assert_scan(v_child,m.get_string('scan_child'));
   else
    select SSCC into v_case_sscc from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_case for update;
    if m.get_string('scan_child') is null or m.get_string('scan_child')!=v_case_sscc then raise_application_error(-20886,'HU_CASE_CARRIER_SCAN_REQUIRED');end if;
   end if;v_link:=v.get_number('link_id');
   if v_kind='HU_ATTACH' then
    insert into RRL_WMS_HU_LINK(HU_LINK_ID,PARENT_UID,CHILD_PALLET_UID,CHILD_CASE_TASK_ID,ACTIVE_FLAG,LINK_VERSION,LINKED_OPERATION_ID,LINKED_BY)
     values(v_link,v_uid,v_child,v_case,1,0,v_op,p_actor);
   else
    update RRL_WMS_HU_LINK set ACTIVE_FLAG=0,LINK_VERSION=LINK_VERSION+1,UNLINKED_OPERATION_ID=v_op,UNLINKED_AT=systimestamp,UNLINKED_BY=p_actor
     where HU_LINK_ID=v_link and ACTIVE_FLAG=1 and PARENT_UID=v_uid and(CHILD_PALLET_UID=v_child or CHILD_CASE_TASK_ID=v_case);
    if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: HU child link');end if;
   end if;
   bump(v_uid);
   if v_case is null then bump(v_child);
   else
    update RRL_CASE_PICK_TASK set CONTENT_VERSION=CONTENT_VERSION+1,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=v_case;
    insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,PAYLOAD_JSON,CREATED_BY)
     values(RRL_CASE_PICK_EVENT_SQ.nextval,v_case,case v_kind when 'HU_ATTACH' then 'HU_PACKED' else 'HU_UNPACKED' end,p_request,p_actor);
   end if;
   -- Packing changes the control signature of all CASE children in the touched tree.
   -- Moving the intact tree above deliberately preserves admission.
   for ct in(select CASE_PICK_TASK_ID,LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(
    select CASE_ID from json_table(v_parent_nodes,'$[*]' columns(CASE_ID number path '$.case_task_id'))
    union select CASE_ID from json_table(v_child_nodes,'$[*]' columns(CASE_ID number path '$.case_task_id'))) order by CASE_PICK_TASK_ID) loop
    if ct.LEGACY_SBORKA_PALLET_ID is not null then
     update RRL_SBORKA_PALLETS set SCAN_CONTENT_SIGNATURE=null,WEIGHT_CONTENT_SIGNATURE=null,
      SCAN_MARK_PROVED=0,SCAN_PHYSICAL_UNIT_COUNT=0,SCAN_ITEM_PROVED=0 where ID=ct.LEGACY_SBORKA_PALLET_ID;
     update RRL_CASE_PICK_TASK set STATUS='WAIT_CONTROL',UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID;
     insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,PAYLOAD_JSON,CREATED_BY)
      values(RRL_CASE_PICK_EVENT_SQ.nextval,ct.CASE_PICK_TASK_ID,'CONTROL_REVOKED',p_request,p_actor);
    end if;
   end loop;
   a:=v.get_object('parent_snapshot').get_array('ancestors');
   for i in 0..a.get_size-1 loop x:=treat(a.get(i) as json_object_t);bump(x.get_string('uid'));end loop;
  end if;
  j:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(v_uid));j.put('operation_id',v_op);j.put('command',v_kind);p_result:=j.to_clob;
 end;
end;
/
