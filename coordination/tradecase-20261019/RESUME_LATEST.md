# Продолжение СНС/BLC — текущее состояние 23.10.2026

Владелец поручил продолжать до завершения всех спринтов совместно с Claude Code. Прежний предел19.10 18:00 отменён последующими поручениями. Все спринты ещё не завершены: T01 завершён; T02–T12 частичны. DONE.json со статусом complete не создавать. Работать дальше, не заканчивать обычным промежуточным отчётом.

## Сначала прочитать

Последний инкремент: resources-бланк/сверка/PDF1440/390 готов; полный UI внесения факта ещё открыт. API12832/session54441, UI3000/index-CdrWbWjh.js. Native6/6/6,31focused/gate/TS PASS;3concurrent emptyHU1234 дали одну квитанцию,1233/1234 DONE, parent PH23.68eb5dba.HU вA, stock/HARD неизменны. ClaudeC0155 безACK; CLIauthfalse/modelcalls0,17зарегистрировано. Детали и следующий блок — в последнем разделе этого файла и wiki/database/paper_task_version_20261023.md.

1. AGENTS.md и wiki/index.md (оглавление сокращено до63строк, старые ссылки сохранены в wiki/sources/wiki_index_history_20261023.md).
2. wiki/roadmap/tradecase_execution_20261019.md и wiki/roadmap/tradecase_acceptance_20261021.md.
3. Для следующего блока — coordination/retailcase-claude/TASK_C0155_PAPER_TASKS.md и последние сообщения канала.

Источник программы — снимок Google Drive revision27 от21.10: wiki/sources/tradecase_20261021.md, wiki-raw/tradecase_source_review_20261021/program.txt. TRADECASE — торгово-производственный СНС/BLC; RETAILCASE не подменяет его. При новой сверке Drive использовать установленный skill и connector. SAP/SAP_INTEGRATION не публиковать. Нового поручения на GitHub push/fetch/PR нет.

## Среда и сохранность

- CWD C:\projects\TMS. API8088: PID16532/session68199, serv.bat с TMS_API_RELOAD=0. После изменения Python нужен явный restart; после замены stateful Oracle-пакета тоже перезапускать API, иначе pooled сессия может один раз дать ORA-04068.
- Frontend3000: preview dist,330модулей, index--Ei2oZYN.js. Последний build и оба TS прошли. Итоговый gate: runtime/test-evidence/tradecase/2026-10-23/T12/quality-gate-inbound-final.txt —1231файл/0циклов/72долга/24теста/обаTS PASS. Encoding-inbound-final PASS.
- Oracle dev RABAEV@127.0.0.1:1521/orcl. Для local scripts задавать WMS_ORACLE_DSN явно: loader не разбирает DEFAULT_ORACLE_DSN в serv.bat. Код/SQL до apply фиксировать commit, fresh before SHA, rollback, wiki/database и live verify обязательны.
- Основные остатки:210564699=250/H0;215266197=1000/H0;219023232=10/H0;220793322=7/H5.225837931 не изменять. У220793322 CASE1168 выехала на33665, CASE1169 в ожидании на33666; не отменять их ради уборки.
- Собственный quality склад212476763=0/H0: все3тестовые единицы списаны. Старые QA не восстанавливать; новые создаются отдельно и отключаются. Исходящие SAP/CRPT остаются PENDING, не объявлять внешне подтверждёнными.
- Docker routing: OSRM5000/Valhalla8002 отвечают timeout; TCP listener не означает готовность. Docker Desktop engine unable to start. Start/restart уже пробовали, forcekill/WSL shutdown/пересборку карт не делать. Контролируемый кэш не считать реальным провайдером.

## Последние принятые участки

### T09: дополнительный заезд и скорость

