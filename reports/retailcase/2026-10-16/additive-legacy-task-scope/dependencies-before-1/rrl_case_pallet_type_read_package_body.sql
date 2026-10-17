create or replace package body RRL_CASE_PALLET_TYPE_READ as
 function describe_type(p_task number,p_actor varchar2)return clob is
  ct RRL_CASE_PICK_TASK%rowtype;j json_object_t:=json_object_t();planned_type number;planned_name varchar2(160);actual_name varchar2(160);
  held_no number;lot_no number;parent_no number;reason_value varchar2(100);
 begin
  RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_view');
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  planned_type:=RRL_RECIPIENT_PALLET_POLICY.type_id(ct.CUSTOMER_ID,ct.CUSTOMER_STORE_MAP_ID);
  if planned_type is not null then select PALLET_TYPE_NAME into planned_name from RRL_PALLET_TYPE where PALLET_TYPE_ID=planned_type;end if;
  select PALLET_TYPE_NAME into actual_name from RRL_PALLET_TYPE where PALLET_TYPE_ID=ct.PALLET_TYPE_ID;
  select count(*)into held_no from RRL_TARE_BOOK where PLACE_KIND='CASE'and PLACE_ID=to_char(p_task,'TM9')and STATUS='HELD';
  select count(*)into lot_no from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=p_task;
  select count(*)into parent_no from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=p_task and ACTIVE_FLAG=1;
  if ct.STATUS not in('NEW','ASSIGNED')or ct.STARTED_AT is not null or nvl(ct.PICKED_QTY,0)!=0 or lot_no>0 then reason_value:='CASE_TYPE_USE_PHYSICAL_REPACK';
  elsif ct.LEGACY_SBORKA_PALLET_ID is not null or ct.CURRENT_CELL is not null or parent_no>0 then reason_value:='CASE_TYPE_BOUND_PLACE_REPACK_REQUIRED';
  elsif held_no>0 then reason_value:='CASE_TYPE_RELEASE_EMPTY_TARE_FIRST';end if;
  j.put('case_task_id',p_task);j.put('warehouse_id',ct.WARE_ID);j.put('sscc',ct.SSCC);j.put('version',nvl(ct.CONTENT_VERSION,0));j.put('status',ct.STATUS);
  j.put('planned_pallet_type_id',planned_type);j.put('planned_type_name',planned_name);j.put('planned_source','RECIPIENT_RULE');
  j.put('actual_pallet_type_id',ct.PALLET_TYPE_ID);j.put('actual_type_name',actual_name);j.put('can_change_empty_type',reason_value is null);
  j.put('change_blocker',reason_value);j.put('assigned_to',ct.ASSIGNED_TO);j.put('stock_changed',false);
  return j.to_clob;
 end;
end;
/
