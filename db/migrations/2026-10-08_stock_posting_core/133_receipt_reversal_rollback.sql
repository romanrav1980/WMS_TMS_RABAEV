declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_BALANCE_CORE authid definer
 accessible by(package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_EVENT_BRIDGE,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number,
   p_base_uom varchar2,p_uom_version number,p_expected_version number default null);
 procedure write_move(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,p_uom_version number,p_line number,p_actor varchar2,p_event out number);
 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2,
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null);
end;
/

create or replace package RRL_STOCK_LOCATION_CORE authid definer
 accessible by(package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure assert_receiving(p_cell varchar2,p_expected_warehouse number);
 procedure assert_quarantine(p_cell varchar2,p_expected_warehouse number);
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2);
end;
/

create or replace package RRL_STOCK_UNIT_CORE authid definer
 accessible by(package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_INVARIANT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_TRANSFER_CORE,
 package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RECEIPT_CORE) as
 function automatic_units(p_uid varchar2,p_cell varchar2,p_qty number) return clob;
 procedure admit_captured(p_uid varchar2,p_cell varchar2);
 procedure assert_composition(p_uid varchar2,p_cell varchar2);
 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob);
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob);
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0);
end;
/

create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure reset_connection;
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
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null) is
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
   USER_ID,PRIHOD_NAKL_ID,OTHOD_NAKL_ID,PALLET_ROW_ID,OPERATION_ID,LINE_NO,LEG_NO,BASE_QTY,BASE_UOM,UOM_POLICY_VERSION)
   values(p_event,p_from,p_to,sysdate,abs(p_qty),p_type,p_uid,p_actor,v_prihod,p_outgoing_doc,p_pallet_row,v_op,p_line,p_leg,p_qty,p_base_uom,p_uom_version);
  RRL_STOCK_CTX_API.end_effect;
 exception when others then RRL_STOCK_CTX_API.end_effect;raise;
 end;
 procedure write_move(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,p_uom_version number,p_line number,p_actor varchar2,p_event out number) is
 begin
  if p_from is null or p_to is null or p_from=p_to or p_qty is null or p_qty<=0 then raise_application_error(-20870,'MOVE_JOURNAL_CONTRACT');end if;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_from),4);
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_to),4);
  write_event(p_uid,p_from,p_to,p_qty,p_base_uom,p_uom_version,p_line,1,2,p_actor,p_event);
 end;
 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2,
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null) is
 begin
  if p_signed_qty is null or p_signed_qty=0 or
   (p_signed_qty<0 and (p_from is null or p_to is not null)) or
   (p_signed_qty>0 and (p_to is null or p_from is not null)) then
   raise_application_error(-20870,'SIGNED_LEG_LOCATION_CONFLICT');
  end if;
  write_event(p_uid,p_from,p_to,p_signed_qty,p_base_uom,p_uom_version,p_line,p_leg,p_type,p_actor,p_event,p_outgoing_doc,p_pallet_row);
 end;
end;
/

create or replace package body RRL_STOCK_LOCATION_CORE as
 procedure assert_receiving(p_cell varchar2,p_expected_warehouse number) is v_ware number;v_block number;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_cell),4);
  select WARE_ID,nvl(BLOCKED_FOR_ACCEPT,0) into v_ware,v_block from RRL_CELLS where CELL=p_cell;
  if v_ware is null or p_expected_warehouse is null or v_ware!=p_expected_warehouse or v_block!=0 then raise_application_error(-20879,'RECEIVING_LOCATION_UNAVAILABLE');end if;
 end;
 procedure assert_quarantine(p_cell varchar2,p_expected_warehouse number) is v_ware number;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_cell),4);
  select WARE_ID into v_ware from RRL_CELLS where CELL=p_cell;
  if v_ware is null or p_expected_warehouse is null or v_ware!=p_expected_warehouse then raise_application_error(-20877,'QUARANTINE_WAREHOUSE_CONFLICT');end if;
 end;
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2) is
  v_ware number;v_remain number;v_replenish number;v_accept number;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_cell),4);
  select WARE_ID,nvl(BLOCKED_FOR_REMAINS,0),nvl(BLOCKED_FOR_POPOLNENIE,0),nvl(BLOCKED_FOR_ACCEPT,0)
   into v_ware,v_remain,v_replenish,v_accept from RRL_CELLS where CELL=p_cell;
  if p_expected_warehouse is null or v_ware is null or v_ware!=p_expected_warehouse then
   raise_application_error(-20877,'WAREHOUSE_LOCATION_CONFLICT');
  end if;
  if p_role not in('SOURCE','TARGET','RECEIVE') or p_role is null then raise_application_error(-20878,'LOCATION_ROLE_INVALID'); end if;
  if v_remain!=0 or v_replenish!=0 or(p_role in('TARGET','RECEIVE') and v_accept!=0) then
   raise_application_error(-20879,'LOCATION_BLOCKED: quarantine/unavailable cell excluded');
  end if;
 end;
