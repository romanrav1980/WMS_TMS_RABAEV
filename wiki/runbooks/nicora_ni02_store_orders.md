# NI02 — заказы SAP, транспорт и задание на сборку

7 октября 2026 года. **in_progress_manual_bridge_implemented**: неизменный импорт заказа магазина и подключение к существующей СТ/назначению рейса реализованы. Основой остаются действующие WMS customer order, TMS и складские планы. Поздние решения/ограничения NICORA/оригинальный auto-split остаются. [Полностью пересмотренный план revision 10](../requirements/nikora_delivery_v55/implementation_plan.md).

## Первый срез

Нормализованный WarehouseCustomerOrder v1 от файлового шлюза: Sender/MessageId/OrderNumber, CustomerCode/StoreCode, WarehouseId, OrderDate/OperationalDate/DeliveryDate, PickingStartAt/PickingFinishAt/ShipmentAt с offset, строки Material/Quantity unit/необязательный TargetWeightKg. Это рабочий контракт разработчика, не объявленный стандартный SAP IDoc. [Пример и описание](../../exchange/contracts/ni02/README.md).

StoreCode сопоставляется с существующим CUSTOMER_STORE_MAP и CustomerCode. Адрес должен быть зарегистрирован минимум за семь календарных дней до первого заказа. Товар предварительно поступает через ARTMAS от того же Sender. Коэффициенты упаковки переводят quantity в base UoM Decimal; первоначальная XML потребность сохранена без изменения и без списания/резерва stock.

Источник склада/магазина настраивается явно: дни доставки, UTC offset, день-в-день. Основной shipment — следующий день относительно начала работы; after-midnight finish остаётся в исходном OperationalDate. Начало отдельной работы после полуночи требует нового операционного дня. Граница поступления — 16:00 локального операционного дня. Поздний заказ PENDING_LATE/DRAFT не запускает сборку: guard действует и на старые PL/SQL/HTTP пути.

Один MessageId/bytes возвращает durable результат; другой payload конфликтует. Новый MessageId с той же неизменной потребностью не создаёт вторую сущность, изменённая потребность существующего Sender/OrderNumber отвергается. Raw/hash/строки/source/result сохраняются атомарно.

## Запуск

Существующий API — `serv.bat`; файловый вход — `sap-store-orders.bat`, default `exchange/sap_store_orders/inbox`, отдельный `--root` при настройке. Переиспользуется gateway OS-lock/archive/error/recovery NI01. Пример не импортировать без настройки склада/магазина/SKU.

- POST `/api/integrations/sap/store-orders`: raw XML, право sap_store_order_import.
- GET список/detail: customer_order_view; результаты видны и в прежнем customer-orders API.
- PUT `/api/integrations/sap/store-orders/warehouses/{warehouse}/stores/{store_code}/calendar`: customer_rule_edit. Тело: utc_offset_minutes, delivery_weekdays [1..7], allow_same_day.

GLOBAL_ADMIN сохраняет *. API не создаёт фиктивные маршруты/рейсы. Миграция 008 и три guard trigger — [database mirror](../database/nicora_ni02_store_orders.md); installation logs/source checkpoint — runtime/ni02.

## Следующие изменения NI02

**Назначение СТ/заказов на рейс и транспортный пульт уже существуют и переиспользуются:** TransportDispatchPage → POST tasks/{id}/sts → assign_sts → RRL_TT_ADD_PALL → SBORKA_PALLETS.TRANSTASK_ID. [Подробная карта исходников и SAP-стыка](../components/nicora_order_trip_reuse.md).

SAP–СТ срез установлен: POST /api/integrations/sap/store-orders/{order_id}/prepare-st, право customer_order_import, operation_id и pallets[{lines:[{articul,quantity}]}]. В существующем customer-orders UI оператор загружает SAP-заказ, редактирует разбиение по паллетам и подтверждает подготовку; затем может вызвать прежнее назначение на выбранный рейс.

Команда вызывает существующие ORDERS/SBORKA writers, требует точного количества без legacy округления и корректных упаковок/массы/габаритов. PLANNED fulfillment имеет нулевой факт; подготовка не списывает stock и не означает физической сборки. СТ SAP_<id>, внутренние паллеты OP_SAP_<id>_<index>; эти коды не выдаются за SSCC. Preparation hash/result предотвращает дублирование.

Миграция 009: Statements=3, Errors=0; три metadata поля и ENABLED fulfillment constraint с PLANNED прочитаны в live RABAEV. Назначение по прежнему API теперь имеет общую транзакцию и проверку RRL_TT_ADD_PALL/error/readback. [Source files и ограничения](../components/nicora_order_trip_reuse.md).

Автоматический PALL_SPLITTER в dev — compatibility stub; оригинальный body надо восстановить до объявления автоматического разбиения работающим. PLANNED → PICKED/SHIPPED пока не обновляется legacy sync: физические переходы относятся к NI03/NI05. Далее NI02: позднее решение/отказ ERP, календарь исключений, сроки/ворота и недостающие ограничения смешанной тары/температуры. Существующие расчёты массы/объёма/паллет сохраняются. Фактические марки NI01 не подменяются предполагаемыми QR заказа.

Автор разработки не запускает набор тестов Qwen. [Задания Qwen NI01](../../задания%20на%20проведение%20тестов/NI01/README.md) подготовлены отдельно. Реальные SAP files и бизнес-кейсы NI02 пока не исполнялись.

Установка первого среза: 008_apply.sql и идемпотентный повтор с уточнёнными guards — Statements=6, Errors=0. Три таблицы/три trigger VALID в live Oracle. После 009 API import: 374 routes. Тестовые данные и XML не импортировались, rollback не исполнялся.
