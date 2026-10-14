from pathlib import Path
import json,re
out={};d=Path("db/migrations/2026-10-11_ni061_recovery_placement")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));base="../2026-10-11_ni061_recovery_placement/"
def read(n):return out.get((p.parent/n).resolve().relative_to(Path.cwd()).as_posix())or(p.parent/n).read_text(encoding="utf-8")
for pkg,new,body in [
("RRL_STOCK_INTERWARE_PUT","010_original_put_current.sql","003_original_put_body.sql"),
("RRL_STOCK_TASK_PLAN","011_task_plan_current.sql","005_task_plan.sql"),
("RRL_STOCK_TASK_CORE","012_task_core_current.sql","006_task_core.sql"),
("RRL_STOCK_TASK_DOMAIN","013_task_domain_current.sql","007_task_domain.sql"),
("RRL_STOCK_POSTING_API","014_root_current.sql","008_root_body.sql")]:
 sources=[n for n in j["components"]if re.search(r"create\s+or\s+replace\s+package\s+"+pkg+r"\s",read(n),re.I)]
 assert len(sources)==1,(pkg,sources)
 original=read(sources[0]);spec=original.split("\n/\n",1)[0]+"\n/\n"
 out[(d/new).as_posix()]=spec+"\n"+(d/body).read_text(encoding="utf-8")
 at=j["components"].index(sources[0]);j["components"][at]=base+new
 if pkg=="RRL_STOCK_INTERWARE_PUT":j["components"][at:at]=[base+"002_put_cell.sql",base+"004_recovery_put.sql"]
j["packages"]+=["RRL_STOCK_IW_PUT_CELL","RRL_STOCK_IW_RECOVERY_PUT"]
j["startup_scripts"].append(base+"001_schema.sql")
j["additional_scripts"]+=[base+n for n in ["003_original_put_body.sql","004_recovery_put.sql","005_task_plan.sql","006_task_core.sql","007_task_domain.sql","008_root_body.sql","009_guards.sql"]]
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_shortage.py");s=p.read_text(encoding="utf-8")
s=s.replace("        recovered_keys=set()",'''        placement=None
        placement_plan=None
        if recovery and recovery[4]:
            cur.execute("""select pp.TASK_ID,t.STATUS,pp.TARGET_CELL,p.OPERATION_ID
                from RRL_IW_RECOVERY_PUT_PLAN pp join RRL_WAREHOUSE_TASK t on t.TASK_ID=pp.TASK_ID
                left join RRL_IW_RECOVERY_PLACEMENT p on p.TASK_ID=pp.TASK_ID
                where pp.RECOVERY_OPERATION_ID=:recovery_id and t.STATUS!='CANCELLED'
                fetch first 2 rows only""",recovery_id=recovery[4])
            candidates=cur.fetchall()
            if len(candidates)>1:raise StoreReturnReceiveError("RECOVERY_PLACEMENT_AMBIGUOUS","Несколько действующих заданий размещения",409)
            placement_plan=candidates[0]if candidates else None
            placement=placement_plan if placement_plan and placement_plan[3]else None
        recovered_keys=set()''',1)
s=s.replace('status="RECOVERED_PENDING_PLACEMENT"if recovery and recovery[4]','recovery_placement_task_id=placement_plan[0]if placement_plan else None,recovery_placement_task_status=placement_plan[1]if placement_plan else None,\n                    recovery_placement_target_cell=placement_plan[2]if placement_plan else None,recovery_placement_operation_id=placement[3]if placement else None,\n                    status="RECOVERED_PLACED_PENDING_REDELIVERY"if placement else"RECOVERED_PENDING_PLACEMENT"if recovery and recovery[4]',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8");pos=s.index('id="iwRecoveryStatus"');end=s.index("</",pos);end=s.index(">",end)+1
s=s[:end]+'<button id="iwRecoveryPlace" type="button">Создать задание размещения найденного товара</button>'+s[end:];out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('el("iwRecoveryStatus").textContent=r.recovery_receipt_operation_id?','el("iwRecoveryStatus").textContent=r.recovery_placement_operation_id?"Найденный товар размещён; требуется повторная доставка · "+r.recovery_placement_target_cell:r.recovery_placement_task_id?"Задание размещения "+r.recovery_placement_task_id+" · "+r.recovery_placement_task_status:r.recovery_receipt_operation_id?',1)
needle=' el("iwFoundReceive").addEventListener'
s=s.replace(needle,''' el("iwRecoveryPlace").addEventListener("click",async()=>{if(busy||pending)return;try{
 const r=currentShortage;if(!r||r.receipt_operation_id!==el("iwShortReceipt").value||!r.recovery_receipt_operation_id||r.recovery_placement_task_id)throw Error("Загрузите найденный товар без действующего задания размещения.");
 const intent={path:"/recovery-placement",body:{operation_id:"INTERWARE.RECOVERY.PUT:"+crypto.randomUUID(),recovery_operation_id:r.recovery_receipt_operation_id}};
 localStorage.setItem(key(),JSON.stringify(intent));pending=intent;await send(key());currentShortage=null;
 }catch(e){say(e.message);controls();}});
'''+needle,1);out[p.as_posix()]=s
out[(d/"015_ledger.sql").as_posix()]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-301-recovery-placement'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Found goods placement using existing TASK_COMPLETE',sysdate,user,'db/migrations/2026-10-11_ni061_recovery_placement/apply.sql','db/migrations/2026-10-11_ni061_recovery_placement/rollback.sql','APPLIED','Actual ordinary+marked recovered2 placed by existing task kernel; stock conserved, native rollback and exact replay; common target cell policy, original departed trip retained. No redelivery or new government ACK.');commit;
"""
out["wiki/database/retailcase_ni061_recovery_placement_20261011.md"]="""# NI06.1 — размещение найденного груза (301)
11.10.2026. Migration 2026-10-11-301-recovery-placement, dev RABAEV/orcl, ACTIVE/compatOFF.

