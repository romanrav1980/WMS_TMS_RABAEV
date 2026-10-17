# Финансы: scoped-доступ и независимое согласование

## Продолжение16.10 — изменения ставок и XLSX

**Актуальный результат:** APPLIED SHA6eb16a7c75dcbb033c3f9158cbb5780297f20680f895a18ba831e2fc18b19831/readback1trigger/ERROR0/INVALID0.20HTTP rates/monthly/XLSX/PLATFORM shell/GROUP/revoke/repeat/rollback/REV PASS, narrow expense approver не меняет ставки. Composite invoice531/all-WARE и6 native independence checks подтверждены отдельно — [[retailcase_driver_self_scope_20261016]]. Счета530/531 — нулевая TEST metadata, новый финансовый эффект не зафиксирован. Ниже PREPARED описывает историю подготовки, не текущий статус.

PREPARED_NOT_APPLIED/NOT_ACCEPTED: `2026-10-16-finance-rate-scope`, SQL `db/migrations/2026-10-16_finance_rate_scope/`. История BOX/monthly ставок допускает текущую create_tt_price WARE/GROUP роль и прежний legacy home/global. Shared ACCESS_REV берётся до Python admission и непосредственно в native history trigger; компоненты/версия/неизменность истории сохраняются. Expense-only approval не даёт управления ставками. Source before1 trigger/INVALID0 сохранён в finance-write-export-scope/before.

XLSX счёта/реестра получает actor из HTTP, проверяет все фактические WARE выбранных ST/load/cost-run в том же READ ONLY snapshot до сумм/строк. Неразрешённый счёт не урезается до частичной суммы. Реестр с неизвестной областью хотя бы одного документа отклоняется для scoped-only пользователя; прежняя совместимость пустых документов с legacy view сохраняется. Native/API matrix и текущий gate обязательны до завершения; первые10 offline tests не заменяют Oracle.

Миграция2026-10-15-finance-scoped-decisions. По утверждённой модели прав: существующие неизменяемые журналы расходов/решений сохраняются, RRL_LOG_EXPENSE_GUARD и RRL_LOG_EXP_DECISION_GUARD используют RRL_ACCESS_API по фактическому WARE_ID. Новые узкие права expense_logist_approve/expense_finance_approve не дают права менять ставки. Legacy calc_tt_price/create_tt_price остаются совместимым источником полномочий.

Автор расхода не утверждает свой расход. Финансовое решение остаётся независимым от логистического; существующий trigger уже проверял LOGIST!=FINANCE, теперь добавлен и автор. GLOBAL_ADMIN не обходит этот бизнес-инвариант. Квитанция уже выполненного решения возвращается до новой проверки автора; новое содержимое под старым ключом отклоняется.

[Apply](../../db/migrations/2026-10-15_finance_scoped_decisions/apply.sql), [rollback](../../db/migrations/2026-10-15_finance_scoped_decisions/rollback.sql), before_USER_SOURCE и checkpoint.json рядом. Данные расходов не переписываются. Первая проверка new-role ожидаемо выявила старый trigger gate; доступы/машина очищены, immutable тестовая статья оставлена неактивной с историей. Следующие проверки — один rollback-only Oracle fixture, без отключения триггеров и без удаления истории.

Статус PREPARED до native verify.

Live APPLIED: новые trigger guards установлены Errors0. Rollback-only fixture6checks PASS: разные автор/LOGIST/FINANCE, узкое право без ставок/чужого склада, неизменный repeat. Вся проверочная транзакция откачена, финансовое признание не выполнялось. Первая неактивная тестовая статья сохраняет историю; её доступы/машина удалены. [Evidence](../../reports/retailcase/2026-10-14/access-knowledge/finance-independence.json).

## Продолжение16.10 — чтение ставок и расходов

Исправлен последний gap: `_lines` и transport invoice snapshot фильтровали строки по legacy home, что могло дать частичный итог составного документа. Единый bounded preflight всех фактических складов ST/load/cost-run выполняется до rich rows в том же READ ONLY snapshot; отсутствие хотя бы одной области даёт403. DTO и финансовые записи не меняются.

Новый FC16 actor home1/flat view0: actual composite trip31050 (WARE9201+9202) с частичным grant403, обе области200, revoke одной403, полный GROUP200/member-remove403/restore200; foreign33641/403. Три invoice1 чтения admin200 и чужой scope403.14HTTP,5unit PASS; разрешённая детализация тестового рейса пустая, новая финансовая проводка не создавалась. Actor/assignments/role/group retired. Источник `finance-scoped-read/composite.json`; общий SQL review100 explicit pairs/max730мс. Существующий invoice DTO scope VISIBLE_WAREHOUSES сохранён для совместимости, но preflight теперь требует все фактические области объекта; частичный итог не возвращается.

Реализовано: убран лишний flat API gate только у warehouse rates/history и реестра расходов; native `require_warehouse(...transport_dispatch_view)` остаётся authoritative. Допуск и bounded выборка расходов теперь в одном READ ONLY snapshot. Остальные rates writes/trip/invoice endpoints не расширялись.33 actual HTTP PASS на новом FS16 actor home1/flat view0: три API, два РЦ, WARE/GROUP/чужой/отзыв/member-remove; свои grants/user/role/group retired. Источник `reports/retailcase/2026-10-16/finance-scoped-read/acceptance.json`. Выборки разрешённых складов могут быть пустыми; это проверка scoped чтения, не новая финансовая проводка. Отдельный unit подтверждает одну транзакцию допуска/чтения. Исходные6 native independence checks остаются отдельным доказательством.
