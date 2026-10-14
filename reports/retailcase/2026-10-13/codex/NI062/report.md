# NI06.2 — приёмка возврата → точное размещение и восстановление

14 октября 2026. Авторский блок готов, общий gate выполняет ведущий. Новые движения и DDL не создавались.

## Завершённый путь

Подтверждённый ответ приёмки теперь показывает документ, точное количество, ячейку, operation_id и переход к размещению именно этой приёмки. Ответ сверяется с исходными operation_id/pickup_operation_id, количеством без float, единицей и native статусом. Неподходящий ответ сохраняет исходный запрос для повтора.

В существующем GET `/api/inventory/store-return-putaway/warehouses/{ware_id}/pending` добавлен optional `receipt_operation_id` (согласовано ведущим). Equality по bind применяется до limit100; прежние warehouse/right/not-placed ограничения сохранены. Поэтому переход не теряет выбранный возврат за первой сотней. Без параметра прежняя очередь. Если приёмки нет в текущем результате, другая паллета не выбирается. После native создания задания открывается exact task_id; никакого автопроведения или заполнения физических сканов.

В обоих существующих журналах receive/putaway: запись подтверждается чтением, повтор сохраняет operation_id/body, ответ сверяется, удаляется только неизменившаяся запись. Повреждение запрещает новую команду до явного архива и успешного текущего GET склада. Ошибка архива/чтения сохраняет исходник. Изменённая валидная команда другой вкладки перечитывается для её собственного повтора, а не объявляется повреждённой. Аналогичная уточняющая строка внесена в NI06.1 helper caller после его RELEASE.

return-mark-draft больше не заменяет повреждённые сканы пустым составом молча. Приёмка блокируется; явная очистка сначала архивирует raw. Добавление проверяет readback/неизменность; getEvidence отвергает повреждённый или изменившийся исходник.

## Файлы

- wiki-raw/wms_admin_ui_reference/store-return-receiving.js и .html
- wiki-raw/wms_admin_ui_reference/store-return-putaway.js и .html
- wiki-raw/wms_admin_ui_reference/return-mark-draft.js
- новые return-command-intent.js и return-receipt-result.js в той же папке
- api/wms_api_server/app/modules/inventory/contracts_return_putaway.py
- api/wms_api_server/app/modules/inventory/api/return_putaway_routes.py
- api/wms_api_server/app/modules/inventory/infrastructure/return_putaway.py

## Проверки

Восемь browser checks PASS, errors=[], четыре перехваченных/modelled POST, реальных POST0. Неверные ответы и pending queue моделировались; historical result shape реально прочитан из RRL_STOCK_OPERATION для REUSE643.RECEIVE:dc1889623c. Точные quantity3EA, warehouse14524201, document25234 соответствуют native истории. Проверены переход, отсутствие ложного выбора, exact retry, повреждённые оба журнала, сохранение повреждённых сканов и новый точный QR. [Browser](browser.json), [скриншот](receipt-result.png), просмотрен. Node syntax и Python compile PASS.

После согласованного рестарта API8088 реальный optional GET подтверждён OpenAPI и ответами: pending RETURN.BAR.RECEIVE:bf76071c4f склада9104 возвращает ровно1; завершённый REUSE643 и отсутствующий идентификатор возвращают0. Тот же pending из другого склада не возвращается. [HTTP/SQL](live_read.json), [direct read-only Oracle](direct_read.json). Неправильный HTTP ответ и отказ записи проверяются браузером без записи в БД. Независимой приёмкой это не является.

## Производительность

Exact query SQL_ID2rbsv71aszfp3: среднее3.803мс,11 исполнений,126 buffer gets суммарно. HTTP350–731мс включает API/auth/audit. Equality по operation_id перед ограничением позволяет точечный поиск без расширения очереди. V$SQL_PLAN недоступен текущим правам; фактический план не заявлен просмотренным. Решение: сохранить bind equality/limit100 и существующие ключи, новый индекс не вводить по этому измерению. Массовый производственный профиль отдельно.

## Конечный остаток в этом блоке

Подтверждённые кодовые пробелы receipt→putaway, wrong response, damaged intent/scans устранены. Native SAP-основание, полные коробки REUSE, маркированные агрегаты/сохранённая паллета, поставщик/утилизация и сквозное досье уже существовали и не переписаны. Реальные SAP/Track&Trace ACK, физические сканеры/весы и независимая приёмка целого маршрута остаются отдельными статусами; ожидание их не означает отсутствие перечисленного кода.