# NI06.1: продолжение списка межскладских мест

Checkpoint662–664, 12.10.2026. Владелец inventory; delivery business commands и единое ядро остатка не меняются.

Прежний GET /api/inventory/interwarehouse/group-warehouses/{ware_id} сохраняет ответ-список и default limit200. Добавлены limit1..200 и after_operation_id. Курсор относится к существующему плану того же принимающего склада. Проверка текущего пользователя/WARE выполняется перед чтением каждой страницы. Неизвестный или чужой курсор отклоняется.

Порядок прежний: ARRIVAL_DUE DESC, OPERATION_ID ASC. Продолжение использует дату неизменяемого исходного плана и идентификатор при равных датах. Дата не конвертируется в локальное время Python и не обрезается до секунд. OFFSET не применяется. Каждая страница читается в прежнем READ ONLY снимке; это не один замороженный снимок между HTTP-запросами. Новые планы следует получать через Обновить.

В существующем interwarehouse-groups экране — страницы по100, кнопка следующей страницы. Смена склада/пользователя очищает курсор, устаревший ответ не заменяет новый контекст. Подтверждения склада остаются прежними.

## Подтверждение и ограничения
[case663](../../scripts/case663_group_queue.py) — реальный RABAEV/orcl, существующий источник, первая страница, пустое продолжение, неизвестный курсор и границы limit. PASS; без новых планов и изменения P/H. В dev нет двух групп одного принимающего склада: положительная вторая страница и равные даты ещё не подтверждены. Браузерная приёмка не заявляется.

JavaScript syntax и Python compilation PASS; architecture678 / cycles0 / debt76 PASS. Предыдущий полный quality gate661 PASS; после662 архитектура и изменённый JS проверены отдельно.

[slow664](../../scripts/slow664_group_queue.py): native shared SQL children16.959ms/29.5buffers и44.225ms/561.5buffers на малом dev-источнике. Решение inventory: сохранить складской фильтр, keyset и ограничение200; не добавлять индекс по единственной строке. При росте очереди проверить план существующего TARGET_WARE индекса и сортировки ARRIVAL_DUE/OPERATION_ID; owner inventory, backlog перед промышленным объёмом.

Источники: [reader](../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_read.py), [API](../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py), [экран](../../wiki-raw/wms_admin_ui_reference/interwarehouse-groups.js). Состав требований/полный NI06.1 остаются открыты.
