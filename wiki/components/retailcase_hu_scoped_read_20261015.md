# Дерево HU: чтение по текущей области

15.10.2026. Реализовано и проверено actual HTTP. `GET /api/warehouse-hus/composition` и `/target-slots` используют identity пользователя без требования входа в admin shell. В inventory применяется прежний native `RRL_ACCESS_API.allowed(actor, warehouse_task_view, WAREHOUSE, actualWARE)`: global/legacy семантика сохраняется, назначения WARE/GROUP/CURRENT/SNAPSHOT обслуживает общий owner.

До чтения состава/CASE QC разрешение проверяется по минимальным данным физического склада. CASE использует свой WARE; текущий HU/stock — фактическую ячейку; отгруженный HU — исходный склад из immutable departure archive. После получения дерева — повторная проверка перед placement/tare в той же READ ONLY TX. Неизвестная/неограниченная location не допускается. Этим read-инкрементом POST-команды не менялись;16.10 отдельно выполнены базовые CREATE/ATTACH/DETACH/MOVE — [[../database/retailcase_hu_scoped_execute_20261016]]. Остальные POST owners остаются отдельной матрицей.

13 focused tests и независимое чтение diff PASS. Первый actual preflight обнаружил Oracle reserved bind `:uid`; исправлен на`:p_uid` до создания фикстуры, исходный сбой не является успешным тестом.

Изолированный N2140.VIEW: homeWARE13583852, flat view/execute/admin=0; actual HU1069:4bb85f1f15 находится наWARE5062399. WARE assignment дал200 для двух GET, отзыв —403. CURRENT GROUP assignment дал200, удаление склада из группы —403. Домашний склад без назначения и admin login дали403. Девять exact ACCESS receipts сохранены; role/group inactive, оба grants revoked, actor deleted. Товарных команд0; исходные HU, stock-operation/clock/outbox counts сохранены. [Frozen plan](../../reports/retailcase/2026-10-15/hu-scoped-view/frozen-plan.json), [actual execution](../../reports/retailcase/2026-10-15/hu-scoped-view/execution-journal.json).

Первоначальный план включал дополнительный GROUP caller-rollback; root исключил его повторение, поскольку actual committed GROUP HTTP и отзыв покрывают требуемый путь. Журнал явно описывает исполненные фазы, не приписывает неисполненный шаг.

SQL:16 Oracle/local pairs, maxHTTP260ms;8 error/denial transaction records6-23ms не являются долгими запросами. Native HU shared cursor cumulative avg≤15.85ms, не p95 данного сценария. Решение — сохранить exact UID/WARE lookups, tree200/depth16/units10000 и slots200, без нового индекса/кэша. Inventory/platform проверяет execution deltas/планы при повторных500ms или1000ms на пилоте. [SQL evidence](../../reports/retailcase/2026-10-15/hu-scoped-view/sql-review.json).

UI массы отдельно проверен на Vite localhost3000 с реальным API,390px: новый блок источников, дерево3nodes, опубликованная help v3, ошибок/изменяющих запросов0. Production bundle отдельно проверен с mock API на3ширинах; этот live-прогон не выдаётся за исполнение dist bundle. [Actual read](../../reports/retailcase/2026-10-15/hu-mass-ui/native-read/native-ui.json). Это не SHIPPING_GROSS capture/QC и не физический пилот.

[[retailcase_operator_ui_evidence_20261015]] · [[../concepts/retailcase_nested_hu_consolidation_20261015]].
