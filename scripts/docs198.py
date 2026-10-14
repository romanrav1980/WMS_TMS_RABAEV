from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_weight_choice_demand")
out[str(f/"003_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-198-weight-choice-demand'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original demand pending and fulfilled whole weight box adjustments',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_choice_demand/apply.sql','db/migrations/2026-10-11_ni042_weight_choice_demand/rollback.sql','APPLIED',
'Own QW19831BAC690EF rev282 original10/actual8/current waiver2 and QW19841B760AF91 rev283 original10/actual12/no negative quantity. Pending SOFT/HARD prevents duplicate original demand; exact key pick/replay/return reopens10/immutable original/native cleanup13520/20.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@003_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
old="../2026-10-11_ni042_weight_demand/002_pool.sql";pos=m["components"].index(old)
m["components"][pos:pos+1]=["../2026-10-11_ni042_weight_choice_demand/001_reader.sql","../2026-10-11_ni042_weight_choice_demand/002_pool.sql"]
m["packages"].append("RRL_WEIGHT_CHOICE_DEMAND_READ");out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/nicora_ni042_weight_choice_demand_20261011.md"]="""# NI04.2: исходная потребность при выборе целой коробки
198 APPLIED. [[nicora_ni042_weight_choice_demand_design_20261011]]. Existing RRL_STOCK_POOL_READ retains original requested_base_quantity. Pure helper exposes weight_choice_pending_quantity separately from accepted_weight_deviation_quantity. USED existing active plan/PT and original SOFT or selected unit's current HARD suppress unallocated original demand, never create physical fact. Completed exact selected CASE/PT/current whole-order requested/actual equals frozen original prior actual+net/current physical key proof may waive own remaining gap. Explicit LAST_WHOLE_BOX exception independent of pct; WITHIN stays in frozen window. No balance/history rewrite. Return/cancel invalidates both pending and waived.
Actual8: QW19831BAC690EF/WARE23259078/rev282/wave436/CASE1075; pendingSOFT10 then HARD8+pending2, actual8/H8+waiver2/unallocated0/original10 retained. Native planner replay same plan. Return/PTcancel→picked0/waiver0/pending0/unallocated10.
Actual12: QW19841B760AF91/WARE24306784/rev283/CASE1076; pending original10 then HARD12/no pending, actual12/unallocated0/waiver0/original10. Return reopens10. Both exact physical unit/storage20/full replenishment/native weighted CASE/replay/tare release/countcleanup13520/20.
First29bc80ad91/rev281 found positive-only math.quantity cannot parse frozen previous actual0; fixed explicit zero branch (nonzero still exact positive parser). No stock effects from reader failure. Failed fixture natively cancelled/choice retired/P-H0/own actor retired.
SQL sparse current lookup8cys85tx03mch .104ms/84, fetchf3zajmc2jmq4j .627ms/12; retain exact sparse predicate, bounded200orderrows/2000PT and plan index. Inventory owner batch/plan review before larger load.197 planline lookup72336qkj6syfb1.573ms3, countftnxrqp6r6yj21.465ms3; indexed read retained.
NS36 last box software path8/12 implemented; real physical scale/gateway commissioning and independent acceptance remain. NS37/pick-by-line/category B/piece/route continue.
"""
for path,line in[("wiki/index.md","- [Потребность после целой коробки](database/nicora_ni042_weight_choice_demand_20261011.md):198 pending separately/actual8 waiver2/actual12 original10/return reopens10/no stock rewrite."),
("wiki/log.md","2026-10-11:198 installed pure current demand pending/fulfilled box rules. Own31bac690ef8vs10 acceptedgap2,41b760af9112vs10 original10 and no negativeqty; both native pick/replay/return demand10/cleanup passed. Explicit frozen previous actual0 parsing fixed; failed own fixture retired. Bounded sparse reads .104ms84/.627ms12 retained inventory batch/plan owner."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni04_2.md","11.10.2026:198 current original demand/whole box pending, actual8vs10 waiver2 and12vs10 preserved, return reopens10 delivered. NS36 last-box software path completed; next NS37 confirmed pick-by-line gap/categoryB/piece/route. Real hardware/independent acceptance remain open.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"198_whole_box_original_demand.md")]="""# Qwen:198
Run ni042_weight_choice_demand_case.py uniqueTAG 8 and12. Original10 retained throughout. SOFT-bound choice suppresses unallocated demand as pending10, HARD8 pending2, actual8 waiver2 only after exact completed native CASE/PT/current source.12 actual has no negative quantity or fabricated original12. Existing original planner returns sameplan, no extra2KG task. Return cancels current PT→pending/waiver0/current need10, immutable original approval remains. Change original order/frozen prior actual/current task/source/card; invalid approval must not waive demand. Existing193 loose9.6 accepted .4 waiver remains; ordinary nochoice stillold pool. Sparse/plan indexes and200/2000 bounds; batch before large load. Original request is not shipment proof.
"""
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
for item in m.get("sprints",[]):
 if item.get("id",item.get("code"))=="NI04.2":
  for value in("196","197","198"):
   if value not in item.setdefault("implementedSlices",[]):item["implementedSlices"].append(value)
out[str(p)]=json.dumps(m,ensure_ascii=True,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
