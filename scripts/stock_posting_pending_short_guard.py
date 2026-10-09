"""Close two source/fact races without additional stock writers."""
import json
from pathlib import Path
d=Path("db/migrations/2026-10-08_stock_posting_core")
p=d/"068_shipping.sql";s=p.read_text(encoding="utf-8")
needle="   if v_order_count>1 then raise_application_error(-20887,'SHIPMENT_CUSTOMER_ORDER_AMBIGUOUS');end if;"
assert s.count(needle)==1
s=s.replace(needle,needle+"\n   if v_return_supplier is not null and v_customer_order is not null then raise_application_error(-20887,'SUPPLIER_RETURN_CUSTOMER_SOURCE_CONFLICT');end if;",1)
out={str(p):s}
p=d/"160_case_pick_command.sql";s=p.read_text(encoding="utf-8")
needle="  if ct.ASSIGNED_TO is not null and ct.ASSIGNED_TO!=p_actor"
assert s.count(needle)==1
guard="""  -- Reporting/rejecting a short uses CONFIG exclusive; this command holds CONFIG shared
  -- and the same task/line anchors, so the pending decision cannot change this fact mid-post.
  select count(*) into n from RRL_CASE_PICK_SHORT where CASE_PICK_LINE_ID=line_id
   and STATUS in('CREATED','PENDING_APPROVAL');
  if n>0 then raise_application_error(-20886,'CASE_SHORT_DECISION_PENDING');end if;
"""
s=s.replace(needle,guard+needle,1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
