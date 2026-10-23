create or replace package body RRL_STOCK_POOL_READ as
 function line_snapshot_json(p_line number)return clob is
  o RRL_CUSTOMER_ORDER_ROW%rowtype;h RRL_CUSTOMER_ORDER%rowtype;
  base varchar2(20);p_article varchar2(160);qty number;requested number;waived_qty number;choice_pending number;choice_waived number;hard_qty number;picked_qty number;picked_hard number;
  num number;den number;scale number;conversion number;x json_object_t;
  v_row_status varchar2(40);v_order_status varchar2(40);v_customer number;
 begin
  if p_line is null or p_line<1 or p_line!=trunc(p_line)then raise_application_error(-20881,'POOL_LINE_IDENTITY_REQUIRED');end if;
  select *into o from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ROW_ID=p_line;
  select *into h from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=o.CUSTOMER_ORDER_ID;
  p_article:=o.ARTICUL;v_row_status:=o.STATUS;v_order_status:=h.STATUS;v_customer:=h.CUSTOMER_ID;
  select BASE_UOM into base from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1
   order by POLICY_VERSION desc fetch first 1 row only;
   if o.UNIT_CODE is null then raise_application_error(-20868,'POOL_ORDER_UOM_REQUIRED');end if;
   select NUMERATOR,DENOMINATOR,BASE_SCALE,POLICY_VERSION into num,den,scale,conversion from RRL_STOCK_UOM_CONVERSION
    where ARTICUL=p_article and INPUT_UOM=o.UNIT_CODE and BASE_UOM=base order by POLICY_VERSION desc fetch first 1 row only;
   qty:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(o.ORDER_QTY),num,den,scale);
   select nvl(sum(sr.BASE_QTY),0) into hard_qty from RRL_STOCK_RESERVATION sr
    join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=sr.PICK_PLAN_LINE_ID
    where pl.CUSTOMER_ORDER_ROW_ID=o.CUSTOMER_ORDER_ROW_ID and sr.RESERVATION_KIND='HARD'
     and sr.ARTICUL=p_article and sr.STATUS in('ACTIVE','ALLOCATED','PICKING');
   -- Demand already secured physically must not be promised again in the common pool.
   select nvl(sum(nvl(pt.FACT_QTY,0)),0) into picked_qty from RRL_PICK_TASK pt
    join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID
    where pl.CUSTOMER_ORDER_ROW_ID=o.CUSTOMER_ORDER_ROW_ID and pt.ARTICUL=p_article
     and pt.STATUS in('IN_PROGRESS','DONE');
   -- Confirmed picks still carry HARD until shipment; count their overlap once.
   select nvl(sum(sr.BASE_QTY),0) into picked_hard from RRL_STOCK_RESERVATION sr
    join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=sr.PICK_PLAN_LINE_ID
    left join RRL_PICK_TASK pt on pt.PICK_TASK_ID=sr.SOURCE_LINE_ID
    where pl.CUSTOMER_ORDER_ROW_ID=o.CUSTOMER_ORDER_ROW_ID and sr.RESERVATION_KIND='HARD'
     and sr.ARTICUL=p_article and sr.STATUS in('ACTIVE','ALLOCATED','PICKING')
     and (exists(select 1 from RRL_CASE_CARRIER_LOT lot where lot.LOT_UID=sr.UID_PALLET)
      or (pt.TASK_TYPE='FULL_PALLET' and exists(select 1 from RRL_PICK_WAVE_TASK wt
       join RRL_WAREHOUSE_TASK wh on wh.SOURCE_TASK_ID=wt.PICK_WAVE_TASK_ID
       join RRL_WAREHOUSE_TASK_STOCK_MOVE mv on mv.TASK_ID=wh.TASK_ID
       where wt.PICK_TASK_ID=pt.PICK_TASK_ID and wh.TASK_SOURCE='WAVE' and wh.TASK_TYPE='PICKING_MOVE'
        and mv.TARGET_UID_PALLET=sr.UID_PALLET and mv.TO_CELL=sr.CELL)));
   requested:=qty;waived_qty:=RRL_WEIGHT_DEVIATION_READ.waived_line(o.CUSTOMER_ORDER_ROW_ID);qty:=greatest(0,qty-hard_qty-greatest(0,picked_qty-picked_hard)-waived_qty);
   RRL_WEIGHT_CHOICE_DEMAND_READ.adjustments(o.CUSTOMER_ORDER_ROW_ID,qty,choice_pending,choice_waived);
   waived_qty:=waived_qty+choice_waived;qty:=greatest(0,qty-choice_pending-choice_waived);
   x:=json_object_t();x.put('picked_hard_overlap',RRL_STOCK_PLAN_HELPER.decimal_text(picked_hard));x.put('picked_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(picked_qty));x.put('hard_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(hard_qty));x.put('line_id',o.CUSTOMER_ORDER_ROW_ID);x.put('order_id',o.CUSTOMER_ORDER_ID);x.put('customer_id',v_customer);
   x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));x.put('uom_version',conversion);x.put('order_status',v_order_status);x.put('line_status',v_row_status);

  x.put('warehouse',nvl(o.WARE_ID,h.WARE_ID));x.put('article',p_article);x.put('unit',base);
  x.put('requested_base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(requested));
  x.put('weight_choice_pending_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(choice_pending));
  x.put('accepted_weight_deviation_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(waived_qty));
  x.put('quantity_semantics',case when choice_pending>0 then 'UNALLOCATED_BASE_AFTER_PENDING_WEIGHT_CHOICE'when waived_qty>0 then 'UNALLOCATED_BASE_AFTER_ACCEPTED_WEIGHT_DEVIATION'else 'UNALLOCATED_BASE_NOT_SHIPPED_PROOF'end);
  x.put('open',v_row_status in('OPEN','PLANNED_FULL','PLANNED_PARTIAL','NO_STOCK')and
    v_order_status in('IMPORTED','OPEN','PLANNED_FULL','PLANNED_PARTIAL','NO_STOCK')and o.ORDER_QTY>0);
  return x.to_clob;
 exception when no_data_found then raise_application_error(-20868,'POOL_LINE_OR_UOM_NOT_FOUND');end;
 function snapshot_json(p_ware number,p_article varchar2) return clob is
  j json_object_t:=json_object_t();stocks json_array_t:=json_array_t();orders json_array_t:=json_array_t();reserves json_array_t:=json_array_t();x json_object_t;
  enabled number:=0;step number:=1;ver number:=0;available number:=0;eligible number;marked_free number;unit_count number;base varchar2(20);uom varchar2(20);
  n number;num number;den number;scale number;qty number;hard_qty number;picked_qty number;picked_hard number;conversion number;note varchar2(100);tp number;held number;
 begin
  if p_ware is null or p_ware<1 or p_ware!=trunc(p_ware) or p_article is null then raise_application_error(-20881,'POOL_IDENTITY_REQUIRED');end if;
  begin select nvl(SHIP_FROM_STOCK,case STOCK_ALLOC_CLASS when 'DRY_RACK' then 1 else 0 end),PICK_STEP_BASE,ALLOCATION_VERSION into enabled,step,ver from RRL_RECEIPT_SKU_RULE where WARE_ID=p_ware and ARTICUL=p_article;
  exception when no_data_found then null;end;
  select BASE_UOM into base from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1
   order by POLICY_VERSION desc fetch first 1 row only;
  select count(*) into n from RRL_STOCK_RESERVATION where ARTICUL=p_article and RESERVATION_KIND='SOFT'
   and STATUS in('ACTIVE','ALLOCATED') and QTY>0 and POOL_WARE_ID is null;
  if enabled=1 and n>0 then raise_application_error(-20886,'POOL_LEGACY_SOFT_REQUIRES_RECONCILIATION');end if;
  for s in(select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE,r.STOCK_VERSION,r.BASE_UOM from RRL_REMAINS r
    join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA join RRL_CELLS c on c.CELL=r.CELL
    where p.ARTICUL=p_article and c.WARE_ID=p_ware and r.REMAIN>0 order by r.UID_POLETA,r.CELL fetch first 501 rows only) loop
   if stocks.get_size>=500 then raise_application_error(-20881,'POOL_STOCK_BOUND_500');end if;
   eligible:=0;note:=RRL_STOCK_ELIGIBILITY.reason(s.UID_POLETA,s.CELL,p_ware,0,null,null,'ALLOCATE',null,p_article);
   if note is null and enabled=1 then
    if s.BASE_UOM!=base then raise_application_error(-20868,'POOL_BASE_UOM_CONFLICT');end if;
    eligible:=s.REMAIN-s.HARD_RESERVED_BASE;
    select count(*),nvl(sum(case when STOCK_STATUS='AVAILABLE' and HARD_RESERVATION_ID is null then BASE_QTY else 0 end),0)
     into unit_count,marked_free from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=s.UID_POLETA and CURRENT_CELL=s.CELL and STOCK_STATUS!='ISSUED';
    if unit_count>0 then eligible:=least(eligible,marked_free);end if;
   end if;
   available:=available+eligible;x:=json_object_t();x.put('uid',s.UID_POLETA);x.put('cell',s.CELL);
   x.put('stock_version',s.STOCK_VERSION);x.put('free',RRL_STOCK_PLAN_HELPER.decimal_text(eligible));x.put('reason',note);stocks.append(x);
  end loop;
  for o in(select r.CUSTOMER_ORDER_ROW_ID,r.CUSTOMER_ORDER_ID,r.ORDER_QTY,r.UNIT_CODE,r.STATUS ROW_STATUS,h.STATUS ORDER_STATUS,h.CUSTOMER_ID
    from RRL_CUSTOMER_ORDER_ROW r join RRL_CUSTOMER_ORDER h on h.CUSTOMER_ORDER_ID=r.CUSTOMER_ORDER_ID
    where nvl(r.WARE_ID,h.WARE_ID)=p_ware and r.ARTICUL=p_article and h.STATUS in('IMPORTED','OPEN','PLANNED_FULL','PLANNED_PARTIAL','NO_STOCK')
     and r.STATUS in('OPEN','PLANNED_FULL','PLANNED_PARTIAL','NO_STOCK') and r.ORDER_QTY>0

    order by h.SHIPMENT_DATE nulls last,r.SORTFIELD nulls last,h.CUSTOMER_ORDER_ID,r.LINE_NO fetch first 2001 rows only) loop
   if orders.get_size>=2000 then raise_application_error(-20881,'POOL_DEMAND_BOUND_2000');end if;
   x:=json_object_t.parse(line_snapshot_json(o.CUSTOMER_ORDER_ROW_ID));
   -- C-0157: an SAP top-up row is served by its own physical hold (taken over at wave launch), never by the common pool: its open
   -- demand here is reduced by the still ACTIVE hold; a blocked top-up row (cancelled proposal, terms or TRIP mismatch) gets nothing.
   tp:=RRL_TRADE_TOPUP_ADOPT.line_proposal(o.CUSTOMER_ORDER_ROW_ID);
   if tp=-1 then x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(0));
   elsif tp>0 then
    select nvl(sum(BASE_QTY),0)into held from RRL_TRADE_TOPUP_HOLD where PROPOSAL_ID=tp and STATUS='ACTIVE';
    qty:=case when x.get_string('quantity')='0'then 0 else RRL_STOCK_MATH.quantity(x.get_string('quantity'))end;
    x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(greatest(0,qty-held)));
   end if;
   x.remove('warehouse');x.remove('article');x.remove('unit');x.remove('requested_base_quantity');x.remove('quantity_semantics');x.remove('open');
   x.put('dispatch_order',orders.get_size);orders.append(x);
  end loop;
  for sr in(select RESERVATION_ID,SOURCE_DOC_ID,SOURCE_LINE_ID,QTY,RESERVATION_VERSION,STATUS from RRL_STOCK_RESERVATION
   where RESERVATION_KIND='SOFT' and POOL_WARE_ID=p_ware and ARTICUL=p_article and STATUS in('ACTIVE','ALLOCATED')
   order by RESERVATION_ID fetch first 2001 rows only) loop
   if reserves.get_size>=2000 then raise_application_error(-20881,'POOL_RESERVATION_BOUND_2000');end if;
   x:=json_object_t();x.put('id',sr.RESERVATION_ID);x.put('order_id',sr.SOURCE_DOC_ID);x.put('line_id',sr.SOURCE_LINE_ID);
   x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(sr.QTY));x.put('version',sr.RESERVATION_VERSION);x.put('status',sr.STATUS);reserves.append(x);
  end loop;
  j.put('warehouse',p_ware);j.put('article',p_article);j.put('from_stock',enabled);j.put('policy_version',ver);
  j.put('step',RRL_STOCK_PLAN_HELPER.decimal_text(step));j.put('unit',base);j.put('available',RRL_STOCK_PLAN_HELPER.decimal_text(available));
  j.put('stocks',stocks);j.put('orders',orders);j.put('reservations',reserves);return j.to_clob;
 end;
end;
/
