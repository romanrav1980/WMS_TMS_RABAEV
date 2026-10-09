"""Restrict existing shipment allocation to its scanned bound CASE carrier."""
import json
from pathlib import Path
d=Path("db/migrations/2026-10-08_stock_posting_core");out={}
p=d/"160_case_pick_command.sql";s=p.read_text(encoding="utf-8")
s=s.replace("accessible by(package RRL_STOCK_CASE_SHORT_CMD,","accessible by(package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CASE_SHORT_CMD,",1)
out[str(p)]=s
p=d/"068_shipping.sql";s=p.read_text(encoding="utf-8")
needle="  type quantity_map is table of number index by varchar2(2000);"
s=s.replace(needle,"  v_case_task number;v_case_version number;v_case_cell varchar2(60);v_case_status varchar2(40);v_carrier clob;v_carrier_rows json_array_t;v_carrier_row json_object_t;\n"+needle,1)
needle="  if v_ware is null then raise_application_error(-20886,'SHIPPING_WAREHOUSE_REQUIRED');end if;"
assert s.count(needle)==1
s=s.replace(needle,needle+"""
  if v_kind='SHIP_PALLET' then
   begin
    select CASE_PICK_TASK_ID,CONTENT_VERSION,CURRENT_CELL,STATUS into v_case_task,v_case_version,v_case_cell,v_case_status
     from RRL_CASE_PICK_TASK where LEGACY_SBORKA_PALLET_ID=v_id;
   exception when no_data_found then v_case_task:=null;end;
   if v_case_task is not null then
    if v_customer_order is null or v_case_status not in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP')
     or v_case_cell is null then raise_application_error(-20886,'CASE_SHIPMENT_CARRIER_STATE_REQUIRED');end if;
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_case_task));
    RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(v_case_task));
    v_carrier:=RRL_STOCK_CASE_PICK_CMD.carrier_rows(v_case_task);v_carrier_rows:=json_array_t.parse(v_carrier);
    if v_carrier_rows.get_size=0 then raise_application_error(-20886,'CASE_SHIPMENT_EMPTY_CARRIER');end if;
    for z in 0..v_carrier_rows.get_size-1 loop
     v_carrier_row:=treat(v_carrier_rows.get(z) as json_object_t);
     if v_carrier_row.get_string('cell')!=v_case_cell then raise_application_error(-20887,'CASE_SHIPMENT_CARRIER_LOCATION_CONFLICT');end if;
     RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v_carrier_row.get_string('uid'),v_carrier_row.get_string('article'),v_case_cell,null);
    end loop;
   end if;
  end if;""",1)
needle="      and nvl(br.IS_SHIPMENT_ALLOWED,1)=1"
assert s.count(needle)==1
s=s.replace(needle,needle+"""
      and ((v_case_task is null and not exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=sr.UID_PALLET))
       or (v_case_task is not null and sr.CELL=v_case_cell and exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=sr.UID_PALLET and h.CASE_PICK_TASK_ID=v_case_task)))""",1)
# Unowned legacy allocation must never borrow stock already packed into a CASE carrier.
needle="    where pp.ARTICUL=v_article and rr.CELL=v_cell and rr.REMAIN>rr.HARD_RESERVED_BASE and cc.WARE_ID=v_ware"
assert s.count(needle)==1
s=s.replace(needle,needle+"\n     and not exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=rr.UID_POLETA)",1)
needle="  v.put('return_supplier_id',v_return_supplier);"
assert s.count(needle)==1
s=s.replace(needle,"""  if v_case_task is not null then
   for z in 0..v_carrier_rows.get_size-1 loop
    v_carrier_row:=treat(v_carrier_rows.get(z) as json_object_t);
    k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',v_carrier_row.get_string('uid'),v_carrier_row.get_string('cell')));
    if not used.exists(k) then raise_application_error(-20886,'CASE_SHIPMENT_CONTENT_MISMATCH');end if;
    if used(k)!=RRL_STOCK_MATH.quantity(v_carrier_row.get_string('quantity')) then raise_application_error(-20886,'CASE_SHIPMENT_CONTENT_MISMATCH');end if;
   end loop;
  end if;
  v.put('case_task',v_case_task);v.put('case_version',v_case_version);v.put('case_carrier',v_carrier);
"""+needle,1)
needle="  a:=v.get_array('legs');"
assert s.count(needle)==1
s=s.replace(needle,"""  if v.get_number('case_task') is not null then
   declare ct RRL_CASE_PICK_TASK%rowtype;v_task number:=v.get_number('case_task');v_current clob;begin
    RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task)));
    select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_task for update;
    if ct.LEGACY_SBORKA_PALLET_ID is null or ct.LEGACY_SBORKA_PALLET_ID!=v_id or ct.CUSTOMER_ORDER_ID!=v.get_number('customer_order_id')
     or ct.CONTENT_VERSION!=v.get_number('case_version') or ct.STATUS not in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP')
     then raise_application_error(-20890,'CLOSURE_CHANGED: CASE shipment');end if;
    v_current:=RRL_STOCK_CASE_PICK_CMD.carrier_rows(v_task);
    if dbms_lob.compare(v_current,v.get_clob('case_carrier'))!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: CASE contents');end if;
   end;
  end if;
"""+needle,1)
needle="  j.put('operation_id',d.get_string('operation_id'));"
assert s.count(needle)==1
s=s.replace(needle,"""  if v.get_number('case_task') is not null then
   declare v_task number:=v.get_number('case_task');v_operation varchar2(100):=d.get_string('operation_id');begin
    update RRL_CASE_PICK_TASK set STATUS='SHIPPED',SHIPPED_OPERATION=v_operation,
     CONTENT_VERSION=CONTENT_VERSION+1,DONE_AT=systimestamp,UPDATED_AT=systimestamp,UPDATED_BY=p_actor
     where CASE_PICK_TASK_ID=v_task;
   end;
  end if;
  j.put('case_pick_task_id',v.get_number('case_task'));
"""+needle,1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
