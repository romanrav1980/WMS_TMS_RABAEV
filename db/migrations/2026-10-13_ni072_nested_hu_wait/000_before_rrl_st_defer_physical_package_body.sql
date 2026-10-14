create or replace package body RRL_ST_DEFER_PHYSICAL as

 function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null)return clob is

  n number;bad number;expected number;counted number:=0;wait_cell varchar2(50);needs_move boolean:=false;items json_array_t:=json_array_t();item json_object_t;result json_object_t:=json_object_t();

 begin

  select count(*)into bad from RRL_SBORKA_PALLETS p where p.ST_NUMBER=p_st and(

   exists(select 1 from RRL_INTERWARE_ONWARD_BIND b where b.ST_ID=p.ID)

   or exists(select 1 from RRL_IW_GROUP_ST_BIND b where b.ST_ID=p.ID)

   or exists(select 1 from RRL_IW_RECOVERY_ST_BIND b where b.ST_ID=p.ID));

  if bad!=0 then raise_application_error(-20886,'ST_DEFER_INTERWARE_REVISION_REQUIRED');end if;

  select count(*)into bad from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS p on p.ID=c.LEGACY_SBORKA_PALLET_ID

   where p.ST_NUMBER=p_st and exists(select 1 from RRL_CASE_CARRIER_LOT l join RRL_REMAINS r on r.UID_POLETA=l.LOT_UID where l.CASE_PICK_TASK_ID=c.CASE_PICK_TASK_ID and(r.REMAIN>0 or r.HARD_RESERVED_BASE>0));

  if bad>0 then return RRL_ST_DEFER_CASE_WAIT.snapshot(p_st,p_ware,p_ignore_plan);end if;

  select count(*),sum(case when nvl(f.FACT_QTY,0)>0 then 1 else 0 end)into expected,n

   from RRL_CUSTOMER_ORDER_FULFILLMENT f join RRL_SBORKA_PALLETS p on p.ID=f.LEGACY_SBORKA_PALLET_ID where p.ST_NUMBER=p_st;

  if nvl(n,0)=0 then result.put('state','UNPICKED');return result.to_clob;end if;

  if expected>200 then raise_application_error(-20881,'ST_DEFER_PREPARED_MEMBER_BOUND_200');end if;

  select count(*)into bad from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS p on p.ID=c.LEGACY_SBORKA_PALLET_ID where p.ST_NUMBER=p_st;

  if bad!=0 then raise_application_error(-20886,'ST_DEFER_PREPARED_CASE_DECISION_REQUIRED');end if;

  select max(DEFER_WAIT_CELL)into wait_cell from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=p_ware;

  for x in(select f.FULFILLMENT_ID,f.LEGACY_SBORKA_PALLET_ID,f.STATUS,f.FACT_QTY,f.FACT_UOM,f.PICKED_PALLET_UID,

    sum(f.FACT_QTY)over(partition by f.PICKED_PALLET_UID) LOT_FACT_QTY,f.PICKED_CASE_TASK_ID,f.PICKED_WAREHOUSE_TASK_ID,f.PICKED_OPERATION_ID,f.PICKED_STOCK_VERSION,

    t.STATUS TASK_STATUS,t.TASK_TYPE,t.TO_WARE_ID,t.TO_CELL PICKED_CELL,r.CELL TO_CELL,nvl(t.TARGET_UID_PALLET,t.UID_PALLET)TASK_UID,

    r.REMAIN,r.HARD_RESERVED_BASE,r.BASE_UOM,r.STOCK_VERSION,cell.WARE_ID CELL_WARE

   from RRL_CUSTOMER_ORDER_FULFILLMENT f join RRL_SBORKA_PALLETS p on p.ID=f.LEGACY_SBORKA_PALLET_ID

   left join RRL_WAREHOUSE_TASK t on t.TASK_ID=f.PICKED_WAREHOUSE_TASK_ID

   left join RRL_REMAINS r on r.UID_POLETA=f.PICKED_PALLET_UID and(r.REMAIN>0 or r.HARD_RESERVED_BASE>0)

   left join RRL_CELLS cell on cell.CELL=r.CELL where p.ST_NUMBER=p_st order by f.FULFILLMENT_ID)loop

   if x.STATUS!='PICKED'or nvl(x.FACT_QTY,0)<=0 or x.PICKED_CASE_TASK_ID is not null or x.PICKED_WAREHOUSE_TASK_ID is null

    or x.PICKED_OPERATION_ID is null or nvl(x.TASK_STATUS,'NONE')!='DONE'or nvl(x.TASK_TYPE,'NONE')!='PICKING_MOVE'

    or nvl(x.TO_WARE_ID,-1)!=p_ware or nvl(x.CELL_WARE,-1)!=p_ware or x.PICKED_PALLET_UID is null

    or nvl(x.TASK_UID,'NONE')!=x.PICKED_PALLET_UID or nvl(x.REMAIN,-1)!=x.LOT_FACT_QTY or nvl(x.HARD_RESERVED_BASE,-1)!=x.LOT_FACT_QTY

    or x.FACT_UOM is null or nvl(x.BASE_UOM,'NONE')!=x.FACT_UOM then raise_application_error(-20886,'ST_DEFER_WHOLE_PREPARED_STOCK_REQUIRED');end if;

   select count(*)into bad from RRL_WMS_HU_LINK h where h.ACTIVE_FLAG=1 and(h.CHILD_PALLET_UID=x.PICKED_PALLET_UID or h.PARENT_UID=x.PICKED_PALLET_UID);

   if bad!=0 then raise_application_error(-20886,'ST_DEFER_PREPARED_NESTED_DECISION_REQUIRED');end if;

   select count(*)into bad from RRL_WAREHOUSE_TASK w where w.STATUS not in('DONE','CANCELLED')and(w.UID_PALLET=x.PICKED_PALLET_UID or w.TARGET_UID_PALLET=x.PICKED_PALLET_UID) and(p_ignore_plan is null or not exists(select 1 from RRL_ST_DEFER_WAIT_PLAN wp where wp.TASK_ID=w.TASK_ID and wp.PLAN_OPERATION_ID=p_ignore_plan));

   if bad!=0 then raise_application_error(-20886,'ST_DEFER_PREPARED_PHYSICAL_TASK_OPEN');end if;

   if wait_cell is null or x.TO_CELL!=wait_cell then needs_move:=true;end if;

   item:=json_object_t();item.put('fulfillment_id',x.FULFILLMENT_ID);item.put('st_member_id',x.LEGACY_SBORKA_PALLET_ID);

   item.put('pallet_identifier',x.PICKED_PALLET_UID);item.put('cell',x.TO_CELL);item.put('original_picked_cell',x.PICKED_CELL);item.put('task_id',x.PICKED_WAREHOUSE_TASK_ID);

   item.put('picked_operation_id',x.PICKED_OPERATION_ID);item.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(x.FACT_QTY));

   item.put('pallet_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(x.LOT_FACT_QTY));item.put('base_uom',x.FACT_UOM);item.put('stock_version',x.STOCK_VERSION);item.put('picked_stock_version',x.PICKED_STOCK_VERSION);items.append(item);counted:=counted+1;

  end loop;

  if counted!=expected or counted<1 then raise_application_error(-20886,'ST_DEFER_EXACT_PREPARED_MEMBERS_REQUIRED');end if;

  select count(*)into bad from RRL_SBORKA_PALLETS p where p.ST_NUMBER=p_st and not exists(select 1 from RRL_CUSTOMER_ORDER_FULFILLMENT f where f.LEGACY_SBORKA_PALLET_ID=p.ID);

  if bad!=0 then raise_application_error(-20886,'ST_DEFER_MIXED_PREPARED_UNPICKED_REQUIRED');end if;

  result.put('state','PREPARED_WHOLE_STOCK');result.put('members',items);result.put('physical_move_required',needs_move);result.put('stock_changed',false);return result.to_clob;

 end;

end;


/
