from pathlib import Path
import json,re
f=Path("db/migrations/2026-10-11_ni052_unload");out={}
def write(p,s):
 out[str(p)]=s
p=f/"apply.sql";s=p.read_text(encoding="utf-8")
for name in ["010_sample_guard.sql","011_recompile.sql","012_ledger.sql"]:
 if "@@"+name not in s:s+="@@"+name+"\n"
write(p,s)
p=f/"rollback.sql";s=p.read_text(encoding="utf-8").replace("@@000_before_member_guard.sql","@@000_before_member_guard.sql\n@@000_before_sample_guard.sql");write(p,s)
p=Path("scripts/cleanup212_case.py");write(p,p.read_text(encoding="utf-8").replace("CASE1106/wave460","CASE1113/wave467"))
p=Path("wiki-raw/wms_admin_ui_reference/transport-loading.html");s=p.read_text(encoding="utf-8").replace("Вложенные места обрабатываются целиком.","Для вложенного места или переданной водителю тары требуется отдельное решение.");write(p,s)
write(f/"012_ledger.sql","""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-212-standalone-case-unload' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Native standalone CASE unload before departure with restored original stock and HARD',sysdate,user,
'db/migrations/2026-10-11_ni052_unload/apply.sql','db/migrations/2026-10-11_ni052_unload/rollback.sql','APPLIED',
'Actual CASE1113/wave467/original load-6 retained/unload+6/P6H6; late rollback and concurrent one winner, replay/current wrong warehouse403. Shipping history immutable/control revoked/native cleanupP0H0/protected13520/20. Nested cargo, captured units and transferred tare require explicit extension.');
commit;
""")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for name,sql in [("RRL_STOCK_BALANCE_CORE","003_balance.sql"),("RRL_STOCK_RESERVE_CORE","004_reserve.sql"),("RRL_STOCK_FULFILLMENT_FACT","005_fulfillment.sql"),("RRL_STOCK_POSTING_API","006_root.sql")]:
 matches=[x for x in m["components"] if re.search(r"create\s+or\s+replace\s+package(?:\s+body)?\s+"+name+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)]
 assert matches,name
 m["components"]=[("../2026-10-11_ni052_unload/"+sql)if x==matches[-1]else x for x in m["components"]if x not in matches[:-1]]
if "RRL_STOCK_UNLOAD_CMD" not in m["packages"]:m["packages"].append("RRL_STOCK_UNLOAD_CMD")
new="../2026-10-11_ni052_unload/002_command.sql"
if new not in m["components"]:m["components"].insert(next(i for i,x in enumerate(m["components"])if x.endswith("006_root.sql")),new)
for sql in ["007_load_guard.sql","008_member_guard.sql","009_unload_guard.sql","010_sample_guard.sql"]:
 names=re.findall(r"create\s+or\s+replace\s+trigger\s+(\w+)",(f/sql).read_text(encoding="utf-8"),re.I)
 for name in names:
  matches=[x for x in m["additional_scripts"]if re.search(r"create\s+or\s+replace\s+trigger\s+"+name+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)]
  m["additional_scripts"]=[x for x in m["additional_scripts"]if x not in matches]
 new="../2026-10-11_ni052_unload/"+sql
 if new not in m["additional_scripts"]:m["additional_scripts"].append(new)
new="../2026-10-11_ni052_unload/001_schema.sql"
if new not in m["startup_scripts"]:m["startup_scripts"].append(new)
m["required_columns"]["RRL_TT_UNLOAD_FACT"]=["OPERATION_ID","LOAD_OPERATION_ID","TT_ID","CASE_PICK_TASK_ID","WARE_ID","CELL_CODE","COMPOSITION_JSON","REASON","CREATED_BY","CREATED_AT"]
write(p,json.dumps(m,indent=2)+"\n")
# Intermediate generators are not migration entry points. Preserve drafts as evidence, forbid accidental stale regeneration.
for name in ["build212_unload.py","extend212_reserve.py","build210_case.py","build211_case.py"]:
 p=Path("scripts")/name;s=p.read_text(encoding="utf-8")
 guard='raise SystemExit("Retired authoring draft: use checked-in final SQL/fixture sources; do not regenerate over verified fixes.")'
 if guard not in s:write(p,guard+"\n"+s)
print(json.dumps(out,ensure_ascii=True))

