declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_BALANCE_CORE authid definer
 accessible by(package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number,
   p_base_uom varchar2,p_uom_version number,p_expected_version number default null);
 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2,
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null);
end;
/

create or replace package RRL_STOCK_TRANSFER_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,
 package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_MES_CORE) as
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null);
end;
/

create or replace package RRL_STOCK_MOVE_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure manual_whole(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_TASK_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_INVARIANT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 function snapshot_stock(p_resources clob) return clob;
 procedure verify_posting(p_resources clob,p_before clob,p_operation varchar2);
end;
/

create or replace package body RRL_STOCK_BALANCE_CORE as
 procedure assert_context is v_tx varchar2(100);
 begin
  v_tx:=dbms_transaction.local_transaction_id(false);
  if v_tx is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=v_tx then
   raise_application_error(-20863,'STOCK_WRITE_FORBIDDEN');
  end if;
 end;
 procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number,
   p_base_uom varchar2,p_uom_version number,p_expected_version number default null) is
  v_p number;v_h number;v_ver number;v_uom varchar2(20);v_article varchar2(160);v_scale number;v_exists boolean:=true;
 begin
  assert_context;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  if p_cell is null or p_base_uom is null or p_delta_p is null or p_delta_h is null then
   raise_application_error(-20864,'STOCK_IDENTITY_OR_DELTA_MISSING');
  end if;
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('SKU',v_article),4);
  begin
   select BASE_SCALE into v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article
    and INPUT_UOM=p_base_uom and BASE_UOM=p_base_uom and POLICY_VERSION=p_uom_version
    and NUMERATOR=DENOMINATOR;
  exception when no_data_found then raise_application_error(-20865,'BASE_UOM_POLICY_REQUIRED');
  end;
  RRL_STOCK_MATH.assert_base(p_delta_p,v_scale);RRL_STOCK_MATH.assert_base(p_delta_h,v_scale);
  begin
   select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM into v_p,v_h,v_ver,v_uom
    from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell for update;
  exception when no_data_found then v_exists:=false;v_p:=0;v_h:=0;v_ver:=0;v_uom:=p_base_uom;
  end;
  if v_uom is null or v_uom!=p_base_uom then raise_application_error(-20866,'STOCK_BASE_UOM_CONFLICT'); end if;
  if p_expected_version is not null and p_expected_version!=v_ver then raise_application_error(-20867,'VERSION_CONFLICT'); end if;
  RRL_STOCK_MATH.assert_base(v_p+p_delta_p,v_scale);RRL_STOCK_MATH.assert_base(v_h+p_delta_h,v_scale);
  if v_p+p_delta_p<0 then raise_application_error(-20868,'STOCK_INSUFFICIENT'); end if;
  if v_h+p_delta_h<0 or v_h+p_delta_h>v_p+p_delta_p then raise_application_error(-20869,'RESERVATION_CONFLICT'); end if;
  RRL_STOCK_CTX_API.begin_effect('STOCK',p_uid,p_cell);
  if v_exists then
   update RRL_REMAINS set REMAIN=REMAIN+p_delta_p,HARD_RESERVED_BASE=HARD_RESERVED_BASE+p_delta_h,
    STOCK_VERSION=STOCK_VERSION+1,TIME_OF_LAST_UPDATE=sysdate
    where UID_POLETA=p_uid and CELL=p_cell and STOCK_VERSION=v_ver;
   if sql%rowcount!=1 then raise_application_error(-20867,'VERSION_CONFLICT'); end if;
  else
   insert into RRL_REMAINS(UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM,TIME_OF_LAST_UPDATE)
    values(p_uid,p_cell,p_delta_p,p_delta_h,1,p_base_uom,sysdate);
  end if;
  RRL_STOCK_CTX_API.end_effect;
 exception when others then RRL_STOCK_CTX_API.end_effect;raise;
 end;
 procedure write_event(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null) is
  v_prihod number;v_op varchar2(100);
 begin
  assert_context;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  if p_qty is null or p_qty=0 or p_base_uom is null or p_line is null or p_line<1 or p_leg is null or p_leg<1 then
   raise_application_error(-20870,'JOURNAL_FACT_INVALID');
  end if;
  v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
  select PRIHOD_NAKLAD_ID into v_prihod from RRL_PALLETS where UID_PALLET=p_uid;
  select RRL_EVENT_ID_SQ.nextval into p_event from dual;
  RRL_STOCK_CTX_API.begin_effect('JOURNAL',p_uid,nvl(p_from,p_to));
  insert into RRL_EVENTS(ID_EVENT,CELL_FROM,CELL_TO,DATE_EVENT,COUNT_EVENT,TYPE_EVENT,UID_POLETA,
   USER_ID,PRIHOD_NAKL_ID,OTHOD_NAKL_ID,OPERATION_ID,LINE_NO,LEG_NO,BASE_QTY,BASE_UOM,UOM_POLICY_VERSION)
   values(p_event,p_from,p_to,sysdate,abs(p_qty),p_type,p_uid,p_actor,v_prihod,p_outgoing_doc,v_op,p_line,p_leg,p_qty,p_base_uom,p_uom_version);
  RRL_STOCK_CTX_API.end_effect;
 exception when others then RRL_STOCK_CTX_API.end_effect;raise;
 end;
 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2,
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null) is
 begin
  if p_signed_qty is null or p_signed_qty=0 or
   (p_signed_qty<0 and (p_from is null or p_to is not null)) or
   (p_signed_qty>0 and (p_to is null or p_from is not null)) then
   raise_application_error(-20870,'SIGNED_LEG_LOCATION_CONFLICT');
  end if;
  write_event(p_uid,p_from,p_to,p_signed_qty,p_base_uom,p_uom_version,p_line,p_leg,p_type,p_actor,p_event,p_outgoing_doc);
 end;
