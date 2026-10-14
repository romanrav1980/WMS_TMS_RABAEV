from pathlib import Path
import json
out={}
page="wiki/database/retailcase_ni081_warehouse_depot_20261011.md"
out[page]="""# База отправления существующего склада
285 NI08.1, 11.10.2026. Склад использует ссылку на существующий RRL_ADDR, без нового справочника адресов/складов. RRL_WARE_DEPOT_HISTORY хранит неизменяемые версии, причину, actor, OPID, полный запрос/результат. Native RRL_WARE_DEPOT_API проверяет текущий активный RUSERS/right/WARE до и после ожидания общего CONFIG6. warehouse_settings_edit добавлено в существующий METADATA_TX allowlist; отдельного порядка блокировок нет. Чистая транзакция, одна версия, журнал+настройка без внутреннего COMMIT; повтор OPID проверяет фактический payload/actor/WARE. Resolve ждёт тот же mutex перед NOT_RECORDED. Прямой DML закрыт guard; reason500 CHAR сохраняет русские причины.
 
Native TIME sourceV4 включает warehouse_origins и текущие координаты ссылки; ROUTE наследует snapshot. Изменение ссылки/координат делает старое согласование устаревшим. Физическая история не отменяется и не переутверждается автоматически.
 
Существующий OR-Tools использует настроенную базу для расстояний и направленного времени. Один склад — его база; несколько складов пока явно centroid, полный multi-depot не объявлен. Cache читается в одном snapshot, максимум201 адрес (200 остановок+база). Неизвестные road cost остаются оценками; physical_site_verified=false. Старые savings/cluster не приобретают выдуманное точное расписание.
 
Панель встроена в warehouses.html: чтение версии, адрес/причина, явная очистка, durable intent API+actor до отправки, точный повтор/ожидаемый resolve. Самостоятельного второго пульта нет.
 
Авторские результаты: own9807 положительная настройка существующего геокодированного адреса под outer rollback меняет sourceHash own33564; rollback точно восстанавливает источник/настройку, protected P20H20. Фактические конкурентные публикации пустой настройки дали200/409; один журнал, повтор/resolve RECORDED, другое содержимое409. tmp/context285.json сохраняет OPID. Реальная база RETAILCASE не угадана: текущая настройка9807 null. Gateway403. Architecture624/0cycles76; frontend typecheck passed. Независимый Qwen/browser и реальная база/страна/окна/нормы водителя остаются открыты.
 
SQL решение: сохранить warehouse/version unique и адресный справочник; получить профиль конкретного запроса после итогового case. Canonical manifest содержит схему/пакет/метаданные/sourceV4; на ACTIVE применять только версионные скрипты. Rollback сначала отвергает непустую историю, потом восстанавливает прежние TIME/metadata bodies.
"""
for path,line in [
("wiki/index.md",f"- [База отправления склада]({page.removeprefix('wiki/')}):285 existing-address reference, native version/CONFIG6/sourceV4, real concurrent200/409; depot unset pending owner."),
("wiki/index.md","- [Проект базы отправления](database/retailcase_ni081_warehouse_depot_design_20261011.md):285 reference boundary and current route invalidation."),
("wiki/log.md","2026-10-11:285 native warehouse depot reference/version/immutable history CONFIG6/currentWARE/exactreplay+awaitedresolve; metadata existing allowlist expanded warehouse_settings_edit. TIME sourceV4 origin+coordinates invalidates changedbase oldapprovals. Actualown9807 positive config outerrollback/exactrestore/P20H20; realnull-setting concurrency200/409/replay/resolve/collision. ExistingORtools configuredorigin/cache201 same snapshot; multiscope explicitcentroid. Existingwarehousepanel durableintent. Architecture624/0cycles76, frontendtypecheck passed. RealRETAILCASEhub/driverlaw/Qwen notclaimed."),
("wiki/runbooks/retailcase_active_work.md","Latest285 Native TIME sourceV4/WARE_DEPOT history+API and METADATA permission; app285 existingwarehousepanel/configuredORtoolsorigin. tmp/context285.json actualone null-setting9807 version1, no guessedrealbase. Positive configuredgeocodedorigin onlyouterrollback, exactsource restoration/P20H20. Original33564route/timeold stale, preserve. Next shared road/storewindow admission; awaiting country/base/regulatory config owner."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md","11.10.2026:285 Реализована версионная база отправления склада (ссылка на существующий адрес), текущий sourceV4/прежний OR-Tools/панель складов. Конкуренция200/409, exact replay/awaitedresolve, positiveconfig rollback. RealRETAILCASE depot не угадан, multi-depot/window-law admission и independentQwen открыты.")
]:out[path]=out.get(path,Path(path).read_text(encoding="utf-8"))+"\n"+line+"\n"
out["wiki/index.md"]=out["wiki/index.md"].replace("current native280/app284/","current native285/app285/")
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
next(x for x in j["increments"]if x["id"]=="NI08.1").setdefault("implementedSlices",[]).append("285 configuredexistingwarehouseorigin/nativeversion-history/currentsourceV4/oldORtools cache201/singleWARE/durableexistingpanel, concurrent200-409")
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));j["packages"].append("RRL_WARE_DEPOT_API")
print(type(j["components"]).__name__,file=__import__("sys").stderr)
if isinstance(j["components"],list):j["components"].append("../2026-10-11_ni081_warehouse_depot/002_api.sql")
else:j["components"]["RRL_WARE_DEPOT_API"]="../2026-10-11_ni081_warehouse_depot/002_api.sql"
j["startup_scripts"].append("../2026-10-11_ni081_warehouse_depot/001_schema.sql")
j["additional_scripts"].extend(["../2026-10-11_ni081_warehouse_depot/007_metadata.sql","../2026-10-11_ni081_warehouse_depot/005_time_body.sql"])
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
p=Path("db/migrations/2026-10-11_ni081_warehouse_depot/rollback.sql")
out[p.as_posix()]=p.read_text(encoding="utf-8").replace("@@004_before_time_body.sql","@@004_before_time_body.sql\n@@006_before_metadata.sql")
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[(root/"NI08.1"/"285_warehouse_depot.md").as_posix()]="# Qwen285\nПроверить currentactorWARE до/после CONFIG6, expectedversion concurrentwinner, OPID фактический payload, no guessedRETAILCASEhub. SourceV4 includeslatestorigin+coords, oldapprovals stale/historyretained. Positiveconfig авторunderrollback; actualnullsettingonehistory200/409, retry/resolve RECORDED/collision409. ExistingORtools singleWARE hub/201cache/directionalprofile; multiWARE centroidexplicit, unknownspeedbasis explicit. UI durableAPIactor/retry/resolve +stalegeneration. Не объявлять physicalverified, законный режим водителя или independentacceptance. Rollbacknonemptyhistory refuses BEFORE package revert.\n"
out["db/migrations/2026-10-11_ni081_warehouse_depot/008_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-285-warehouse-depot-source-v4'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Configured existing warehouse origin and sourceV4',sysdate,user,'db/migrations/2026-10-11_ni081_warehouse_depot/002_api.sql','db/migrations/2026-10-11_ni081_warehouse_depot/rollback.sql','APPLIED','CurrentWARE CONFIG6 version history exactreplay; sourceV4 origins; actualpositive outerrollback +nullsetting concurrent200/409/replay/resolve. No guessedrealbase or qty.');
commit;
"""
print(json.dumps(out,ensure_ascii=True))
