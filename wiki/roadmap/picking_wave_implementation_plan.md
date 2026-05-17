# Стратегический И Тактический План Реализации: Комплектация И Сборка По Волнам

Статус: план реализации после утверждения ТЗ.

Дата: 2026-05-17.

Связанные документы:

- [Комплектация / Picking Planning](../requirements/picking_planning_tz.md)
- [Сборка по волнам / Wave Picking](../requirements/wave_picking_tz.md)
- [Администрирование сборки по волнам](../requirements/wave_picking_admin_tz.md)
- [Legacy rights model](../concepts/legacy_rights_model.md)
- [Oracle Change Protocol](../database/oracle_change_protocol.md)

## 1. Цель

Сделать в текущем WMS/MES проекте управляемый контур комплектации заказов клиентов:

- заказ клиента становится отдельным объектом;
- клиент становится отдельной сущностью с адресами и правилами;
- система планирует отбор по заказу клиента, маршруту и воротам;
- остатки резервируются так, чтобы исключить двойное назначение;
- дефицит фиксируется явно;
- заказы можно группировать в волны сборки;
- запуск волны переводит резерв в жесткий операционный режим;
- админка показывает запуск, статусы, задачи, резервы, дефицит и аудит;
- физические движения по-прежнему должны быть согласованы со старым WMS-механизмом, без прямого изменения остатков в обход старого ядра.

## 2. Стратегическая Позиция

### 2.1. Oracle Остается System Of Record

На текущем этапе PostgreSQL не вводится. Основная база остается Oracle `RABAEV`.

Все новые сущности создаются как additive schema в Oracle:

- без удаления legacy tables;
- без изменения старых процедур, если это не требуется явно;
- через versioned migrations;
- с `apply`, `verify`, `rollback` или безопасным rollback-пояснением;
- с wiki mirror и smoke-проверками.

### 2.2. Старый WMS Не Ломаем

Старый WMS продолжает отвечать за физические остатки, ячейки, паллеты и движения.

Новый контур:

- читает остатки и паллеты;
- рассчитывает планы;
- создает резервы;
- создает задачи;
- передает физические операции в WMS bridge или terminal flow;
- не пишет напрямую в `RRL_REMAINS` и подобные критичные остаточные таблицы.

### 2.3. Планирование И Исполнение Разделяются

Нужно сохранить два уровня:

- `Picking Planning`: расчет, soft reserve, дефицит, привязка к заказу клиента.
- `Wave Picking`: групповой запуск, hard reserve, задачи пополнения и отбора.

Это важно, потому что заказ может быть рассчитан заранее, но не запущен в работу. Волна является операционным событием старта сборки.

### 2.4. Права И Аудит Сразу В MVP

Права должны идти через legacy модель:

- `RUSERS`;
- `USER_GROUP`;
- `RIGHTS`.

Нельзя повторять ошибку с hardcoded admin.

Все изменяющие действия должны попадать:

- в Oracle API audit;
- в доменный audit log по волнам и резервам;
- в локальный лог backend, если API был вызван.

### 2.5. Админка Сначала Raw UI, Потом Production Frontend

На первом этапе делаем raw admin UI в стиле текущей WMS PRO админки:

- быстрее проверяем бизнес-процесс;
- сохраняем единый визуальный стиль;
- не тратим первый инкремент на сложный frontend framework.

После проверки процесса raw UI можно перенести в полноценную современную админку.

## 3. Стратегические Этапы

### Этап 1. Данные Клиентов И Заказов

Цель: отделить клиента от legacy строки адреса.

Результат:

- есть `RRL_CUSTOMER`;
- есть адреса и точки доставки;
- legacy `RRL_ORDERS.ADDR` мапится на клиента;
- заказ клиента читается как канонический объект;
- факт исполнения заказа отделен от плана.

Зачем это нужно: без клиента нельзя корректно применять требования по сроку годности, укладке, типу машины и делению заказа.

### Этап 2. Правила Комплектации

