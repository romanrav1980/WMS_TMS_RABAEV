# CASE CLOSE по текущей области исполнителя

15.10.2026. **APPLIED; положительный ordinary 1EA PICK → CLOSE → canonical RETURN и независимый readback PASS.** Узкий metadata-инкремент inventory; не закрывает binding, ASM или shipping-QC.

Применён v2-комплект с исправленным различением RAW USER_SOURCE и нормализованного source hash:10 statements/0 errors,2 exact source, global INVALID0. Первоначальные файлы и before evidence сохранены. Четыре native/Python caller-rollback запрета на CASE1139 прошли: версия, незавершённые строки, чужое задание1138, отсутствующий actor. Положительный отбор/закрытие/канонический возврат затем принят отдельным журналом ниже. Доказательства DDL: [root apply](../../reports/retailcase/2026-10-15/case-scoped-close/root-apply.json), [readback](../../reports/retailcase/2026-10-15/case-scoped-close/independent-readback.json).

## Контракт

`POST /api/case-pick/tasks/{task_id}/close-current` принимает только `operation_id` и `expected_content_version`. Actor берётся из текущей API-сессии. Новый identity-only маршрут не обходит native права и не подменяет legacy маршрут close-pallet.

`RRL_CASE_LIFECYCLE_API.begin_close` сначала проверяет текущую область, затем вызывает strict begin_plan, берёт RRL_ACCESS_REV SHARE и прежние RELEASE/STOCK, CONFIG/WAREHOUSE X, WAREHOUSE.METADATA fences. Wave/CASE/actor resources объявлены до фактических row locks. Порядок фактических блокировок: wave → CASE → actor. Закреплённые TX/task/actor globals и фактически удерживаемые policy/ROW keys проверяются при каждом callback. Неуспешный вложенный вход не очищает чужой plan; end очищает только собственный текущий TX.

Текущий scoped actor должен быть назначенным исполнителем CASE и иметь case_pick_execute на actual WARE через существующий has_current_scoped_execute, включая SELF/GROUP semantics. Legacy case_pick_execute использует прежний assert_scope. Для нового scoped CLOSE дополнительно нужен scoped_executor: только обычная счётная сборка, без HU и активной ASM. Отдельно проверяются OPEN/BLOCKED/HOLD assembly sessions; старый ordinary helper сам HOLD не исключал.

Старая exact CLOSE-квитанция читается **до** допуска нового исполнения. Поэтому дальнейшее штатное перемещение/упаковка не уничтожает историческую квитанцию, если actor сохраняет текущие права фактического склада. Нового закрытия неподдерживаемого контекста это не разрешает.

## Единственный существующий effect owner

`case_carrier_close.py` получает только два необязательных callback: metadata_context и assert_new. Defaults сохраняют старый metadata owner. Проверка закрытых строк, pending short, количества carrier lots, статусный переход, metadata UPDATE и immutable CASE event journal остаются прежними. Новый native пакет не пишет P/H/резервы, не создаёт таблиц или CREATE CONTEXT.

`case_current_close.py` использует server actor и прежний CaseCarrierCloseRequest с полным старым journal body. Ошибки не объявляются durable REJECTED: для неизвестного исхода нужен тот же operation_id и неизменный запрос. Старые журналы не переписываются.

## Приёмка и ограничения

- 23 focused tests проверяют strict body, порядок replay/admission, native callbacks, failed-begin cleanup и валидацию сохранённой квитанции внутри UOW до фиксации. Malformed JSON envelope даёт409 без нового исполнения. API/Oracle-конкуренцию они не доказывают.
- Миграция: `db/migrations/2026-10-15_case_scoped_close/`; before sources зафиксированы root в `reports/retailcase/2026-10-15/case-scoped-close/before/`.
- Root зафиксировал 115 CLOSED/CLOSE_ACK, max ID3746 и exact identity/payload SHA каждого события. Guard сравнивает этот ограниченный baseline до применения и rollback; root выполняет отдельные review/apply/native/API checks.
- Rollback не удаляет историю. Любой новый CLOSED/CLOSE_ACK относительно frozen baseline должен перевести восстановление в forward-only.
- После фактического цикла выполнен [[../components/retailcase_joint_sql_review_20261015|bounded SQL review]]; original before-DDL этап бизнес-workload не выполнял.

