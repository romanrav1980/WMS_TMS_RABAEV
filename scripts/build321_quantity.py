from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_aggregation_quantity");out={}
old=Path("db/migrations/2026-10-12_ni061_sap_aggregation_scan/001_aggregation.sql").read_text(encoding="utf-8")
new=old.replace("u.BASE_QTY=RRL_STOCK_MATH.quantity(j.Q)","u.BASE_QTY=case when j.Q is not null then RRL_STOCK_MATH.quantity(j.Q) else u.BASE_QTY end")
assert new!=old
for n,t in {"000_before.sql":old,"001_aggregation.sql":new,"apply.sql":"@@001_aggregation.sql\n@@002_ledger.sql\n","rollback.sql":"@@000_before.sql\n","verify.sql":"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_IW_AGG_SCAN';\n",
"002_ledger.sql":"merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-321-aggregation-persisted-quantity' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID) when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Missing source member quantity uses exact already born immutable physical unit quantity; explicit quantity must match','12-OCT-26',user,'apply.sql','rollback.sql','APPLIED');\ncommit;\n"}.items():out[(d/n).as_posix()]=t.replace("'12-OCT-26'","sysdate")
p=Path("scripts/source316_nested_case.py");s=p.read_text(encoding="utf-8").replace("316","322").replace('dict(UnitId=unit["unit_id"],Quantity="1",Code=code)','dict(UnitId=unit["unit_id"],Code=code)')
assert "Quantity=\"1\"" not in s
out["scripts/source322_nested_case.py"]=s
p=Path("scripts/case314_nested_receive.py");s=p.read_text(encoding="utf-8").replace("context316.json","context322.json").replace("314","322")
out["scripts/case322_nested_receive.py"]=s
print(json.dumps(out))
