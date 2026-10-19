create or replace package body RRL_TRADE_STOCK_GUARD as
 procedure fail(p_code varchar2) is begin raise_application_error(-20911,p_code);end;
 function owner_allowed(p_actor varchar2,p_ware number,p_owner varchar2,p_write number default 0) return number is n number;
 begin
  if RRL_ACCESS_API.is_admin(p_actor)=1 then return 1;end if;
  select count(*)into n from RRL_TRADE_OWNER_GRANT where USERNAME=p_actor and WARE_ID=p_ware and OWNER_ID=p_owner
   and CAN_VIEW=1 and(p_write=0 or CAN_OPERATE=1);return least(n,1);
 end;
 procedure assert_owner(p_actor varchar2,p_ware number,p_owner varchar2,p_write number default 0) is begin
  if owner_allowed(p_actor,p_ware,p_owner,p_write)<>1 then raise_application_error(-20882,'TRADE_OWNER_ACCESS_DENIED');end if;
 end;
 function reason(p_uid varchar2,p_cell varchar2,p_ware number,p_purpose varchar2) return varchar2 is n number;total number;tagged number;pending number;mixed number;
 begin
  select count(*)into n from RRL_TRADE_SITE where WARE_ID=p_ware;
  select count(*),count(a.PHYSICAL_UNIT_KEY),nvl(sum(case when a.MARK_STATE<>'VALID' then 1 else 0 end),0)
   into total,tagged,pending from RRL_WMS_RECEIPT_UNIT u left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
   where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_cell and u.STOCK_STATUS<>'ISSUED';
  if n=0 and tagged=0 then return null;end if;
  if total=0 or total<>tagged then return 'TRADE_ATTRIBUTES_REQUIRED';end if;
  select count(*)into mixed from(select distinct a.OWNER_ID,a.SKU_ID,a.MRC,a.EXPIRY_DATE from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_cell and u.STOCK_STATUS<>'ISSUED');
  if mixed>1 then return 'TRADE_MIXED_PALLET_BLOCKED';end if;
  select count(*)into n from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
   where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_cell and u.STOCK_STATUS<>'ISSUED'and a.MARK_STATE='REJECTED';
  if n>0 then return 'TRADE_CODE_REJECTED';end if;
  if pending>0 then return 'TRADE_CODE_VALIDATION_PENDING';end if;
  if p_purpose<>'REPLENISH'then
   select count(*)into n from RRL_TRADE_BUYOUT_UNIT bu join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=bu.PHYSICAL_UNIT_KEY
    join RRL_TRADE_BUYOUT bo on bo.BUYOUT_ID=bu.BUYOUT_ID
    where bu.HOLD_ACTIVE=1 and bo.BUYOUT_MODE='BEFORE_PICK'and u.CURRENT_CELL=p_cell
     and(u.CURRENT_UID=p_uid or exists(select 1 from RRL_TRADE_CELL_POLICY cp where cp.CELL=p_cell and cp.ZONE_KIND='PICK'));
   if n>0 then return 'TRADE_BUYOUT_RESERVATION_PENDING';end if;
   select count(*)into n from RRL_TRADE_CELL_POLICY cp join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_CELL=cp.CELL
    join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
    where cp.CELL=p_cell and cp.ZONE_KIND='PICK'and u.CURRENT_UID=p_uid and u.STOCK_STATUS<>'ISSUED'and cp.OWNER_ID<>a.OWNER_ID;
   if n>0 then return 'TRADE_PICK_OWNER_RANGE';end if;
  end if;
  if p_purpose<>'REPLENISH'or RRL_TRADE_PICK_CONTEXT.has_line=1 then return RRL_TRADE_PICK_CONTEXT.reason(p_uid,p_cell,p_ware,p_purpose);end if;
  return null;
 end;
 procedure assert_shipping_stock(p_uid varchar2,p_cell varchar2,p_ware number,p_actor varchar2,p_is_load number default 1)is
  v_task number;v_mode varchar2(20);v_target varchar2(100);v_reason varchar2(100);n number;
 begin
  begin
   select cl.PICK_TASK_ID,t.BUYOUT_MODE,t.TARGET_OWNER_ID into v_task,v_mode,v_target from RRL_CASE_CARRIER_LOT h
    join RRL_CASE_PICK_LINE cl on cl.CASE_PICK_LINE_ID=h.CASE_PICK_LINE_ID join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=cl.PICK_PLAN_LINE_ID
    join RRL_TRADE_ORDER_LINE t on t.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID where h.LOT_UID=p_uid;
  exception when no_data_found then
   begin
    select pt.PICK_TASK_ID,t.BUYOUT_MODE,t.TARGET_OWNER_ID into v_task,v_mode,v_target from RRL_PICK_TASK pt
     join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID join RRL_TRADE_ORDER_LINE t on t.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID
     where pt.PALLET_UID=p_uid and pt.TASK_TYPE='FULL_PALLET'and pt.STATUS='DONE';
   exception when no_data_found then raise_application_error(-20886,'TRADE_PICKED_SHIPMENT_BINDING_REQUIRED');end;
  end;
  RRL_TRADE_PICK_CONTEXT.enter_pick_task(v_task,p_actor);v_reason:=reason(p_uid,p_cell,p_ware,'SHIP');RRL_TRADE_PICK_CONTEXT.clear_line;
  if v_reason is not null then raise_application_error(-20886,v_reason);end if;
  if p_is_load=1 and v_mode in('BEFORE_PICK','AFTER_PICK')then
   select count(*)into n from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where u.CURRENT_UID=p_uid and u.STOCK_STATUS<>'ISSUED'and a.OWNER_ID<>v_target;
   if n>0 then raise_application_error(-20886,'TRADE_BUYOUT_REQUIRED_BEFORE_LOADING');end if;
  end if;
 exception when too_many_rows then RRL_TRADE_PICK_CONTEXT.clear_line;raise_application_error(-20886,'TRADE_PICKED_SOURCE_AMBIGUOUS');
 when others then RRL_TRADE_PICK_CONTEXT.clear_line;raise;
 end;
 procedure assert_command_stock(p_uid varchar2,p_request clob,p_actor varchar2) is
  j json_object_t:=json_object_t.parse(p_request);src json_object_t:=j.get_object('source');
  command_kind varchar2(80):=j.get_string('command_type');task_kind varchar2(80);v_task_id number;v_case_line number;n number;v_pick_task number;v_from varchar2(60);v_reason varchar2(100);
 begin
  for w in(select distinct c.WARE_ID from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL
   where r.UID_POLETA=p_uid and r.REMAIN>0 and(exists(select 1 from RRL_TRADE_SITE s where s.WARE_ID=c.WARE_ID)
    or exists(select 1 from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where u.CURRENT_UID=p_uid)))loop
   if command_kind in('OUTGOING_PALLET_CHECK','LOAD_SHIPMENT','HU_SHIP','SHIP_PALLET','SHIP_DOCUMENT')then
    select CELL into v_from from RRL_REMAINS where UID_POLETA=p_uid and REMAIN>0;
    assert_shipping_stock(p_uid,v_from,w.WARE_ID,p_actor,case when command_kind='OUTGOING_PALLET_CHECK'then 0 else 1 end);
   elsif command_kind in('CASE_PICK_CONFIRM','CASE_CARRIER_MOVE')then
    v_task_id:=src.get_number('case_task_id');if command_kind='CASE_PICK_CONFIRM'then v_case_line:=src.get_number('case_line_id');end if;
    select count(*)into n from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid and CASE_PICK_TASK_ID<>v_task_id;
    if n>0 then raise_application_error(-20886,'TRADE_CASE_FOREIGN_LOT');end if;
    begin
     select h.PICK_TASK_ID into v_pick_task from RRL_CASE_PICK_LINE h join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=h.CASE_PICK_TASK_ID
      where ct.CASE_PICK_TASK_ID=v_task_id and ct.WARE_ID=w.WARE_ID and h.CASE_PICK_LINE_ID=
       case when command_kind='CASE_PICK_CONFIRM'and not exists(select 1 from RRL_CASE_CARRIER_LOT lot where lot.LOT_UID=p_uid)
        then v_case_line
        else(select min(lot.CASE_PICK_LINE_ID)from RRL_CASE_CARRIER_LOT lot where lot.LOT_UID=p_uid and lot.CASE_PICK_TASK_ID=v_task_id having count(distinct lot.CASE_PICK_LINE_ID)=1)end;
    exception when no_data_found then raise_application_error(-20886,'TRADE_CASE_ORDER_BINDING_REQUIRED');end;
    RRL_TRADE_PICK_CONTEXT.enter_pick_task(v_pick_task,p_actor);
    select CELL into v_from from RRL_REMAINS where UID_POLETA=p_uid and REMAIN>0;
    v_reason:=reason(p_uid,v_from,w.WARE_ID,'PICK');RRL_TRADE_PICK_CONTEXT.clear_line;
    if v_reason is not null then raise_application_error(-20886,v_reason);end if;
   elsif command_kind='TASK_COMPLETE' then
    v_task_id:=src.get_number('task_id');
    select TASK_TYPE into task_kind from RRL_WAREHOUSE_TASK where TASK_ID=v_task_id;
    if task_kind='REPLENISHMENT'then
     begin
      select rt.PICK_TASK_ID,wh.FROM_CELL into v_pick_task,v_from from RRL_WAREHOUSE_TASK wh join RRL_PICK_WAVE_REPLENISH_TASK rt
       on wh.TASK_SOURCE='WAVE'and wh.SOURCE_DOC_ID=rt.PICK_WAVE_ID and wh.SOURCE_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID
       join RRL_PICK_WAVE pw on pw.PICK_WAVE_ID=rt.PICK_WAVE_ID
       where wh.TASK_ID=v_task_id and pw.WARE_ID=w.WARE_ID and wh.UID_PALLET=p_uid;
     exception when no_data_found then fail('TRADE_TASK_BINDING_REQUIRED');end;
     RRL_TRADE_PICK_CONTEXT.enter_pick_task(v_pick_task,p_actor);
     v_reason:=reason(p_uid,v_from,w.WARE_ID,'REPLENISH');RRL_TRADE_PICK_CONTEXT.clear_line;
     if v_reason is not null then fail(v_reason);end if;
    elsif task_kind<>'PUTAWAY'then fail('TRADE_TASK_BINDING_REQUIRED');end if;
   elsif command_kind not in('SAP_RECEIPT','RECEIPT_REVERSE','INTERNAL_MOVE','MANUAL_MOVE','COMPAT_MANUAL_MOVE','MOVE_QUARANTINE','INVENTORY_COUNT','WAVE_LAUNCH','WAVE_RESERVE_SOURCES','WAVE_PICK_RELEASE')then
    fail('TRADE_ORDER_BINDING_REQUIRED');
   end if;
   for o in(select distinct a.OWNER_ID from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
    where u.CURRENT_UID=p_uid and u.STOCK_STATUS<>'ISSUED')loop assert_owner(p_actor,w.WARE_ID,o.OWNER_ID,1);end loop;
  end loop;
 exception when too_many_rows then RRL_TRADE_PICK_CONTEXT.clear_line;raise_application_error(-20886,'TRADE_PICKED_SOURCE_AMBIGUOUS');
 when others then RRL_TRADE_PICK_CONTEXT.clear_line;raise;
 end;
 procedure assert_cell(p_cell varchar2) is
  v_ware number;policy RRL_TRADE_CELL_POLICY%rowtype;n number;total number;tagged number;groups_count number;pallet_mix number;face_count number;v_owner varchar2(100);
 begin
  select WARE_ID into v_ware from RRL_CELLS where CELL=p_cell;
  select count(*)into n from RRL_TRADE_SITE where WARE_ID=v_ware;
  select count(*),count(a.PHYSICAL_UNIT_KEY)into total,tagged from RRL_WMS_RECEIPT_UNIT u
   left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where u.CURRENT_CELL=p_cell and u.STOCK_STATUS<>'ISSUED';
  if total=0 or(n=0 and tagged=0)then return;end if;
  begin select *into policy from RRL_TRADE_CELL_POLICY where CELL=p_cell and WARE_ID=v_ware;
  exception when no_data_found then fail('TRADE_CELL_POLICY_REQUIRED');end;
  if policy.ZONE_KIND not in('RECEIVE','EXPEDITION') and total<>tagged then fail('TRADE_CELL_ATTRIBUTES_REQUIRED');end if;
  select count(*)into pallet_mix from(
   select CURRENT_UID from(select distinct u.CURRENT_UID,a.OWNER_ID,a.SKU_ID,a.MRC,a.EXPIRY_DATE
    from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
    where u.CURRENT_CELL=p_cell and u.STOCK_STATUS<>'ISSUED') group by CURRENT_UID having count(*)>1);
  if pallet_mix>0 then fail('TRADE_MIXED_PALLET_BLOCKED');end if;
  if policy.ZONE_KIND in('STORAGE','PICK')then
   select count(*),min(OWNER_ID)into groups_count,v_owner from(select distinct a.OWNER_ID,a.SKU_ID,a.MRC,a.EXPIRY_DATE
    from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
    where u.CURRENT_CELL=p_cell and u.STOCK_STATUS<>'ISSUED');
   if groups_count>1 then fail('TRADE_CELL_MIXED_STOCK');end if;
   if policy.ZONE_KIND='PICK' and v_owner<>policy.OWNER_ID then fail('TRADE_PICK_OWNER_RANGE');end if;
  end if;
  if policy.ZONE_KIND='PICK'then
   for item in(select distinct a.SKU_ID,a.OWNER_ID,a.MRC from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
    where u.CURRENT_CELL=p_cell and u.STOCK_STATUS<>'ISSUED')loop
    select count(distinct u.CURRENT_CELL)into face_count from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
     join RRL_TRADE_CELL_POLICY cp on cp.CELL=u.CURRENT_CELL and cp.WARE_ID=v_ware and cp.ZONE_KIND='PICK'
     where a.SKU_ID=item.SKU_ID and a.OWNER_ID=item.OWNER_ID and a.MRC=item.MRC and u.STOCK_STATUS<>'ISSUED';
    if face_count>3 then fail('TRADE_MAX_THREE_PICK_CELLS');end if;
   end loop;
  end if;
 end;
end;
/
