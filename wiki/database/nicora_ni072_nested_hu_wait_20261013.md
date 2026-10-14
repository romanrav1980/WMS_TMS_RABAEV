# NI07.2 — целое вложенное HU в ожидание
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
