-- Bind delivered generic replenishment to existing CASE consumers; no second stock writer.
create or replace package RRL_STOCK_REPL_BIND authid definer
 accessible by(package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE) as
 procedure plan_bind(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_anchors in out nocopy json_array_t,p_plan out json_object_t);
 procedure execute_bind(p_task RRL_WAREHOUSE_TASK%rowtype,p_uid varchar2,p_reservation number,p_plan json_object_t,p_actor varchar2);
end;
/
create or replace package body RRL_STOCK_REPL_BIND as
 function coverage(p_pick number) return number is q number;
 begin
  select nvl(sum(BASE_QTY),0) into q from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'
   and SOURCE_LINE_ID=p_pick and RESERVATION_DOMAIN='PICKING' and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
  return q;
 end;
 function consumer_signature(p_task RRL_WAREHOUSE_TASK%rowtype) return varchar2 is
  a json_array_t:=json_array_t();x json_object_t;
 begin
  for l in(select l.CASE_PICK_LINE_ID,l.PICK_TASK_ID,l.PLANNED_QTY,l.PICKED_QTY,l.STATUS,ct.STATUS CASE_STATUS
   from RRL_CASE_PICK_LINE l join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID
   where l.PICK_WAVE_ID=p_task.SOURCE_DOC_ID and l.ARTICUL=(select ARTICUL from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=p_task.SOURCE_TASK_ID) and l.CELL_CODE=p_task.TO_CELL
    and l.STATUS not in('PICKED','CANCELLED') and ct.STATUS!='CANCELLED'
   order by l.PICK_SEQUENCE nulls last,l.CASE_PICK_LINE_ID fetch first 201 rows only) loop
   if a.get_size>=200 then raise_application_error(-20881,'GENERIC_REPLENISHMENT_CONSUMER_BOUND');end if;
   x:=json_object_t();x.put('line',l.CASE_PICK_LINE_ID);x.put('pick',l.PICK_TASK_ID);x.put('planned',l.PLANNED_QTY);
   x.put('picked',l.PICKED_QTY);x.put('status',l.STATUS);x.put('case_status',l.CASE_STATUS);x.put('covered',coverage(l.PICK_TASK_ID));a.append(x);
  end loop;
  return rawtohex(dbms_crypto.hash(a.to_clob,dbms_crypto.hash_sh256));
 end;
 procedure plan_bind(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_anchors in out nocopy json_array_t,p_plan out json_object_t) is
  rt RRL_PICK_WAVE_REPLENISH_TASK%rowtype;x json_object_t;bindings json_array_t:=json_array_t();q number;remaining number;rid number;covered number;
 begin
  p_plan:=json_object_t();p_plan.put('lines',bindings);
  if p_task.TASK_SOURCE!='WAVE' or p_task.TASK_TYPE!='REPLENISHMENT' then return;end if;
  select * into rt from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=p_task.SOURCE_TASK_ID;
  if rt.PICK_TASK_ID is not null then
   declare pt RRL_PICK_TASK%rowtype;covered_target number;begin
    select * into pt from RRL_PICK_TASK where PICK_TASK_ID=rt.PICK_TASK_ID;
    if pt.TASK_TYPE!='CASE_PICK' then return;end if;
    select nvl(sum(BASE_QTY),0) into covered_target from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'
     and SOURCE_DOC_ID=p_task.SOURCE_DOC_ID and SOURCE_LINE_ID=pt.PICK_TASK_ID and CELL=p_task.TO_CELL
     and RESERVATION_DOMAIN='PICKING' and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
    p_plan.put('explicit',true);p_plan.put('pick_task',pt.PICK_TASK_ID);p_plan.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(pt.QTY));
    p_plan.put('fact',RRL_STOCK_PLAN_HELPER.decimal_text(nvl(pt.FACT_QTY,0)));p_plan.put('status',pt.STATUS);
    p_plan.put('target_covered',RRL_STOCK_PLAN_HELPER.decimal_text(covered_target));
    RRL_STOCK_PLAN_HELPER.row_key(p_anchors,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(pt.PICK_TASK_ID));
    return;
   end;
  end if;
  p_plan.put('signature',consumer_signature(p_task));
  if rt.SOURCE_RESERVATION_ID is null then raise_application_error(-20886,'GENERIC_REPLENISHMENT_RESERVATION_REQUIRED');end if;
  select least(BASE_QTY,p_qty) into remaining from RRL_STOCK_RESERVATION where RESERVATION_ID=rt.SOURCE_RESERVATION_ID;
  for l in(select l.* from RRL_CASE_PICK_LINE l join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID where ct.STATUS!='CANCELLED' and l.PICK_WAVE_ID=rt.PICK_WAVE_ID and l.ARTICUL=rt.ARTICUL
    and l.CELL_CODE=rt.TARGET_CELL_CODE and l.STATUS not in('PICKED','CANCELLED')
    order by l.PICK_SEQUENCE nulls last,l.CASE_PICK_LINE_ID fetch first 201 rows only) loop
   exit when remaining<=0;
   if bindings.get_size>=200 then raise_application_error(-20881,'GENERIC_REPLENISHMENT_CONSUMER_BOUND');end if;
   covered:=coverage(l.PICK_TASK_ID);q:=least(remaining,greatest(0,l.PLANNED_QTY-l.PICKED_QTY-covered));
   if q<=0 then continue;end if;
   select RRL_STOCK_RESERVATION_SQ.nextval into rid from dual;
   RRL_STOCK_PLAN_HELPER.row_key(p_anchors,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(rid));
   RRL_STOCK_PLAN_HELPER.row_key(p_anchors,'RRL_CASE_PICK_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(l.CASE_PICK_LINE_ID));
   RRL_STOCK_PLAN_HELPER.row_key(p_anchors,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.CASE_PICK_TASK_ID));
   RRL_STOCK_PLAN_HELPER.row_key(p_anchors,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_TASK_ID));
   for sr in(select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'
    and SOURCE_LINE_ID=l.PICK_TASK_ID and RESERVATION_DOMAIN='PICKING' and RESERVATION_KIND='HARD'
    and STATUS in('ACTIVE','ALLOCATED','PICKING') order by RESERVATION_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(p_anchors,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(sr.RESERVATION_ID));
   end loop;
   x:=json_object_t();x.put('line',l.CASE_PICK_LINE_ID);x.put('pick_task',l.PICK_TASK_ID);x.put('reservation',rid);
   x.put('planned',RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY));x.put('picked',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICKED_QTY));
   x.put('covered',RRL_STOCK_PLAN_HELPER.decimal_text(covered));x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(q));x.put('status',l.STATUS);
   bindings.append(x);remaining:=remaining-q;
  end loop;
  p_plan.put('lines',bindings);
 end;
 procedure execute_bind(p_task RRL_WAREHOUSE_TASK%rowtype,p_uid varchar2,p_reservation number,p_plan json_object_t,p_actor varchar2) is
  sr RRL_STOCK_RESERVATION%rowtype;l RRL_CASE_PICK_LINE%rowtype;pt RRL_PICK_TASK%rowtype;
  x json_object_t;detail json_object_t;bindings json_array_t;units json_array_t;wire clob;qty number;total number;ver number;rid number;lid number;repl_pick number;
  function selected_units(p_id number,p_qty number) return clob is n number;q number:=0;a json_array_t:=json_array_t();
  begin
   select count(*) into n from RRL_WMS_RECEIPT_UNIT where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED';
   if n=0 then return null;end if;
   for u in(select PHYSICAL_UNIT_KEY,BASE_QTY,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT where HARD_RESERVATION_ID=p_id
    and STOCK_STATUS!='ISSUED' order by PHYSICAL_UNIT_KEY) loop
    exit when q=p_qty;
    if u.STOCK_STATUS!='AVAILABLE' or q+u.BASE_QTY>p_qty then raise_application_error(-20884,'GENERIC_REPLENISHMENT_WHOLE_UNITS_REQUIRED');end if;
    a.append(u.PHYSICAL_UNIT_KEY);q:=q+u.BASE_QTY;
    if a.get_size>10000 then raise_application_error(-20881,'GENERIC_REPLENISHMENT_UNIT_BOUND');end if;
   end loop;
   if q!=p_qty then raise_application_error(-20884,'GENERIC_REPLENISHMENT_UNIT_QUANTITY_CONFLICT');end if;
   return a.to_clob;
  end;
 begin
  if p_task.TASK_SOURCE!='WAVE' or p_task.TASK_TYPE!='REPLENISHMENT' then return;end if;
  select PICK_TASK_ID into repl_pick from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=p_task.SOURCE_TASK_ID;
  if repl_pick is not null then
   if not p_plan.has('explicit') then return;end if;
   select * into pt from RRL_PICK_TASK where PICK_TASK_ID=repl_pick for update;
   select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=p_reservation for update;
   select nvl(sum(BASE_QTY),0) into total from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'
    and SOURCE_DOC_ID=p_task.SOURCE_DOC_ID and SOURCE_LINE_ID=repl_pick and CELL=p_task.TO_CELL and RESERVATION_ID!=p_reservation
    and RESERVATION_DOMAIN='PICKING' and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
   if pt.TASK_TYPE!='CASE_PICK' or pt.STATUS!=p_plan.get_string('status')
    or RRL_STOCK_PLAN_HELPER.decimal_text(pt.QTY)!=p_plan.get_string('quantity')
    or RRL_STOCK_PLAN_HELPER.decimal_text(nvl(pt.FACT_QTY,0))!=p_plan.get_string('fact')
    or RRL_STOCK_PLAN_HELPER.decimal_text(total)!=p_plan.get_string('target_covered')
    or sr.SOURCE_DOC_TYPE!='PICK_WAVE' or sr.SOURCE_DOC_ID!=p_task.SOURCE_DOC_ID or sr.SOURCE_LINE_ID!=repl_pick
    or sr.RESERVATION_DOMAIN!='PICKING' or sr.UID_PALLET!=p_uid or sr.CELL!=p_task.TO_CELL then
     raise_application_error(-20890,'CLOSURE_CHANGED: explicit CASE replenishment consumer');end if;
   qty:=greatest(0,sr.BASE_QTY-greatest(0,pt.QTY-nvl(pt.FACT_QTY,0)-total));
   if qty>0 then
    select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=sr.ARTICUL
     and INPUT_UOM=sr.BASE_UOM and BASE_UOM=sr.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
    wire:=selected_units(p_reservation,qty);
    RRL_STOCK_UNIT_CORE.release_units(p_reservation,qty,wire);
    RRL_STOCK_RESERVE_CORE.release_hard(p_reservation,qty,ver,'PICK_WAVE',p_task.SOURCE_DOC_ID,p_actor);
   end if;
   return;
  end if;
  if p_plan.get_string('signature')!=consumer_signature(p_task) then raise_application_error(-20890,'CLOSURE_CHANGED: generic consumer set');end if;
  bindings:=p_plan.get_array('lines');
  if p_reservation is null then raise_application_error(-20886,'GENERIC_DELIVERED_RESERVATION_REQUIRED');end if;
  select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=p_reservation for update;
  if sr.SOURCE_DOC_TYPE!='PICK_WAVE' or sr.SOURCE_DOC_ID!=p_task.SOURCE_DOC_ID or sr.RESERVATION_DOMAIN!='WAVE'
   or sr.SOURCE_LINE_ID!=p_task.SOURCE_TASK_ID or sr.UID_PALLET!=p_uid or sr.CELL!=p_task.TO_CELL then
   raise_application_error(-20886,'GENERIC_DELIVERED_RESERVATION_IDENTITY_CONFLICT');end if;
  select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=sr.ARTICUL
   and INPUT_UOM=sr.BASE_UOM and BASE_UOM=sr.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
  for i in 0..bindings.get_size-1 loop
   x:=treat(bindings.get(i) as json_object_t);lid:=x.get_number('line');rid:=x.get_number('reservation');
   select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=lid for update;
   if l.STATUS!=x.get_string('status') or RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY)!=x.get_string('planned')
    or RRL_STOCK_PLAN_HELPER.decimal_text(l.PICKED_QTY)!=x.get_string('picked')
    or RRL_STOCK_PLAN_HELPER.decimal_text(coverage(l.PICK_TASK_ID))!=x.get_string('covered')
    or l.CELL_CODE!=p_task.TO_CELL or l.PICK_WAVE_ID!=p_task.SOURCE_DOC_ID or l.ARTICUL!=sr.ARTICUL then
    raise_application_error(-20890,'CLOSURE_CHANGED: generic replenishment consumer');end if;
   select * into pt from RRL_PICK_TASK where PICK_TASK_ID=l.PICK_TASK_ID for update;
   if pt.TASK_TYPE!='CASE_PICK' or pt.ARTICUL!=l.ARTICUL or pt.PICK_PLAN_LINE_ID!=l.PICK_PLAN_LINE_ID
    or pt.CUSTOMER_ORDER_ID!=l.CUSTOMER_ORDER_ID or pt.STATUS in('DONE','CANCELLED','FAILED') then raise_application_error(-20886,'GENERIC_PICK_CONSUMER_IDENTITY_CONFLICT');end if;
   qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));wire:=selected_units(p_reservation,qty);
   RRL_STOCK_UNIT_CORE.release_units(p_reservation,qty,wire);
   RRL_STOCK_RESERVE_CORE.release_hard(p_reservation,qty,ver,'PICK_WAVE',p_task.SOURCE_DOC_ID,p_actor);
   detail:=json_object_t();detail.put('reservation_scope','QTY');detail.put('pick_wave_id',p_task.SOURCE_DOC_ID);
   detail.put('customer_order_id',l.CUSTOMER_ORDER_ID);detail.put('customer_id',l.CUSTOMER_ID);
   detail.put('pick_plan_id',pt.PICK_PLAN_ID);detail.put('pick_plan_line_id',pt.PICK_PLAN_LINE_ID);
   RRL_STOCK_RESERVE_CORE.create_hard(rid,p_uid,p_task.TO_CELL,qty,sr.BASE_UOM,ver,'PICK_WAVE',p_task.SOURCE_DOC_ID,l.PICK_TASK_ID,'PICKING',p_actor,detail.to_clob);
   RRL_STOCK_UNIT_CORE.reserve_units(p_uid,p_task.TO_CELL,rid,qty,wire);
  end loop;
  -- Surplus of this delivered chunk returns to free stock for subsequent waves.
  select BASE_QTY into total from RRL_STOCK_RESERVATION where RESERVATION_ID=p_reservation;
  if total>0 then
   wire:=selected_units(p_reservation,total);
   RRL_STOCK_UNIT_CORE.release_units(p_reservation,total,wire);
   RRL_STOCK_RESERVE_CORE.release_hard(p_reservation,total,ver,'PICK_WAVE',p_task.SOURCE_DOC_ID,p_actor);
  end if;
 end;
end;
/
