from pathlib import Path
import json,re
out={};f=Path("db/migrations/2026-10-11_ni042_route_sequence")
out[str(f/"003_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-209-case-issued-route-sequence'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Enforce original issued CASE linear route under same native CASE lock',sysdate,user,
'db/migrations/2026-10-11_ni042_route_sequence/apply.sql','db/migrations/2026-10-11_ni042_route_sequence/rollback.sql','APPLIED',
'Own CASE1106/wave460/two physical cells/ranks1then2/source4/picked2: ahead409,no stock; facefuture99 leaves issued1; both native picks/replay/close rollback. Cleanup exact original cells/native stock0/protected13520/20. All-null legacy DIRECT retained; laying-stage validation remains.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@003_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
name="RRL_STOCK_CASE_PICK_CMD";matches=[x for x in m["components"]if re.search(r"create\s+or\s+replace\s+package(?:\s+body)?\s+"+name+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)]
assert matches
m["components"]=[("../2026-10-11_ni042_route_sequence/002_case.sql")if x==matches[-1]else x for x in m["components"]if x not in matches[:-1]]
m["components"].append("../2026-10-11_ni042_route_sequence/001_admission.sql");m["packages"].append("RRL_CASE_ROUTE_ADMISSION")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/nicora_ni042_route_sequence_20261011.md"]="""# NI04.2: выданный маршрут исполняется последовательно

209 APPLIED; [[nicora_ni042_route_sequence_design_20261011]]. Existing linear topology040 and copied CASE PICK_SEQUENCE retained. Native CASE_PICK_CONFIRM checks bounded200 CASE lines before compile and again after current CASE mutex: unfinished earlier rank blocks later, actually picked later rank prevents backtrack. Same-rank rows allowed; accepted SHORT_PICKED is terminal, unresolved shortage/replenishment blocks. No independent stock writer/route engine. All-null legacy DIRECT behavior preserved; mixed missing route rejects. No current topology used to overwrite issued task.

Actual own QC209544A92C7A7 and secondSKU B, WARE25524114, CASE1106/wave460/revision308. Two distinct pick cells Q209D544a92c7a7/Q209E544a92c7a7 with issued ranks1/2, original source2+2. First attempted rank2 ->409 CASE_ROUTE_EARLIER_POINT_UNFINISHED, picked0. Future face rank1 changed99; issued CASE remains1. Real native/HTTP first1 then second1, each replay, whole close rollback/replay, P4H2. First cleanup mistakenly returned both leaves to first cell; native refused CASE_RETURN_SCAN_ORIGINAL_CELL_REQUIRED. Corrected cleanup maps each actual line source, native return/release, tare release, wave finished RETURNED_TO_PLANNING, stock count0; protected13520/20 unchanged. Runnable author corrected to retain original per-leaf destinations. No quantity deletion/copy.

TSD resumes first unfinished line after server state changes, shows next unfinished source/rank, removes circular wrapping for routed tasks. Previous/next navigation only views; native gate owns permission to actually pick. Durable retry unchanged. Heavy foundation/middle/top classification and compatibility with physical one-way route are next slice, not claimed complete.

Live no INVALID; route aggregate7mp4c8x34wddb .722ms/5 uses existing CASE index/bounded200. Keep original index; owner fulfillment re-evaluates plan at volume. Actual physical warehouse pilot and independent review remain separate.
"""
for path,line in [
("wiki/index.md","- [Исполнение выданного линейного маршрута](database/nicora_ni042_route_sequence_20261011.md):209 native min unfinished rank/backtrack gate, actual two cells/issued order stable/TSD resumes; no second planner."),
("wiki/log.md","2026-10-11:209 original CASE route order now enforced before compile and under existing CASE mutex. Actual1106 two cells ranks1→2, ahead409/no stock, future face99 preserves issued1, picks/replay/close rollback. Cleanup original-cell refusal corrected per-leaf and native0, protected13520/20. Aggregate.722ms/5 retained CASE index/200bound. Laying stage remains."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni04_2.md","11.10.2026:209 existing linear route copied to CASE now enforced native: earlier incomplete point blocks later, no backtrack after physical progress, unresolved shortage stays current; same CASE lock/no second planner. Actual two distinct cells/ranks1→2/futureface99 leaves issued1/replay/native cleanup. TSD resumes first unfinished; heavy foundation/middle/top validation still open.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI04.2").setdefault("implementedSlices",[]).append("209 original CASE issued linear route enforced under existing mutex/no skip/backtrack; same-snapshot ranks retained across future face change; TSD next unfinished")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"209_issued_linear_route.md")]="""# Qwen:209
Run scripts/ni042_issued_route_case.py dedicateddev. Two own SKU/source2+2/CASE two different cells/ranks1→2. Ahead refused409 and no pickedstock; futureface99 retains issued1. First1 then second1/replay; original close rollback. Each return must scan/map its own original line cell, not first cell globally; native cleanup0 and protected13520/20. Read current SHORT_PICKED terminal semantics; unresolved shortage cannot skip, mixed missingrank rejects, allnullDIRECT old behavior preserved. TSD state change selects first unfinished, navigation does not wrap; server owns gate. Heavy layering remains separate.
"""
print(json.dumps(out,ensure_ascii=True))
