import json
from pathlib import Path
d=Path("db/migrations/2026-10-08_stock_posting_core");out={}
p=d/"167_case_carrier_move.sql";s=p.read_text(encoding="utf-8")
s=s.replace("'WAIT_CONTROL','READY','CONTROLLED'","'WAIT_CONTROL','READY_TO_SHIP','CONTROLLED'",1)
out[str(p)]=s
p=d/"068_shipping.sql";s=p.read_text(encoding="utf-8")
needle="  v_case_task number;v_case_version"
s=s.replace(needle,"  v_customer_status varchar2(30);v_closed_fulfillment number;\n"+needle,1)
needle="   if v_customer_order is not null then\n    RRL_STOCK_PLAN_HELPER.row_key"
assert s.count(needle)==1
s=s.replace(needle,"""   if v_customer_order is not null then
    select STATUS into v_customer_status from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=v_customer_order;
    select count(*) into v_closed_fulfillment from RRL_CUSTOMER_ORDER_FULFILLMENT
     where LEGACY_SBORKA_PALLET_ID=v_id and PALLET_UID=v_uid and STATUS in('CANCELLED','SHIPPED');
    if v_customer_status='CANCELLED' or v_closed_fulfillment>0 then raise_application_error(-20886,'SHIPMENT_CUSTOMER_FULFILLMENT_CLOSED');end if;
    RRL_STOCK_PLAN_HELPER.row_key""",1)
needle="  if v.get_number('case_task') is not null then\n   declare ct"
assert s.count(needle)==1
s=s.replace(needle,"""  if v.get_number('customer_order_id') is not null then
   declare v_customer number:=v.get_number('customer_order_id');v_state varchar2(30);v_closed number;begin
    select STATUS into v_state from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=v_customer for update;
    select count(*) into v_closed from RRL_CUSTOMER_ORDER_FULFILLMENT
     where LEGACY_SBORKA_PALLET_ID=v_id and PALLET_UID=v_uid and STATUS in('CANCELLED','SHIPPED');
    if v_state='CANCELLED' or v_closed>0 then raise_application_error(-20886,'SHIPMENT_CUSTOMER_FULFILLMENT_CLOSED');end if;
   end;
  end if;
"""+needle,1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
