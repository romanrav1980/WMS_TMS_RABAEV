# AK06-A: scoped TASK_ASSIGN / TASK_START

Статус: APPLIED native + actual HTTP для ordinary STOCK одного actual склада; fixture canonically cancelled/retired, история сохранена. [[retailcase_task_scoped_complete_20261015]], [[../components/retailcase_task_scoped_write_increment_20261015]].

## Проверенный исходный путь

Router assign/start требует flat warehouse_task_execute. Python run_existing_task_action открывает RRL_STOCK_METADATA_TX.begin_change с тем же flat правом, сериализует domain затем TASK; ACCESS.assert_scope проверяет legacy RUSERS.WARE_ID. RESOURCE_POLICY требует flat execute actor/target и сохраняет session/shift/type/qualification/equipment/warehouse/physical-step guards. Native-only роль упирается во все эти слои, одного identity router недостаточно.

Существующий metadata эффект: RRL_WAREHOUSE_TASK status/assignee/resource/session/equipment/start clocks; RRL_RESOURCE_FACT_EVENT; при START SESSION.CURRENT_TASK_ID; зеркальный статус RRL_PICK_WAVE_REPLENISH_TASK либо RRL_PICK_WAVE_TASK. Ни stock writer, ни goods quantities не нужны. Существующий canonical TASK_PLAN.signature уже включает status/assignment/resources/start clocks; алгоритм не копируется.

## Рассмотренная семантика

Только ordinary STOCK task, обе actual FROM/TO cells через RRL_CELLS и согласованность сохранённых WARE_ID; HU_CONTENT_VERSION/CONTAINER/CASE-linked/MES-production исключены из нового пути. Старые legacy действия и FORCE остаются отдельным прежним путём. View не разрешает назначение либо старт.

SELF execute разрешает START уже назначенного себе задания. ASSIGN с SELF допускается только как подтверждённое неизменное назначение себе с прежними итоговыми resource/session/equipment. Захват ещё неназначенного задания требует warehouse_task_assign на каждом actual warehouse с owner=NULL плюс target warehouse_task_execute на каждом actual warehouse. Иной target дополнительно требует resource_dispatch_manage на каждом actual warehouse. Новое scoped назначение не переassign чужого уже assigned task и не выводит FORCE из scope. Target active RUSERS обязателен.

RESOURCE_POLICY остаётся единым владельцем physical/session/qualification правил. Узкое новое pure authorization helper разрешает только ASSIGN/START ordinary scoped branch; остальные правила выполняются прежние. Mutation и replay повторно проверяют current role/actualWARE; отзыв между ожиданием lock и выполнением закрывает доступ под ACCESS_REV SHARE.

## План файлов

Версионированный комплект db/migrations/2026-10-15_warehouse_task_scoped_assignment: exact before snapshots ACCESS spec/body и TASK_RESOURCE_POLICY body; отдельный RRL_WTASK_ASSIGN_VERSION без ALTER TASK; AFTER ROW derived trigger; append-only metadata receipt table; новый RRL_WTASK_ASSIGN_API spec/body; guards/apply/rollback/verify/checkpoint. RRL_STOCK_POSTING_API, CASE/ASM packages и TASK_PLAN.signature не меняются.

API/resources domain: contracts_task_assignment.py, infrastructure/task_assignment_commands.py, api/task_assignment_routes.py либо маленький адаптер существующих двух routes; public exports. Legacy service не расширяется новым native сценарием. Inventory detail projection через публичный read контракт добавляет assignment_version; существующий task_signature сохраняется. Новый явный request требует operation_id, expected_task_signature, expected_assignment_version, target/session/resource/equipment. Actor только authenticated identity; неизвестные поля не становятся native authority. Отказ новой команды не переключается на legacy fallback.

## Version, receipts, transaction

ASSIGNMENT_VERSION читается из sidecar RRL_WTASK_ASSIGN_VERSION: у старых заданий без строки baseline0. Новое TASK INSERT создаёт clock0; первое реальное изменение старого задания создаёт clock1, далее только old+1. AFTER ROW trigger отслеживает status/assignment/resources/start/finish clocks и source identity/quantity. Любой legacy Python или Stock writer проходит trigger; возврат к прежним полям не возвращает прежнюю version (ABA).

