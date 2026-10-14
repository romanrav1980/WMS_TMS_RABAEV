from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_weight_box_planning")
out[str(f/"004_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-194-weight-box-planning-read'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Actual whole weighted box options and shared current warehouse planner admission',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_box_planning/apply.sql','db/migrations/2026-10-11_ni042_weight_box_planning/rollback.sql','APPLIED',
'Own SKU QW19416DCF25046 original10, actual source boxes8/12/gross8.3/12.3/volume.024/.036/current signed source/default15/both explicit exceptions/no split/P20H0 unchanged; foreign warehouse refused; no saved choice yet.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@004_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["components"].extend(["../2026-10-11_ni042_weight_box_planning/001_access.sql","../2026-10-11_ni042_weight_box_planning/003_admission.sql"])
m["components"].append("../2026-10-11_ni042_weight_box_planning/002_options.sql");m["packages"].extend(["RRL_PICK_PLAN_ACCESS","RRL_WEIGHT_BOX_PLANNING_READ"])
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_weight_box_planning_20261011.md"]="""# NI04.2: предварительный выбор целой коробки
194 APPLIED. [[retailcase_ni042_weight_box_planning_design_20261011]], [[retailcase_ni042_weight_demand_20261011]].
Pure native original-order-row preview returns actual AVAILABLE physical boxes, UID/cell/stock version/net/gross/volume/reference/raw label, current weighted serialized KG card/version/default15 and original whole orderSKU requested/picked/current row unallocated minus unlaunched SOFT. Boxes within order window versus exception_required explicitly separated; measurement readiness/no_split enforced in display. No stock/reservation/saved choice.
Original planner current actor/warehouse/right scope extracted into RRL_PICK_PLAN_ACCESS, reused existing174 before and after sorted locks; no duplicated permission engine. New /api/picking/order-rows/{row}/weighted-box-options requires existing pick_plan_create/current warehouse native. Typed boundary/services/API factory, original customer-order KG row button renders real box table with safe textContent and identifier label. Approval/apply next195.
Own scripts/ni042_weight_box_planning_read_case.py QW19416DCF25046/WARE21498354/revision267/order requested10/sourceP20H0/physical boxes8 and12/gross8.3 and12.3/vol.024 and.036: both outside15 require explicit lastbox exception, no split, current source/signature/deterministic repeat; foreign Q134 current warehouse native20882, P/H unchanged. Native countcleanup/original13520/20 unchanged. No normal plan launch invoked for unmatched10KG.
Bounds200 original rows/200 source lots/100 physical options, has_more truthful. Native syntax/application6stmt0errors/targeted USER_ERRORS empty; architecture548/0cycles/76debt and rawJS syntax PASS.
Read8pq8pt300jy2j39.450ms/2 cold, foreignscope5.882ms/1; retain bounded lot/unit windows/current indexes, inventory owner batch original order totals/plan review before high-history pilot; no extra speculative index or capacity claim.
Next accepted immutable selected whole box/current source snapshot, existing plan consumes decision and reserves exact unit, current fulfillment waiver/reversal. NS36 lastbox execution remains open.
"""
for path,line in [
("wiki/index.md","- [Предварительный выбор целой коробки](database/retailcase_ni042_weight_box_planning_20261011.md):194 actual8/12 vs original10/default15/current source/ARM table; explicit approval/apply next."),
("wiki/log.md","2026-10-11:194 APPLIED actual sealed weighted-box options/current shared planner scope. Own8/12 net+gross+volume/original10/default15/exception/no split/read repeat/foreignWARE refusal/P20H0 unchanged passed. Architecture548/0/76/JS PASS;39.450ms/2 bounded200lots100boxes, inventory batching/plan owner."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:194 actual whole box8/12 planning preview/source version/default15/explicit exception/no split/current warehouse/customer-order UI delivered. Approved choice/old-plan+HARD consumption/current fulfillment waiver next; no completed lastbox claim.")]:
 p=Path(path);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"194_whole_box_options.md")]="""# Qwen:194
Run ni042_weight_box_planning_read_case.py dedicated dev. Original10/sourceboxes8and12/exactgross/volume/current stock/policy/source signature/no_split/both exception required; no stock/reservation/saved choice. Native foreign warehouse/revoked/deleted/duplicate actor scope. Already picked/other row sameSKU/activeSOFT/current blocked or reserved box/missing physical measures/current default15 and configured pct. Customer-order KG button shows safe actual candidates/has_more100 and correct pallet identifier. Existing planner current scope must still run before and after locks. No approval/apply until195/196. Review200rows200lots100boxes/current lookup plan/batching.
"""
print(json.dumps(out,ensure_ascii=True))