Цель: хранить и применять правила клиента.

Результат:

- срок годности в днях и процентах;
- правила укладки по артикулу и группе товаров;
- разрешение докладывать товар сверху;
- индивидуальные нормы коробов на паллете;
- типы машин и емкость;
- разделение заказа на shipment parts.

### Этап 3. Резервы И Picking Planning

Цель: рассчитывать план комплектации без двойного назначения остатков.

Результат:

- soft reservations;
- полнопалетный отбор;
- покоробочный отбор;
- shortage-протокол;
- объяснение выбора партии, паллета и ячейки;
- API для расчета и просмотра планов.

### Этап 4. Топология Отбора И Pick Face

Цель: дать системе понимание, откуда комплектовщик берет коробочный товар.

Результат:

- таблицы pick face;
- порядок обхода ячеек;
- несколько pick face для одного SKU;
- подготовка к dynamic pick face и пополнению.

### Этап 5. Wave Picking Core

Цель: запустить управляемую волну сборки.

Результат:

- волна как объект;
- заказы и строки в волне;
- hard reservations;
- задачи пополнения;
- задачи отбора;
- статусы волны;
- аудит.

### Этап 6. Админка Управления Волнами

Цель: дать диспетчеру склада рабочий экран управления волнами.

Результат:

- реестр волн;
- диалог `Запуск волны`;
- preview;
- запуск;
- отмена;
- мониторинг резервов, пополнений, задач, дефицитов;
- настройки волн;
- права доступа.

### Этап 7. Terminal Execution

Цель: связать волны с исполнением на терминале.

Результат:

- терминал получает задачи пополнения;
- терминал получает задачи отбора;
- сканирование паллета, SSCC, ячейки;
- подтверждение выполнения;
- ошибки оператора возвращаются в API и audit.

### Этап 8. Оптимизация И Промышленная Эксплуатация

Цель: довести модуль до промышленного режима.

Результат:

- нагрузочные тесты;
- конкурентный запуск волн;
- мониторинг зависших резервов;
- аварийное освобождение с правами;
- аналитика выполнения;
- подготовка к wave optimization.

## 4. Тактический План Реализации

Текущий статус на 2026-05-17:

- инкремент 0 выполнен для стартовых legacy sources: подтверждены `RRL_ORDERS`, `RRL_ORDER_ROWS`, `RRL_SBORKA_PALLETS`, `RRL_SBORKA_PALLET_ROWS`, `RRL_CLIENT_REG_PROFILE`;
- в живой Oracle до `014` не было `RRL_CUSTOMER*`, `RRL_PICK*`, `RRL_SHIPMENT_PART*`;
- инкремент 1 выполнен через migration `014`: customer/order foundation, `RRL_CUSTOMER_ORDER_API`, backend endpoints, smoke и cleanup;
- инкремент 2 выполнен через migration `015`: customer shelf-life rules, stack rules, vehicle types, customer vehicle rules, shipment parts, `RRL_CUSTOMER_RULE_API`, backend endpoints, smoke и cleanup;
- инкремент 3 выполнен через migration `016`: picking plans, tasks, soft reservations, shortages, decision log, `RRL_PICKING_API`, backend endpoints, smoke и cleanup;
- инкремент 4 выполнен через migration `017`: pick routes, route cells, pick faces, SKU assignment, `RRL_PICK_TOPOLOGY_API`, case-pick target cells and sequence, backend endpoints, smoke и cleanup;
- инкремент 5 выполнен через migration `018`: wave picking core, hard reservations, wave demand, replenishment/picking tasks, `RRL_PICK_WAVE_API`, backend endpoints, smoke и cleanup;
- Oracle invalid objects после `018`: `0`.

### Инкремент 0. Подготовка И Инвентаризация

Цель: уточнить реальные источники данных перед DDL.

Задачи:

