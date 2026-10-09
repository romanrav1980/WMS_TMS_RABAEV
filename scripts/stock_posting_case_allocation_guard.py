"""Packed CASE stock cannot enter a new allocation or unrelated merge."""
import json
from pathlib import Path
d=Path("db/migrations/2026-10-08_stock_posting_core");out={}
p=d/"020_reservations.sql";s=p.read_text(encoding="utf-8")
needle="p_details clob default null) is v_article varchar2(160);v_ware number;v_details json_object_t;"
assert s.count(needle)==1
s=s.replace(needle,needle+"v_carrier number;",1)
needle="  lock_identity(p_id);\n  select ARTICUL into v_article"
assert s.count(needle)==1
s=s.replace(needle,"""  lock_identity(p_id);
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));
  select count(*) into v_carrier from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid;
  if v_carrier>0 then raise_application_error(-20869,'CASE_CARRIER_NOT_ALLOCATABLE: unpack through carrier return');end if;
  select ARTICUL into v_article""",1)
out[str(p)]=s
p=d/"032_transfer_core.sql";s=p.read_text(encoding="utf-8")
needle="select count(*) into v_sum from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid;"
assert s.count(needle)==1
s=s.replace(needle,"select count(*) into v_sum from RRL_CASE_CARRIER_LOT where LOT_UID in(p_uid,p_target_uid);",1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
