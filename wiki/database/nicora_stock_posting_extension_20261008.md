> Текущий срез после 121–130: [[nicora_stock_posting_continuation_20261008]]. Числа 45/9/22 ниже относятся к установке через 119.

# Дополнение проводки: компоненты 100–119

08.10.2026. RABAEV/orcl, тот же экземпляр. Это продолжение [[nicora_stock_posting_handlers]], а не объявление завершённого перехода.

## Реализованный код

- Native RRL_MES_PRODUCTION_API.apply_mes_movements_to_wms собирает существующие движения в одну MES_MOVEMENTS: максимум 200, детерминированный ID набора; прежнее применение с перехватом ошибки по каждой строке сохранено только для PREPARED.
- INVENTORY_COUNT и HTTP POST /api/inventory/stock-posting/inventory/counts: документ RRL_REVIZION, конкретные UID/артикул/ячейка, измеренное количество строкой, обязательная версия остатка, причина, optional unit_keys. Сохраняется HARD, проводится только разница. Количество ниже HARD отклоняется; положительная корректировка маркированного товара без capture не реализована и отклоняется. Паллетный объект должен уже существовать.
- GET /api/inventory/stock-posting/inventory/{revision_id}/lots возвращает партии/срок/базовые единицы/версию; окно 200 строк.
- WAVE_LAUNCH проводит настоящий HARD и привязку единиц, затем вызывает фиксированную реализацию прежних wave projections/tasks. RRL_PICK_WAVE_META ограничен ACCESSIBLE BY; это извлечённая прежняя логика, не новый планировщик.
- Пополнение переиспользует собственный PICKING reserve по PICK_TASK_ID. Перенос допускает собственный HARD плюс свободную часть; полное перемещение переносит весь HARD.
- WAVE_RELEASE/WAVE_CANCEL снимают общий HARD и меняют прежние проекции/незапущенные warehouse tasks в общей транзакции. Начатый/выполненный физический task запрещает автоматическую отмену.
- PICK_PLAN_CANCEL снимает резервы плана, включая принадлежащие волне и связанные резервы пополнения; отменяет незапущенные задания и прежний план. Сохраняется старый decision log.
- Публичные native wave команды и HTTP actions требуют operation_id в ACTIVE. Один ID на весь срок жизни волны недопустим: после release возможен новый launch. Native cancel_plan использует одноразовую идентичность отмены плана.
- SHIP_PALLET для заказа с существующей RRL_CUSTOMER_ORDER_FULFILLMENT использует только собственный HARD заказа, завершённый PICK_TASK и базовую конверсию EI. Списание общего резерва/помарочного состава и fulfillment одной транзакцией. Legacy SHIP_DOCUMENT остаётся unreserved pick-face маршрутом.
- Проверка RRL_PROD_BATCH_READY_V сохранена/добавлена для launch и shipment. Она не заменяет незакрытые fences всех regulatory writers.
- Native create_plan сохранён: FEFO/FIFO, topology, shortages и projections. В ACTIVE он считает спрос в базовых единицах и P-H, вычитает только SOFT, исключает чужой склад/недоступные ячейки, читает без FOR UPDATE stock. HARD гарантируется только launch.
- Исправлены base-policy версии при SAP receipt и MES movement; входная BOX/KG политика используется для конверсии, identity base policy — для balance core.

## Oracle JSON

Фактическая попытка получила ORA-40573 при JSON getter в статическом SQL. В 16 maintained runtime components getters вынесены в typed local bind blocks; миграция 114 применена, новые объекты VALID. Raw checkpoints не переписаны. См. [[../incidents/oracle_stock_json_bindings_20261008]].

Вторая попытка остановлена DIRTY_TRANSACTION: тест предварительно записывал revision и release state. Защита не ослаблена, всё незакоммиченное откатилось. Успешная физическая проводка/replay этим прогоном **не подтверждены**. Скрипт inventory smoke теперь предназначен только для периода после реального ACTIVE и не подменяет release state.

## Установка и предел подтверждения

Source checkpoints/парные rollback — фазы 101, 103, 104, 108–114, 117–119 в runtime/stock_posting_20261008. Полная база/VM не копировалась. [Manifest](../../db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json): 45 package pairs; specs-first bundle 115. Реестр: 9 ADAPTED / 22 UNCONVERTED.

Свежая Oracle выборка: PREPARED, B0 NULL, stock/events/operations 0, compatibility 0, изменённые RRL_STOCK_*, PICKING/WAVE/MES packages VALID. Python modules компилируются; приложение и новые OpenAPI routes загружаются.

RRL_SQL_SLOW_LOG за 08.10.2026 по STOCK/inventory не содержит записей. Случай выполнялся напрямую через Oracle и не создаёт API audit. Решение: не добавлять индексы без замера; после первого успешного physical case снять top SQL/slow SQL (владелец: разработчик stock core). Нагрузка/мощность не подтверждены.

## До полного переключения

Остаются legacy receipt/reversal/инвентаризация/ARTICULS writers и косвенные callers; CASE pick physical carrier и правильная отгрузочная идентичность; partial marked split и closure вложенных HU; все metadata/config/regulatory fences; полный реестр writers; B0 и единый cutover. Guards не являются заменой этих функций.
