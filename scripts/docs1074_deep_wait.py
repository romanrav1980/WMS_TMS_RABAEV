from pathlib import Path
import json,hashlib
files={}
report="""# 26 · Матрёшка и товар уже в ожидании

13.10.2026, продолжение NI07.2/NI04.1.

## Функциональный результат
Тот же существующий товар20EA упакован в пустую внешнюю паллету HU1069:4bb85f1f15. Дерево: внешнийPALLET → исходныйROLL_CAGE → дваCASE12+8 → исходные2партии. Новый товар/марки/заказ не создавались. ПрежниеHU_CREATE/ATTACH/PLAN_MOVE/TASK_COMPLETE переиспользованы. CASE parent-chain правильно достигает внешнегоRoot, одноTOP не считается как два машиноместа.

После штатного размещения на контроль создано одно задание1152 для возврата всегоTOP вQW. DONE1HU/SYNCED, journal2lots20EA, P20/H20; CTFF1131=14/14,1132=9/9; внешнийRoot3/внутренний12. Exactplan/move replay подтверждены. Это адресный native dev-case с заданными сканами, не реальное оборудование.

## Конкуренция
Отдельная сессия держала только строку собственного TT33635 FOR UPDATE без изменения данных. Новый план получил retryable20840 за0.191секунды, не создал WAIT_RUN/WHT и не изменил20/20. После освобождения строки тот же operation/request штатно создал план и исполнился. Подтверждены нужный ресурс/NOWAIT и атомарность данного отказа; это не доказательство отсутствия всех возможных deadlocks.

## Уже находится в ожидании
Новое обращение после фактического прибытия возвращает tasks[]/already_waiting[TOP], сохраняет immutable metadata receipt и точный repeat. Задания/stock-operation/версии не создаются и не меняются. Под metadata exclusive fence дополнительно запрещено использовать ID посторонней уже проведённой команды HU_CREATE/stock; actualcollision409/noWAIT_RUN подтверждён.

Native1072/HTTP1073: текущий deepTOP, DONE1152/SYNCED, no-move exactcached result — PASS. Перед перезапуском API один повтор вернул503 без захваченного nativecode; после штатногоrootserv.bat тот же сохранённый запрос прошёл. Причину503 не объявляем установленной; owner platform должен сохранять nativecode для подобных неизвестных отказов. Две неверные GET-попытки composition в авторском HTTPскрипте исправлены на наблюдаемый /composition; эти попытки не PASS/не складские операции.

Скриншот32 показывает реальное дерево/2партии/12+8/H12+8/ячейкуQW. Calculatedgrossunknown отображается как отсутствующий; фиктивный вес илиcapacity admission не заявляется.

SQL1072 operation-collision check5.287ms/16buf,2exec. Решение inventory: оставитьOPprimarykey/metadata fence и200treebound; high-leaf/multiTOP профилирование отдельнымticket. Новыйиндекс не требуется на этом свидетельстве.

Gate1067:24 architecture/tooling, обаTS, architecture696/0cycles/76debt PASS. Native after019Errors[]Invalid[]. Последние native extensions не менялиPython/TS; encoding после финальных документов отдельно.

Остаток: несколькоTOP или mixedFULLPAL/CASE однойСТ, slots/capacity waiting target, межскладскаяревизия и полная независимая/внешняя приёмка. Все18 не завершены.
"""
files["reports/nicora/2026-10-13/26-deep-hu-wait-report.md"]=report
files["reports/nicora/2026-10-13/26-deep-hu-wait-evidence.json"]=json.dumps({"deep":json.loads(Path("tmp/context1069.json").read_text(encoding="utf-8")),"already_waiting":json.loads(Path("tmp/context1072.json").read_text(encoding="utf-8")),"http":json.loads(Path("tmp/http1073_deep_wait.json").read_text(encoding="utf-8"))},indent=2,ensure_ascii=False)
p="reports/nicora/2026-10-13/index.html";files[p]=Path(p).read_text(encoding="utf-8").replace("</main>",'<article><h2>26 · Матрёшка и уже в ожидании</h2><p>Два контейнера/дваCASE/20EA/одноTOP; занятый рейс не приводит к зависанию и частичному плану.</p><a href="26-deep-hu-wait-report.md">Отчёт</a><img src="screenshots/32-deep-hu-current-composition.png" alt="Текущее дерево HU: контейнер в контейнере, CASE и исходные партии"></article></main>')
p="wiki/database/nicora_ni072_nested_hu_wait_20261013.md"
files[p]="""# NI07.2 — целое вложенное HU в ожидание
13.10.2026, checkpoint1074. Migration2026-10-13-010-ni072-nested-hu-wait **APPLIED_DEV_VALID**, Errors[]Invalid[]. Plan47, полныйNI07.2 открыт.

## Контракт
ВсяСТ из завершённых CASE находится в одном исходномTOP; дерево/CASE/FF/партии/HARD/currentWARE проверяютсяnative, не агрегируются разныеSKU/UOM. Bound200nodes/200lots/200members; чужой/частичный состав, другая активная задача, loaded/сменённыйрейс/новаяdecisionversion/config запрещены. MixedFULLPAL/несколькоTOP/slots-capacity target/межскладскаяревизия остаются отдельно.

Прежний Root HU_PLAN_MOVE атомарно создаёт1HU WHT и WAIT_RUN+immutable WAIT_PLAN. Planning не подделывает скан; actual HU_TASK_COMPLETE проверяетTOP/from/to/1HU и отвергаетpartialunits. ExistingHU/resource/placement/HARD/journal/outbox и единственный CASEFFbinder сохранены. Дополнительныйhelper владеет read/frozen-source contract, не stockwriter.

Движение/планирование повторно проверяет ST/decision/TT/config/source после locks. TT и ровно нужныеSTrows блокируютсяNOWAIT в согласованномпорядке; rowbusy возвращаетretryable20840. Невозможность всехdeadlocks не заявляется. Replay возвращает finalAPPLIED Root.RESULT_JSON сoutbox послеoriginalrequest/currentrolecheck; промежуточный WAIT_RUN не переписывается.

Alreadywaiting: под metadata exclusive fence current whole source/config/decision → immutable no-move receipt, emptytasks/already_waitingTOP. НикакихновыхWHT/stockcmd/versionchanges. Внутри того жеfence исключается конфликт сID постороннегоRootoperation.

## Actual
1057/1149: сохранённые987/1002 twoCASE12+8→wholeHU WAIT, DONE1/SYNCED/journal20/P20H20, positive plan+move rollback/exactreplays; TAREbookHELD/чужой20неизменён. Состояние на1064: root9/CTFF12+7. Теперьэтоистория.

1069/1152: emptyouterPALLET создан metadataкомандой, вложен исходныйROLL_CAGE/twoCASE/oldgoods20. Control→WAIT wholeTOP, exactreplay; Root3/inner12/CTFF14+9/P20H20. ОтдельныйTTrow holder:20840 за.191sec/no plan/stock, послеreleaseoriginalrequest прошёл. 1072alreadyWaiting/no newtask/nativecollision409; HTTP1073/currentbrowser/screen32. Всё dev/author, неhardware/независимая/Gov/SAP ACK.

## Исправления и восстановление
Capture1051/1053/1054+checksum/pairedrollback beforeapply. Initial1055 compile separator→011; missingcontractversion→012; STscalar columnshadow timeout→013/NOWAIT; ancestryscalar→014; finaloutboxcache→015; alreadywaiting→017/018; RootID underfence→019. Неуспешные этапы не отмечалисьPASS, source reused/no factorybirth.
Rollback016preflight отказывает, покаестьopen HU_WAIT; после восстановления originalcallers helperdrop+compile. История/caches сохраняются, rollbackнеиспытан.
Existing slottedrepack clock separately fixed [[nicora_ni041_repack_clock_20261013]].

## Экран и SQL
Queue extracted into inventory TaskQueueRead; sparse WAITbinding distinguishesHUwaiting while exactSOURCE_DOC filter retained. 1080oldDONE3EA unchanged. SQL sourceST.662ms/4buf, boundedwait17.918/142,OPguard5.287/16. Ownerinventory: bounds/keys/NOWAIT retained, high-leaf/multiTOPplanprofiling backlog, no unsupported index/prodclaim.
[Отчёт25](../../reports/nicora/2026-10-13/25-nested-hu-wait-report.md) · [Отчёт26](../../reports/nicora/2026-10-13/26-deep-hu-wait-report.md).
"""
p="wiki/database/nicora_ni041_repack_clock_20261013.md"
files[p]="""# NI04.1 — начало упаковки при слотовой переупаковке
13.10.2026, migration2026-10-13-011-ni041-repack-clock **APPLIED_DEV_VALID**, capture1058/checksum/pairedrollback, nativeErrors[]Invalid[]1064. Rollbackнеиспытан.

ExistingRRL_HU_PACK_CLOCK не принимал действующий HU_REPACK_SLOT (onlyHU_ATTACH/HU_REPACK), из-за чего actual1057 packing полностью откатился. Enumдополнен настоящей командой; Rootcontext/currenttransaction/IN_FLIGHT/actor/heldHUanchor и проверкаemptyBOX сохранены. NonBOX ROLL_CAGE не получает фиктивныйBOXclock; existingtare/link/measure validation unchanged.

Повтор сохранённого1057 source послеcanonicalmeasurement0.75 успешноупаковалCASE12+8 в тот жеRoot, P20H20/исходныеtareHELD. Не запускаласьfactory, новыеостаткине создавались. [Фактыиошибки](../../reports/nicora/2026-10-13/25-nested-hu-wait-report.md). PositiveemptyBOX slottedcycle отдельно отпройденногоROLL_CAGE, не объявляетсяпринятым этимслучаем.
"""
p="db/migrations/2026-10-13_ni072_nested_hu_wait/checkpoint.json";v=json.loads(Path(p).read_text(encoding="utf-8"));v["state"]="APPLIED_DEV_VALID";v["extensions_evidence"]="reports/nicora/2026-10-13/26-deep-hu-wait-evidence.json";v["native_errors"]=[];v["native_invalid"]=[]
files[p]=json.dumps(v,indent=2,ensure_ascii=False)+"\n"
p="wiki/requirements/nikora_delivery_v55/implementation_plan.json";v=json.loads(Path(p).read_text(encoding="utf-8"));v["planRevision"]=47;files[p]=json.dumps(v,indent=2,ensure_ascii=False)+"\n"
p="wiki/requirements/nikora_delivery_v55/implementation_plan.md";files[p]=Path(p).read_text(encoding="utf-8").replace("**Revision 46,","**Revision 47,")+"\nRevision47/checkpoint1074: actualdeepPALLET→ROLL_CAGE→twoCASE/1152DONE1HU/P20H20/ROWbusy20840 .191sec/unchanged no-move result. DeepnestedoneTOP gap addressed; remaining multipleTOP/mixedFULLPAL/targetslots/interWARE/independentexternal. Report26/screen32, all18 notclosed.\n"
for p in("wiki/requirements/nikora_delivery_v55/execution/active/ni07_2.md","wiki/requirements/nikora_delivery_v55/execution/active/ni04_1.md"):
 files[p]=Path(p).read_text(encoding="utf-8")+"\n1069–1074: actualtwoHUlevels/1152DONE1TOP20/P20H20/CTFF14+9/NOWAITTTrow.191sec/no partialplan; alreadywaiting no task/stockcmd/versions/exactcache/nativeRootIDcollision409. Report26/screen32, fullstatusin_progress. MultiTOP/mixed/targetslots/externalremain.\n"
