# C-0049 · Исследование: что уже есть и на что опирается ролевая модель

Дата 14.10.2026. Источники: исходники `api/wms_api_server/app`, `admin/wms_admin_frontend`, `terminal/wms_terminal_web`, `wiki-raw/wms_admin_ui_reference`, ТЗ ред. 57 (`wiki/requirements/retailcase_business_processes`), договор модульной разработки. Живые данные — только GET существующего API (`reports/.../C0049/live_rights_snapshot.txt`, без персональных данных). Runtime не менялся.

Машинные приложения: [api_inventory.md](api_inventory.md) / `.json` — 686 маршрутов с правом; [permission_usage.md](permission_usage.md) — право → маршруты → число групп в RIGHTS. Генераторы — `../tools/`.

## 1. Модель доступа сегодня (факт)

| Элемент | Где | Свойство, важное для ролей |
|---|---|---|
| Пользователь | `RUSERS(ID, NAME, PASS, USER_GROUP, WARE_ID, SMENA, PRAVO_*…)` | **Ровно одна группа** доступа; одна область склада `WARE_ID` (default 1); legacy флаги `PRAVO_*` desktop |
| Группа | `USER_GROUP(ID VARCHAR2(15), NAME)` | Код ≤ 15 символов |
| Право | `RIGHTS(USER_GROUP, RIGHT1 VARCHAR2(30), DESCR)` | Право ≤ 30 символов, нижний регистр в API |
| Python | `auth.load_admin_user` → `GLOBAL_ADMIN` = `{"*"}`, иначе права группы; `PRAVO_ADMIN_LOGIN=1` добавляет `wms_admin_login` | `require_permission(code)` → 403 `Permission required: code` |
| Oracle | `RRL_HAS_WRIGHT(user, right)` | GLOBAL_ADMIN → 1; иначе RIGHTS группы; исключение → 0. Используется в delivery/finance/store сценариях (подтверждение получателя, согласование затрат, ingest весов) |
| Область | `WARE_ID` пользователя; отдельные проверки в SQL (`cost_access`, `store_directory.card`, scope QC/workload) | Общего механизма «область роли» нет: магазин/регион/перевозчик не моделируются |
| Исполнение | модуль `resources`: ресурсы, оборудование, квалификации, смены, сессии ТСД, нагрузка, dispatch-nearest | Это и есть «фактический исполнитель задачи» по ТЗ (сотрудник + техника + пост) |
| Водитель | `driver-bindings` (`/api/transport/driver-bindings`) + `/api/driver/*` (проверка привязки учётной записи к водителю) | Отдельная модель, не через права группы |

**Вывод для проекта.** Совмещение ролей и области магазина/региона/перевозчика сегодня невыразимы: одна `USER_GROUP`, один `WARE_ID`. Нужен аддитивный слой назначений, при котором прежняя группа продолжает работать без изменений (см. permission_matrix.md §2).

## 2. Живые группы (снимок 14.10.2026, 758 активных, 237 групп, 157 прав)

| Группа | Польз. | Права в RIGHTS | Вероятная должность (подтвердить у владельца) |
|---|---|---|---|
| SBORSHIK | 401 | — (desktop/терминал по legacy) | комплектовщик |
| SHTABELER | 71 | — | водитель ричтрака/штабелёра |
| KLADOVSHIK | 51 | check_weight, create_vycherk, komplect, view_billing, view_vesov | кладовщик / контроль |
| STOCK_MANAGER | 46 | change_articul, check_weight, internal_move, stock_manager, view_billing, view_pall_hist, view_route, view_vesov | контролёр остатков / учёт |
| VESOV | 46 | check_weight, create_fake_pal, create_vycherk, internal_move, op_change, op_delete, view_route, view_vesov | весовой контроль |
| STOPPER | 21 | create_vycherk, divide_st, load_st, view_route, view_vesov | экспедиция / погрузка («стопер» ворот) |
| GLOBAL_ADMIN | 20 | `*` | администраторы |
| NONE | 19 | — | без доступа |
| REVIZOR | 15 | view_route, view_vesov | инвентаризатор (КРО) |
| ST_PRIEMO_SD | 15 | view_route, view_vesov | старший приёмки |
| ST_SMEN | 10 | internal_move, komplect, print_op_passport_unlimit, view_billing, view_route | старший / начальник смены |
| LOGIST | 10 | calc_tt_price, change_addr, change_route, change_tt_dock, change_voditel, create_route, create_tt_price, delete_route, divide_st, edit_bill_tt, load_st, plan_tt_time, view_adress, view_billing, view_route, view_tt_billing, view_vesov | транспортный логист |

