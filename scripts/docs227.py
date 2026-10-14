from pathlib import Path
import json,re
out={};f=Path("db/migrations/2026-10-11_ni061_marked_placement")
out[str(f/"004_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-227-original-marked-interwarehouse-placement'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original warehouse task places exact marked interwarehouse units',sysdate,user,'db/migrations/2026-10-11_ni061_marked_placement/apply.sql','db/migrations/2026-10-11_ni061_marked_placement/rollback.sql','APPLIED','Actual225->226->227 original UID FULL.QA:13508027ed/PUTAWAY953 DONE/SYNCED/receiving0/outbound3H0/3same units6codes/version9. Native rollback/concurrent one winner/replay/foreign current plan403/protected20/20. Existing resource44/session40/equipment14 PUTAWAY qualification and assignment; session requirement preserved. Native VALID/previous226 API quality24/bothTS/557files0cycles76debt; no new API change.');
commit;
"""
out[str(f/"apply.sql")]="@@001_placement.sql\n@@002_root.sql\n@@003_recompile.sql\n@@004_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for package,sql in[("RRL_STOCK_INTERWARE_PUT","001_placement.sql"),("RRL_STOCK_POSTING_API","002_root.sql")]:
 matches=[x for x in m["components"]if re.search(r"create\s+or\s+replace\s+package(?:\s+body)?\s+"+package+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)]
 m["components"]=[x for x in m["components"]if x not in matches]+["../2026-10-11_ni061_marked_placement/"+sql]
m["additional_scripts"].append("../2026-10-11_ni061_marked_placement/003_recompile.sql");out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni061_marked_placement_20261011.md"]="""# NI06.1: штатное размещение маркированного межскладского состава
227 APPLIED RABAEV/orcl. [[retailcase_ni061_marked_receive_20261011]]; [[retailcase_ni061_marked_placement_design_20261011]].
Original INTERWARE PUTAWAY planner previously refused current marked SKU. It now verifies exact immutable225 physical keys/qty/UOM and current whole AVAILABLE/no-HARD units at receipt cell, bounded10000, sorted versioned snapshot frozen in domain/revalidated after native locks. Existing task identity/cells/original receipt/target trip/volume/weight/height/slot restrictions retained. Existing TaskPlan/TaskCore/TransferCore already move same physical units with quantities; no new mover or birth. Current target actor before plan saved replay/after mutex wait. Receipt original customer fulfillment not repeated.
Actual original22513508027ed->226targetP3->IW227.PLAN original PUTAWAY953. Initial missing outbound RRL_CELLS was fixture setup omission: added own QO22513508027ed cell/policy against original existing target dock/TT33543. Current actor TR22613508027ed requires real machine session; prepared own qualified PUTAWAY resource44/session40/equipment14/shift, assigned existing953 without disabling policy. Native outer rollback restores sourceP3/units8/taskassignment; concurrent completion different IDs one200/one409, same saved completion replay. TASK_COMPLETE IW227.COMPLETE:13508027ed0 APPLIED/taskDONE/sync tableSYNCED/sourceQI226zero/outboundQO2253H0/samephysical3/codes6/versions9/immutableplacement1/protected13520/20.
Postcommit author assertion incorrectly queried SYNC_STATUS on task table; corrected to actual RRL_WAREHOUSE_TASK_SYNC via read-only/saved replay on SAME completed953. No duplicate fixture/redo movement.
Native allVALID/noerrors;226 unchanged API gate24/bothTS/557files0cycles76debt reused, no broad repeat. SQLunitmatrix8ugfmawj1c4dr4.648ms/7, putPlan3z2sdy9g8xp22 29.912ms/1, placement6m8g9r4sq51bm10.44ms/2: retain original unit/source unique indexes, sorted bounded matrix/no duplicate index. No throughput claim.
Current target P3 retained for onward. Custody release/onward source and nested/aggregate/loading remain next; no real regulatory ACK/full NI06.1 acceptance.
"""
for path,line in[
("wiki/index.md","- [Размещение маркированной межскладской паллеты](database/retailcase_ni061_marked_placement_20261011.md):227 same original task953 DONE/SYNCED/receiving0/outbound3H0/same units3 codes6/version9/real resource session."),
("wiki/log.md","2026-10-11:227 existing INTERWARE PUTAWAY owner extended exact225 current physical keys/qty/UOM/versions, source admission only; original transfer already moves units. Same225->226->953 DONE/SYNCED/source0/outbound3H0/3units6codes/version9. Native rollback/concurrent one winner/replay/currentscope/protected20/20; real qualified resource44/session40/equipment14 assignment retained. Author SYNC_STATUS table mistake corrected by SAME saved replay/read-only proof. NativeVALID/226 API gates reused. SQL4.648/29.912/10.44ms retain indexed bounded source. Next custody/onward."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md","11.10.2026:227 marked original receipt moved by existing PUTAWAY953 DONE/SYNCED/real machine session, same physical units and codes/version9, source0/outboundP3H0/native rollback/concurrent/replay/current target scope. Marked onward/nested/aggregation remain open.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI06.1").setdefault("implementedSlices",[]).append("227 exact marked source admitted in original PUTAWAY owner/task953 real machine session/native rollback/concurrent/source0-outbound3H0/same3units6codes/version9; onward/nesting remain");out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"));out[str(root/"NI06.1"/"227_marked_original_placement.md")]="""# Qwen:227 — штатное размещение маркированной паллеты
Новая собственная фикстура исходной отгрузки->225manifest->226receipt. Уже DONE953 не повторять/не удалять.
Проверить original INTERWARE_PUTAWAY_PLAN/TaskPlan/TaskCore/TransferCore; exact physical keys/quantity/UOM/no HARD/versioned current snapshot; чужая единица/нецелый состав/резерв/несколько cell/изменённые target trip/dock/capacity ->отказ без P.
PLANNED->ASSIGNED->COMPLETE с настоящей квалифицированной PUTAWAY машинной сессией; без сессии обычный actor получает TASK_MACHINE_SESSION_REQUIRED. Не выдавать forceassign для обхода.
Outer rollback после native execute сохраняет sourceP/units/task/session; concurrency different IDs один победитель; sameID saved replay без второй проводки.
DONE953/sync читать из RRL_WAREHOUSE_TASK_SYNC, не несуществующий task.SYNC_STATUS. Source0/target3H0/same units3/codes6/version+1/no births/original first customer fulfillment retained/immutableplacement1.
Current actor warehouse/right before saved planning and completion replay; UI existing task workflow uses confirmed native results.
Длинные SQL matrix bounded10000/currentUID/indexed original key; явное решение по slow SQL.
Не заявлять полную агрегацию/матрешку/межскладское второе плечо/госACK этим срезом.
"""
print(json.dumps(out,ensure_ascii=True))
