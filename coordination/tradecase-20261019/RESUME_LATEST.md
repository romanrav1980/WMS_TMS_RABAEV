# Продолжение СНС/BLC — текущее состояние 23.10.2026

Владелец поручил продолжать до завершения всех спринтов совместно с Claude Code. Прежний предел19.10 18:00 отменён последующими поручениями. Все спринты ещё не завершены: T01 завершён; T02–T12 частичны. DONE.json со статусом complete не создавать. Работать дальше, не заканчивать обычным промежуточным отчётом.

## Сначала прочитать

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
