from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_direct_receiving")
out[str(f/"006_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-199-direct-receiving-pick-plan'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing DIRECT SAP source planning and atomic placement handoff',sysdate,user,
'db/migrations/2026-10-11_ni042_direct_receiving/apply.sql','db/migrations/2026-10-11_ni042_direct_receiving/rollback.sql','APPLIED',
'Own QPB1999A1F92AB wave444 SAP20 to original store orders12/8; wait before birth/current IN_PROGRESS refusal/no target or replenishment/current HARD/native CASE picks/replay; outer rollback restores putaway and HARD0; original taskQTY retained; narrow planned native SAP CASE clone trigger; native cleanup/original13520/20.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@006_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["components"]=[x.replace("../2026-10-09_ni032_alternative_face/003_eligibility.sql","../2026-10-11_ni042_direct_receiving/004_eligibility.sql").replace("../2026-10-11_ni042_weight_unit_pin/002_launch.sql","../2026-10-11_ni042_direct_receiving/003_launch.sql")for x in m["components"]]
m["components"]=[x for x in m["components"]if x not in("../2026-10-11_ni042_weight_choice_plan/002_picking_contract.sql","../2026-10-11_ni042_weight_choice_plan/002_picking_body.sql")]
m["components"].insert(m["components"].index("../2026-10-11_ni042_direct_receiving/003_launch.sql"),"../2026-10-11_ni042_direct_receiving/001_direct.sql")
m["components"].append("../2026-10-11_ni042_direct_receiving/002_picking.sql");m["packages"].append("RRL_DIRECT_RECEIVING_PICK")
m["additional_scripts"].append("../2026-10-11_ni042_direct_receiving/005_sap_guard.sql");out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/nicora_ni042_direct_receiving_20261011.md"]="""# NI04.2: pick-by-line по исходной SAP-приёмке
199 APPLIED. [[nicora_ni042_direct_receiving_design_20261011]]. Existing DIRECT rule had admission but native planner always resolved rack pickface, generating unusable replenishment from receiving. Now admitted current SAP receive UID/cell under DIRECT yields CASE_PICK targetnull, so existing CASE source/warehouse/code rules and WAVE HARD apply directly, no new allocator.
Root WAVE_LAUNCH declares original unstarted SAP PUTAWAY ROW20 and reserved claim SLOT40, preserves original task/status/quantity/slot in immutable resolved plan, then atomically cancels placement/frees reserved claim. IN_PROGRESS blocks source. PhysicalP unchanged, original task QTY remains history; current remainder may explicitly replan200.
Own QPB1999A1F92AB/wave444: real ARTMAS10 EA20/SAP XML supply recipient/current physical receipt. Two existing customer IDs/order12+8; before receipt NO_STOCK/no physical reserve, in-progress placement blocks planning. Afterreceipt source HARD20, no rack target/no replenishment, native CASE12/8/replay/source0+CASE20. Native outer rollback restored original placement PLANNED/H0. Existing return/release/countcleanup/original13520/20.
First author used nonexistent header PLANNED_QTY; corrected sum original planline. Subsequent actual case exposed old RRL_SAP_PALLET_WRITE_GUARD blocking lawful native CASE split (20804). Narrow new insert allowance ONLY current trustedTX/op IN_FLIGHT CASE_PICK_CONFIRM, exact resolved original source→child UID+quantity, original SAP receipt document/stock-origin and held source+child UID50. Direct update/delete/rebirth still denied. Initial helper used nonexistent WH UPDATED fields; removed. Later fixture CPT cell was incorrectly ordinary; native correctly refused CASE_TRANSIT_SYSTEM_LOCATION_REQUIRED, fixture fixed system cell rather than relax rule. All born failed fixtures nativecleaned.
Slow original-task cancel2sdf4ahdhn5g81.175ms13; exact native clone proofab5qqfq84pf7a2.441ms9. Retain PK and bounded200 tasks/claims; inventory owner task-source index/plan batching review before larger load. No industrial/govACK claim. Marked12 codes/5+7 source lineage is201 next.
"""
out["wiki/database/nicora_ni042_direct_residual_20261011.md"]="""# NI04.2: текущий остаток на размещение
200 existing SAP putaway replan software delivered. [[nicora_ni042_direct_residual_design_20261011]].
Under current business CONFIG X/scanned original pallet/cell/currentwarehouse and original SAP admission, current P/H/version readlocked. Changed quantity allowed ONLY original applied WAVE_LAUNCH direct handoff task+UID+cell proof and no current HARD/active original direct task projection. Exact original task UOM→BASE1:1. Positive current<=original; unrelated source change still refuses. Existing task/replan idempotency/placement/claim/outbox reused; QTY bound as Decimal, original receipt quantity retained. UI shows current task quantity.
Own QPB200106BF7EE/task901/wave447: SAP received20, DIRECTorder12, unstarted putawayoriginal20 cancelled byroot. Replan while pending sourceH12 refused409; after CASEactual12 sourceP8H0, replan records original20/current8/stockversion/handoff. Retry originalresult, TASK_QTY8/PLANNED/storage; operator closes CASE before machinery (earlier native FINISH_OPERATOR_CASE_CARRIER_FIRST correctly refused). Existing TASK_COMPLETE storage8 and SAP placement outbox base_quantity8, original POSTED_BASE_QTY20 unchanged. Native return/countcleanup/original13520/20.
First200 test hit API old process during delayed reload and got oldreplan; explicit rootserv restart applied current code. Next found same operator carrying CASE cannot do putaway; fixture closes carrier rather than widen permissions. Architecture549/0cycles/76debt, current rawJS syntax PASS.
Native handoff read7harmm029cn7p2.811ms4; retain OP PK +bounded original resolved plan. Inventory owner prepared batch/plan review; no quantity denormalization or external ACK.
"""
for path,line in[("wiki/index.md","- [Прямой отбор из SAP приёмки](database/nicora_ni042_direct_receiving_20261011.md):199 actual20→12/8/no replenishment/atomic putaway handoff/rollback; [остаток на размещение](database/nicora_ni042_direct_residual_20261011.md):200 original20/actualCASE12/storage8/outbox8."),
("wiki/log.md","2026-10-11:199 APPLIED DIRECT native old planner/source HARD/CASE and atomic original putaway cancellation; actual9a1f92ab20→12/8/rollback/replay/native cleanup passed. Narrow old SAP guard allowance for exactly planned native CASE child.200 original20/direct12/currentfree8 replan+TASK_COMPLETE/outbox8/current handoff/no active reserves/replay passed106bf7ee; CASE closure required before same operator machinery. Indexed proof2.811ms4/clone2.441ms9 retained/bounded inventory plan owner. Architecture5490cycles76debt/JS."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni04_2.md","11.10.2026:199/200 NS37 software unmarked directSAP20→stores12/8/current receiving source/no rack replenishment/atomic original putaway hold+rollback; partial direct12 currentfree8→explicit existingreplan/storage8/outbox8/original receipt20 retained. Marked12 codes→5/7, categoryB/piece/route remain.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"199_200_direct_receiving.md")]="""# Qwen:199/200
Run ni042_direct_receiving_case.py and ni042_direct_residual_case.py in dedicated dev. Actual SAP20→original stores12/8 from receiving, SOURCE_PICK_MODE DIRECT/no replenishment, before receipt no HARD, IN_PROGRESS putaway refuses. Native WAVE launch original putaway/slot cancellation+HARD atomic/outer rollback. Narrow SAP guard permits only current root IN_FLIGHT planned source-child CASE clone, exact UID+quantity+origin/doc and heldUID50; arbitrary DML staysblocked.
PartialDIRECT12/received20→currentfree8 replan ONLY applied handoff proof/scannedsource/currentWARE/no HARD/pendingtask/exactUOM1:1; pending replan409 and unrelated quantitychange409. Existing task8/baseDecimal/slot/outbox reused, original20 retained; completed CASE before same operator machine. Existing TASK_COMPLETE moves8 and SAP event8. Unknown outcome reuses original operation+body. UI current quantity. Marked12/5+7 is201 next. Planline/source-task/OP PK bounded SQL evidence; no production/hardware/legal ACK.
"""
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
for item in m.get("sprints",[]):
 if item.get("id",item.get("code"))=="NI04.2":
  for value in("199","200"):
   if value not in item.setdefault("implementedSlices",[]):item["implementedSlices"].append(value)
out[str(p)]=json.dumps(m,ensure_ascii=True,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
