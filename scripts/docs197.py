from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_weight_unit_pin")
out[str(f/"005_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-197-weight-choice-physical-pin'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Exact approved physical box key for existing native HARD owners',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_unit_pin/apply.sql','db/migrations/2026-10-11_ni042_weight_unit_pin/rollback.sql','APPLIED',
'Own QW197353B7C4585 rev279 actual12 original10 CASE1073 and QW19722B684C190 rev280 actual8 original10 CASE1074; exact selected HARD physical key/storage full source20/native replenishment/actual CASE pick/replay/return/countcleanup original13520/20. Demand deviation198 next.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@005_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["components"].insert(m["components"].index("106_wave_launch.sql"),"../2026-10-11_ni042_weight_unit_pin/001_reader.sql")
m["components"]=[x.replace("106_wave_launch.sql","../2026-10-11_ni042_weight_unit_pin/002_launch.sql").replace("../2026-10-10_ni032_partial_target/001_wave.sql","../2026-10-11_ni042_weight_unit_pin/003_replenish.sql")for x in m["components"]]
# Replenishment needs the reader before compilation as well.
r="../2026-10-11_ni042_weight_unit_pin/001_reader.sql";m["components"].remove(r);m["components"].insert(m["components"].index("../2026-10-11_ni042_weight_unit_pin/003_replenish.sql"),r)
m["packages"].append("RRL_WEIGHT_CHOICE_UNIT_READ");m["additional_scripts"].append("../2026-10-11_ni042_weight_unit_pin/004_index.sql")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_weight_unit_pin_20261011.md"]="""# NI04.2: точный физический резерв коробки
197 APPLIED. [[retailcase_ni042_weight_unit_pin_design_20261011]]. Existing native WAVE_LAUNCH and replenishment HARD owners receive exact immutable selected physical key from read-only accessible-by helper. Ordinary nochoice remains old automatic selection. Current native TX/held STOCK UID50/current SKU policy and AVAILABLE physical unit/net checked; larger reservation only for every free source box, preserving full-pallet replenishment. UNIT_CORE.reserve_units/sole posting root retain all effects.
Real original10/selected12: QW197353B7C4585/WARE23488636/rev279/wave434/CASE1073, exact key3db48f06d66e6a85ae0825063af09de6026146c60c6118a34ecb000fd173cf22. Original10/selected8: QW19722B684C190/WARE22274948/rev280/CASE1074, exact key9cc4c64733256bf6cb5b86d281c259dbfec90ae4c1198c129b3e504e5b7f7102. Both storage source20/full replenishment to pickface/native HARD exact approved one box/actual weighted CASE_CONFIRM8or12/replay/P20 Hactual/native return/tare-release/countcleanup/original13520/20 preserved.
First8fd36b62b6/rev278/CASE1072 actual12 positive passed, cleanup incorrectly called whole-plan cancel after historical FACT12; native correctly refused PICK_PLAN_PHYSICAL_TASK_ALREADY_STARTED even though return cancelled PT. Correct cleanup uses existing CASE return/finish and retires choice after PT cancellation, preserving FACT history, no bypass.
196 failed fixtures now retired by cleanup196_failed_fixtures.py: all P/H0/cancelled choice history retained/own actors retired. No ordinary stock changes or fake shipment.198 demand pending/fulfilled waiver and return restoration next; NI04.2 open.
"""
for path,line in[("wiki/index.md","- [Точный резерв весовой коробки](database/retailcase_ni042_weight_unit_pin_20261011.md):197 original10/actual8or12/exact HARD key/full replenishment/CASE pick/replay/native return; demand accounting next."),
("wiki/log.md","2026-10-11:197 exact approved physical HARD key installed in existing launch/replenishment. Own353b7c4585 actual12 and22b684c190 actual8 against original10 passed storage20/full replenishment/native CASE/replay/return/cleanup. Existing plan cancel after historical FACT correctly refused, author cleanup corrected.196 failed fixtures retired."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:197 original10/whole8or12 selected physical key HARD and actual CASE pick delivered with existing replenishment/return.198 common demand/pending/deviation/return restoration next.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"197_exact_physical_box.md")]="""# Qwen:197
Run ni042_weight_unit_pin_case.py TAG 8 and TAG 12. Original10 remains; existing native planner picks approved unit, source20/full replenishment actual volume. HARD key equals approved registry key, wrong otherbox refused, current SKU/source/version/ownership and quantity match. Native CASE actual8or12/replay/no split/no second writer. Return cancels task but retains FACT; do not bypass whole-plan cancellation refusal after historical picks. Current pool underweight demand is198 next. Inspect native read bounded indexed task/line/key/current policy.
"""
print(json.dumps(out,ensure_ascii=True))
