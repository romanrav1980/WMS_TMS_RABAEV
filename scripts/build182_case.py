import json,hashlib
from pathlib import Path
folder=Path("db/migrations/2026-10-11_ni042_weight_box_case");s=(folder/"000_before_case.sql").read_text(encoding="utf-8")
a="  if remaining<=0 or fact>l.PLANNED_QTY then raise_application_error(-20886,'CASE_PICK_FACT_NOT_INCREASING_OR_EXCEEDS_PLAN');end if;"
b="  if fact<=before_qty or fact>l.PLANNED_QTY then raise_application_error(-20886,'CASE_PICK_FACT_CONFLICT');end if;"
assert s.count(a)==1 and s.count(b)==1
s=s.replace(a,a+"\n  RRL_CASE_WEIGHT_SCAN.assert_scan(p_request,l.ARTICUL,line_id,nvl(l.PICKED_QTY,0));")
s=s.replace(b,b+"\n  RRL_CASE_WEIGHT_SCAN.assert_scan(p_request,article,line_id,before_qty);")
out={str(folder/"002_case_contract.sql"):s,str(folder/"002_case_body.sql"):s[s.index("create or replace package body"):],
 str(folder/"apply.sql"):"-- MIGRATION_ID:2026-10-11-182-weighted-case-label\n@@001_scan.sql\n@@002_case_body.sql\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n",
 str(folder/"rollback.sql"):"@@000_before_case.sql\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n",
 str(folder/"verify.sql"):"select object_name,object_type,status from user_objects where object_name in('RRL_CASE_WEIGHT_SCAN','RRL_STOCK_CASE_PICK_CMD');\nselect name,line,text from user_errors where name in('RRL_CASE_WEIGHT_SCAN','RRL_STOCK_CASE_PICK_CMD');\n"}
out[str(folder/"checkpoint.json")]=json.dumps({"migration_id":"2026-10-11-182-weighted-case-label","sha256":{p:hashlib.sha256(v.encode()).hexdigest()for p,v in out.items()},"before_source_sha256":hashlib.sha256((folder/"000_before_case.sql").read_bytes()).hexdigest(),"recovery":"Fresh case package and paired rollback; no database copy"},indent=2)
print(json.dumps(out,ensure_ascii=True))
