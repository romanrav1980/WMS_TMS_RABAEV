from pathlib import Path
import json,hashlib
out={};f=Path("db/migrations/2026-10-11_ni042_weight_choice_plan")
ledger="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-196-weight-choice-native-plan'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Approved whole weight box consumed by existing native planner and SOFT owner',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_choice_plan/apply.sql','db/migrations/2026-10-11_ni042_weight_choice_plan/rollback.sql','APPLIED',
'QW19612A0973586 revision277 original10/planned8/one existing source SOFT8; outer rollback/concurrent same plan/strategy conflict/cancel only after native plan cancellation/history retained/P20H0; current package VALID. Physical HARD pin197 next.');
commit;
"""
out[str(f/"007_ledger.sql")]=ledger
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@005_choice.sql\n@@007_ledger.sql\n"
out[str(f/"rollback.sql")]=(f/"rollback.sql").read_text(encoding="utf-8").replace("@@000_before_guard.sql","@@000_before_guard.sql\n@@000_before_choice.sql")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["components"]=[x.replace("../2026-10-11_ni042_weight_box_choice/005_recompile_api.sql","../2026-10-11_ni042_weight_choice_plan/005_choice.sql")for x in m["components"]]
m["components"].extend(["../2026-10-11_ni042_weight_choice_plan/001_bind.sql","../2026-10-11_ni042_weight_choice_plan/002_picking_contract.sql","../2026-10-11_ni042_weight_choice_plan/002_picking_body.sql"])
m["packages"].extend(["RRL_WEIGHT_PLAN_BIND","RRL_PICKING_API"])
m["additional_scripts"]=[x.replace("../2026-10-11_ni042_weight_box_choice/004_guard.sql","../2026-10-11_ni042_weight_choice_plan/003_guard.sql")for x in m["additional_scripts"]]
# Binder context creation is already included after its own package in 001.
m["additional_scripts"].append("../2026-10-11_ni042_weight_choice_plan/004_index.sql")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/nicora_ni042_weight_choice_plan_20261011.md"]="""# NI04.2: утверждённая коробка в прежнем плане
196 APPLIED. Existing RRL_PICKING_API.create_plan owns plan/line/PT/legacy SOFT and immutable choice binding in one transaction. Original requested10 retained; selected actual NET8 or12 becomes planned quantity. Private accessible-by RRL_WEIGHT_PLAN_BIND/current original order+row+source locks and private TX context; no new allocator or stock writer. Under-target original gap marked WEIGHT_BOX_CHOICE_PENDING, physical completion not yet implied.
Own QW19612A0973586/WARE21220759/rev277: choice8 vs original10/default15; native outer rollback restores ACCEPTED/no plan; two concurrent calls return one plan; original PL requested10/planned8, original PT8/sourceUID+cell, SOFT8. Changed strategy409. Active USED cancellation409; native plan cancellation then metadata cancellation retains source and original plan references. Native inventory cleanup/current P20H0 unchanged beforecleanup/original135 P20H20 retained.
Earlier author SQL used wrong SOURCE_UID/STATUS names for existing PT/projection; corrected to PALLET_UID/RESERVATION_STATUS. Failed5a59c3e883/acbb6a8b40 stock cleaned natively, cancelled bindings retained pending metadata retirement. Local API temporary CLOB stream twice hung SQL*Net more data from client while CONFIG metadata fence held; restart released session. Bounded ASCII <=16KB canonical request now bound VARCHAR then implicitly converted in Oracle before package entry. Default pooled call_timeout30s (WMS_ORACLE_CALL_TIMEOUT_MS bounded1..120s), cleanup3s/discard broken lease. Both original refusal and successful roundtrip passed after fix; no unexplained retry/new operation ID.
All objects VALID after196. Active sparse-index query rewritten with exact CASE predicate: fydk55x4jhbw2 .592ms/19; native sparse lookup8m8340myqp1ks .665ms/6; cancel11.930ms/1cold. Retain indexed bounded lookups and order/status/plan index; inventory owner batch and plan/statistics check before high-volume pilot.
197 exact physical HARD key and198 current pending/fulfilled demand remain; NI04.2 open.
"""
for name,line in [("wiki/index.md","- [Коробка в существующем плане](database/nicora_ni042_weight_choice_plan_20261011.md):196 original10/planned8/SOFT8/atomic rollback/concurrent one plan/cancel history; exact HARD pin next."),
("wiki/log.md","2026-10-11:196 native old planner+approved box implemented/live VALID; own12a0973586 original10/planned8/SOFT8, rollback and concurrent sameplan/strategy conflict/cancelled history passed. Fixed small request temporary-CLOB transport/pooled call deadline after observed held metadata fence. Indexed active choice .592ms19 retained; inventory batch/plan owner."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni04_2.md","11.10.2026:196 approved whole-box choice now consumed by existing planner/SOFT atomically; original10/planned8/current cancellation/history.197 physical key pin and198 actual fulfillment/return demand remain.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"196_weight_choice_native_plan.md")]="""# Qwen:196
Run ni042_weight_choice_plan_case.py dev. Assert original10/planned8 and12/only approved source SOFT, outer rollback removes binding and plan, concurrent one active plan/current actor scope, changed strategy409, canceled PT required before choice cancellation, immutable history. Old ordinary planner remains. Inspect original demand gap pending, not shipment. Test pooled call timeout/cleanup discard and canonical <=16KB VARCHAR-to-CLOB binding with 1000-character Unicode reason; unknown outcome same ID.197 HARD key pin remains pending.
"""
print(json.dumps(out,ensure_ascii=True))
