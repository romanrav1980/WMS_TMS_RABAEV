-- Read-only stock/demand view. Python domain owns proportional apportionment.
create or replace package RRL_STOCK_POOL_READ authid definer as
 function snapshot_json(p_ware number,p_article varchar2) return clob;
end;
/
create or replace package body RRL_STOCK_POOL_READ as
 function snapshot_json(p_ware number,p_article varchar2) return clob is
  j json_object_t:=json_object_t();stocks json_array_t:=json_array_t();orders json_array_t:=json_array_t();reserves json_array_t:=json_array_t();x json_object_t;
  enabled number:=0;step number:=1;ver number:=0;available number:=0;eligible number;marked_free number;unit_count number;base varchar2(20);uom varchar2(20);
  n number;num number;den number;scale number;qty number;conversion number;note varchar2(100);
 begin
  if p_ware is null or p_ware<1 or p_ware!=trunc(p_ware) or p_article is null then raise_application_error(-20881,'POOL_IDENTITY_REQUIRED');end if;
  begin select nvl(SHIP_FROM_STOCK,case STOCK_ALLOC_CLASS when 'DRY_RACK' then 1 else 0 end),PICK_STEP_BASE,ALLOCATION_VERSION into enabled,step,ver from RRL_RECEIPT_SKU_RULE where WARE_ID=p_ware and ARTICUL=p_article;
  exception when no_data_found then null;end;
  select BASE_UOM into base from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1
   order by POLICY_VERSION desc fetch first 1 row only;
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
     and not exists(select 1 from RRL_PICK_PLAN pp join RRL_PICK_TASK pt on pt.PICK_PLAN_ID=pp.PICK_PLAN_ID
      where pp.CUSTOMER_ORDER_ID=h.CUSTOMER_ORDER_ID and pt.ARTICUL=p_article and pt.STATUS in('IN_PROGRESS','DONE'))
    order by h.SHIPMENT_DATE nulls last,r.SORTFIELD nulls last,h.CUSTOMER_ORDER_ID,r.LINE_NO fetch first 2001 rows only) loop
   if orders.get_size>=2000 then raise_application_error(-20881,'POOL_DEMAND_BOUND_2000');end if;
   if o.UNIT_CODE is null then raise_application_error(-20868,'POOL_ORDER_UOM_REQUIRED');end if;
   select NUMERATOR,DENOMINATOR,BASE_SCALE,POLICY_VERSION into num,den,scale,conversion from RRL_STOCK_UOM_CONVERSION
    where ARTICUL=p_article and INPUT_UOM=o.UNIT_CODE and BASE_UOM=base order by POLICY_VERSION desc fetch first 1 row only;
   qty:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(o.ORDER_QTY),num,den,scale);
   x:=json_object_t();x.put('line_id',o.CUSTOMER_ORDER_ROW_ID);x.put('order_id',o.CUSTOMER_ORDER_ID);x.put('customer_id',o.CUSTOMER_ID);
   x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));x.put('uom_version',conversion);x.put('order_status',o.ORDER_STATUS);x.put('line_status',o.ROW_STATUS);
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
