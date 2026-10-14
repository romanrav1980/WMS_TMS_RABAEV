from pathlib import Path
import json,re
out={};d=Path("db/migrations/2026-10-11_ni061_recovery_redelivery")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));base="../2026-10-11_ni061_recovery_redelivery/"
sources=[n for n in j["components"]if re.search(r"create\s+or\s+replace\s+package\s+RRL_STOCK_INTERWARE_NEXT\s",(p.parent/n).read_text(encoding="utf-8"),re.I)];assert len(sources)==1,sources
out[(d/"007_next_current.sql").as_posix()]=(d/"000_before_rrl_stock_interware_next_package.sql").read_text(encoding="utf-8")+"\n"+(d/"003_next_body.sql").read_text(encoding="utf-8")
at=j["components"].index(sources[0]);j["components"][at:at+1]=[base+"002_recovery_next.sql",base+"007_next_current.sql"]
j["packages"].append("RRL_STOCK_IW_RECOVERY_NEXT");j["startup_scripts"] += ["../2026-10-11_ni061_recovery_placement/016_lookup_index.sql",base+"001_schema.sql"]
j["additional_scripts"] +=[base+n for n in ["002_recovery_next.sql","003_next_body.sql","004_dispatch_guard.sql","005_binding_guard.sql"]]
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
out[(d/"008_ledger.sql").as_posix()]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-302-recovery-redelivery'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Found cargo corrective original ST and final1+2 delivery',sysdate,user,'db/migrations/2026-10-11_ni061_recovery_redelivery/apply.sql','db/migrations/2026-10-11_ni061_recovery_redelivery/rollback.sql','APPLIED','Actual ordinary+marked recovered2 existing ST/QC/load/depart/STORE; original FF3 once, buyer1+2=3, loss2/recovered2 history. Native load+store rollback/replay, codehashes unchanged; source index/shared kernel/no fake ACK.');
commit;
"""
p=d/"apply.sql";out[p.as_posix()]=p.read_text(encoding="utf-8")+"@@005_binding_guard.sql\n@@006_stats.sql\n@@008_ledger.sql\n"
p=d/"rollback.sql";s=p.read_text(encoding="utf-8").replace("drop trigger RRL_IW_REC_DISPATCH_GUARD;","drop trigger RRL_IW_REC_ST_INSERT_GUARD;\ndrop trigger RRL_IW_REC_DISPATCH_GUARD;");out[p.as_posix()]=s
out["wiki/database/retailcase_ni061_recovery_redelivery_20261011.md"]="""# NI06.1/NI05.3 — повторная доставка найденного остатка (302–303)
Migration 2026-10-11-302-recovery-redelivery, dev RABAEV/orcl ACTIVE/compatOFF. Источник: [[retailcase_ni061_recovery_placement_20261011]], затем прежний конструктор СТ, назначение, QC, LOAD_SHIPMENT, TRIP_DEPART, STORE_RECEIPT.

RRL_IW_RECOVERY_ST_BIND хранит отдельную неизменяемую связь найденной приёмки, новой СТ/планового рейса, исходной СТ/погрузки, склада/остатка/версии и замороженного адреса/владельцев исходной onward-связи. Новое исполнение customer fulfillment не создаётся. Подготовка под существующим CONFIG X до legacy row-locks; актуальные outgoing_pallet_edit+transport_dispatch_edit/currentWARE проверяются до replay. INSERT-guard требует metadata lock и точный сохранённый источник/владельцев. Уникальный recoveryID допускает одну СТ текущего целого восстановления. Новый рейс выбирает оператор; прошедшие рейсы неизменны.

RRL_STOCK_INTERWARE_NEXT делегирует найденную СТ приватному RRL_STOCK_IW_RECOVERY_NEXT. Прежний SHIPPING_CORE сохраняется. В LOAD проверяются actual2/H0/current stockversion, исходные найденные UNIT/key/qty/UOM/currentversion, адрес и назначение рейса; проведённое движение/QR/журнал/SAPintent/common outbox плюс RRL_IW_RECOVERY_DISPATCH — одна транзакция. native RUS-проверка также исправляет неоднозначное WARE_ID=ware_id: локальная переменная переименована v_warehouse в старой и новой ветви.

Actual tmp/context302_291/_292: оригинальным конструктором созданы2 отдельные СТqty2 и назначены на2 новые рейса; QCordinary/marked4QR, native outer rollback LOAD восстановилP2 и удалилdispatch; realLOAD+DEPART/exactreplay оставилиP0/FFsource3 один. Защищённые20/20 сохранены.

303 не добавляет магазинный receiver: actual STORE_RECEIPTqty2 ordinary/marked4QR с rollback/replay. tmp/context303_291/_292: покупатель accepted1+2=3, shipped3, unreceived0, original FF.SHIPPED3 один, 2 окончательные lineage, noSTOREstockevent. Все6 оригинальныхcodehashes сохранены. Existingfullorder2030 accepted3/unreceived0 сохранён. Nonadmin/physicalhardware/independent release не заявлены.

OrderDelivery читает bounded<=200 original loads/<=2000 receipt lines в одном RO snapshot. Обе конечные доставки связываются с исходным UID только доказанными APPLIEDloss/recovery/dispatch. Domain receipt_totals проверяет уникальные actualLoad/UID/receipt, общий исходный anchor1+loss2=3, единый lossID, corrective credited<=recovered2, sum accepted/missing/refused/damaged=actualshipped и итог<=original3. Дубликат/излишек/foreignloss/несогласованные disposition отклоняются. Shared partial owner остаётся explicit allocation, без пропорционального угадывания.

