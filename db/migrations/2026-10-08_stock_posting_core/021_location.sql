create or replace package RRL_STOCK_LOCATION_CORE authid definer
 accessible by(package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure assert_receiving(p_cell varchar2,p_expected_warehouse number);
 procedure assert_quarantine(p_cell varchar2,p_expected_warehouse number);
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2);
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
