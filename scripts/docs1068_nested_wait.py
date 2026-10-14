from pathlib import Path
import json,hashlib
files={}
report="""# 25 · Целое вложенное HU в ожидание рейса

13.10.2026. Связанный функциональный участок NI07.2/NI04.1. Использована сохранённая собственная СТ MULTI987:4bb85f1f15; новые приходы и запасы не создавались.

## Что работает
Вся подготовленная СТ из двух CASE внутри одного верхнего HU переносится одним штатным HU-заданием. Исходные физические партии, HARD, версии CASE/fulfillment, дерево и принадлежность каждого места проверяет Oracle. Частичное дерево или чужие листья не допускаются. Смена рейса, загрузка, новая версия решения или изменение настроенной ячейки останавливают устаревшее исполнение.

Новый read/frozen-source helper подключает прежние HU_PLAN_MOVE/HU_TASK_COMPLETE. Одно Root-проведение планирования создаёт WHT и immutable WAIT_RUN/WAIT_PLAN; повтор возвращает окончательный APPLIED Root.result с outbox. Не создаётся второй запас/движение/SSCC-registry. Реальное проведение завершает прежний WHT/SYNC/journal/outbox и обновляет те же CASE/FF через единственный binder.

Автоматическое планирование не выдаётся за физическое сканирование. При исполнении обязательны верхний идентификатор, источник, назначение и1HU; частичная выборка unit_keys запрещена. Ресурсы проверяются действующей HU/task policy. Этот участок пока допускает всюСТ изCASE в одномTOP; mixedFULLPAL, разныеTOP, slots/capacity целевой ячейки ожидания и межскладская ревизия остаются отдельными задачами.

## Фактический результат
Существующий root HU994:4bb85f1f15 переупакован из исходных двухCASE12+8 в QI, затем задание1149 переместило1HU/20EA вQW4bb85f1f15. Native positive rollback планирования и движения, точные повторы, отказ частичного исходного дерева/частичной выборки — подтверждены. WHT1149 DONE/FACT1/SYNCED, journal2parties/20EA, P20/H20. CASE1131 CT12/FF12; CASE1132 CT7/FF7; root9. Обе исходные брони тары HELD, контрольный чужой склад6667491P20/H20 неизменён.

HTTP1067 подтверждает то же WHT/WAITread и точный cached planning/outbox5131. Браузер/скриншот31 показывает1HU и текущую ссылку состава. Физический сканер/оборудование, независимая приёмка и промышленная мощность не объявлены подтверждёнными.

## Исправленные реальные ошибки
Начальная компиляция1055: отсутствовал разделитель после замены SQL scalar; исправлен011 до операций. Первое планирование не содержало contract_version2, исправлен012. Затем trial показал timeout: имя переменной ST_NUMBER разрешалось как колонка, locked cursor выбирал лишние строки; исправлен013 на v_st_number/точные строки/NOWAIT→retryable20840. Также014 отличает ancestry scalar от PARENT_UID. Корректные trial rollback/committed move затем прошли. Эти ошибки не объявлялись PASS.

Первый committed plan вернул outbox, WAIT_RUN replay — pre-outbox projection. Исправлен015: неизменяемая промежуточная проекция сохраняется, повтор отдаёт final Root RESULT_JSON с текущими actor/right checks. Уже созданное1149 восстановлено поAPPLIED Root, повторный план не создавался.

Переупаковка обнаружила прежний CLOCK enum, не принимающий действующийHU_REPACK_SLOT. Отдельная миграция011 добавила actualcommand, сохранив Root/state/actor/held-anchor и создание clock только для пустогоBOX. NonBOX rollcage не получает фиктивныйBOXcycle. Неправильный '.75' в авторском измерении был исправлен на canonical'0.75' отдельным operation_id после отказа/полного отката; qty-парсер не ослаблялся.

## Структура и SQL
Миграции010/011 с fresh captures/checksum/pairedrollback применены в RABAEV/orcl, текущие USER_ERRORS[]/INVALID[] (1064). Миграционный rollback не запускался.

Существующая очередь извлечена в небольшой inventory TaskQueueRead. DEFER_WAITING теперь включает HU только через настоящий immutable wait-plan; точный фильтр source_doc_type=ST_DEFER_CASE сохранён. Деталь/строки показывают исходнуюСТ/решение/рейс. Старый1080 остаётсяDONE3EA. UI больше не говорит, что всеCASE/HU обязательно требуют ещё не реализованного решения.

SQL1064: bounded wait-read17.918ms/142buf; exact ST cursor0.662ms/4buf; wait-run lookups.845–3.439ms/3.7–10buf, insert4.863ms/56.5buf. Решение inventory: сохранять bound200nodes/lots/members и existing PK/ST keys/NOWAIT; mixed/high-leaf профилирование — отдельный owner backlog, не новый индекс безплана. Промышленное ускорение/невозможность всех deadlocks не заявляются.

Все18 спринтов ещё не завершены.
"""
files["reports/nicora/2026-10-13/25-nested-hu-wait-report.md"]=report
files["reports/nicora/2026-10-13/25-nested-hu-wait-evidence.json"]=json.dumps({"source":json.loads(Path("tmp/context1057.json").read_text(encoding="utf-8")),"read":json.loads(Path("tmp/read1064_nested_wait.json").read_text(encoding="utf-8")),"queue":json.loads(Path("tmp/read1066_hu_wait_queue.json").read_text(encoding="utf-8")),"http":json.loads(Path("tmp/http1067_hu_wait.json").read_text(encoding="utf-8"))},indent=2,ensure_ascii=False)
p="reports/nicora/2026-10-13/index.html";files[p]=Path(p).read_text(encoding="utf-8").replace("</main>",'<article><h2>25 · Целое HU в ожидание рейса</h2><p>Задание1149:1HU/дваCASE/20EA, P20/H20, текущиеверсии и штатныеRoot/SYNC/outbox.</p><a href="25-nested-hu-wait-report.md">Отчёт</a> · <a href="25-nested-hu-wait-evidence.json">Фактические данные</a><img src="screenshots/31-hu-waiting-completed.png" alt="Выполненное задание1149 на целое HU"></article></main>')
for d in("db/migrations/2026-10-13_ni072_nested_hu_wait/","db/migrations/2026-10-13_ni041_repack_clock/"):
 p=d+"checkpoint.json";v=json.loads(Path(p).read_text(encoding="utf-8"));v["state"]="APPLIED_DEV_VALID";v["evidence"]="reports/nicora/2026-10-13/25-nested-hu-wait-evidence.json";v["native_errors"]=[];v["native_invalid"]=[]
 files[p]=json.dumps(v,indent=2,ensure_ascii=False)+"\n"