Остальные ~225 групп — тестовые (Q*, QC*, DR*, OWN*), созданные проверками; не переносить в каталог.

**Важно:** 45 прав существуют только в RIGHTS (legacy desktop `WindowsApplication2`, терминал) и не проверяются новым API; их семантику сохраняем как есть. 12 прав проверяются API, но **не выданы ни одной группе** — сейчас доступны только GLOBAL_ADMIN: `warehouse_receipt_confirm`, `warehouse_receipt_reconcile`, `sap_supply_view`, `sap_return_import`, `warehouse_task_assign`, `stock_receipt_reverse`, `stock_posting_manual_move`, `stock_compatibility_admin`, `store_return_transport`, `tare_adjust`, `transport_dispatch_close`, `transport_fleet_edit`. Без ролевых групп приёмка по SAP и закрытие рейсов фактически требуют администратора.

## 3. Рабочие места, которые уже есть

- **Raw UI (`wiki-raw/wms_admin_ui_reference`, 56 страниц, меню `admin-nav.js` с `data-permission`)**: приёмка SAP, складские задания, ТСД ричтрака, ТСД сборки, комплектация, панель смены по волне, пополнение волны, симуляция, ресурсы, нагрузка, прогноз, контроль отгрузки, грузовые места, пересчёт, погрузка и выезд, межсклад, возвраты (магазин → склад → поставщик/утилизация), тара (8 экранов), расследования поставок, сверка дня, затраты/расходы, магазины, права, API-аудит, внешние отправки, MES/BOM/сырьё/ГП.
- **React admin (`App.tsx`)**: twin (цифровой двойник), warehouse-map, topology, transport (диспетчеризация), planner (VRP), gantt, fleet, kpi, users, driver (мобильная страница водителя); `features/delivery` — акт магазинной приёмки, кейсы, весы.
- **Терминал PWA (`terminal/wms_terminal_web`)**: товар по EAN/DataMatrix, паллета, место, производство, legacy TSERVER, диагностика; журнал намерений draft/sent/accepted/rejected/uncertain.
- **Уведомления**: `/api/admin/notifications/*` (подписка/рассылка/настройки) — пригодны для эскалаций, но защищены только `transport_dispatch_view`.

## 4. Найденные проблемы вне объёма C-0049 (передать владельцу/root)

1. **Без аутентификации:** `routers/production.py` — все `/api/production-batches/*`, `/api/raw-batches*`, `/api/aggregations/*`, `/api/mercury-operations*`, `/api/regulatory/*`, `/api/crpt-codes/status` (включая POST/PATCH). `POST /api/gps/track` тоже без проверки (возможно, намеренно для трекеров — нужен токен устройства).
2. `/api/terminal/*` и `/api/legacy/tserver/execute` требуют только вход (`get_current_admin`), без права — допуск определяется legacy процедурами.
3. Несоответствие уровня права действию: `POST /api/admin/notifications/broadcast|settings` — под `transport_dispatch_view`; `GET /api/inventory/tare` и `GET /api/inventory/store-returns` (часть) — под `warehouse_settings_edit`; `rights_admin_edit` проверяется в одном `POST /api/admin/transport/*`.

Эти пункты не исправляются в C-0049 (идёт публикация; runtime заморожен) и перечислены в implementation_plan.md как предварительные условия.

## 5. Роли из ТЗ (resource_management.md и 15 процессов)

ТЗ уже задаёт: начальник склада (ресурсы и правила), начальник смены (план и исключения, выход/перерывы), диспетчер ричтраков (водители ↔ техника), руководитель экспедиции (свои сотрудники), руководитель качества (операции аудиторов), транспортный логист (план, рейсы, ворота), транспортный диспетчер (отгрузка/доставка), управляющий магазина (приёмка), КРО (инвентаризация, потери, корректировки), департамент транспорта (тара), начальник кросс-дока, владельцы справочников, департамент цепей поставок. Группы исполнения: комплектовщики, водители ричтраков, аудиторы инвентаризации, аудиторы собранного товара, консолидация, погрузка, экспедиция кросс-дока. Правило: сотрудник может совмещать роли, но имеет один фонд времени и одно независимое задание.