Три количества раздельны: historical_transport_shortage2, recovered_transport_quantity2, confirmed_transport_shortage0 (ещё потерянное). unreceived уменьшается только finalreceipt, не складской находкой. До последней приёмки actualaccepted1/unreceived2, даже послеwarehousefound2. После final2 accepted3/unreceived0; история2 не удаляется. UI показывает отдельные колонки/lineage и повторную СТ, долговечный pending OPID.

SQL actual303 first broad joins147.101ms/4213buffers average7; scoped NL plan plus source-load index/new-table statistics дали warm3reads12.490ms total/4.163ms mean/222buffers. Сохранены bounded reads и PK/index; не добавлен cache и не заявлен промышленный миллион операций. Recovery nativebind PK read0.657ms/20exec, dispatch binding PK0.400ms/12exec. 301placementlookup123.579ms cold→7.603ms после sparse RECOVERY_OPERATION_ID/TASK_ID index+stats; native placementinsert3.669ms/4exec. Не включать DDL/statistics в операционную latency.

Оставшееся: частичное восстановление одного акта, повторная потеря той же physicalunit (сегодня ledgerPK блокирует новый цикл), вложенные/агрегированные грузовые места и совместная переупаковка. RealERP/government ACK, legalrules/realrouting, hardware и независимая acceptance требуют реальных входов; не имитировать их.
"""
p=Path("wiki/database/retailcase_ni061_recovery_placement_20261011.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\nПродолжение [[retailcase_ni061_recovery_redelivery_20261011]]: 302–303 обе найденные2 уже повторно отгружены и приняты магазином, текущийP0. SQL301 решение: добавлен sparse RRL_IW_REC_PUT_RECEIPT_IX +stat только двух новых journals; lookupcold123.579→7.603ms, bounds2 preserved.\n"
p=Path("wiki/index.md");s=p.read_text(encoding="utf-8").replace("current native301/app301","current native302/app303",1);out[p.as_posix()]="- [Повторная доставка найденного остатка](database/retailcase_ni061_recovery_redelivery_20261011.md):302–303 originalST/QC/LOAD/DEPART/STORE reused; buyer1+2=3/originalFF3once/history2-found2-net0.\n"+s
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 11.10.2026 302–303: actual recovered ordinary+marked2 correctiveST/newtrip/originalQC-load-depart-STORE; buyer1+2=3/sourceFF3one/historyloss2+found2. Native rollback/replay/code6/protected20-20/allVALID; arch632/0cycles76; current scope variable ambiguity fixed. ScopedNL/sourceindex/stats warm4.163ms. Manifest/wiki/Qwen updated; partial/recurrent recovery next.\n"
p=Path("wiki/runbooks/retailcase_active_work.md");s=p.read_text(encoding="utf-8");a=s.index("Native manifest301:");b=s.index("\n\n## Последняя",a)
s=s[:a]+"""Native manifest302/app303: Root/task301/BALANCE-LOCATION-PART-UnitCore300; NEXT302 delegates recovery source to sameSHIPPING_CORE. Source indexes298+302, placementindex301. Actual recovery receipts300 + placement301 + newST/QC/load/depart302 + finalSTORE303 done both291/292. Buyer3=1+2, originalFFSHIPPED3 once, recoveredPALcurrentP0, historicalloss2/found2/net0. Do not rerun initial300/301 rollbackcases or sourcebirth. Context303 repeats/getters safe.
Restartrootserv303 afterfinalread/UI patches. Arch632/0cycles76. Next wholeloss assumptions ->partial/recurrent scoped history; residual nestedpacking/routelegal/ERP/hardware requires honest inputs."""+s[b:];out[p.as_posix()]=s
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
for inc in j["increments"]:
 if inc["id"]in["NI06.1","NI05.3"]:
  inc.setdefault("implementedSlices",[]).append("302-303 actualcorrectivefound2 existingST/QC/LOAD/DEPART/STORE; buyer1+2=3/originalFF3one/historyloss2-found2-net0/scopedNLwarm4.163ms")
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
qroot=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(qroot/"NI06.1/302_303_corrective_redelivery.md").as_posix()]="""# Qwen302–303 corrective redelivery
Read wiki/database/retailcase_ni061_recovery_redelivery_20261011.md/context302 and303_291/_292. Bothrealshipments/finalreceipts alreadycommitted/P0; no sourcebirth or initial rollback scripts.
ExactOP/body replays noquantity/FF/outboxrepeat; changedbody or new competingbind409. Foreign/current revokedWARE actor403 beforecache; currenttrip/cell/version/thermal/markings refuse. Native rollbackload restoresP2/units/clearsdispatch; Store rollbackno finalfact/customercredit.
Customer projection originalshipped3 once; initial1+corrective2 accepted3/unreceived0; historicalloss2/recovered2/net0. Beforefinal2 warehousefound doesn'tcreditcustomer. Duplicate/excess/foreignloss/dispositionmismatch rejects. Shared partial leaf no proportionalownership. SixoriginalQR birthhashes unchanged/no governmentACK.
UI no rawJSON; pendingOPID persisted beforeHTTP, actor/API/receipt fences; sourceindexes/bounded oneRO/read warm SQL. Separate executed tests fromstatic review/independent acceptance. Partial/recurrent loss intentionallynotaccepted yet.
"""
print(json.dumps(out))
