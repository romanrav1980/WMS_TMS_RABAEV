from pathlib import Path
import json,re
out={};f=Path("db/migrations/2026-10-11_ni052_unload_slot")
out[str(f/"007_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-215-unload-current-storage-slot'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original unloading restores real current measured storage slot through existing placement owner',sysdate,user,'db/migrations/2026-10-11_ni052_unload_slot/apply.sql','db/migrations/2026-10-11_ni052_unload_slot/rollback.sql','APPLIED',
'Actual CASE1117/wave471/WARE34189220/original2.45kg .125m3/OCCUPIED slot214/task931 DONE/SYNCED/HARD same slot; late capacity refusal rolls back full unload; native rollback/concurrent/replay/currentWARE403; original7 units14 codes/new nesting/native cleanup0/protected13520/20.');
commit;
"""
out[str(f/"apply.sql")]="".join("@@"+name+"\n"for name in ["001_slot.sql","002_placement.sql","003_unload.sql","004_task_guard.sql","005_claim_guard.sql","006_recompile.sql","007_ledger.sql"])
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for package,sql in [("RRL_STOCK_UNLOAD_CMD","003_unload.sql"),("RRL_STOCK_HU_SLOT","001_slot.sql"),("RRL_STOCK_HU_PLACEMENT_CORE","002_placement.sql")]:
 matches=[x for x in m["components"]if re.search(r"create\s+or\s+replace\s+package(?:\s+body)?\s+"+package+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)];assert matches,package
 m["components"]=[("../2026-10-11_ni052_unload_slot/"+sql)if x==matches[-1]else x for x in m["components"]if x not in matches[:-1]]
for sql in ["004_task_guard.sql","005_claim_guard.sql"]:
 names=re.findall(r"create\s+or\s+replace\s+trigger\s+(\w+)",(f/sql).read_text(encoding="utf-8"),re.I)
 for name in names:
  matches=[x for x in m["additional_scripts"]if re.search(r"create\s+or\s+replace\s+trigger\s+"+name+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)]
  m["additional_scripts"]=[x for x in m["additional_scripts"]if x not in matches]
 m["additional_scripts"].append("../2026-10-11_ni052_unload_slot/"+sql)
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni052_unload_slot_20261011.md"]="""# NI05.2: выгрузка занимает реальное место хранения
215 APPLIED RABAEV/orcl. [[retailcase_ni052_unload_slot_design_20261011]]; [[retailcase_ni052_unload_hu_20261011]].
Same original unload uses existing native target_json/record_place/move_coverage; no second capacity engine. Optional target_slot_id/scanned_to_slot_code; original slotted HU cell requires target/scan. Root declares CELL_X/current SLOT40/task+sync+claim owners before effects. Original load canonical measured mass/dimensions reused because exact cargo preserved; measurement epoch adjusted to current restored tree, no arbitrary client quantity/weight. After restored original P/H/units/nesting, existing target_json validates current topology/slot capacity/occupied/reserved/planned arrivals/temperature/location and existing aggregate load, record_place writes actual DONE PUTAWAY/SYNCED/OCCUPIED fact. Same original owner HARD moves to current slot. Late capacity refusal rolls back whole unload including goods/units/new links/projection/history/outbox.

Actual QPB2153FEC249F/CASE1117/wave471/WARE34189220: outer+inner+CASE7/14codes, preserved measured2.45kg/.125m3 placed slot214/task931 DONE/SYNCED, owner HARD same214. Capacity1kg refused with no unload/claim, then100kg permits exact same request; late rollback/concurrent one winner/replay/currentWARE403 passed. Native UNPACK outer→inner→CASE across three own slots before original goods return/release/tare/wave defer/count0; original135 P20H20 unchanged. Empty fixture containers retain truthful measured occupied metadata, no goods; do not claim all physical fixture slots removed.

API strict optional slot fields; exclude_none preserves old canonical command/replay identity. Existing target-slots endpoint reused in unloading UI, shows unavailable places disabled, exact slot scan/durable intent, scopes late fetch to current auth/source. Existing warehouse_task_view right for slot list retained; no blanket grants. Current root stock_shipping right authorizes confirmed scoped unloading placement. No schema duplication/new task lifecycle. Seven invalidated dependent owners recompiled; final INVALID0. Architecture215 PASS24/bothTS/556files0cycles76debt; JS syntax passed.
Capacity occupancy SQLc646jtycu4h07 .327ms/11, original measured claim insert8rsw85n6dsjhx2.81ms/6: retain slot index/current-cell fence and bounded existing capacity reads. Production load capacity not inferred from one fixture. Full FULLPAL/custody reverse/independent/equipment/regulatory acceptance remain.
"""
for path,line in [
("wiki/index.md","- [Выгрузка в фактически занятый слот](database/retailcase_ni052_unload_slot_20261011.md):215 original measured2.45kg/.125m3/OCCUPIED214/native DONE931/SYNCED, same HARD slot and late capacity rollback."),
("wiki/log.md","2026-10-11:215 original unload reuses native target_json/record_place/move_coverage under CELL_X/SLOT/task-sync-claim closure. Actual1117/4712.45kg/.125m3/slot214/task931, late capacity refusal/no partial unload, rollback/concurrent/replay/currentWARE403/native goods cleanup0/protected13520/20. UI existing slot list/scans/current-scope fetch; optional null exclusion preserves old command identity. Quality24/bothTS/556cycles0debt76; SQL.327/2.81ms retain bounded capacity."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni05_2.md","11.10.2026:215 slotted whole-HU unload reuses original measured dimensions/mass and actual placement owner. SLOT/CELL_X capacity guards; OCCUPIED214/DONE931/SYNCED/HARD same slot, late capacity rollback/concurrency/replay/currentWARE/native cleanup passed. UI slot selection/scan added; FULLPAL and accepted tare reverse custody next."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_1.md","11.10.2026:215 reverse unload now occupies real measured current slot via existing DONE PUTAWAY/SYNCED/claim owner, never orphan container. Actual2-level2.45kg/.125m3/slot214/capacity refusal full rollback/owner HARD slot unchanged identity; subsequent native UNPACK preserves goods and places.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI05.2").setdefault("implementedSlices",[]).append("215 slotted original whole-HU unload through existing measured native placement/capacity owner with CELL_X/SLOT, actual DONE/SYNCED/OCCUPIED and same HARD slot, late refusal rolls back all, UI existing slot list/exact scan")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI05.2"/"215_slotted_unload.md")]="""# Qwen:215
Dedicated fresh scripts/ni052_slotted_hu_unload_case.py. Whole outer/inner/CASE7+14 codes/original measured2.45kg/.125m3. Published current slot scan required; occupied/reserved/planned arrival/undersized/temperature/current topology refusal must leave original shipped P0H0/issued units/old inactive links/no unload/no claim/outbox. Capacity1kg refuses late;100kg allows same saved command. Actual P7H7/new links2/OCCUPIED/taskDONE/SYNCED/original HARD current slot; native rollback/concurrent/replay/currentWARE403. API old bodies omit null slot fields and replay unchanged. UI existing target-slots current scope and scanner. Cleanup existing UNPACK across own3 slots before original goods return/release/tare/wave/count0; empty container measured occupied metadata may remain truthful. Protected13520/20; no independent acceptance inference.
"""
print(json.dumps(out,ensure_ascii=True))