# Prevent old code from handling an open new HU-wait task without its frozen decision guard.
d="db/migrations/2026-10-13_ni072_nested_hu_wait/"
preflight="""declare n number;begin
 select count(*)into n from RRL_ST_DEFER_WAIT_PLAN p join RRL_WAREHOUSE_TASK t on t.TASK_ID=p.TASK_ID
 where p.BASE_UOM='HU'and t.STATUS not in('DONE','CANCELLED');
 if n>0 then raise_application_error(-20886,'ROLLBACK_REQUIRES_RECOVERY_OF_OPEN_HU_WAIT_TASKS');end if;
end;
/
"""
files[d+"016_rollback_preflight.sql"]=preflight
files[d+"rollback.sql"]="@@016_rollback_preflight.sql\n"+Path(d+"rollback.sql").read_text(encoding="utf-8")+"\ndrop package RRL_ST_DEFER_HU_WAIT;\n/\n@@009_compile.sql\n"
p=d+"checkpoint.json";v=json.loads(files[p]);v["rollback_warning"]="unverified; preflight refuses open HU_WAIT tasks; completed history/caches retained; new helper dropped only after original callers restored"
v["sha256"].update({p:hashlib.sha256(t.encode()).hexdigest()for p,t in files.items()if p.startswith(d)and p.endswith(".sql")})
files[p]=json.dumps(v,indent=2,ensure_ascii=False)+"\n"
for p in("wiki/database/nicora_ni072_nested_hu_wait_20261013.md","wiki/database/nicora_ni041_repack_clock_20261013.md"):
 files[p]=Path(p).read_text(encoding="utf-8")+"\n## Checkpoint1068 — APPLIED_DEV_VALID\n\n"+report