Выбран sidecar, поскольку ALTER RRL_WAREHOUSE_TASK каскадно затрагивает 60 зависимых объектов, включая 10 package specs. Base TASK row всегда блокируется раньше clock; AFTER ROW выводит version без повторного чтения mutating TASK. RRL_WTASK_VERSION_API доступен только двум названным triggers через ACCESSIBLE BY, разрешение DML связано с точным task и текущей transaction. Прямой DML clock и DELETE clock отвергаются. FK без ON DELETE CASCADE сохраняет историю: tracked TASK удалять нельзя, ID не переиспользуется и clock не обнуляется.

Read-only аудит USER_SOURCE не нашёл прямых native PACKAGE BODY DELETE FROM RRL_WAREHOUSE_TASK. Старый scripts/warehouse_task_scoped_complete_smoke.py динамически удалял собственное временное TASK; после появления clock такой cleanup должен стать явным metadata retirement с сохранением истории, а не удалением version. Это намеренное ограничение QA cleanup, не изменение штатной отмены.

Scoped обход flat checks в RESOURCE_POLICY доступен только внутри доверенного нового metadata owner: точные TX/task/action/actor/target в RRL_WTASK_ASSIGN_CTX плюс повторный pure current-scope helper. Обычный legacy вызов RESOURCE_POLICY сохраняет старые flat и FORCE правила. Новый writer требует явную actual session, квалифицированный resource и shift в одном из actual FROM/TO warehouses.

Начало: strict begin_plan, затем ACCESS_REV SHARE, RELEASE/CONFIG policy fence и WAREHOUSE.METADATA resource, current release/auth, domain row, TASK row, resource session. Полный набор planned locks определяется до записи. Ни metadata write перед clean begin_plan, ни дополнительный stock writer.

Exact request immutable actor/body/hash; operation key не переиспользуется и не переписывается. Mutation metadata+event+mirrors+receipt в одной caller-owned transaction. APPLIED exact replay возвращает исходную квитанцию только после current native authorization, без повторного event/clock/version. После последующей смены assignee SELF не раскрывает исторический результат. Новый op со stale signature/version отклоняется. Ожидаемый domain409 после auth/fences сохраняется как неизменный REJECTED receipt; изменившийся позже источник не превращает старый запрос в действие. Auth/revoke/unknown DB errors не создают ложного definite receipt.

## Acceptance plan

Native rollback ordinary existing QA task: native-only warehouse assign/SELF start; unchanged-id replay; body conflict; expected version/signature conflict; two concurrent same request; revoked while waiting fence; active-target/session/shift/qualification/equipment/other-task/other-CASE/wave-release denials. Mixed warehouses require execute/assign on both actual cells; executeA+viewB fails. SELF cannot claim unassigned or rebind assignment resources, dispatcher cannot use target without current execute, retired actor denied. Legacy admin assignment/start remain unchanged; new native HU/CASE/MES denied.

Original task and P/H/stock versions compared exactly, no quantity writes or stock commit. Metadata fixture, если потребуется для concurrent proof, отдельно ограничивается и согласуется с root до commit; immutable receipts/history не удаляются как cleanup. Проверить finished native sources/ledger/USER_ERRORS/global INVALID, focused unit/actual HTTP, slow SQL/audit, encoding и общий quality gate. Rollback DDL допустим только при пустых receipt и clock tables; любой version/receipt history требует forward recovery. История не уничтожается.

## Подготовленный комплект и границы доказательства

Комплект содержит before8 exact snapshots (ACCESS spec/body, RESOURCE_POLICY body и пять неизменных зависимых bodies), after15 source SHA guards, схемы/guards, apply/verify/rollback/rollback_verify/checkpoint. verify выполняется до APPLIED ledger, проверяет source, constraints/FK/indexes, trusted context binding и global INVALID0. Восстановление затрагивает только три изменённых старых source и штатно recompiles пять неизменных dependents; stock writer source не меняется.