1. Проверить актуальные legacy таблицы заказов:
   - `RRL_ORDERS`;
   - `RRL_ORDER_ROWS`;
   - `RRL_SBORKA_PALLETS`;
   - `RRL_SBORKA_PALLET_ROWS`.
2. Проверить поля паллет, партий, SSCC, ячеек и остатков.
3. Проверить существующие rights, группы и пользователей.
4. Зафиксировать, какие данные можно читать напрямую, а какие только через PL/SQL.
5. Обновить wiki mirror.

Результат:

- короткий отчет в wiki;
- список реальных legacy sources;
- подтверждение, что Oracle invalid objects = `0`.

Статус: выполнено в рамках подготовки migration `014`.

### Инкремент 1. Migration 014: Customer And Order Foundation

Цель: создать основу клиента и заказа клиента.

Ожидаемые файлы:

- `db/migrations/.../014_apply.sql`
- `db/migrations/.../014_verify.sql`
- `db/migrations/.../014_rollback.sql`
- `db/migrations/.../014_smoke.sql`
- `db/migrations/.../014_cleanup.sql`

Состав:

- `RRL_CUSTOMER`;
- `RRL_CUSTOMER_ADDRESS`;
- `RRL_CUSTOMER_STORE_MAP`;
- `RRL_CUSTOMER_ORDER`;
- `RRL_CUSTOMER_ORDER_ROW`;
- `RRL_CUSTOMER_ORDER_FULFILLMENT`;
- sequence/index/constraints;
- package `RRL_CUSTOMER_ORDER_API`.

API:

- `GET /api/customers`;
- `GET /api/customers/{id}`;
- `POST /api/customers/import-legacy`;
- `GET /api/customer-orders`;
- `GET /api/customer-orders/{id}`;
- `POST /api/customer-orders/import-legacy/{legacy_order_id}`;
- `GET /api/customer-orders/{id}/fulfillment`.

Smoke:

- импортировать один legacy order;
- создать draft customer из `RRL_ORDERS.ADDR`;
- проверить строки;
- проверить fulfillment placeholder;
- cleanup тестовых данных.

Критерий готовности:

- заказ клиента можно читать как новый объект;
- legacy mapping работает;
- Oracle invalid objects = `0`.

Статус: выполнено. Следующий практический инкремент - `015 Customer Rules And Vehicle Capacity`.

### Инкремент 2. Migration 015: Customer Rules And Vehicle Capacity

Цель: добавить правила клиента, которые влияют на комплектацию.

Состав:

- `RRL_CUSTOMER_SHELF_LIFE_RULE`;
- `RRL_CUSTOMER_PRODUCT_STACK_RULE`;
- `RRL_VEHICLE_TYPE`;
- `RRL_CUSTOMER_VEHICLE_RULE`;
- `RRL_SHIPMENT_PART`;
- package methods для выбора правил по priority и period.

API:

- `GET /api/customers/{id}/shelf-life-rules`;
- `POST /api/customers/{id}/shelf-life-rules`;
- `GET /api/customers/{id}/stack-rules`;
- `POST /api/customers/{id}/stack-rules`;
- `GET /api/customers/{id}/vehicle-rules`;
- `POST /api/customers/{id}/vehicle-rules`;
- `GET /api/vehicle-types`.

Admin UI:

- raw page or section для правил клиента;
- минимально можно начать с API и smoke, UI сделать в следующем инкременте.

Smoke:

- клиент с правилом срока годности;
- клиент с укладкой по артикулу;
- клиент с фурой `33` паллета;
- заказ на `80` паллет делится на `33 + 33 + 14`.

Критерий готовности:

- правила клиента выбираются детерминированно;
- действует fallback к правилу по умолчанию;
- конфликт правил виден в диагностике.

Статус: выполнено. Следующий практический инкремент - `016 Picking Plan And Reservations`.

### Инкремент 3. Migration 016: Picking Plan And Reservations

Цель: создать расчет планов комплектации и soft reservation.

Состав:

- `RRL_PICK_PLAN`;
- `RRL_PICK_PLAN_LINE`;
- `RRL_PICK_TASK`;
- `RRL_PICK_RESERVATION`;
- `RRL_PICK_SHORTAGE`;
- `RRL_PICK_DECISION_LOG`;
- package `RRL_PICKING_API`.

Логика:

- расчет полнопалетного отбора;
- расчет покоробочного остатка;
- FEFO/FIFO;
- учет `IS_SHIPMENT_ALLOWED` как критерия планирования;
- учет активных резервов;
- soft reserve;
- shortage-протокол;
- partial plan.

API:

- `POST /api/picking/plans`;
- `GET /api/picking/plans`;
- `GET /api/picking/plans/{id}`;
- `POST /api/picking/plans/{id}/cancel`;
- `GET /api/picking/plans/{id}/shortages`;
- `GET /api/picking/reservations`.

Smoke:

- заказ с достаточным остатком;
- заказ с частичным дефицитом;
- второй план не может взять уже зарезервированный остаток;
- отмена плана освобождает soft reserve.

Критерий готовности:

- двойное назначение исключено;
- shortage объясним;
- старые WMS остатки не меняются.

Статус: выполнено. Следующий практический инкремент - `017 Pick Face And Pick Route`.

### Инкремент 4. Migration 017: Pick Face And Pick Route

Цель: подготовить топологию покоробочного отбора.

Состав:

- `RRL_PICK_FACE`;
- `RRL_PICK_FACE_ARTICUL`;
- `RRL_PICK_ROUTE`;
- `RRL_PICK_ROUTE_CELL`;
- настройки min/max capacity для pick face;
- связь SKU с несколькими ячейками отбора.

API:

- `GET /api/picking/pick-faces`;
- `POST /api/picking/pick-faces`;
- `GET /api/picking/pick-route-cells`;
- `POST /api/picking/pick-route-cells`.

Smoke:

- SKU имеет одну pick face;
- SKU имеет две pick face;
- задачи сортируются по pick sequence;
- pick face capacity учитывается при планировании.

Критерий готовности:

- покоробочные задачи имеют порядок обхода;
- можно рассчитывать потребность пополнения.

Статус: выполнено. Следующий практический инкремент - `018 Wave Picking Core`.

### Инкремент 5. Migration 018: Wave Picking Core

Цель: реализовать доменную основу волны.

Состав:

- `RRL_PICK_WAVE_SETTING`;
- `RRL_PICK_WAVE`;
- `RRL_PICK_WAVE_ORDER`;
- `RRL_PICK_WAVE_LINE`;
- `RRL_PICK_WAVE_RESERVATION`;
- `RRL_PICK_WAVE_DEMAND`;
- `RRL_PICK_WAVE_REPLENISH_TASK`;
- `RRL_PICK_WAVE_TASK`;
- `RRL_PICK_WAVE_SHORTAGE`;
- `RRL_PICK_WAVE_AUDIT`;
- package `RRL_PICK_WAVE_API`.

Логика:

- создание волны;
- расчет кандидатов;
- preview;
- запуск волны;
- перевод soft reserve в hard reserve;
- защита от double assignment;
- создание replenishment tasks;
- создание picking tasks;
- отмена до старта физических задач;
- audit.

API:

- `GET /api/picking/waves`;
- `POST /api/picking/waves`;
- `GET /api/picking/waves/candidates`;
- `POST /api/picking/waves/{id}/calculate`;
- `POST /api/picking/waves/{id}/launch`;
- `POST /api/picking/waves/{id}/cancel`;
- `POST /api/picking/waves/{id}/release-reservations`;
- `GET /api/picking/waves/{id}/reservations`;
- `GET /api/picking/waves/{id}/replenishment-tasks`;
- `GET /api/picking/waves/{id}/tasks`;
- `GET /api/picking/waves/{id}/audit`.

Concurrency:

- использовать транзакционную блокировку кандидатов;
- повторно проверять активные резервы перед launch;
- предусмотреть `SKIP LOCKED` или lock/claim таблицу.