p="wiki/requirements/nikora_delivery_v55/implementation_plan.json";v=json.loads(Path(p).read_text(encoding="utf-8"));v["planRevision"]=46
files[p]=json.dumps(v,indent=2,ensure_ascii=False)+"\n"
p="wiki/requirements/nikora_delivery_v55/implementation_plan.md";files[p]=Path(p).read_text(encoding="utf-8").replace("**Revision 45,","**Revision 46,")+"\nRevision46/checkpoint1068: nested allCASE oneHU waiting via existingRoot/HU tasks, actual1149DONE1HU/20EA/P20H20/CTFF12+7/queueUI/http/replay; clock slottedrepack actual bug fixed. FullNI07.2/NI04.1 remainin_progress; twoHUlevels/mixedplaces/targetslots/external gates next.\n"
for p in("wiki/requirements/nikora_delivery_v55/execution/active/ni07_2.md","wiki/requirements/nikora_delivery_v55/execution/active/ni04_1.md"):
 files[p]=Path(p).read_text(encoding="utf-8")+"\n1055–1068: original fullCASE-tree HU waiting Rootplan/move/immutable source; actual1149DONE1HU/20EA/P20H20/FF12+7/queue+HTTP+browser, report25. Existingclock now supports actualslottedrepack. Remainingmixed/multiTOP/deepcontainer/hardware/external/independent not closed.\n"
for p,note in [
("wiki/index.md","- [Checkpoint1068: целое HU в ожидание](database/nicora_ni072_nested_hu_wait_20261013.md): migration010/011VALID, actual1149DONE1HU/twoCASE20/P20H20/replay/queue/report25/screen31, plan46.\n"),
("wiki/log.md","\n- checkpoint1068 APPLIED_DEV_VALID: originalHu waiting1149DONE1HU/20EA, CTFF12+7/root9/P20H20, positive plan+move rollback/exactRootcachedoutbox; oldclock correctionVALID. Extracted taskqueue sparse immutable WAITbinding/currentSource exactfilters; report25/screen31/plan46. All18notcomplete, nextdeep/mixed/sourcecapacity functionality.\n")]:
 t=Path(p).read_text(encoding="utf-8");files[p]=note+t if p.endswith("index.md")else t+note
files["задания на проведения тестов/NI07.2/1068_вложенное_HU_ожидание.md"]="""# NI07.2 — целое HU в ожидание
Source1057/1149 DONE/currentP20H20 сохранён; никогда не перезапускать старые987/1002 factories. Проверить nativeRoot planning andmove, immutable source/ownCASEleaves/HARD/FF/currentSTdecisiontrip/WARE. Изменённый source/loaded trip/partialtree/unitkeys долженотклоняться атомарно. Replayplan долженвключать outbox5131, first+repeat одинаковы; WAITRUNprojection не переписывать. Пример25 author evidence не независимаяприёмка. CheckNOWAIT onlyneededTT/ST rows; deep multiplecontainers ещёпроверить, mixedFULLPAL/multiTOP/targetslots покаexplicitrefusal. Existingqueue family includes1HU but exactST_DEFER_CASE excludes1149. TarebookHELD andP20H20 preserved. Отчёт25/скрин31. Физическийscanner/Gov/SAP ACK не подменять локальным результатом.
"""
p="wiki/runbooks/nicora_active_work.md";files[p]="# Checkpoint1068 — продолжаем до всех спринтов\n\nНовое поручение владельца отменяет прежний20:00. Plan46/currentNI03.3; linkedNI07.2 nestedwaiting010/clock011 APPLIED_DEV_VALID, report25/screen31. Retained1057 used987+1002 stock NO factory: rootHU994:4bb85f1f15 nowQW4bb85f1f15/version9/twoCASE1131CTFF12+1132CTFF7; P20/H20, bothTARE987HELD. WHT1149 DONE1HU/SYNCED/2lots20EA; planHU1057.PLAN cachedfinaloutbox5131. DoNOT1057factoryphaseNEW/rerunread1062(single phase recovery only). Corrections011separator/012contractversion/013exactSTscalar+NOWAIT20840/014parent scalar/015finalcache, allErrors[]Invalid[]1064. OriginalclockactualHU_REPACK_SLOT1059 fixed.\n\nAPI1066 currenttaskqueue extraction/helperWAITbinding; actualHTTP1067/screen31. Fullgate session93480 pendingpoll; prior1044fullPASS, arch1065PASS6960/76. Encoding final afterlatestdocs pending. Browserorder1043Tab821857750 Chrome2 currentlywarehouseTask1149, orderReportFs1043. Report23–25/screens29–31 durable. No GitHub conditionalall not met. Nextfunctional deep outerHU waiting+bounded row contention, thenmixed/shared source gaps; use existingroot/goods20 only. NewhelperalreadyWaiting currentlyexplicitDEFER_HU_ALREADY_WAITING_NO_MOVE_REQUIRED; oldallnoqty alternatives remain future. Rollbackpreflight refuses open newHUWAIT before restoring oldcode/helperdrop; rollback untested.\n\n"+Path(p).read_text(encoding="utf-8")
print(json.dumps(files,ensure_ascii=True))