for p,note in [
("wiki/index.md","- [Checkpoint1074: глубокое HU](database/nicora_ni072_nested_hu_wait_20261013.md):1152DONE1TOP/twolevels/P20H20, ROWbusy20840.191sec, alreadywaitingno writes/report26/screen32/plan47.\n"),
("wiki/log.md","\n- checkpoint1074: deepHU1069 source987 reused/outeremptyonly,1152DONE1TOP20/CTFF14+9/P20H20; exactboundedrowbusy20840/no partialplan and alreadywaitingmetadata no stock/task/versions, collisionRootID409. NativeVALID, HTTP1073afterrootrestartPASS (initial503codeunknown, ownerplatform diagnosticsbacklog). Report26/screen32/plan47, nextmultiTOP/mixed source scope, all18notcomplete.\n")]:
 t=Path(p).read_text(encoding="utf-8");files[p]=note+t if p.endswith("index.md")else t+note
files["задания на проведения тестов/NI07.2/1074_глубокое_HU_и_ожидание.md"]="""# NI07.2 — deepHU/no-move
Сохранённый1069 outerHU1069:4bb85f1f15/innerHU994/twoCASE14+9/20EA P20H20,1152DONE. Не повторятьfactories987/1002/1057/1069/1072 NEW. Cachedrequest изcontext1072 допускаетexactreplay; новоеоперационное действие толькоявноизолированнымсценарием. Проверитьточнуюparentchain, no leafdoubling, permissions/currentWARE/decision/trip/config, bounded resource rowcontest and20840 retry withoutpartialplan. УжевWAIT→tasks[]/alreadywaitingTOP/unchangedstock+versions. ExistingRootID differentkind cannotbe reusedmetadataunderfence. REPORT26 authorproof не независимыйPASS. MultiTOP/mixed/targetslots ещёотдельно; realhardware/Gov/SAP notconfirmed.
"""
p="wiki/runbooks/nicora_active_work.md";files[p]="# Checkpoint1074 — непрерывно до всех спринтов\n\nПрежний20:00 отменён новымпоручением. Plan47/currentNI03.3; all18notcomplete/noGithub untilactualall. API1073 currentafterlaterDDL, originalrecords preserved. Migration010 nestedwait now017/018alreadywaiting +019underfenceRootIDcollision, APPLIED_DEV_VALID/nativeErrors[]Invalid[]1072. RootCore unchanged commandfamilyHU_PLAN_MOVE/HU_TASK_COMPLETE, no stockfactory/copies/agents/goals.\n\nCURRENT retained goods987:20EA/P20H20/WARE5062399. OuterHU1069:4bb85f1f15 VERSION3 atQW4bb85f1f15; innerHU994:4bb85f1f15 VERSION12; CASE1131CTFF14/CASE1132CTFF9; oldTAREbookHELD. Context1069DONE: original1151control task then1152waittaskDONE1HU/SYNCED/2lots20, Rootplan/move exactreplay. Rowholder ownTT33635 NOWAIT20840 .19086sec/no plan/no stock, afterrelease sameoperation succeeded. Context1072DONE: metadataAlreadyWaiting emptytasks/no stockcmd/task/versionchanges; unrelatedRootHU1069.CREATE collision409/noRun. DoNOTrerun factories/NEW stages of987/1002/1057/1069/1072, read1062 one-shot recovery no longer valid.\n\nReport25 historical root9/CTFF12+7 and1149; report26 currentdeep3/inner12/CTFF14+9 and1152, screens31/32. HTTP1073initial503 no nativecode captured; afterrootrestart cachedrequestPASS. ScriptGETinitialbadpaths404/405 corrected actual /api/warehouse-hus/composition (notPASS). Nativecode diagnostics503 backlogownerplatform. Fullgate1067PASS24/bothTS/arch6960/76; latestnative extensions noPy/TSchange. Encoding afterlatestdocs pending.\n\nBrowserorder1043Tab821857750 Chrome2 nowHU1069?identifier=...#huComposition, orderReportFs1043, screens32realcurrent. Reports01–26/screens01–32 durable. Nextfunction: multiTOP/mixedprepared ST waiting; existing HU planning onlyone root, dirty nested Root transaction prohibited. Need reuseoriginal singleRoot multi-domainplanning/child frozen sources or explicitly separate atomicper-rootplans with durable aggregate recovery, never call multipleRoot aftermetadatawrites. 80%functionality; no broadload/Qwenruns. Existing all-CASEoneTOP complete extension; targetslots/capacity and interWARE remainexplicitrefusal. No final untilactualall; budget/context compaction continue.\n\n"+Path(p).read_text(encoding="utf-8")
print(json.dumps(files,ensure_ascii=True))
