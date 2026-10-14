from pathlib import Path
import json
f={};root="db/migrations/2026-10-14_ni022_stock_floor_type/"
p=Path(root+"002_read.sql");s=p.read_text(encoding="utf-8")
point="  select count(*),min(CELL)into n,cell_value"
insert="""  select count(*)into n from RRL_WMS_HU_LINK where CHILD_PALLET_UID=p_uid and ACTIVE_FLAG=1;
  if n>0 then raise_application_error(-20886,'PALLET_FLOOR_INDEPENDENT_TOP_REQUIRED');end if;
  select count(*)into n from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid;
  if n>0 then raise_application_error(-20886,'PALLET_FLOOR_INDEPENDENT_TOP_REQUIRED');end if;
"""
assert point in s;s=s.replace(point,insert+point,1).replace("j.put('uid',p_uid);","j.put('article',p.ARTICUL);j.put('uid',p_uid);",1);f[str(p)]=s
p=Path(root+"003_command.sql");s=p.read_text(encoding="utf-8")
old="""  for item in(select ID from RRL_REMAINS where UID_POLETA=uid_value and REMAIN>0)loop
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_REMAINS',RRL_STOCK_PLAN_HELPER.decimal_text(item.ID));
  end loop;"""
new="  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,uid_value,j.get_string('article'),j.get_string('cell'),null);"
assert old in s;s=s.replace(old,new,1);f[str(p)]=s
f[root+"apply_stock_keys_correction.sql"]="@@002_read.sql\n@@003_command.sql\nalter package RRL_STOCK_POSTING_API compile body;\n/\n"
print(json.dumps(f))
