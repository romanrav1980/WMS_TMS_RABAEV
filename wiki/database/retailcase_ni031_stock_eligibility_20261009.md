# NI03.1 — единый допуск источника товара

09.10.2026. Реализовано и установлено в существующей **RABAEV/orcl ACTIVE**, compatibility=0. Миграция **2026-10-09-007-stock-source-eligibility**, [SQL/apply/checkpoint/rollback/verify](../../db/migrations/2026-10-09_ni031_stock_eligibility/apply.sql). Продолжение [[retailcase_stock_posting_cutover_20261009]]. Stock core не переводился повторно.

## Подтверждённый gap и решение

В ACTIVE подбор выполняет Oracle RRL_STOCK_WAVE_CMD, а старая Python ветвь _reserve_replenishment_sources не исполняется. Патч направлен в действующий путь. Подбор не проверял pending placement/допуск партии; reuse собственного HARD обходил часть срока годности. RRL_PICKING_API проверял склад/блокировки, но не весь допуск; его SOFT подсчёт был по UID без CELL.

Authoritative implementation — **RRL_STOCK_ELIGIBILITY.reason**: чистое чтение для preview. **assert_source** вызывает то же правило под существующими CONFIG/CELL fences и HU/STOCK anchors. Никакой второй Python версии правила, нового stock registry, commit или внешнего запроса внутри проверки нет.

Правило: warehouse/article identity; блокировки ячейки; корректные P/H/base unit; отсутствие packed CASE membership; production batch readiness; срок/остаточный срок/процент; pending PUTAWAY/текущая SAP receive cell; system location; действующий pick-face mapping для CASE отбора; P−H с точным собственным HARD. Проверка физического состава переиспользует read-only RRL_STOCK_UNIT_CORE.assert_composition, ACL расширен для policy package. Состав одной маркированной единицы не умножается по числу профилей.

Новые условия включены в RRL_PICKING_API (ACTIVE selection и SOFT по UID+CELL), replenishment free/own selection и locked execute, WAVE_LAUNCH, HARD create/promotion и CASE pick. TASK_COMPLETE/WAVE проверяет источник до движения. Для полного пополнения уже зарезервированной паллеты сохранено перемещение всех HARD с прежними владельцами; допуск не выдаёт чужой HARD как новый свободный запас.

## Настройка и рабочее место

В существующую RRL_RECEIPT_SKU_RULE добавлен SOURCE_PICK_MODE:
- AFTER_PUTAWAY — default, поступившая паллета не предлагается до размещения.
- DIRECT — явное разрешение прямого PICK/ALLOCATE из приёмки для товара/склада. REPLENISH всё равно требует размещения.

Права настройки — существующее warehouse_settings_edit. Запись через ReceiptConfiguration/configuration_transaction с CONFIG X. Приёмка товара сохраняет поля PICK_CELL, температуру и shelf life. Карантинные BLOCKED_FOR_REMAINS/BLOCKED_FOR_POPOLNENIE запрещают источник при любом SOURCE_PICK_MODE; P сохраняется. BLOCKED_FOR_ACCEPT не запрещает обычный source, его target/receive семантика остаётся прежней.

На receiving.html поле «Отбор из приёмки» сохраняется/читается вместе с правилом SKU. На wave-replenishment.html у строки есть «Источники»: точные P/H/free/base и понятная причина отказа, страницы по 50 строк. Это свободные источники для нового резерва, а не подтверждение физической операции. Собственный HARD проверяется командой отдельно.

GET /api/inventory/stock-posting/source-availability: существующее pick_wave_view/RUSERS, warehouse+article обязательны, limit <=100, stable cursor UID/CELL; причины и количества строками. API не читает SQL напрямую — typed port и инфраструктурный reader; auth dependency привязана в composition root. Server authority остаётся в Oracle, preview может устареть до команды.

## Фактическое подтверждение

В изолированной QA ячейке/новой паллете проверены: допустимый источник, другой склад, недостаточный shelf life; карантин и отказ реального RESERVATION_CREATE при P=1/H=0; pending PUTAWAY; явный DIRECT для PICK при запрете REPLENISH; HARD=1 запрещает новый свободный резерв и разрешает распознавание собственного покрытия; release и count до **P=H=0**. Физические изменения выполнялись через root posting.

Два ранних сбоя fixture script: слишком длинное имя ячейки для legacy CELL(15) и зарезервированный Oracle bind :uid. Исправлены только в diagnostic script. После сбоя birth один QA остаток восстановлен явным INVENTORY_COUNT; история сохранена. Не выполнялось удаления бизнес-журнала или копирования базы.

Реальный HTTP: без авторизации 401; admin получает source preview/reason/exact quantity strings. 11 адресных adapter/replay тестов passed. JS syntax и UTF-8 checks passed; новые Oracle packages/body без USER_ERRORS. API перезапущен. Полный браузерный прогон/положительный маркированный fixture и независимая приёмка не объявляются выполненными.

Global retailcase_quality_gate вызван, architecture этап FAIL по ранее накопленным нарушениям в integration/fulfillment и прежних inventory routes/error handlers. Новая source route первоначально импортировала legacy auth; исправлена на injected permission из composition root. После исправления новых debt keys этих файлов нет. Общий gate не объявляется PASS, baseline/пороги не повышались. Владелец отдельного исправления общего debt — architecture owner; объём не подменяет NI03.1.

## Slow SQL и дальнейшие действия

Oracle v$sql: policy point read 5 executions / 92.2 ms суммарно (~18.4 ms); metadata verification — до 47 ms. Preview bounded 100+1 и точный article/warehouse/cursor. Решение: сохранить ограниченное чтение без нового индекса на основании маленького dev случая; при реальном объёме оптимизировать batch policy evaluation и проверять UID/CELL/task/receipt планы, не обещать миллионы operations/day.

[Следующий NI03.2](../requirements/retailcase_delivery_v55/execution/active/ni03_2.md): оставшиеся составные переходы заданий/частичного исполнения, назначения и восстановления. Функциональная реализация NI03.1 подтверждена адресными случаями; отдельные широкая приёмка и общий architecture debt остаются открытыми.

Для source-availability в RRL_SQL_SLOW_LOG за последний час записей нет; Oracle top SQL использован как доступное подтверждение. Это не заменяет измерение планов/нагрузки на реальных объёмах.
