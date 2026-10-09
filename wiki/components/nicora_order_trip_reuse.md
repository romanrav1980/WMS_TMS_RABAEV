# NI02 — существующая привязка заказа/СТ к рейсу

7 октября 2026 года. **Назначение СТ на рейс уже реализовано. Повторная реализация назначения, новая таблица order–trip или второй транспортный пульт не требуются.** После чтения исходников SAP-вход подключён к существующим legacy writers; миграция 009 установлена в RABAEV. Бизнес-прогоны не выполнялись. [Глобальный анализ и ограничения](nicora_global_reuse_analysis_20261007.md).

## Действующая цепочка

| Участок | Существующий источник и поведение |
|---|---|
| Старый WinForms | [Form1.cs:7683](../../WindowsApplication2/WindowsApplication2/Form1.cs:7683), button39_Click: выделенные СТ добавляются в текущий маршрут через RRL_TT_ADD_PALL |
| React диспетчер | [TransportDispatchPage.tsx:785](../../admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx:785), handleAssign; тот же вызов есть при создании рейса с выбранными СТ |
| HTTP | [transport.py:428](../../api/wms_api_server/app/routers/transport.py:428), POST /api/admin/transport/tasks/{task_id}/sts; GET состава и DELETE снятия уже существуют |
| Backend | [transport_service.py:839](../../api/wms_api_server/app/services/transport_service.py:839), assign_sts: проверка счёта/другого рейса, вызов RRL_TT_ADD_PALL, перестановка адресов и очистка cache |
| Live Oracle | RRL_TT_ADD_PALL(TT_ID,ST_NUMBER1): строки 14–17 обновляют RRL_SBORKA_PALLETS.TRANSTASK_ID для ST_NUMBER; TT_ID≤0 снимает назначение. Строки 21–22 обновляют регион рейса |
| Состав/плановая потребность | get_task_sts/list_available_sts работают на RRL_SBORKA_PALLETS/ROWS, группируют СТ/адреса, считают паллеты, ORDER_WEIGHT; свободные СТ также имеют объём TARESIZE×PACK_COUNT |
| Связь современного заказа с legacy | Live RRL_CUSTOMER_ORDER_API.sync_fulfillment_from_legacy: ORDER_NO сопоставляется с ORIGINAL_ORDER_NUMBER/ST_NUMBER/ORIGINAL_ST_NUMBER/NAKLAD_NUMBER; RRL_CUSTOMER_ORDER_FULFILLMENT хранит LEGACY_SBORKA_PALLET_ID/PALLET_UID |

Таким образом, уже имеется путь customer order → существующая fulfillment/legacy паллета (когда связь заполнена) → СТ → TRANSTASK_ID → RRL_TRANSPORT_TASK. Нельзя объявлять всю эту связь отсутствующей только потому, что в новом importer нет столбца TRANSPORT_TASK_ID.

## Точный стык нового SAP-входа

StoreOrders.receive сохраняет заказ без автоматической сборки/остатков. Новая отдельная команда POST /api/integrations/sap/store-orders/{order_id}/prepare-st подключает его к действующим ORDERS.CREATE_ORDER/ADD_ORDER_ROW и RRL_SBORKA_PALLETS_ADD2/ROWS_ADD4; явную укладку подтверждает оператор в существующем customer-orders UI.

SAP identity сопоставлена через существующий customer_order_id: СТ SAP_<id>, внутренние паллеты OP_SAP_<id>_<index>, LEGACY_ORDER_ID и PLANNED fulfillment. Это внутренние идентификаторы, не SSCC. Сумма укладки обязана точно совпасть с заказом; неизвестная упаковка/нулевые параметры/legacy округление отвергаются. Preparation hash/result сохраняются миграцией 009 в исходном SAP metadata, повтор не создаёт вторую СТ. После подготовки используется тот же assign_sts/RRL_TT_ADD_PALL.

Ручной SAP–СТ bridge реализован. Автоматический PALL_SPLITTER в текущем dev содержит compatibility stubs (split_ufa/split_vegetables return 0); оригинальный алгоритм нельзя объявлять восстановленным. Также sync_fulfillment_from_legacy только вставляет отсутствующие rows: PLANNED → PICKED/SHIPPED завершается физическими командами NI03/NI05.

## Замеченные ограничения и различия

- WinForms передаёт дополнительный user_id1, а текущая live функция имеет два входных аргумента; React/FastAPI передаёт два. Наличие старого вызова подтверждает историю функции, но не доказывает работоспособность данной старой сборки с текущей сигнатурой. Не исправлять WinForms вне конкретной необходимости.
- Live RRL_TT_ADD_PALL ловит OTHERS и возвращает err2; raise после return недостижим. Прежний assign_sts игнорировал результат и делал отдельные commits. Теперь он делегирует transport/infrastructure/st_assignment.py: одна транзакция, блокировка рейса/паллет, проверка legacy error и readback; тот же writer/TRANSTASK_ID и очистка cache сохранены.
- Уже вычисляемые плановые масса/объём/паллеты переиспользовать. Сначала сравнить конкретные правила NICORA по таре/температуре/смешанной загрузке с существующим валидатором, затем дополнять только найденные пробелы.

Slow SQL измерений нет: runtime cases не выполнялись. Документ не присваивает системе PASS и не назначает общий аудит/нагрузку. [План NI02](../runbooks/nicora_ni02_store_orders.md).