[[retailcase_case_resource_commands_20261015]] · [[../concepts/retailcase_nested_hu_consolidation_20261015]].

## Положительный цикл CASE1139 — фактически выполнен root

Root выполнил отдельный замороженный сценарий `N1939.GQC`: обычный отбор 1EA назначенным scoped исполнителем с текущими WARE+SELF, затем CLOSE в чистой TX, точные повторы исходных PICK/CLOSE и запрет изменённого тела CLOSE. Фактический HTTP `POST /api/case-pick/tasks/1139/close-current` с тем же operation_id/телом и обычной identity вернул полную исходную квитанцию; снимок задания, событий и остатков не изменился. GROUP-only допуск количественной команды доказан отдельно caller-rollback сценарием, а не этим committed циклом.

После положительного CLOSE root отдельно проверил RETURN с caller rollback, затем выполнил canonical RETURN, WAVE_CANCEL570, PICK_PLAN_CANCEL2201, отмену собственной tare-booking, simulated TEST TARE_COUNT0 и logout59. Все шесть Stock-квитанций APPLIED, их сохранённые полные результаты и outbox совпадают с журналом. Sequence outbox_id между пробой с rollback и commit закономерно различается; сравниваются все остальные поля, а committed outbox проверяется отдельно. Exact replay сравнивает полный committed результат вместе с его outbox_id.

Независимый SELECT-only readback подтвердил: CASE1139 CANCELLED, picked_qty1, content_version4, session59 CLOSED; parent22 + старый child1 + новый child1 лежат в исходной QIPcdbf4c0962, итог24/H0. Исходный stock origin и отдельные UID сохранены без слияния. Все назначения N1939.OP отозваны, GLOBAL INVALID0 и ошибок целевых пакетов0. Manual-time остаётся version8/OFF/IDLE. TYPE32, SSCC, фактический TEST старт и история PICK/CLOSE/RETURN не переписаны.

Доказательства: [root journal](../../reports/retailcase/2026-10-15/n1939-positive-close/journal.json), [независимый readback](../../reports/retailcase/2026-10-15/n1939-positive-close/independent-readback.json).

Root затем выполнил отдельный postpositive retirement без Stock-команд: CASE_PICK qualification выключена, ROLE_SAVE перевёл N1939.CASE.EXEC из ACTIVE/version3 в inactive/version4, CONFIG-owner выключил только resource63 и пометил только N1939.OP удалённым. [Новый независимый SELECT-only readback](../../reports/retailcase/2026-10-15/n1939-positive-close/retirement-independent-readback.json) подтверждает эти состояния, отсутствие активных CASE/warehouse TASK на resource63 и активных назначений actor, CLOSED session59, clock8/OFF/IDLE, INVALID0 и неизменный полный положительный checkpoint24/H0. Предыдущий независимый отчёт сохранён неизменным. Root перед запуском проверил точные hash исходного retirement runner и замороженного плана; их идентичность записана в отчёте. Этот разовый runner не объявляется универсальным: будущий переиспользуемый вариант должен отдельно закреплять нормализованное тело ROLE_SAVE и полный ACK вместо доверия mutable plan.

Ограничения: программная изолированная TEST фикстура, аппаратная печать/сканирование/весы не заявляются. Полного публичного pure RETURN compiler нет: его ACCESSIBLE BY и clean-TX fence сохранены, поэтому полная RETURN admission проверялась после PICK commit и отдельного CLOSE, с принятой root forward-only границей восстановления. Положительный mixed HU, ASM и shipping-QC этим сценарием не доказан.

SQL: независимый readback использует точные CASE/operation/UID фильтры и сохраняет top5 фактических shared Oracle cursors в отчёте. Накопленное ELAPSED_TIME не является временем этого изолированного теста. Решение — сохранить bounded readback; ранее выявленный dictionary/catalog plan backlog остаётся у operations/schema-verification owner, оснований добавлять stock index по этому кейсу нет.
