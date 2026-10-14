from pathlib import Path
import json,re
out={};f=Path("db/migrations/2026-10-11_ni052_unload_fullpal")
out[str(f/"003_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-217-fullpal-original-unload'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original bound FULLPAL unload via same native fulfillment and stock owner',sysdate,user,'db/migrations/2026-10-11_ni052_unload_fullpal/apply.sql','db/migrations/2026-10-11_ni052_unload_fullpal/rollback.sql','APPLIED','Actual WARE5747578/wave473/FULL.ST:562cdaa306/original SINGLE.FULL.LOAD:562cdaa306/new FULL217.UNLOAD:562cdaa306:OTHER; original-3/new+3/P3H3/late rollback/concurrent one winner/exact replay/currentWARE403; same original DONE task/UID retained and PICKED current stock version. Own spare native zero; primary3/3 retained for fresh QC/reload. Protected13520/20.');
commit;
"""
out[str(f/"apply.sql")]="@@001_fulfillment.sql\n@@002_unload.sql\n@@003_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for package,sql in [("RRL_STOCK_FULFILLMENT","001_fulfillment.sql"),("RRL_STOCK_UNLOAD_CMD","002_unload.sql")]:
 matches=[x for x in m["components"]if re.search(r"create\s+or\s+replace\s+package(?:\s+body)?\s+"+package+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)]
 if not matches and package=="RRL_STOCK_FULFILLMENT":
  actual=re.search(r"create\s+or\s+replace\s+package\s+(\w+)",(f/sql).read_text(encoding="utf-8"),re.I).group(1)
  matches=[x for x in m["components"]if re.search(r"create\s+or\s+replace\s+package(?:\s+body)?\s+"+actual+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)]
 assert matches,package
 m["components"]=[("../2026-10-11_ni052_unload_fullpal/"+sql)if x==matches[-1]else x for x in m["components"]if x not in matches[:-1]]
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki-raw/wms_admin_ui_reference/transport-unloading.js");s=p.read_text(encoding="utf-8");old='row.root_case_task_id != null || row.root_kind === "CONTAINER"';assert old in s;out[str(p)]=s.replace(old,old+' || row.root_kind === "STOCK"',1)
out["wiki/database/retailcase_ni052_unload_fullpal_20261011.md"]="""# NI05.2: разгрузка исходной целой паллеты
217 APPLIED RABAEV/orcl. [[retailcase_ni052_unload_fullpal_design_20261011]]; [[retailcase_ni052_unload_slot_20261011]].
Existing UNLOAD_SHIPMENT accepts original bound FULLPAL as standalone STOCK root or whole archived HU member. Original one fulfillment SHIPPED/same source load, bound physical UID, actual original DONE PICKING_MOVE task, active original wave/ST and whole current UID physical/held zero required. Current article/UOM must equal archived legs. Original negative movement remains; exact original quantity/units and original HARD ownership restored atomically. Existing fulfillment owner projects PICKED/current stock version, keeps original DONE task/UID/history. Wave/task/FF/ST/HU/unit resources declared before effects. Current permission/warehouse before replay and after waits. No second binding or allocator.
Actual WARE5747578/wave473/ST FULL.ST:562cdaa306/original SINGLE.FULL.LOAD:562cdaa306/new FULL217.UNLOAD:562cdaa306:OTHER: original-3/new+3/P3H3, late rollback left original LOADED, distinct simultaneous HTTP commands one200/one409, exact replay and current wrongWARE403. Original task DONE and UID unchanged; current FF PICKED version equals restored stock version. Own spare native cleaned0; primary3/3 deliberately retained for fresh QC/reload, rather than clearing fulfilled stock. Protected13520/20 unchanged.
Raw unloading screen includes STOCK roots through same endpoint/body/durable retry. Transferred FULLPAL own tare recovery and whole mixed HU positive proof remain separate. No independent acceptance or equipment/legal ACK claimed. Native objects checked VALID/no USER_ERRORS after application. Rollback refuses FULLPAL unload history; forward physical operations retain journal.
"""
for path,line in [
("wiki/index.md","- [Разгрузка целой паллеты](database/retailcase_ni052_unload_fullpal_20261011.md):217 same original binding/task/UID, native -3/+3/P3H3, current FF version and fresh QC before reload."),
("wiki/log.md","2026-10-11:217 original FULLPAL unloading reuses native journal/reserve/fulfillment, archived task/UID preserved; actual WARE5747578/wave473 original-3/new+3/P3H3/rollback/concurrent/replay/currentWARE403. Stock-root UI enabled. Own spare0, primary3/3 retained for fresh QC/reload. Protected13520/20. No independent acceptance."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni05_2.md","11.10.2026:217 original FULLPAL unload implemented with same actual DONE task/bound UID/native original quantity/HARD/FF PICKED current stock version. Actual3/3/rollback/concurrent/replay/currentWARE403; UI STOCK roots. Fresh QC/reload and own FULLPAL tare recovery next.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI05.2").setdefault("implementedSlices",[]).append("217 original bound FULLPAL unload retains DONE picking task/UID and projects current PICKED stock version; actual -3/+3/P3H3, rollback/concurrent/replay/current scope, STOCK-root UI");out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[str(root/"NI05.2"/"217_fullpal_unload.md")]="""# Qwen:217 original FULLPAL unload
Fresh scripts/ni052_fullpal_unload_case.py dedicated dev. Existing completed picking task and original full pallet bind/load reused. Original -3 retained/new +3/P3H3/current FF PICKED stock version/same DONE task and physical UID. Native late outer rollback, distinct concurrent HTTP one winner, exact replay, current foreignWARE403. Wrong original task/UID/article/UOM/nonzero current UID/departed load refuse. Spare native cleanup0; primary3/3 deliberately remains for fresh QC/reload. Never zero primary while fulfillment PICKED. Protected13520/20. Mixed HU/transferred FULLPAL tare independent cases.
"""
print(json.dumps(out,ensure_ascii=True))