Read-only before guard PASS для LF и CRLF. Первое сравнение HU_TASK выявило только пять потерянных snapshot-helper trailing LF (13850 live против13845 snapshot), функционального drift нет; исправлено сохранением точного USER_SOURCE после удаления CR, без stripping trailing LF. ALL_CONTEXT показывает только контексты текущей сессии, не используется как доказательство регистрации: verify_binding выполняет безвредный probe через trusted package и очищает его.

На момент PREPARED: native DDL/runtime assignment acceptance ещё не выполнены, Python identity-only router только подготовлен, UI не менялся. Новые маршруты resources public: task_resource_router, task_resource_service, build_task_resource_service; root композиция подключает их после native приёмки. Dedicated resource-context даёт server-derived version/signature, старые assign/start/complete endpoints не переключаются на новый путь автоматически.

## Применённый prefix и последующая проверка физического склада

Root применил DDL, recompiles и exact16 source checks; первый запуск остановился до ledger на WTASK_INDEXES, поскольку исходный verifier посчитал два служебных LOB indexes вместе с тремя PK/task indexes. Исходные apply.sql/verify.sql сохранены. complete_after_index_verify_fix.sql выполнил6 statements/0errors: corrected full verify/index identities/trusted-context probe, USER_ERRORS0/global INVALID0 и ledger APPLIED. DDL не повторялся, история не удалялась. Для нового чистого развёртывания выбран apply_verified.sql, проверка verify_index_fix.sql; затем отдельный forward ниже.

Исторические unseeded TASK также защищены BEFORE DELETE/UPDATE OF TASK_ID guard: удаление и настоящая смена ID запрещены, no-op same-ID update разрешён. Это закрывает ABA до первого sidecar clock. Адаптирован прежний QA cleanup: canonical cancel/close/retire, сохранение Task/version/event/access audit.

Отдельный APPLIED7/0 комплект db/migrations/2026-10-15_warehouse_task_session_warehouse заменяет один predicate нового metadata owner: fc.WARE_ID=tc.WARE_ID и resource.WARE_ID=shift.WARE_ID=fc.WARE_ID. Scoped rights продолжают проверять обе actual стороны до domain effect; cross-WARE physical task workflow не поддерживается этим ordinary increment и отклоняется WTASK_PHYSICAL_WAREHOUSE_REQUIRED. Legacy/MES/Stock writer не меняются. Новая actual session требует единого физического склада. STARTED_AT_INSTANT — SYSTIMESTAMP с offset; сохранённый STARTED_SHIFT_TIME_ZONE использует прежнюю интерпретацию DB SESSIONTIMEZONE, это не доказанная timezone склада.

## Фактическая приёмка и ограничения

Изолированный fixture: новые MANUAL/PUTAWAY TASK1188/1189, synthetic SOURCE_TASK_ID равен собственному новому ID, qty1 без reservation/stock posting; resource62 REACHTRUCK/equipment, PUTAWAY qualification, shift67/session58 и два новых QA actor. Метаданные staged после caller-rollback preflight. Первый preflight отверг одинаковые отсутствующие SOURCE_TASK_ID по старому unique TASK_U2 и целиком откатился; source identity исправлен в fixture, business schema не ослаблялась. Старое REVOKE назначение не реактивируется: ошибочная попытка восстановления дала VERSION_CONFLICT без изменения данных, восстановление выполнено новым canonical grant с сохранением старой revoke history.