C0154 RELEASE7f15288c получен; root исправил metadata fence/полный отпечаток/часовой пояс (561eb8e1), native extra-stop10/7/10,0ошибок.5групп настоящего HTTP/Oracle прошли: предложение/согласование/replay, изменённый запрос, повторное согласование, пробег/устаревание, запрет новых точек, роль и отзыв. Evidence T09/ES23bd3fdbf2fa.json. Тестовые рейсы33671–33674 выведены из работы, свои плановые операции/плечи убраны, история сохранена. UI28проверок1440/390: root JSON сохранён в T09/extra-stop-ui-root.json; исходный отчёт Claude восстановлен из git.

Transport metadata helper39b87b8f установлен7/8/7. Scope optimization871f8a48 установлен5/5/5: CASE проверяет существующий текущий склад перед прежним общим поиском; проверки фактических складов рейса не меняются.12полных JSON одинаковы, native median384→139мс; HTTP3/этап343→93мс. QA-акторы разные с теми же правами/складом/источником; не выдавать за нагрузочную пропускную способность. Evidence T09/TP2389cdbba1f0.json (до+DDL) и TP23e025cf4b0e.json (послеPASS). Первый HTTP после DDL получил04068/slowlog6354; факт сохранён, API перезапущен. См wiki/database/transport_scope_precheck_20261023.md.

Правила магазина и depot role-only приняты ранее; контролируемый road-refresh прошёл native/API/UI. Настоящий полный маршрут блокирован провайдером. Владельцу задан один существенный вопрос: сохранить15мин отдыха после120мин вождения и исправить пример13:55→14:10? Ответа пока нет. Действующее правило не менять без ответа.

### T10: входящий двор завершён как отдельный инкремент

Native yard_inbound: bcea2b84, verifier recovery4bff16f7. Первая apply скомпилировала всё, но SHA содержалCRLF; live текст совпал с нормализованным SQL. finish_failed_apply3/0, пустой rollback10/0, reapply12/0, INVALID0. После появления INBOUND истории rollback намеренно отказывается её удалять.

Входящий визит содержит1–200принятых SUPPLY и введённый сотрудником номер машины; ERP-поле машины не придумано. Версии источников сохранены в RRL_YARD_VISIT_SUPPLY; helper/guard разрешают запись только native владельцу визита. Native текущие owner-права проверяются на всех основаниях до replay и изменения. Изменившийся источник блокирует ARRIVE; старую квитанцию можно повторить при сохранённых правах. Количеств товарного остатка эти команды не меняют.

36реальных HTTP прошли: T10/YI23b8590eaf6c.json (3группы); первый35-запросный прогонYI2338ff7c3a0f сохранён. Две разные машины на одни ворота, межскладская машина, атомарный отказ частично занятого списка, смешанный SNS/BLC без второго owner, источник/роль/revoke прошли. Контролируемые SUPPLY metadata fixtures не выдавать за реальное сообщение SAP или фактический приезд машины. Все свои визиты закрыты, QA retired/owner0, исходные остатки прежние.

Настоящий UI1440/390 создал визит и пережил503, намеренно подставленный ПОСЛЕ native commit: reload+точный повтор вернули один visit_id. T10/inbound-live-ui.json и снимки,390 просмотрен. Тёмные поля/ссылка на поставки/локальная справка/контекст pending команды доведены. Два UI ожидания отменены. Direct INSERT/UPDATE связей запрещены; реальный общий Гант показал оба завершённых входящих интервала («приёмка»), T10/inbound-independent-verification.json. Повтор200hidden+visible после нового фильтра:187/218мс, YV2359eef0e3d1.json.27целевых unit PASS. Входящая товарная приёмка и резервирование интервала ворот этим не закрываются.

Старый yard уже прошёл native lifecycle и17scopedHTTP. Конкуренция одного визита: T10/YC235649bdfa4b.json. Mirror wiki/database/yard_inbound_20261023.md и tradecase_yard_visit_20261022.md.

### T11 и T12

