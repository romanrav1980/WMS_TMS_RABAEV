from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_nested_onward");out={}
p=d/"000_before_depart_gate.sql";s=p.read_text(encoding="utf-8")
old="and l.ROOT_UID=r.ROOT_UID \n and RRL_STOCK_MATH.quantity(json_value(l.COMPOSITION_JSON,'$.nodes[0].quantity'))=r.BASE_QTY"
assert old in s
new="""and(
 (l.ROOT_UID=r.ROOT_UID and RRL_STOCK_MATH.quantity(json_value(l.COMPOSITION_JSON,'$.nodes[0].quantity'))=r.BASE_QTY)
 or(o.COMMAND_TYPE='HU_SHIP'and l.ROOT_UID!=r.ROOT_UID
 and json_value(o.RESOLVED_PLAN_JSON,'$.domain.loading.trip'returning number)=p_trip
 and exists(select 1 from RRL_INTERWARE_ONWARD_DISPATCH dispatch where dispatch.OPERATION_ID=l.LOAD_OPERATION_ID
  and dispatch.BIND_OPERATION_ID=b.OPERATION_ID and dispatch.RECEIPT_OPERATION_ID=r.OPERATION_ID
  and dispatch.ROOT_UID=r.ROOT_UID and dispatch.ST_ID=b.ST_ID and dispatch.BASE_QTY=r.BASE_QTY and dispatch.BASE_UOM=r.BASE_UOM)
 and(select count(*)from json_table(l.COMPOSITION_JSON,'$.nodes[*]'columns(
  K varchar2(20)path '$.kind',U varchar2(200)path '$.uid',Q varchar2(60)path '$.quantity'))archive
  where archive.K='STOCK')=1
 and(select count(*)from json_table(l.COMPOSITION_JSON,'$.nodes[*]'columns(
  K varchar2(20)path '$.kind',U varchar2(200)path '$.uid',Q varchar2(60)path '$.quantity'))archive
  where archive.K='STOCK'and archive.U=r.ROOT_UID and RRL_STOCK_MATH.quantity(archive.Q)=r.BASE_QTY)=1))
"""
out[(d/"007_depart_gate.sql").as_posix()]=s.replace(old,new,1)
p=d/"apply.sql";out[p.as_posix()]=p.read_text(encoding="utf-8").replace("@@006_ledger.sql","@@007_depart_gate.sql\n@@006_ledger.sql")
p=d/"rollback.sql";out[p.as_posix()]=p.read_text(encoding="utf-8")+"@@000_before_depart_gate.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));m["additional_scripts"].append("../2026-10-12_ni061_nested_onward/007_depart_gate.sql");out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out))