- Native ASSIGN13 checks и START6 checks: actual native-only actor, metadata/event/clock/receipt effect внутри caller rollback, stale version/signature, session identity, SELF запрет unassigned claim, executeA+viewB отказ, обе права не разрешают unsupported cross-WARE physical workflow, old unseeded TASK identity/ABA. Два source-readback checks повторяются между стадиями; эти группы не выдаются за19 уникальных сценариев.
- Actual HTTP28 вызовов: ASSIGN12, START10, revoke/restore3 и HU/MES/CASE3. Два concurrent fresh ASSIGN дали одну durable mutation/version1 и одинаковую квитанцию; START version2. Exact repeat/GET, changed-body conflict с outcome_confirmed=false, forbidden browser actor, чужой receipt и неизменные старые flat endpoints проверены. Старый REJECTED intent остаётся тем же отказом после последующего START.
- Actual Oracle revoke fence6 groups: V$SESSION показал SID248, enq: TM - contention, blocking_session58, P2 совпал с RRL_ACCESS_REV object86939. Canonical revoke committed до продолжения waiter; current native authority повторно отказала перед чтением original receipt. Новый canonical SELF grant восстановил только exact original replay. Task/stock/clock/event/receipt не менялись.
- Physical guards2: resource и shift в разных складах, revoked PUTAWAY qualification. Только новые QA metadata временно committed через существующих владельцев и восстановлены в finally; сам command/REJECTED receipt caller-rollback.
- History/capability guards5: DELETE/UPDATE receipt, DELETE clock, прямой вызов derive вне ACCESSIBLE BY и подделка trusted context отвергнуты без изменения истории.
- Два canonical cancel caller-rollback preflight PASS; затем canonical cancel commit обоих новых TASK с FACT0, close session, revoke native grants и явный retirement собственных actor/resource/equipment/shift/cell. TASK1188 CANCELLED/version3 и1189 CANCELLED/version1, session58 CLOSED/currentTaskNULL, actor deleted/resource inactive. Три metadata receipts, clocks и все events/access audit сохранены. Native source16 exact/USER_ERRORS0/global INVALID0 и обе APPLIED ledger подтверждены независимо.

Товарного TASK_COMPLETE/StockPosting исполнения этим инкрементом не было. Parent lot остаётся23/H1/version12, returned child1/H0 в QIP, нулевые старые location rows неизменны. AggregateP24/H1; H1 принадлежит отдельному CRES WAVE569/PLAN2200, не этим metadata TASK. CASE1136/1138, main ASM, scale и prefix не изменялись. Это native/software resource model, не испытание физического ричтрака.

Доказательства: [каталог отчётов](../../reports/retailcase/2026-10-15/task-assignment/), [final verification](../../reports/retailcase/2026-10-15/task-assignment/final-verification.json), [revoke wait](../../reports/retailcase/2026-10-15/task-assignment/revoke-wait.json), [canonical cleanup](../../reports/retailcase/2026-10-15/task-assignment/cleanup.json). Повторный stage не создаёт новый fixture поверх retained history автоматически.

Python19 focused tests PASS: строгий authenticated actor, correlation/body hash, malformed ACK rollback503, resource IDs>0, aware started_at_instant, definitive REJECTED commits versus unconfirmed exception. Общий gate на этой стадии: architecture1046/0cycles/debt72 +24 tooling/adminTS PASS, terminalTS сначала остановился на missing CaseWorkApp, после появления параллельных UI файлов повтор достиг новых case-work/contracts.ts (DTO narrowing) и journal.ts (Promise<Promise<T>>). Это отдельный UI owner; global acceptance до исправления не объявлен. Последняя architecture проверка1055/0cycles/debt72, tooling24/adminTS PASS. Baseline не расширялся.

## SQL/SKV после фактических кейсов

[SQL review](../../reports/retailcase/2026-10-15/task-assignment/sql-review.json):25 own TASK/receipt HTTP calls сопоставлены Oracle и local FINISHED audit, max243ms; три отдельных unsupported-source HTTP calls находятся в своём отчёте. RRL_SQL_SLOW_LOG latest1200: только ожидаемые operation conflicts51/35ms и revoke denial8ms. V$SQL execute_command39 calls/1598.352ms total, mean40.983ms; receipt3.291ms mean, context7.776ms, version lookup0.108ms native mean. Это небольшая DEV выборка, не P95/load/pilot capacity.

Решение: дополнительный индекс не нужен — TASK/version/operation PK и task-actor-recorded index ограничивают новый путь. Existing other-IN_PROGRESS/CASE physical-work COUNT сохраняют actor predicates; resources/platform проверит планы длинной истории при resource/Gantt pilot load. Intentional revoke lock wait является concurrency evidence, не SQL regression. Реальный warehouse timezone и cross-WARE physical task owner остаются отдельными задачами; старые MES/legacy quantity guards не ослаблены.