Настоящее списание2EA+1EA в отдельных делах качества прошло через StockPosting: собственный склад0, units ISSUED, hold RELEASED, CASE POSTED. События6433/6442 CRPT PENDING, SAP outgoing PENDING. Карантин role-only: a78603bb/ff802519 по5/5/5; b7cf23bf replay7/6/7.11HTTP подтвердили исходную квитанцию после списания и нового hold; изменённый запрос409, отзыв MOVE/owner/WARE403. Mirror quarantine_role_scope_20261023.md, evidence T11/quarantine-*.json, quality-release-scope.json. Не пересоздавать физические единицы.

Task queue: тот же500строчный результат, SQL median200→78мс, scoped/revoke/retired проверены, no schema/index. MES пять старых падений были ошибкой stub: добавлено текущее чтение WARE и revocation test; производственный MES код не менялся.29focused PASS в b7cf23bf. Available-ST/background query614мс остаётся отдельным Codex/T12 backlog, не приписывать его91мс yard-команде.

## Claude и следующий шаг

Файловый канал coordination/retailcase-claude/{TASK.md,CODEX_TO_CLAUDE.md,CLAUDE_TO_CODEX.md,CLAUDE_STATUS.md}.17запросов зарегистрированы в coordination/tradecase-20261019/claude-budget.json. Это не новый жёсткий лимит владельца: позднее он разрешил больше делегирования. Регистрировать новый запрос до отправки.

Последний подтверждённый ответ Claude — C0154 RELEASE K0120. C0155 PAPER_TASKS передан, старт повторно подтверждён, ACK НЕТ. Не утверждать, что он работает. Владельцу дан короткий prompt прочитать TASK и начатьC0155. Root резервировал yard paths до приёмки; после сохранения инкремента сообщить release. Paper paths root ещё не редактировал. Можно независимо изучить существующие backend task/print/execute contracts и подготовить API readiness, не делать параллельный engine/ledger. При необходимости разделить: root backend/native, Claude бумажный UI/help/печать — явно зафиксировать в канале до изменений.

Далее продолжать исходные незакрытые T02–T12. Бумажный режим — следующий большой доступный блок; внешний SAP/СКМ, hardware и реальный pilot не считать выполненными. Не придумывать новые критерии/нормативы. Каждое изменение сохранять с доказательствами и анализом SQL. Не повторять уже прошедшие физические сценарии без связанного изменения или нерешённой ошибки.

Чужие dirty файлы не трогать: live_tare_handover.py, live_wave_case_filter.py, retailcase_roles_initial_review_20261014.md, slow_sql_review.md и старые coordination/report артефакты. Никакого git add all.

Последняя приёмка UI: после native commit подставлены503, затем403 на повтор (до native), затем native cached200; один visit_id и3одинаковых тела. sendPending получает признак прежней команды до save: новый первый отказ остаётся отказом, отказ доступа/валидации на повтор не теряет неизвестный первый исход. Уникальные JSON и снимки сохраняются по timestamp, latest — inbound-live-ui.json. Build index--Ei2oZYN.js. Последний SQL36HTTP:yard≤91мс, фоновыйavailable-ST614мс — Codex/T12 backlog.

Для C0155 уже найдены GET warehouse-tasks/{id}.task_signature и WarehouseTaskStatusRequest.expected_task_signature. Native STOCK_TASK_PLAN проверяет signature при compile и после блокировок через closure. Hash включает статус, назначение, ресурс/сеанс, количество, паллету/ячейки, документ: новый ledger не нужен. API_READY_C0155 ещё не написан. Назначение/START меняют signature; печать не является началом работы. Сначала изучить действующие resource assignment actions и native execution replay, затем дать Claude точную API readiness. Root paper paths ещё не редактировал.