end;
/

create or replace package body RRL_STOCK_TRANSFER_CORE as
 procedure require_row(p_id number) is
 begin
  begin RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_RESERVATION',
   RRL_STOCK_PLAN_HELPER.decimal_text(p_id)));
  exception when others then
   if sqlcode=-20850 then raise_application_error(-20890,'CLOSURE_CHANGED: reservation set');else raise;end if;
  end;
 end;
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null) is
  v_p number;v_h number;v_ver number;v_uom varchar2(20);v_article varchar2(160);v_sum number;
  v_hmove number:=0;v_event number;v_units number;v_unit_qty number;v_selected number;v_expected number;
  v_r RRL_STOCK_RESERVATION%rowtype;v_result_reservation number;
 begin
  if p_uid is null or p_target_uid is null or p_from is null or p_to is null or p_from=p_to
   or p_qty is null or p_qty<=0 then raise_application_error(-20886,'TRANSFER_CONTRACT_INVALID');end if;
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_target_uid));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_target_uid));
  RRL_STOCK_LOCATION_CORE.assert_ordinary(p_from,nvl(p_source_warehouse,p_warehouse),'SOURCE');
  RRL_STOCK_LOCATION_CORE.assert_ordinary(p_to,p_warehouse,'TARGET');
  select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM into v_p,v_h,v_ver,v_uom
   from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_from;
  if v_uom is null or v_uom!=p_uom or p_qty>v_p then raise_application_error(-20868,'TRANSFER_STOCK_CONFLICT');end if;
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  select count(*) into v_sum from RRL_STOCK_RESERVATION where UID_PALLET=p_uid and CELL=p_from and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING') and (BASE_QTY is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!=p_uom);
  if v_sum>0 then raise_application_error(-20869,'HARD_BASE_IDENTITY_CONFLICT');end if;
  select nvl(sum(BASE_QTY),0) into v_sum from RRL_STOCK_RESERVATION where UID_PALLET=p_uid
   and CELL=p_from and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
  if v_sum!=v_h then raise_application_error(-20869,'HARD_MATERIALIZATION_CONFLICT');end if;
  for r in(select RESERVATION_ID from RRL_STOCK_RESERVATION where UID_PALLET=p_uid and CELL=p_from
   and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING')) loop require_row(r.RESERVATION_ID);end loop;
  if p_qty=v_p and p_target_uid=p_uid then
   v_hmove:=v_h;
  elsif p_reservation is not null then
   require_row(p_reservation);
   select * into v_r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_reservation;
   if v_r.UID_PALLET is null or v_r.UID_PALLET!=p_uid or v_r.CELL is null or v_r.CELL!=p_from
    or v_r.RESERVATION_KIND!='HARD' or v_r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
    or v_r.BASE_QTY is null or v_r.BASE_QTY<p_qty then raise_application_error(-20869,'TRANSFER_RESERVATION_CONFLICT');end if;
   v_hmove:=p_qty;
  elsif p_qty>v_p-v_h then raise_application_error(-20869,'TRANSFER_UNRESERVED_INSUFFICIENT');end if;
  if p_target_uid!=p_uid then
   declare t RRL_PALLETS%rowtype;s RRL_PALLETS%rowtype;
   begin
    select * into s from RRL_PALLETS where UID_PALLET=p_uid;
    select * into t from RRL_PALLETS where UID_PALLET=p_target_uid;
    if t.ARTICUL!=s.ARTICUL or t.PRIHOD_NAKLAD_ID!=s.PRIHOD_NAKLAD_ID
     or (t.EXPIRY_DATE!=s.EXPIRY_DATE or (t.EXPIRY_DATE is null and s.EXPIRY_DATE is not null) or (t.EXPIRY_DATE is not null and s.EXPIRY_DATE is null)) or (t.PRODUCED_DATE!=s.PRODUCED_DATE or (t.PRODUCED_DATE is null and s.PRODUCED_DATE is not null) or (t.PRODUCED_DATE is not null and s.PRODUCED_DATE is null))
     or (t.PROD_BATCH_ID!=s.PROD_BATCH_ID or (t.PROD_BATCH_ID is null and s.PROD_BATCH_ID is not null) or (t.PROD_BATCH_ID is not null and s.PROD_BATCH_ID is null)) then raise_application_error(-20887,'TRANSFER_LOT_IDENTITY_CONFLICT');end if;
   end;
  end if;
  select count(*),nvl(sum(BASE_QTY),0) into v_units,v_unit_qty from RRL_WMS_RECEIPT_UNIT
   where CURRENT_UID=p_uid and CURRENT_CELL=p_from and STOCK_STATUS!='ISSUED';
  if v_units>0 then
   if p_target_uid!=p_uid then raise_application_error(-20888,'HU_REBIND_HANDLER_REQUIRED');end if;
   if v_unit_qty!=v_p then raise_application_error(-20884,'COMPOSITION_STOCK_CONFLICT');end if;
   if p_qty!=v_p and p_units is null then raise_application_error(-20884,'PARTIAL_UNIT_SELECTION_REQUIRED');end if;
   select count(*),nvl(sum(u.BASE_QTY),0) into v_selected,v_unit_qty from RRL_WMS_RECEIPT_UNIT u
    where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_from and u.STOCK_STATUS!='ISSUED' and
     (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
   if v_unit_qty!=p_qty then raise_application_error(-20884,'SELECTED_UNIT_QUANTITY_CONFLICT');end if;
   if p_units is not null then
    select count(distinct K) into v_expected from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
    if v_expected!=v_selected then raise_application_error(-20884,'SELECTED_UNIT_IDENTITY_CONFLICT');end if;
   end if;
   if p_qty!=v_p and p_reservation is not null then
    select nvl(sum(u.BASE_QTY),0) into v_unit_qty from RRL_WMS_RECEIPT_UNIT u
     where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_from and u.HARD_RESERVATION_ID=p_reservation and
      (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
    if v_unit_qty!=v_hmove then raise_application_error(-20869,'RESERVED_UNIT_SELECTION_CONFLICT');end if;
   end if;
   for u in(select PHYSICAL_UNIT_KEY,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT
    where CURRENT_UID=p_uid and CURRENT_CELL=p_from and STOCK_STATUS!='ISSUED' and
     (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=PHYSICAL_UNIT_KEY))) loop
    begin RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',u.PHYSICAL_UNIT_KEY));
    exception when others then if sqlcode=-20850 then raise_application_error(-20890,'CLOSURE_CHANGED: unit set');else raise;end if;end;
    if u.HARD_RESERVATION_ID is not null and p_qty!=v_p and
      (p_reservation is null or u.HARD_RESERVATION_ID!=p_reservation) then raise_application_error(-20869,'UNIT_RESERVED_BY_OTHER_OWNER');end if;
   end loop;
  else
   select nvl(max(MARKING_REQUIRED),0) into v_expected from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article;
   if v_expected=1 then raise_application_error(-20884,'MARKED_BINDING_REQUIRED');end if;
  end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(p_uid,p_from,-p_qty,-v_hmove,p_uom,p_uom_version,v_ver);
  RRL_STOCK_BALANCE_CORE.apply_delta(p_target_uid,p_to,p_qty,v_hmove,p_uom,p_uom_version);
  if v_hmove>0 then
   for r in(select RESERVATION_ID,BASE_QTY from RRL_STOCK_RESERVATION
    where UID_PALLET=p_uid and CELL=p_from and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING')
     and (p_qty=v_p or RESERVATION_ID=p_reservation)) loop
    RRL_STOCK_RESERVE_CORE.move_coverage(r.RESERVATION_ID,p_new_reservation,p_target_uid,p_to,p_warehouse,
     case when p_qty=v_p then r.BASE_QTY else p_qty end,p_target_slot,p_actor,v_result_reservation);
    RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_from);
    update RRL_WMS_RECEIPT_UNIT set HARD_RESERVATION_ID=v_result_reservation,UNIT_VERSION=UNIT_VERSION+1
     where CURRENT_UID=p_uid and CURRENT_CELL=p_from and HARD_RESERVATION_ID=r.RESERVATION_ID and
      (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=PHYSICAL_UNIT_KEY));
    RRL_STOCK_CTX_API.end_effect;
   end loop;
  end if;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_from);
  update RRL_WMS_RECEIPT_UNIT set CURRENT_UID=p_target_uid,CURRENT_CELL=p_to,UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_from and STOCK_STATUS!='ISSUED' and
    (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
  RRL_STOCK_BALANCE_CORE.write_leg(p_uid,p_from,null,-p_qty,p_uom,p_uom_version,p_line,1,2,p_actor,v_event);
  RRL_STOCK_BALANCE_CORE.write_leg(p_target_uid,null,p_to,p_qty,p_uom,p_uom_version,p_line,2,2,p_actor,v_event);
 end;
end;
/

create or replace package body RRL_STOCK_MOVE_CORE as
 procedure manual_whole(p_request clob,p_actor varchar2,p_result out clob) is
  v_doc json_object_t:=json_object_t.parse(p_request);v_source json_object_t;v_lines json_array_t;
  v_line json_object_t;v_result json_object_t:=json_object_t();v_facts json_array_t:=json_array_t();v_fact json_object_t;
  v_uid varchar2(200);v_article varchar2(160);v_actual varchar2(160);v_from varchar2(60);v_to varchar2(60);
  v_unit varchar2(20);v_base varchar2(20);v_sscc varchar2(32);v_quality varchar2(40);v_warehouse number;
  v_n number;v_q number;v_p number;v_h number;v_version number;v_num number;v_den number;v_scale number;
  v_policy number;v_marked number;v_event_from number;v_event_to number;v_line_no number;v_expected number;
  type seen_set is table of boolean index by varchar2(200);
  v_seen seen_set;v_line_seen seen_set;
 begin
  v_doc.on_error(1);
  if RRL_HAS_WRIGHT(p_actor,'stock_posting_manual_move')!=1 then raise_application_error(-20882,'MANUAL_MOVE_FORBIDDEN'); end if;
  v_source:=v_doc.get_object('source');v_source.on_error(1);
  if v_source.get_string('type') is null or v_source.get_string('type')!='MANUAL' or v_source.get_string('reason') is null
   or length(v_source.get_string('reason'))>1000 then raise_application_error(-20883,'MANUAL_SOURCE_REQUIRED'); end if;
  v_warehouse:=v_source.get_number('warehouse_id');
  if v_warehouse is null or v_warehouse<1 or v_warehouse!=trunc(v_warehouse) then raise_application_error(-20883,'WAREHOUSE_REQUIRED'); end if;
  if v_doc.get_array('units').get_size!=0 then raise_application_error(-20884,'COMPOSITION_HANDLER_REQUIRED'); end if;
  v_lines:=v_doc.get_array('lines');
  for i in 0..v_lines.get_size-1 loop
   v_line:=treat(v_lines.get(i) as json_object_t);v_line.on_error(1);
   v_uid:=v_line.get_string('uid');v_article:=v_line.get_string('article');
   v_from:=v_line.get_string('source_cell');v_to:=v_line.get_string('target_cell');
   v_unit:=v_line.get_string('unit');v_line_no:=v_line.get_number('line_number');
   if v_line_no is null or v_line_no<1 or v_line_no!=trunc(v_line_no)
    or v_line_seen.exists(to_char(v_line_no,'TM9')) then raise_application_error(-20881,'COMMAND_LINE_ID_INVALID'); end if;
   v_line_seen(to_char(v_line_no,'TM9')):=true;
   if v_seen.exists(v_uid) then raise_application_error(-20885,'PALLET_REPEATED'); end if;
   v_seen(v_uid):=true;
   if v_from=v_to or v_line.get_string('target_uid') is null or v_line.get_string('target_uid')!=v_uid
    or v_line.get_string('reservation_action') is null or v_line.get_string('reservation_action')!='NONE' or not v_line.get('reservation_id').is_null then
    raise_application_error(-20886,'DEDICATED_MOVE_HANDLER_REQUIRED');
   end if;
   RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',v_uid));
   RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid));
   RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('SKU',v_article),4);
   select ARTICUL,SSCC,QUALITY_STATUS into v_actual,v_sscc,v_quality from RRL_PALLETS where UID_PALLET=v_uid;
   if v_actual!=v_article or v_actual is null then raise_application_error(-20887,'PALLET_ARTICLE_CONFLICT'); end if;
   if v_quality is not null and v_quality!='RELEASED' then raise_application_error(-20884,'QUALITY_HANDLER_REQUIRED'); end if;
   -- Fail closed: no guessed regulatory status and no rebuilding of existing composition.
   select MARKING_REQUIRED into v_marked from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article;
   select count(*) into v_n from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article;
   if v_marked!=0 or v_marked is null or v_n!=0 then raise_application_error(-20884,'MARKED_HANDLER_REQUIRED'); end if;
   select count(*) into v_n from RRL_WMS_RECEIPT_UNIT where UID_PALLET=v_uid;
   if v_n!=0 then raise_application_error(-20884,'UNIT_HANDLER_REQUIRED'); end if;
   select count(*) into v_n from RRL_CRPT_AGGREGATION where UID_PALLET=v_uid or SSCC=v_sscc or PARENT_SSCC=v_sscc;
   if v_n!=0 then raise_application_error(-20884,'HU_HANDLER_REQUIRED'); end if;
   RRL_STOCK_LOCATION_CORE.assert_ordinary(v_from,v_warehouse,'SOURCE');
   RRL_STOCK_LOCATION_CORE.assert_ordinary(v_to,v_warehouse,'TARGET');
   select max(POLICY_VERSION) into v_policy from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_unit;
   select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale
    from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_unit and POLICY_VERSION=v_policy;
   v_q:=RRL_STOCK_MATH.convert_exact(v_line.get_string('quantity'),v_num,v_den,v_scale);
   select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION into v_p,v_h,v_version from RRL_REMAINS where UID_POLETA=v_uid and CELL=v_from;
   if v_line.has('expected_stock_version') and not v_line.get('expected_stock_version').is_null then
    v_expected:=v_line.get_number('expected_stock_version');
    if v_expected is null or v_expected!=v_version then raise_application_error(-20867,'VERSION_CONFLICT'); end if;
   end if;
   select count(*) into v_n from RRL_REMAINS where UID_POLETA=v_uid and CELL!=v_from and (REMAIN!=0 or HARD_RESERVED_BASE!=0);
   if v_n!=0 or v_p!=v_q or v_h!=0 then raise_application_error(-20886,'WHOLE_UNRESERVED_PALLET_REQUIRED'); end if;
   select count(*) into v_n from RRL_STOCK_RESERVATION where UID_PALLET=v_uid and RESERVATION_KIND='HARD'
    and STATUS in('ACTIVE','ALLOCATED','PICKING');
   if v_n!=0 then raise_application_error(-20886,'RESERVATION_HANDLER_REQUIRED'); end if;
   RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_from,-v_q,0,v_base,v_policy,v_version);
   RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_to,v_q,0,v_base,v_policy);
   RRL_STOCK_BALANCE_CORE.write_leg(v_uid,v_from,null,-v_q,v_base,v_policy,v_line_no,1,2,p_actor,v_event_from);
   RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,v_to,v_q,v_base,v_policy,v_line_no,2,2,p_actor,v_event_to);
   v_fact:=json_object_t();v_fact.put('line_number',v_line_no);v_fact.put('uid',v_uid);
   v_fact.put('source_cell',v_from);v_fact.put('target_cell',v_to);v_fact.put('base_quantity',to_char(v_q,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''));
   v_fact.put('base_uom',v_base);v_fact.put('uom_policy_version',v_policy);
   v_fact.put('source_event_id',v_event_from);v_fact.put('target_event_id',v_event_to);v_facts.append(v_fact);
  end loop;
  v_result.put('operation_id',v_doc.get_string('operation_id'));v_result.put('command_type','MANUAL_MOVE');
  v_result.put('status','APPLIED');v_result.put('lines',v_facts);p_result:=v_result.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_TASK_CORE as
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob) is
  v_doc json_object_t:=json_object_t.parse(p_request);v_meta json_object_t;v_source json_object_t;v_domain json_object_t;
  v_plan clob;v_task RRL_WAREHOUSE_TASK%rowtype;v_residual RRL_WAREHOUSE_TASK%rowtype;v_pallet RRL_PALLETS%rowtype;
  v_task_id number;v_qty number;v_original number;v_qbase number;v_target varchar2(200);v_base varchar2(20);
  v_factor_num number;v_factor_den number;v_scale number;v_version number;v_article varchar2(160);
  v_residual_id number;v_reservation number;v_new_reservation number;v_ware number;v_pick_task number;
  v_signature varchar2(64);v_hash varchar2(64);v_op varchar2(100);v_units clob;v_n number;v_doc_status varchar2(40);
  v_result json_object_t:=json_object_t();v_resource number;v_session number;v_equipment number;v_sync_id number;v_sync_key varchar2(400);v_session_actor varchar2(100);v_input_uom varchar2(20);v_source_p number;
 begin
  v_doc.on_error(1);v_source:=v_doc.get_object('source');v_meta:=v_doc.get_object('metadata');v_meta.on_error(1);
  v_op:=v_doc.get_string('operation_id');v_task_id:=v_source.get_number('task_id');
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'TASK_COMPLETE_FORBIDDEN');end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id)));
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
  v_domain:=json_object_t.parse(v_plan).get_object('domain');
  select * into v_task from RRL_WAREHOUSE_TASK where TASK_ID=v_task_id for update;
  if RRL_STOCK_TASK_PLAN.signature(v_task)!=v_domain.get_string('task_signature') then
   raise_application_error(-20890,'CLOSURE_CHANGED: task identity');
  end if;
  if v_task.STATUS is null or v_task.STATUS not in('PLANNED','ASSIGNED','IN_PROGRESS') then
   raise_application_error(-20886,'TASK_STATE_CONFLICT');end if;
  v_task.FROM_WARE_ID:=v_domain.get_number('from_ware_id');v_task.TO_WARE_ID:=v_domain.get_number('to_ware_id');
  if v_task.FROM_WARE_ID is null or v_task.TO_WARE_ID is null or v_task.FROM_WARE_ID!=v_task.TO_WARE_ID then
   raise_application_error(-20886,'INTERWAREHOUSE_COMMAND_REQUIRED');end if;
  if upper(trim(v_meta.get_string('scanned_pallet'))) is null or
   trim(v_meta.get_string('scanned_pallet')) not in(nvl(v_task.UID_PALLET,v_task.SSCC),nvl(v_task.SSCC,v_task.UID_PALLET))
   or upper(trim(v_meta.get_string('scanned_from_cell'))) is null or upper(trim(v_meta.get_string('scanned_from_cell')))!=upper(v_task.FROM_CELL)
   or upper(trim(v_meta.get_string('scanned_to_cell'))) is null or upper(trim(v_meta.get_string('scanned_to_cell')))!=upper(v_task.TO_CELL) then
   raise_application_error(-20886,'TASK_SCAN_CONFLICT');end if;
  v_original:=v_task.QTY;v_qty:=v_original;
  if v_meta.has('fact_qty') and not v_meta.get('fact_qty').is_null then v_qty:=RRL_STOCK_MATH.quantity(v_meta.get_string('fact_qty'));end if;
  if v_qty is null or v_qty<=0 or v_qty>v_original or (v_task.QTY_MODE='PALLET' and v_qty!=v_original) then
   raise_application_error(-20886,'TASK_QUANTITY_CONFLICT');end if;
  v_target:=v_domain.get_string('target_uid');v_residual_id:=v_domain.get_number('residual_task_id');
  v_reservation:=v_domain.get_number('source_reservation_id');v_new_reservation:=v_domain.get_number('new_reservation_id');
  v_pick_task:=v_domain.get_number('pick_task_id');
  select * into v_pallet from RRL_PALLETS where UID_PALLET=nvl(v_task.UID_PALLET,v_task.SSCC);
  v_article:=v_pallet.ARTICUL;
  if (v_task.RAW_ARTICUL is not null and v_task.RAW_ARTICUL!=v_article) or (v_task.TARGET_ARTICUL is not null and v_task.TARGET_ARTICUL!=v_article) then raise_application_error(-20887,'TASK_ARTICLE_CONFLICT');end if;
  select BASE_UOM,REMAIN into v_input_uom,v_source_p from RRL_REMAINS where UID_POLETA=v_pallet.UID_PALLET and CELL=v_task.FROM_CELL;
  v_input_uom:=nvl(v_task.UNIT_CODE,v_input_uom);
  select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input_uom;
  select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_factor_num,v_factor_den,v_scale
   from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input_uom and POLICY_VERSION=v_version;
  v_qbase:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(v_qty),v_factor_num,v_factor_den,v_scale);
  if v_version!=v_domain.get_number('uom_version') or RRL_STOCK_PLAN_HELPER.decimal_text(v_qbase)!=v_domain.get_string('base_quantity') or RRL_STOCK_PLAN_HELPER.decimal_text(v_source_p)!=v_domain.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: task quantity policy');end if;
  if v_task.QTY_MODE='PALLET' and v_qbase!=v_source_p then raise_application_error(-20886,'WHOLE_PALLET_STOCK_CHANGED');end if;
  if v_task.TASK_SOURCE='WAVE' then
   select STATUS into v_doc_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_task.SOURCE_DOC_ID for update;
   if v_doc_status='CANCELLED' then raise_application_error(-20886,'SOURCE_DOCUMENT_CANCELLED');end if;
  elsif v_task.TASK_SOURCE='SAP_RECEIPT' then
   if v_qty!=v_original then raise_application_error(-20886,'PUTAWAY_MUST_BE_WHOLE');end if;
   if v_task.TO_CELL_SLOT_ID is not null then
    select count(*) into v_n from RRL_RECEIPT_SLOT_CLAIM cl join RRL_TOPOLOGY_CELL_SLOT sl on sl.CELL_SLOT_ID=cl.CELL_SLOT_ID
     where cl.TASK_ID=v_task_id and cl.STATUS='RESERVED' and sl.ACTIVE=1;
    if v_n!=1 then raise_application_error(-20886,'PUTAWAY_SLOT_CONFLICT');end if;
   end if;
  elsif v_task.TASK_SOURCE in('MES_RAW_SUPPLY','MES_COMPLETION') then
   select STATUS into v_doc_status from RRL_PRODUCTION_ORDER
    where PRODUCTION_ORDER_ID=nvl(v_task.PRODUCTION_ORDER_ID,v_task.SOURCE_DOC_ID) for update;
   if v_doc_status='CANCELLED' then raise_application_error(-20886,'SOURCE_DOCUMENT_CANCELLED');end if;
  else raise_application_error(-20888,'TASK_DOMAIN_HANDLER_REQUIRED');end if;
  if v_target!=v_pallet.UID_PALLET then
   RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','PALLET:'||v_target));
   v_pallet.UID_PALLET:=v_target;v_pallet.SSCC:=null;v_pallet.UNIT_COUNT:=v_qbase;v_pallet.PRINTED:=0;
   if v_pallet.WEIGHT_BRUTTO is not null then v_pallet.WEIGHT_BRUTTO:=v_pallet.WEIGHT_BRUTTO*v_qbase/v_source_p;end if;
   insert into RRL_PALLETS values v_pallet;
  end if;
  if v_meta.has('unit_keys') and v_meta.get_array('unit_keys').get_size>0 then v_units:=v_meta.get_array('unit_keys').to_clob;end if;
  RRL_STOCK_TRANSFER_CORE.move(nvl(v_task.UID_PALLET,v_task.SSCC),v_target,v_task.FROM_CELL,v_task.TO_CELL,
   v_qbase,v_base,v_version,v_task.TO_WARE_ID,p_actor,1,v_reservation,v_units,v_new_reservation,v_task.TO_CELL_SLOT_ID);
  v_resource:=v_meta.get_number('resource_id');v_session:=v_meta.get_number('resource_session_id');v_equipment:=v_meta.get_number('equipment_id');
  if v_session is not null then
   select RESOURCE_ID,EQUIPMENT_ID,OPERATOR_USER_ID into v_resource,v_equipment,v_session_actor from RRL_RESOURCE_SESSION where SESSION_ID=v_session and STATUS='ACTIVE' for update;
   if v_session_actor is null or v_session_actor!=p_actor then raise_application_error(-20882,'TASK_SESSION_OWNER_CONFLICT');end if;
  end if;
  v_hash:=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));
  if v_residual_id is not null then
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_residual_id)));
   v_residual:=v_task;v_residual.TASK_ID:=v_residual_id;v_residual.QTY:=v_original-v_qty;
   v_residual.PARENT_TASK_ID:=v_task_id;v_residual.STATUS:='PLANNED';v_residual.FACT_QTY:=null;
   v_residual.CREATED_BY:=p_actor;v_residual.CREATED_AT:=systimestamp;v_residual.COMPLETION_HASH:=null;
   v_residual.COMPLETION_JSON:=null;v_residual.FINISHED_AT:=null;v_residual.ASSIGNED_TO:=null;
   v_residual.STARTED_AT:=null;v_residual.TARGET_UID_PALLET:=null;v_residual.LAST_ERROR:='Residual of task '||v_task_id;
   insert into RRL_WAREHOUSE_TASK values v_residual;
  end if;
  update RRL_WAREHOUSE_TASK set STATUS='DONE',QTY=v_qty,FACT_QTY=v_qty,TARGET_UID_PALLET=v_target,
   FROM_WARE_ID=v_task.FROM_WARE_ID,TO_WARE_ID=v_task.TO_WARE_ID,FINISHED_AT=systimestamp,ASSIGNED_TO=p_actor,RESOURCE_ID=nvl(v_resource,RESOURCE_ID),
   RESOURCE_SESSION_ID=nvl(v_session,RESOURCE_SESSION_ID),EQUIPMENT_ID=nvl(v_equipment,EQUIPMENT_ID),
   COMPLETION_HASH=v_hash,COMPLETION_JSON=p_request,LAST_ERROR=null where TASK_ID=v_task_id;
  insert into RRL_WAREHOUSE_TASK_STOCK_MOVE(STOCK_MOVE_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,
   SOURCE_TASK_ID,UID_PALLET,TARGET_UID_PALLET,FROM_CELL,TO_CELL,QTY,BASE_QTY,BASE_UOM,OPERATION_ID,CREATED_AT,CREATED_BY)
   values(RRL_WH_TASK_STOCK_MOVE_SQ.nextval,v_task_id,v_task.TASK_SOURCE,v_task.TASK_TYPE,v_task.SOURCE_DOC_TYPE,v_task.SOURCE_DOC_ID,
    v_task.SOURCE_TASK_ID,nvl(v_task.UID_PALLET,v_task.SSCC),v_target,v_task.FROM_CELL,v_task.TO_CELL,v_qty,v_qbase,v_base,v_op,systimestamp,p_actor);
  if v_resource is not null or v_session is not null or v_equipment is not null then
   insert into RRL_RESOURCE_FACT_EVENT(EVENT_ID,TASK_ID,SESSION_ID,RESOURCE_ID,EVENT_TYPE,EVENT_AT,EVENT_BY,PAYLOAD_JSON)
    values(RRL_RESOURCE_FACT_EVENT_SQ.nextval,v_task_id,v_session,v_resource,'COMPLETED',systimestamp,p_actor,p_request);
  end if;
  RRL_STOCK_TASK_DOMAIN.sync_fact(v_task,v_qty,v_target,v_residual_id,p_actor);
  v_sync_id:=v_domain.get_number('sync_id');v_sync_key:=v_domain.get_string('sync_key');
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK_SYNC',RRL_STOCK_PLAN_HELPER.decimal_text(v_sync_id)));
  merge into RRL_WAREHOUSE_TASK_SYNC d using(select v_sync_key SYNC_KEY from dual)s on(d.SYNC_KEY=s.SYNC_KEY)
   when matched then update set d.SYNC_STATUS='SYNCED',d.SYNCED_AT=systimestamp,d.UPDATED_AT=systimestamp,d.UPDATED_BY=p_actor,d.LAST_ERROR=null
   when not matched then insert(SYNC_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_TASK_ID,SOURCE_MOVEMENT_ID,SYNC_KEY,SYNC_STATUS,SYNC_ATTEMPT,CREATED_AT,UPDATED_AT,SYNCED_AT,UPDATED_BY)
    values(v_sync_id,v_task_id,v_task.TASK_SOURCE,v_task.TASK_TYPE,v_task.SOURCE_DOC_TYPE,v_task.SOURCE_DOC_ID,v_task.SOURCE_TASK_ID,v_task.SOURCE_MOVEMENT_ID,v_sync_key,'SYNCED',1,systimestamp,systimestamp,systimestamp,p_actor);
  v_result.put('operation_id',v_op);v_result.put('task_id',v_task_id);v_result.put('status','DONE');
  v_result.put('pallet_identifier',v_target);v_result.put('source_pallet_identifier',nvl(v_task.UID_PALLET,v_task.SSCC));
  v_result.put('cell',v_task.TO_CELL);v_result.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));
  v_result.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qbase));v_result.put('base_uom',v_base);
  v_result.put('residual_task_id',v_residual_id);p_result:=v_result.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_INVARIANT_CORE as
 function stock_uid(p_key raw) return varchar2 is
  v_pos pls_integer:=1;v_len pls_integer;v_end pls_integer;v_hex varchar2(2000):=rawtohex(p_key);
  v_version varchar2(10);v_kind varchar2(20);v_uid varchar2(200);
  function next_part return varchar2 is v_out varchar2(2000);
  begin
   v_end:=instr(v_hex,'3A',v_pos);
   -- RAW bytes are traversed, so UTF-8 component lengths remain byte lengths.
   while v_end>0 and mod(v_end,2)=0 loop v_end:=instr(v_hex,'3A',v_end+1);end loop;
   if v_end=0 then raise_application_error(-20841,'RESOURCE_ENCODING_INVALID');end if;
   v_len:=to_number(utl_i18n.raw_to_char(hextoraw(substr(v_hex,v_pos,v_end-v_pos)),'AL32UTF8'));
   v_pos:=v_end+2;
   v_out:=utl_i18n.raw_to_char(hextoraw(substr(v_hex,v_pos,2*v_len)),'AL32UTF8');v_pos:=v_pos+2*v_len;
   return v_out;
  end;
 begin
  v_version:=next_part;v_kind:=next_part;v_uid:=next_part;
  if v_version!='2' or v_kind!='STOCK' or v_uid is null or v_pos!=length(v_hex)+1
   or RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid)!=p_key then raise_application_error(-20841,'STOCK_RESOURCE_ENCODING_INVALID');end if;
  return v_uid;
 end;
 function snapshot_stock(p_resources clob) return clob is
  v json_array_t:=json_array_t();u json_object_t;x json_array_t;k json_object_t;v_uid varchar2(200);v_count number:=0;
 begin
  for r in(select distinct KEY_HEX from json_table(p_resources,'$[*]'
   columns(RANK_NO number path '$.rank',KEY_HEX varchar2(2000) path '$.key_hex')) where RANK_NO=50 order by KEY_HEX) loop
   v_uid:=stock_uid(hextoraw(r.KEY_HEX));
   RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid));
   u:=json_object_t();x:=json_array_t();u.put('uid',v_uid);
   for b in(select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM from RRL_REMAINS where UID_POLETA=v_uid order by CELL) loop
    v_count:=v_count+1;if v_count>20000 then raise_application_error(-20871,'STOCK_CLOSURE_TOO_LARGE');end if;
    k:=json_object_t();k.put('cell',b.CELL);k.put('p',RRL_STOCK_PLAN_HELPER.decimal_text(b.REMAIN));
    k.put('h',RRL_STOCK_PLAN_HELPER.decimal_text(b.HARD_RESERVED_BASE));k.put('version',b.STOCK_VERSION);k.put('base_uom',b.BASE_UOM);x.append(k);
   end loop;
   u.put('balances',x);v.append(u);
  end loop;
  return v.to_clob;
 end;
 procedure verify_posting(p_resources clob,p_before clob,p_operation varchar2) is
  v_uid varchar2(200);v_p number;v_h number;v_old number;v_delta number;v_sum number;v_bad number;v_base varchar2(20);v_unit_count number;
 begin
  if p_operation is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=p_operation then
   raise_application_error(-20863,'INVARIANT_CONTEXT_REQUIRED');end if;
  for r in(select distinct KEY_HEX from json_table(p_resources,'$[*]'
   columns(RANK_NO number path '$.rank',KEY_HEX varchar2(2000) path '$.key_hex')) where RANK_NO=50) loop
   v_uid:=stock_uid(hextoraw(r.KEY_HEX));
   RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid));
   for c in(
    select CELL from RRL_REMAINS where UID_POLETA=v_uid
    union select j.CELL from json_table(p_before,'$[*]' columns(UID varchar2(200) path '$.uid',
      nested path '$.balances[*]' columns(CELL varchar2(60) path '$.cell')))j where j.UID=v_uid and j.CELL is not null
    union select nvl(CELL_FROM,CELL_TO) from RRL_EVENTS where OPERATION_ID=p_operation and UID_POLETA=v_uid
   ) loop
    v_p:=0;v_h:=0;v_base:=null;
    begin select REMAIN,HARD_RESERVED_BASE,BASE_UOM into v_p,v_h,v_base from RRL_REMAINS where UID_POLETA=v_uid and CELL=c.CELL;
    exception when no_data_found then null;end;
    select nvl(sum(to_number(j.QTY,'999999999999999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''')),0) into v_old
     from json_table(p_before,'$[*]' columns(UID varchar2(200) path '$.uid',
      nested path '$.balances[*]' columns(CELL varchar2(60) path '$.cell',QTY varchar2(100) path '$.p')))j
      where j.UID=v_uid and j.CELL=c.CELL;
    select nvl(sum(BASE_QTY),0) into v_delta from RRL_EVENTS where OPERATION_ID=p_operation and UID_POLETA=v_uid and nvl(CELL_FROM,CELL_TO)=c.CELL;
    if v_p-v_old!=v_delta or v_p<0 or v_h<0 or v_h>v_p then raise_application_error(-20868,'JOURNAL_BALANCE_INVARIANT_FAILED');end if;
    select nvl(sum(BASE_QTY),0),nvl(sum(case when BASE_QTY is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!=v_base then 1 else 0 end),0)
      into v_sum,v_bad from RRL_STOCK_RESERVATION where UID_PALLET=v_uid and CELL=c.CELL
      and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
    if v_sum!=v_h or v_bad>0 then raise_application_error(-20869,'RESERVATION_BALANCE_INVARIANT_FAILED');end if;
    RRL_STOCK_UNIT_CORE.assert_composition(v_uid,c.CELL);
    select count(*) into v_unit_count from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=v_uid and CURRENT_CELL=c.CELL and STOCK_STATUS!='ISSUED';
    for z in(select RESERVATION_ID,BASE_QTY from RRL_STOCK_RESERVATION where UID_PALLET=v_uid and CELL=c.CELL
     and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING')) loop
     select count(*),nvl(sum(BASE_QTY),0) into v_bad,v_sum from RRL_WMS_RECEIPT_UNIT
      where CURRENT_UID=v_uid and CURRENT_CELL=c.CELL and HARD_RESERVATION_ID=z.RESERVATION_ID and STOCK_STATUS!='ISSUED';
     if v_unit_count>0 and v_sum!=z.BASE_QTY then raise_application_error(-20869,'RESERVATION_UNIT_INVARIANT_FAILED');end if;
    end loop;
   end loop;
  end loop;
  -- Every journal leg belongs to a planned stock key.
  for e in(select distinct UID_POLETA from RRL_EVENTS where OPERATION_ID=p_operation) loop
   RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',e.UID_POLETA));
  end loop;
 end;
end;
/