Новая приёмка найденного груза (300) получает обычное задание PUTAWAY существующей таблицы RRL_WAREHOUSE_TASK. Источник MANUAL/RECOVERY ссылается на неизменяемые RRL_IW_RECOVERY_PUT_PLAN и RRL_IW_RECOVERY_PLACEMENT. Количество изменяет прежняя TASK_COMPLETE / TRANSFER_CORE. Планирование не проводит запас.

Цель — существующий исходный выходной буфер межскладского плана; новый рейс ещё не создан. Исторический завершённый рейс не переоткрывается и не является условием допуска. Температурное решение, склад, доступность, масса и занятые места проверяются прежними правилами; контроль ячейки выделен в общий приватный RRL_STOCK_IW_PUT_CELL и применяется также прежним размещением. Опубликованные слоты требуют отдельного слотного потока; высота без доказательства отклоняется.

Только целая найденная паллета, P=2/H=0, один источник, тот же UID/SKU/UOM и точные версии сохранённых физических единиц. Текущая складская область проверяется до replay и после ожидания. Ресурсы объявляются общим lock-планом. Native complete проверяет исходное задание, сканы паллеты/источника/назначения, затем в одной транзакции переносит остаток и единицы, пишет выполнение и обязательный outbox. История недостачи/найденного товара остаётся.

Результат: tmp/context301_291.json и _292: два реальных задания завершены; приёмочные ячейки0, выходные2, H0. Маркированные2 единицы сохранили происхождение/QR и перешли в существующий буфер. Проверены внешний rollback планирования и проведения, точный повтор без второго движения, protected20/20. USER_ERRORS/INVALID пусты. После повторной отгрузки не повторять прежние утверждения о текущем P2.

API POST /api/inventory/interwarehouse/recovery-placement. Прежняя страница межскладского контроля сохраняет OPID/тело до HTTP и отображает реальное задание. Читатель различает приёмку, размещение и ожидание повторной доставки; найденный складской запас не считается принятым покупателем.

Далее: отдельная повторная доставка оставшихся2 с исходной строкой заказа, суммирование независимых конечных приёмок1+2 без повторного FF.SHIPPED, частичные/повторные циклы недостачи. Реальные государственные ответы, оборудование и независимая приёмка не заявлены выполненными.
"""
p=Path("wiki/index.md");s=p.read_text(encoding="utf-8").replace("current native298/app298","current native301/app301",1);out[p.as_posix()]="- [Размещение найденного груза](database/retailcase_ni061_recovery_placement_20261011.md):301 existingTASK_COMPLETE/common cellpolicy/ordinary+marked2 conserved/no buyercredit.\n"+s
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 11.10.2026 301: actual recovered ordinary+marked2 placement via existing TASK_COMPLETE; common target cell checks; native rollback/replay/20-20, allVALID. API/UI durable plan and placement status; corrective redelivery remains.\n"
p=Path("wiki/runbooks/retailcase_active_work.md");s=p.read_text(encoding="utf-8");a=s.index("Native manifest298:");b=s.index("\n\n## Последняя",a)
s=s[:a]+"""Native manifest301: stockRoot/task handlers301; BALANCE/LOCATION/PART/UnitCore300 and recovery guards300; partial custody-NEXT-depart296; source-load index298. Bundle generateFILES only, never reapply ACTIVE.
App301/native301; restart rootserv301 before current API. tmp/context300_291/_292 received lost2, context301_291/_292 now placed2 in original outbound buffers. Do not rerun initial300 rollbackcases or sourcebirth. Next corrective ST/redelivery and customer1+2 lineage; historical shortage2 preserved, recovered2/net0 not customer acceptance."""+s[b:];out[p.as_posix()]=s
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI06.1").setdefault("implementedSlices",[]).append("301 recovered2 existingTASK_COMPLETE placement/common targetpolicy/sameoldunits/stockconserved; corrective redelivery next");out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
qroot=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(qroot/"NI06.1/301_recovery_placement.md").as_posix()]='''# Qwen301: recovered stock placement
Read wiki/database/retailcase_ni061_recovery_placement_20261011.md and tmp/context301_291/_292. Tasks already DONE/P2 outbound; do not rerun source/receipt births or initial rollback phase.
Exact OPID/body -> same result/no move. Changed payload/current foreignWARE/revoked rights/unavailable cell/unitversion conflict denies. Own fresh case plan outerrollback no task; TASK_COMPLETE rollback restores receivingP and units/clears placement/outbox. Wrong scans/partial quantity/otherUID deny. Same race plan one active task; completion serialized. Original departedTT retained. No customer/Gov credit.
Review common helper ordinary interware positive and capacity/thermal/slot denials. Analyze longest queries. Report independent execution separately from static review.
'''
print(json.dumps(out))