23.10 latest: paper checkpoint c36fb430. Root принял реальный HU task1233 на пустом собственном PH23.68eb5dba.HU: старый бланк после START не выполнился, новая подпись complete200, exact replay та же квитанция, изменённое тело409. Найден и исправлен runner: только TASK_EXPECTED_SIGNATURE_CHANGED20890 — окончательный409 без3повторов; прочие CLOSURE_CHANGED сохраняют retry.7runner tests, finalgate PASS. Все protected balances прежние, own2124767630/H0. HU task DONE, stale journal0/open tasks0; пустое место осталось в своей новой QAячейке. Товарный сценарий/оборудование/UI не объявлять принятыми. API7196/session38085. Долгий фоновый available-ST631мс — следующий T12 разбор. Claude C0155 всё ещё без ACK; не дублировать его UI. Files/evidence: live_paper_hu_execution.py, T11/paper-hu-execution.json; изначальный503 сохранён.
23.10 — T12 available-ST: исследован повторный slow SQL631мс. Кандидаты CROSS APPLY совпали по данным/NULL, но дали регрессию склада397→4789мс; точные ключи не дали устойчивого выигрыша. Все продуктовые изменения этого исследования сняты до HEAD, в работающий API не попадали. Индексы/статистика/кэш не менялись. Доказательства и следующий шаг Codex: runbooks/available_sts_performance_20261023.md. Задержка остаётся открытой, T12 не закрыт.
## Последнее состояние: бумага/UI и продолжение

HEAD перед этим пакетом6da76903; новый код сохраняется отдельным локальным commit. API12832/session54441,8088 безreload. UI3000:333модуля/index-CdrWbWjh.js/CSSgzlU4ff9. Native optional guard14e919d7 установлен6/6/6, нет новых DDL. Root resources UI TaskPaperPanel/taskPaperModel/taskPaper.css/ResourceCard + static help/warehouse-task-paper.html: реальный timeline/read UI1440/390/print/PDF, native stale409, injected network/403clears, Enter/lowercase HEX,44px,0JSerror/overflow/POST. Code128PDF203dpiZXing PASS,1600pxpreviewchecksumFAIL (не использовать как доказательство печати); оборудование не принято.31focused/gate/TS/Viteexit0 PASS. Дробные .5/.000000001 изOracleTM9 сохранены точно. Имена товара/слотов в RO snapshot.

StockPosting.post: один немедленный неизменный повтор после TASK_EXPECTED_SIGNATURE_CHANGED на случай commit между receipt lookup и task read; повторный stale409. Остальной closure retry3 сохранён. Native3одновременных complete task1234→200/одинаковыйreceipt/oneoperation; это EMPTYHU, goods moves0. Его parent PH23.68eb5dba.HU вернулся вA;1233/1234 DONE, открытых own tasks0. Старый1233receipt сB возвращается после последующего перемещенияA; staleOp0, changedbody409/outcome_confirmed=false: сохранять исходное намерение. Основные250/0,1000/0,10/0,7/5 и own2124767630/H0 неизменны. Не повторять disposed quality receipt, не трогать225837931. Новых поступлений не делали.

Документ wiki/database/paper_task_version_20261023.md содержит evidence/ограничения. Ввод факта по бумаге UI ещё не внедрён: backend complete есть, следующие действия — изучить существующий terminal warehouse-task flow и передать туда printed signature, сохранив имеющиеся intent/scan/session controls; не создавать вторую систему команд. CASE/picking API и scoped deferred CASE bridge ещё не приняты, не объявлять готовыми по emptyHU. Root resources files по-прежнему закреплены. Claude C0155: admin queue навигация, review, authoring послеACK; местныйCLI loggedIn=false/no modelcall, used17зарегистрировано. Нельзя писать, что Claude работает. API_READY_C0155_READ.md — контракт; прочитать обновлённый TASK перед следующим блоком. T01done/T02–T12partial, не писать DONEcomplete, GitHub/SAP не публиковать. available-ST кандидат полностью снят, исходный файл восстановлен git restore, фактический код совпадаетHEAD; его631мс остаютсяT12.