Smoke:

- две волны одновременно не берут один паллет;
- запуск волны создает hard reserve;
- отмена до старта задач освобождает reserve;
- отмена после старта задач блокируется.

Критерий готовности:

- hard reservation работает;
- задачи пополнения и отбора создаются;
- audit полный.

Статус: выполнено через migration `018`. PL/SQL smoke и HTTP smoke прошли, cleanup оставил `SMOKE_018 = 0` и `SMOKE_018_HTTP = 0`, Oracle invalid objects = `0`. Следующий практический инкремент - `Admin UI: Picking Planning / Wave Picking`.

### Инкремент 6. Admin UI: Picking Planning

Цель: дать диспетчеру просмотр плана комплектации.

Файлы:

- `wiki-raw/wms_admin_ui_reference/picking-plans.html`;
- `wiki-raw/wms_admin_ui_reference/picking-plans.js`;
- nav link и права.

Права:

- `PICK_PLAN_VIEW`;
- `PICK_PLAN_CREATE`;
- `PICK_PLAN_CANCEL`;
- `PICK_RESERVATION_VIEW`;
- `PICK_SHORTAGE_VIEW`.

Функции:

- список планов;
- карточка плана;
- строки;
- резервы;
- shortage;
- объяснение выбора;
- отмена плана.

Критерий готовности:

- план можно проверить глазами до запуска волны;
- права не hardcoded.

### Инкремент 7. Admin UI: Wave Picking

Цель: реализовать админское ТЗ `wave_picking_admin_tz.md`.

Файлы:

- `wiki-raw/wms_admin_ui_reference/wave-picking.html`;
- `wiki-raw/wms_admin_ui_reference/wave-picking.js`;
- обновление nav;
- возможно общий `wave-picking.css`, если не хватает `styles.css`.

Права:

- `PICK_WAVE_VIEW`;
- `PICK_WAVE_CREATE`;
- `PICK_WAVE_CALCULATE`;
- `PICK_WAVE_LAUNCH`;
- `PICK_WAVE_CANCEL`;
- `PICK_WAVE_RELEASE_RESERVES`;
- `PICK_WAVE_SETTINGS_VIEW`;
- `PICK_WAVE_SETTINGS_EDIT`;
- `PICK_WAVE_AUDIT_VIEW`.

Функции:

- реестр волн;
- фильтры;
- диалог `Запуск волны`;
- список открытых заказов;
- preview;
- запуск;
- карточка волны;
- резервы;
- replenishment tasks;
- picking tasks;
- дефицит;
- аудит;
- настройки волн.

Smoke:

- пользователь без права не видит страницу;
- пользователь с view видит реестр;
- launch button скрыт без права;
- preview не создает hard reserve;
- launch создает hard reserve.

Критерий готовности:

- диспетчер может запустить волну из админки;
- результаты видны без обращения к SQL.

### Инкремент 8. Terminal Flow For Wave Tasks

Цель: дать исполнителям рабочий контур.

Состав:

- endpoints для получения задач;
- endpoints для принятия задачи в работу;
- подтверждение source cell/pallet;
- подтверждение target pick face;
- подтверждение case picking;
- обработка ошибок сканирования.

API:

- `GET /api/terminal/waves/tasks`;
- `POST /api/terminal/waves/tasks/{id}/start`;
- `POST /api/terminal/waves/tasks/{id}/confirm`;
- `POST /api/terminal/waves/tasks/{id}/fail`.

Критерий готовности:

- задача из волны может быть выполнена через терминальный контур;
- статус виден в админке.

### Инкремент 9. WMS Bridge And Physical Movements

Цель: связать задачи волны с физическими движениями старого WMS.

Принцип:

- не менять остатки напрямую;
- использовать legacy movement механизм или уже согласованный WMS bridge;
- все движения связать с `WAVE_ID`, task id и reservation id.

Smoke:

- replenishment task приводит к корректному WMS movement;
- full pallet picking приводит к корректному WMS movement;
- case picking приводит к корректному WMS movement;
- резерв переходит в `CONSUMED`.

Критерий готовности:

- старый WMS видит физический результат;
- новый модуль видит исполнение и audit.

### Инкремент 10. Load, Concurrency And Recovery

Цель: проверить модуль в условиях склада.

Нагрузочные сценарии:

- 1000 заказов;
- 30 клиентов в волне;
- 10 волн подряд;
- два оператора запускают волны одновременно;
- 5000 резервов;
- частичный дефицит;
- отмена волны;
- зависший reserve;
- повторный запуск после сбоя API.

Проверки:

- нет двойного резервирования;
- нет потерянных задач;
- audit полон;
- Oracle invalid objects = `0`;
- API отвечает в приемлемое время;
- cleanup тестовых данных работает.

Критерий готовности:

- модуль можно показывать пользователям как пилот.

## 5. Рекомендуемый Порядок Коммитов

1. Документация и plan baseline.
2. Migration `014` + verify + wiki mirror.
3. Backend customer/order API + smoke.
4. Migration `015` + customer rules API.
5. Migration `016` + picking plan API + reservations smoke.
6. Migration `017` + pick face API.
7. Migration `018` + wave API + launch/cancel smoke.
8. Admin page `picking-plans`.
9. Admin page `wave-picking`.
10. Terminal flow.
11. WMS bridge.
12. Load tests and recovery tests.

Каждый коммит должен быть небольшим и проверяемым.

## 6. Риски И Меры

### Риск 1. Двойное Резервирование

Мера:

- единый механизм резервов;
- транзакционная блокировка;
- smoke на конкурентный запуск.

### Риск 2. Расхождение Со Старым WMS

Мера:

- физические движения только через WMS bridge;
- новые планы не пишут остатки напрямую;
- сверка после smoke.

### Риск 3. Сложные Клиентские Правила

Мера:

- priority rules;
- period validity;
- fallback к default;
- decision log.

### Риск 4. Админка Показывает Не То, Что В Базе

Мера:

- все данные только через API;
- backend rights check;
- audit на каждое действие;
- smoke UI/API.

### Риск 5. Кракозябры В Русских Документах И Seed

Мера:

- `scripts/check-encoding.ps1`;
- OracleApply strict UTF-8;
- не использовать неявные encodings.

## 7. Критерий Готовности Всего Блока

Блок `Комплектация + Сборка по волнам` считается готовым для MVP, когда:

- клиент и заказ клиента живут как отдельные сущности;
- legacy `RRL_ORDERS.ADDR` корректно мапится на клиента;
- клиентские правила срока годности, укладки и машины применяются;
- заказ можно рассчитать в picking plan;
- свободный остаток считается с учетом резервов;
- дефицит фиксируется и виден оператору;
- волна может включить несколько клиентов в рамках лимита;
- preview волны показывает последствия запуска;
- запуск волны создает hard reservations;
- задачи пополнения и отбора создаются и видны в админке;
- терминальный контур может исполнять задачи;
- физические движения проходят через WMS bridge;
- аудит и API audit работают;
- права не hardcoded;
- Oracle invalid objects = `0`;
- есть smoke, cleanup и load-проверки.

## 8. Ближайший Практический Шаг

Следующий разумный шаг реализации:

1. Сделать raw admin page для просмотра picking plans: строки, резервы, shortages, decision log.
2. Сделать raw admin page для wave picking: реестр волн, кандидаты, preview, launch, cancel, hard reservations, replenishment tasks, picking tasks и audit.
3. Добавить smoke UI/API на права: пользователь без `pick_wave_view` не видит страницу, без `pick_wave_launch` не может запускать волну.
4. После admin UI перейти к terminal flow для выполнения wave tasks.

Это переведёт модуль от backend/API ядра к рабочему диспетчерскому экрану склада.