end;
/

create or replace package body RRL_STOCK_UNIT_CORE as
 procedure require_context is
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then
   raise_application_error(-20863,'UNIT_WRITE_FORBIDDEN');end if;
 end;
 procedure own_unit(p_key varchar2) is
 begin
  if p_key is null then raise_application_error(-20884,'UNIT_BINDING_REQUIRED');end if;
  begin RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',p_key));
  exception when others then if sqlcode=-20850 then raise_application_error(-20890,'CLOSURE_CHANGED: units');else raise;end if;end;
 end;
 procedure assert_composition(p_uid varchar2,p_cell varchar2) is
  v_p number;v_base varchar2(20);v_total number;v_count number;v_bad number;v_article varchar2(160);v_marked number;v_scale number;
 begin
  select REMAIN,BASE_UOM into v_p,v_base from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell;
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article),0),
   nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=v_article),0),
   case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article) then 1 else 0 end) into v_marked from dual;
  select count(*),nvl(sum(BASE_QTY),0),nvl(sum(case when PHYSICAL_UNIT_KEY is null or STOCK_STATUS is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!=v_base then 1 else 0 end),0)
   into v_count,v_total,v_bad from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and (STOCK_STATUS is null or STOCK_STATUS!='ISSUED');
  select max(BASE_SCALE) into v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and BASE_UOM=v_base;
  if v_scale is null then raise_application_error(-20868,'COMPOSITION_BASE_POLICY_REQUIRED');end if;
  select count(*) into v_bad from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and (STOCK_STATUS is null or STOCK_STATUS!='ISSUED')
   and (STOCK_STATUS is null or BASE_QTY is null or BASE_QTY<=0 or abs(BASE_QTY)>=power(10,18) or trunc(BASE_QTY,v_scale)!=BASE_QTY or BASE_UOM is null or BASE_UOM!=v_base or PHYSICAL_UNIT_KEY is null);
  if v_bad>0 or (v_count>0 and v_total!=v_p) or (v_marked=1 and v_p>0 and v_count=0) then
   raise_application_error(-20884,'PHYSICAL_COMPOSITION_CONFLICT');end if;
 end;
 function automatic_units(p_uid varchar2,p_cell varchar2,p_qty number) return clob is
  a json_array_t:=json_array_t();v_n number;v_qty number:=0;
 begin
  require_context;assert_composition(p_uid,p_cell);
  select count(*) into v_n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';
  if v_n=0 then return null;end if;
  for u in(select PHYSICAL_UNIT_KEY,BASE_QTY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='AVAILABLE' and HARD_RESERVATION_ID is null order by PHYSICAL_UNIT_KEY) loop
   exit when v_qty=p_qty;
   own_unit(u.PHYSICAL_UNIT_KEY);
   if v_qty+u.BASE_QTY>p_qty then raise_application_error(-20884,'PHYSICAL_UNIT_ALLOCATION_REQUIRES_SELECTION');end if;
   a.append(u.PHYSICAL_UNIT_KEY);v_qty:=v_qty+u.BASE_QTY;
   if a.get_size>10000 then raise_application_error(-20884,'UNIT_SELECTION_BOUND');end if;
  end loop;
  if v_qty!=p_qty then raise_application_error(-20884,'ADMITTED_FREE_UNITS_INSUFFICIENT');end if;
  return a.to_clob;
 end;
 procedure admit_captured(p_uid varchar2,p_cell varchar2) is
 begin
  require_context;assert_composition(p_uid,p_cell);
  for u in(select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='CAPTURED') loop own_unit(u.PHYSICAL_UNIT_KEY);end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT set STOCK_STATUS='AVAILABLE',UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='CAPTURED';
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob) is v_total number;v_count number;v_qty number;v_expected number;v_distinct number;
 begin
  require_context;assert_composition(p_uid,p_cell);
  select count(*) into v_total from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';
  if v_total=0 then return;end if;
  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_qty from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  if v_qty!=p_qty then raise_application_error(-20884,'ISSUE_UNIT_QUANTITY_CONFLICT');end if;
  if p_units is not null then
   select count(*),count(distinct K) into v_expected,v_distinct from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
   if v_count!=v_expected or v_expected!=v_distinct then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;
  end if;
  for r in(select PHYSICAL_UNIT_KEY,STOCK_STATUS,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop
   own_unit(r.PHYSICAL_UNIT_KEY);
   if r.HARD_RESERVATION_ID is not null then raise_application_error(-20869,'UNIT_RESERVED_BY_OTHER_OWNER');end if;
   if r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;
  end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT u set STOCK_STATUS='ISSUED',UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob) is
  v_count number;v_total number;v_chosen number;v_qty number;v_expected number;
 begin
  require_context;assert_composition(p_uid,p_cell);
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_total from RRL_WMS_RECEIPT_UNIT
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';
  if v_count=0 then return;end if;
  select count(*),nvl(sum(BASE_QTY),0) into v_chosen,v_qty from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  if v_qty!=p_qty then raise_application_error(-20884,'RESERVATION_UNIT_QUANTITY_CONFLICT');end if;
  if p_units is not null then
   select count(*),count(distinct K) into v_expected,v_count from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
   if v_expected!=v_count or v_expected!=v_chosen then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;
  end if;
  for r in(select PHYSICAL_UNIT_KEY,HARD_RESERVATION_ID,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop
   own_unit(r.PHYSICAL_UNIT_KEY);
   if r.HARD_RESERVATION_ID is not null then raise_application_error(-20869,'UNIT_ALREADY_RESERVED');end if;
   if r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;
  end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT u set HARD_RESERVATION_ID=p_id,UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0) is
  v_qty number;v_count number;v_expected number;v_distinct number;v_uid varchar2(200);v_cell varchar2(60);
 begin
  require_context;
  select UID_PALLET,CELL into v_uid,v_cell from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id;
  assert_composition(v_uid,v_cell);
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid));
  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_qty from RRL_WMS_RECEIPT_UNIT u
   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  if v_count=0 then
   select count(*) into v_expected from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=v_uid and CURRENT_CELL=v_cell and STOCK_STATUS!='ISSUED';
   if v_expected>0 then raise_application_error(-20869,'RESERVATION_UNIT_BINDING_REQUIRED');end if;
   return;end if;
  if v_qty!=p_qty then raise_application_error(-20884,'RESERVATION_UNIT_QUANTITY_CONFLICT');end if;
  if p_units is not null then
   select count(*),count(distinct K) into v_expected,v_distinct from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
   if v_count!=v_expected or v_expected!=v_distinct then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;
  end if;
  for r in(select PHYSICAL_UNIT_KEY,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT u
   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop
   own_unit(r.PHYSICAL_UNIT_KEY);
   if p_issue=1 and r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;
  end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',v_uid,v_cell);
  update RRL_WMS_RECEIPT_UNIT u set HARD_RESERVATION_ID=null,UNIT_VERSION=UNIT_VERSION+1,
   STOCK_STATUS=case when p_issue=1 then 'ISSUED' else STOCK_STATUS end
   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
 end;
end;
/

create or replace package body RRL_STOCK_POSTING_API as
 g_request clob;g_resolution clob;g_change_before clob;g_actor varchar2(50);g_operation varchar2(100);g_kind varchar2(80);g_tx varchar2(100);g_prepared boolean:=false;
 procedure reset_connection is
 begin
  RRL_STOCK_CTX_API.clear_operation;RRL_STOCK_LOCK_API.clear_plan;
  g_request:=null;g_resolution:=null;g_change_before:=null;g_actor:=null;g_operation:=null;g_kind:=null;g_tx:=null;g_prepared:=false;
 end;
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null) is
  v_doc json_object_t;v_policies clob;v_resources clob;v_exists number;v_release varchar2(20);v_domain clob;v_resolution json_object_t:=json_object_t();
  v_plan json_array_t:=json_array_t();v_entry json_object_t:=json_object_t();v_resources_json json_array_t:=json_array_t();
 begin
  p_replay:=null;
  if g_prepared or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then
   raise_application_error(-20862,'POSTING_ALREADY_ENTERED');
  end if;
  if p_request is null or dbms_lob.getlength(p_request)>4194304 then raise_application_error(-20871,'OPERATION_CONTRACT_INVALID'); end if;
  v_doc:=json_object_t.parse(p_request);v_doc.on_error(1);
  g_operation:=v_doc.get_string('operation_id');g_kind:=v_doc.get_string('command_type');
  if v_doc.get_number('contract_version') is null or v_doc.get_number('contract_version')!=2 or v_doc.get_string('actor') is null
   or v_doc.get_string('actor')!=p_actor or p_actor is null or length(p_actor)>50
   or g_operation is null or length(g_operation)>100 or g_kind is null then
   raise_application_error(-20871,'OPERATION_CONTRACT_INVALID');
  end if;
  -- Immutable committed replay is considered before any mutable article/cell/UOM validation.
  select count(*) into v_exists from RRL_STOCK_OPERATION where OPERATION_ID=g_operation;
  if v_exists!=0 then
   v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK')));v_entry.put('mode',4);v_plan.append(v_entry);
   v_entry:=json_object_t();v_entry.put('rank',10);
   v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('OP',g_operation)));v_resources_json.append(v_entry);
   v_policies:=v_plan.to_clob;v_resources:=v_resources_json.to_clob;
  else
   if g_kind in('MANUAL_MOVE','COMPAT_MANUAL_MOVE') then RRL_STOCK_COMMAND_PLAN.compile_move(p_request,g_operation,v_policies,v_resources);
   elsif g_kind='WAVE_LAUNCH' then RRL_STOCK_WAVE_LAUNCH_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='INVENTORY_REGISTER_LOT' then RRL_STOCK_INVENTORY_BIRTH.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='INVENTORY_COUNT' then RRL_STOCK_INVENTORY_CMD.compile_count(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='MES_RAW_TASK_CANCEL' then RRL_STOCK_MES_CANCEL_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('MES_RELEASE_TO_PRODUCTION','MES_CALCULATE_SUPPLY') then RRL_STOCK_MES_SUPPLY_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('DOCUMENT_RELEASE_RESERVATIONS','WAVE_CANCEL','WAVE_RELEASE','PICK_PLAN_CANCEL') then RRL_STOCK_DOC_RESERVE_CMD.compile_release(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='WAVE_RESERVE_SOURCES' then RRL_STOCK_WAVE_CMD.compile_reserve(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('SHIP_DOCUMENT','SHIP_PALLET') then RRL_STOCK_SHIPPING_CORE.compile_shipment(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('INTERNAL_MOVE','MOVE_QUARANTINE') then RRL_STOCK_INTERNAL_CMD.compile_move(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='MES_MOVEMENTS' then RRL_STOCK_MES_MOVEMENT_PLAN.compile_movements(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='SAP_RECEIPT' then RRL_STOCK_RECEIPT_PLAN.compile_receipt(p_request,g_operation,p_hints,v_policies,v_resources,v_domain);
   elsif g_kind='TASK_COMPLETE' then RRL_STOCK_TASK_PLAN.compile_task(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE','RESERVATION_RELEASE','RESERVATION_CANCEL','RESERVATION_CONSUME') then RRL_STOCK_RESERVATION_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED');end if;
  end if;
  RRL_STOCK_LOCK_API.begin_plan;
  RRL_STOCK_LOCK_API.acquire_policies(v_policies);
  RRL_STOCK_LOCK_API.acquire_resources(v_resources);
  select STATE into v_release from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if v_release!='ACTIVE' then raise_application_error(-20860,'STOCK_RELEASE_NOT_ACTIVE'); end if;
  if v_domain is not null then v_resolution.put('domain',json_object_t.parse(v_domain));end if;
  v_resolution.put('stock_before',json_array_t.parse(RRL_STOCK_INVARIANT_CORE.snapshot_stock(v_resources)));
  v_resolution.put('resources',json_array_t.parse(v_resources));
  v_resolution.put('policies',json_array_t.parse(v_policies));
  RRL_STOCK_OPERATION_CORE.begin_operation(p_request,p_actor,g_operation,g_kind,p_replay,v_resolution.to_clob);
  if p_replay is not null then return; end if;
  g_change_before:=RRL_STOCK_CHANGE_AUDIT.snapshot(v_resources);
  g_request:=p_request;g_resolution:=v_resolution.to_clob;g_actor:=p_actor;g_tx:=dbms_transaction.local_transaction_id(false);g_prepared:=true;
  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.begin_staging(v_resolution.get_object('domain').get_string('uid'),v_resolution.get_object('domain').get_string('receive_cell'));end if;
 end;
 procedure execute_prepared(p_result out clob) is
  v_outbox number;v_existing number;v_key varchar2(100);v_json json_object_t;v_resolved json_object_t;v_event json_object_t;v_changes clob;v_resources clob;v_after clob;
 begin
  if not g_prepared or g_tx is null or dbms_transaction.local_transaction_id(false) is null
   or g_tx!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20850,'WRITE_PLAN_VIOLATION'); end if;
  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.end_effect;end if;
  if g_kind in('MANUAL_MOVE','COMPAT_MANUAL_MOVE') then RRL_STOCK_MOVE_CORE.manual_whole(g_request,g_actor,p_result);
  elsif g_kind='WAVE_LAUNCH' then RRL_STOCK_WAVE_LAUNCH_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='INVENTORY_REGISTER_LOT' then RRL_STOCK_INVENTORY_BIRTH.execute_command(g_request,g_actor,p_result);
   elsif g_kind='INVENTORY_COUNT' then RRL_STOCK_INVENTORY_CMD.execute_count(g_request,g_actor,p_result);
   elsif g_kind='MES_RAW_TASK_CANCEL' then RRL_STOCK_MES_CANCEL_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind in('MES_RELEASE_TO_PRODUCTION','MES_CALCULATE_SUPPLY') then RRL_STOCK_MES_SUPPLY_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind in('DOCUMENT_RELEASE_RESERVATIONS','WAVE_CANCEL','WAVE_RELEASE','PICK_PLAN_CANCEL') then RRL_STOCK_DOC_RESERVE_CMD.execute_release(g_request,g_actor,p_result);
  elsif g_kind='WAVE_RESERVE_SOURCES' then RRL_STOCK_WAVE_CMD.execute_reserve(g_request,g_actor,p_result);
  elsif g_kind in('SHIP_DOCUMENT','SHIP_PALLET') then RRL_STOCK_SHIPPING_CORE.execute_shipment(g_request,g_actor,p_result);
  elsif g_kind in('INTERNAL_MOVE','MOVE_QUARANTINE') then RRL_STOCK_INTERNAL_CMD.execute_move(g_request,g_actor,p_result);
  elsif g_kind='MES_MOVEMENTS' then RRL_STOCK_MES_MOVEMENT_CORE.execute_movements(g_request,g_actor,p_result);
  elsif g_kind='SAP_RECEIPT' then RRL_STOCK_RECEIPT_CORE.execute_receipt(g_request,g_actor,p_result);
  elsif g_kind='TASK_COMPLETE' then RRL_STOCK_TASK_CORE.execute_task(g_request,g_actor,p_result);
  elsif g_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE','RESERVATION_RELEASE','RESERVATION_CANCEL','RESERVATION_CONSUME') then RRL_STOCK_RESERVATION_CMD.execute_command(g_request,g_actor,p_result);
  else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED'); end if;
  v_resolved:=json_object_t.parse(g_resolution);
  RRL_STOCK_INVARIANT_CORE.verify_posting(v_resolved.get_array('resources').to_clob,v_resolved.get_array('stock_before').to_clob,g_operation);
  v_key:='STOCK:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(g_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256));
  RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','STOCK.OUTBOX:'||substr(v_key,7)));
  select count(*) into v_existing from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=v_key;
  if v_existing!=0 then raise_application_error(-20889,'OUTBOX_IDENTITY_CONFLICT'); end if;
  v_resources:=v_resolved.get_array('resources').to_clob;
  v_after:=RRL_STOCK_CHANGE_AUDIT.snapshot(v_resources);v_changes:=RRL_STOCK_CHANGE_AUDIT.differences(g_change_before,v_after);
  v_event:=json_object_t();v_event.put('contract_version',3);v_event.put('operation_id',g_operation);v_event.put('command_type',g_kind);
  v_event.put('source',json_object_t.parse(g_request).get_object('source'));v_event.put('result',json_object_t.parse(p_result));
  v_event.put('stock_before',v_resolved.get_array('stock_before'));
  v_event.put('stock_after',json_array_t.parse(RRL_STOCK_INVARIANT_CORE.snapshot_stock(v_resources)));
  v_event.put('composition_changes',json_object_t.parse(v_changes));
  v_event.put('immutable_request_reference',g_operation);
  v_outbox:=RRL_TRACEABILITY_API.enqueue_event('STOCK_POSTED','STOCK_OPERATION',g_operation,v_key,v_event.to_clob,'WMS',g_operation);
  v_json:=json_object_t.parse(p_result);v_json.put('outbox_id',v_outbox);p_result:=v_json.to_clob;
  RRL_STOCK_OPERATION_CORE.finish_operation(g_operation,p_result);
  g_prepared:=false;
 end;
end;
/

@@132_storno_native_rollback.sql
@@014b_recompile.sql
