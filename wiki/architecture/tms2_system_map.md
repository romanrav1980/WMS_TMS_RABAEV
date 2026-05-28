# ТМС-2 — карта системы

Дата обновления: 2026-05-28.

Назначение: быстрый архитектурный обзор ТМС-2 для разработки, ревью и восстановления контекста.

## Границы проекта

ТМС-2 заменяет legacy C# транспортный модуль на FastAPI + React, сохраняя совместимость с Oracle `RABAEV` и важными legacy PL/SQL правилами.

Входит:

- диспетчер рейсов;
- карта заказов и VRP;
- ARM/Гант операций;
- биллинг транспорта;
- API/admin frontend для этих контуров;
- Oracle migrations и compatibility fixes для transport domain.

Не входит:

- `warehouse-map`;
- MES;
- WMS picking/wave;
- SAP/SAP integration;
- другие WMS-модули вне transport domain.

## Runtime слои

| Слой | Назначение | Основные файлы |
|---|---|---|
| React admin frontend | UI диспетчера, карты, Ганта, биллинга | `admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx`, `TransportPlannerPage.tsx`, `styles.css` |
| FastAPI router | HTTP endpoints, permissions, schemas | `api/wms_api_server/app/routers/transport.py`, `schemas.py` |
| Service layer | Бизнес-логика и адаптация legacy Oracle | `api/wms_api_server/app/services/transport_service.py`, `distance_matrix_service.py` |
| Oracle gateway | SQL/PLSQL execution, audit, transaction boundary | `api/wms_api_server/app/oracle_gateway.py` |
| Oracle schema | Tables, views, packages, legacy functions | `RRL_TRANSPORT_TASK`, `RRL_SBORKA_PALLETS`, `RRL_BILL_ORDERS`, `RRL_TR_VEHICLE`, `RRL_ADDR_DISTANCE_MATRIX`, `RRL_PLANNER_PLANS` |
| Tests | Functional API acceptance | `tests/transport/test_sprint*_functional.py` |

## Блоки и владение данными

### Dispatcher, Sprint 1-6

Главный объект: `RRL_TRANSPORT_TASK`.

Связанные данные:

- `RRL_SBORKA_PALLETS` — СТ и паллеты, назначение на рейс через `TRANSTASK_ID`.
- `RRL_SBORKA_PALLET_ROWS` — строки паллет.
- `RRL_TRANSPORT_TYPE` — типы транспорта и нормы.
- `RRL_TR_VODITEL` — водитель, телефон, транспортная компания через `DOVERENNOST_OT`.

Ключевые API:

- `GET /api/admin/transport/available-sts`
- `GET /api/admin/transport/tasks`
- `POST /api/admin/transport/tasks`
- `PATCH /api/admin/transport/tasks/{id}`
- `POST /api/admin/transport/tasks/{id}/close`
- `POST /api/admin/transport/tasks/{id}/cancel`
- `GET/POST/DELETE /api/admin/transport/tasks/{id}/sts`

### MAP / VRP, Sprint 7-10

Главные объекты:

- `RRL_ADDR` coordinates;
- `RRL_ADDR_DISTANCE_MATRIX`;
- `RRL_PLANNER_PLANS`.

Ключевые API:

- `GET /planner/orders`
- `GET /routing/status`
- `POST /distance-matrix/rebuild`
- `POST /planner/solve`
- `POST /planner/apply`
- `GET /planner/metrics`
- `GET /planner/history`
- `GET /planner/demand-forecast`

Critical rule: `apply_vrp_plan` must not return success if route update or ST assignment fails.

### ARM / Gantt, Sprint 11-14

Главные объекты:

- `RRL_TT_OPERATIONS`;
- `RRL_TRANSPORT_NORMS`;
- `RRL_TR_VEHICLE`;
- `RRL_TRANSPORT_TASK`.

Ключевые API:

- `POST /tasks/{id}/operations/plan`
- `GET /tasks/{id}/operations`
- `GET /gantt/vehicles`
- `GET /vehicles/available`
- `GET /plan-fact`

Critical rule: legacy task status is `CONDITION`, not `STATUS`; deletion is `DELETED`.

### Billing, Sprint 15-20

Главные объекты:

- `RRL_BILL_ORDERS`;
- `RRL_TRANSPORT_TASK.PAY_ORDER_ID`;
- `RRL_TRANSPORT_TASK.PRICE`;
- `RRL_TR_VODITEL.DOVERENNOST_OT`.

Ключевые API:

- `GET/POST /billing/orders`
- `GET /billing/orders/{id}`
- `PATCH /billing/orders/{id}/close`
- `PATCH /billing/orders/{id}/pay`
- `GET/POST/DELETE /billing/orders/{id}/tasks`
- `GET /tasks/{id}/billing`
- `POST /tasks/{id}/billing/open`
- `POST /tasks/{id}/recalculate-price`
- `PATCH /tasks/{id}/price`

Critical rule: billed task with `PAY_ORDER_ID` cannot be canceled or have ST composition changed.

## API contract notes

- Transport endpoints generally return legacy uppercase keys for compatibility.
- `GET /tasks` accepts both `shipment_date` and legacy alias `stdate`.
- Billing endpoints use normalized JSON field names such as `order_id`, `task_count`, `total_price`.
- Oracle business-rule messages from legacy functions should surface as 409, not silent success.

## Verification map

Primary acceptance document: [`../requirements/tms2_acceptance_matrix.md`](../requirements/tms2_acceptance_matrix.md).

Current status anchor: [`../subprojects/tms2_current_status.md`](../subprojects/tms2_current_status.md).

