from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_scale_use")
out[str(f/"004_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-188-case-scale-consumption'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Once-only warehouse scale proof inside existing CASE root transaction',sysdate,user,
'db/migrations/2026-10-11_ni042_scale_use/apply.sql','db/migrations/2026-10-11_ni042_scale_use/rollback.sql','APPLIED',
'CASE1062 GROSS10.1/label NET9.8/current device/version/source/freshness/root unique lock; same saved replay/no extra stock; reuse409; native cleanup; architecture544/0/76. NET route and rollback/concurrency acceptance next.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@004_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["components"]=[x.replace("../2026-10-11_ni042_weight_box_case/002_case_contract.sql","../2026-10-11_ni042_scale_use/002_case_contract.sql")for x in m["components"]]
m["components"].append("../2026-10-11_ni042_scale_use/003_recompile.sql");m["packages"].append("RRL_CASE_SCALE_ADMISSION")
m["additional_scripts"].append("../2026-10-11_ni042_scale_use/001_use.sql")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_scale_use_20261011.md"]="""# NI04.2: показание весов в проводке CASE
188 APPLIED. [[retailcase_ni042_warehouse_scale_20261011]].
Existing CASE_PICK_CONFIRM compile adds rank70 UNIQUE WH.SCALE.USE:capture and current source/device/freshness validation; execute revalidates then inserts append-only RRL_WH_SCALE_USE inside the existing operation transaction. Unique capture PK and stock-operation unique FK prevent reuse; root TX/current canonical CASE identity/current actor checked by guard. CONFIG SHARE existing CASE fence prevents device config change during posting.
Current task/line/content version/article/source-cell/carrier must equal archived source. Active calibrated current version/device/sender current dedicated warehouse required; measurement within120seconds. For serialized box original GS1 label must equal captured product; exactly one original physical unit/current gross with reference required; measured gross within device resolution. Existing182 net label/current HARD/marks validation remains. No half-box QC tolerance used as scale accuracy.
Optional request field preserves previous canonical weighted requests via exclude_none. Saved operation replay precedes freshness and uses old canonical proof, so original successful retry remains possible after expiry. TSD offers archive TEST/HARDWARE choices and durable original intent.
Own scripts/ni042_warehouse_scale_use_case.py QW1883C584FA1E1/WARE23954767/wave422 CASE1062 revision255/captureF9053003BF9FEBB4FBBAB751A5EA718BB46A583F3D8ED6D8B5732D00FC4A0FE9: stableGROSS10.1 -> existing physical movementNET9.8, one USE tied CASE.WEIGHT182:1062, exact replay/journal unchanged, anotheroperation409, changedlabel409, P19.6/H9.8 before native cleanup. Original135 P20/H20 unchanged. First author fixture f3a71993e2 native cleaned after helper compile failure; corrected missing procedure END and all targeted USER_ERRORS empty before repeat. No successful movement lost.
Architecture544/0cycles/76debt PASS; JS syntax PASS. Remaining explicit NET route, current use status/read UI, rollback/concurrency/freshness acceptance, order quantity exceptions and real hardware commissioning. NI04.2 remains open.
"""
for path,line in [
("wiki/index.md","- [Показание весов в проводке CASE](database/retailcase_ni042_scale_use_20261011.md):188 once-only GROSS proof/root transaction/NET9.8/exact replay; loose NET next."),
("wiki/log.md","2026-10-11:188 current scale capture consumed once in existing CASE root, immutable USE/unique planned lock/current source/device/120s/GROSS precision. CASE1062 actual10.1->9.8/replay/refusals/native cleanup; architecture544/0/76. NET and extended transactional acceptance next."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:188 original scale proof tied once to existing CASE movement, actual GROSS10.1/NET9.8/replay; NET route/rollback-concurrency and order exceptions still open.")]:
 p=Path(path);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"188_scale_use.md")]="""# Qwen:188
Run scripts/ni042_warehouse_scale_use_case.py on dedicated dev only. Independently check same capture cannot serve two operations, original operation retry after capture expiry/device deactivation returns old result with no movement, other actor/warehouse refused, changed version/source/freshness/gross rejected. Use prepare/execute plus outer rollback: USE/stock/H/CASE/events/outbox all rollback, then same immutable operation succeeds. Concurrent two operations same capture exactly one winner. No manual stock DML, no real hardware/government acceptance claim. Inspect top SQL and bounded PK lookups; record plan/index/batching decision.
"""
print(json.dumps(out,ensure_ascii=True))
