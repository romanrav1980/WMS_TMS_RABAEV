# ТМС-2 — Oracle contract

Дата обновления: 2026-05-28.

Назначение: зафиксировать реальные Oracle-объекты, сигнатуры и compatibility-правила ТМС-2, чтобы не чинить одни и те же рассинхроны повторно.

## Общие правила

- Работать против реальных legacy column names, а не предполагаемой новой схемы.
- Перед использованием legacy function/package проверить `ALL_ARGUMENTS` и `ALL_SOURCE`.
- Если Oracle function делает DML, вызывать ее через PL/SQL block, не через `SELECT ... FROM DUAL`.
- Ошибки бизнес-правил из Oracle не глушить. Возвращать 409/422/404 по смыслу.
- `rows_as_dicts()` может возвращать lowercase; transport service должен нормализовать публичный legacy contract.
- Избегать `TRUNC(date_column)` в фильтрах больших выборок; использовать half-open ranges.

## Dispatcher tables/views

| Объект | Роль | Важные поля |
|---|---|---|
| `RRL_TRANSPORT_TASK` | Рейс | `ID`, `TRANSPORT`, `TRANSTYPE`, `CONDITION`, `SHIPMENT_DATE`, `VODITEL_ID`, `PRICE`, `PAY_ORDER_ID`, `DELETED`, `TEMP_REGION`, `TEMP_WEIGHT` |
| `RRL_SBORKA_PALLETS` | СТ/паллеты | `ST_NUMBER`, `PALLET_UID`, `TRANSTASK_ID`, `STDATE`, `WARE_ID`, `CONDITION`, `LOAD_TYPE`, `ORD` |
| `RRL_SBORKA_PALLET_ROWS` | Товарные строки паллет | `PALLET_UID`, `ARTICUL`, `NAME`, `PACK_COUNT`, `TARESIZE` |
| `RRL_V_AVAILABLE_STS` | Свободные СТ для диспетчера/planner | реальные optional поля проверять через `ALL_TAB_COLUMNS` |
| `RRL_TRANSPORT_TYPE` | Типы транспорта | `TRANSPORTTYPE`, `NORMA_PALLET`, `NORMA_WEIGHT`, `REF`, `ORD` |
| `RRL_TR_VODITEL` | Водители/ТК | `ID`, `F`, `I`, `O`, `TEL`, `DOVERENNOST_OT`, `SOBSTVENNYY` |

Known drift:

- `RRL_TRANSPORT_TYPE` does not have `NAME`, `MIN_PALLET_LOAD`, `MAX_PALLET_LOAD`; map from `TRANSPORTTYPE` and `NORMA_PALLET`.
- `RRL_SBORKA_PALLETS` does not expose `DELETED` in the pallet query path; use `CONDITION <> 2`.
- Task status is `CONDITION`, not `STATUS`.

## MAP / VRP objects

| Объект | Роль | Важные поля |
|---|---|---|
| `RRL_ADDR` | Адреса и координаты | `ADDR`, `SHIROTA`, `DOLGOTA` |
| `RRL_ADDR_DISTANCE_MATRIX` | Матрица расстояний | `FROM_ADDR`, `TO_ADDR`, `DISTANCE_KM`, `DURATION_MIN`, `SOURCE`, `UPDATED_AT` |
| `RRL_PLANNER_PLANS` | Сохраненные планы | `ID`, `PLAN_DATE`, `CREATED_AT`, `SOLVER`, `SCORE`, `PAYLOAD`, `APPLIED_AT` |

Fixture note, 2026-05-29: migration `db/migrations/2026-05-29_tms2_planner_template_fixture/055_apply.sql` inserts a deterministic Sprint 9 historical planner-template row into `RRL_PLANNER_PLANS` (`SOLVER='s9-template-fixture'`, `PLAN_DATE=2026-05-23`) using free STs from accepted release seed date `2026-05-24`. A compatibility row for `PLAN_DATE=2026-05-24` is best-effort when `2026-05-25` source STs still exist. Rollback deletes both fixture rows.

Known drift:

- Matrix column is `DISTANCE_KM`, not `DIST_KM`.
- Matrix timestamp is `UPDATED_AT`, not `CALC_AT`.
- Planner payload column is `PAYLOAD`, not `PLAN_JSON`; API may alias it internally.

## ARM / Gantt objects

| Объект | Роль | Важные поля |
|---|---|---|
| `RRL_TRANSPORT_NORMS` | Нормативы операций | operation norm fields from migration 053 |
| `RRL_TT_OPERATIONS` | План/факт операций рейса | `TT_ID`, operation type, planned/fact timestamps |
| `RRL_TR_VEHICLE` | Машины | vehicle number/type/capacity fields |

Known drift:

- Do not join nonexistent `RRL_TRANSPORTS`; use `RRL_TR_VEHICLE`.
- `RRL_TT_OPERATIONS` migration must not assume a legacy FK target that Oracle cannot validate.

## Billing objects and functions

| Объект | Роль | Важные поля / сигнатура |
|---|---|---|
| `RRL_BILL_ORDERS` | Счета | `ID`, `NUM`, `COMPANY`, `NUM_PLAT`, `DATEOFORDER`, `DATEFROM`, `DATETO`, `CLOSED`, `PAYED` |
| `RRL_TRANSPORT_TASK.PAY_ORDER_ID` | Связь рейса со счетом | `NULL/0` means not billed |
| `RRL_UPDATE_PRICE` | Пересчет цены | function returns `NUMBER`, arg `TT_ID NUMBER IN`, performs DML |
| `RRL_ADD_TT_2_BILLINGORDER` | Add/remove task in bill | function returns `VARCHAR2`, args `BILL_ID`, `TT_ID`, `ACT`; performs DML |
| `RRL_CLOSE_BILLINGORDER` | Закрыть счет | function returns `VARCHAR2`, args `BILL_ID`, `ACT`; performs DML |
| `RRL_PAY_BILLINGORDER` | Оплатить счет | function returns `VARCHAR2`, args `BILL_ID`, `ACT`; performs DML |

Business rules observed in legacy source:

- Task company must equal bill company via `RRL_TR_VODITEL.DOVERENNOST_OT`.
- Task price must be calculated and greater than 0.
- Closed bill cannot be changed.
- Billed task cannot be canceled or have ST composition changed.

## Migrations in current TMS-2 scope

| Migration | Назначение | Dev status |
|---|---|---|
| `051_apply.sql` | MAP/geocoding support | Applied in dev |
| `052_apply.sql` | Distance matrix/planner support | Applied in dev |
| `053_apply.sql` | ARM/Gantt operations/norms | Applied in dev after FK compatibility fix |
| `054_apply.sql` | Billing support | Applied in dev after `COMPANY VARCHAR2(200)` compatibility fix |

Before production:

- Run apply on staging/prod-like Oracle.
- Verify object existence and column names.
- Run rollback rehearsal where possible.
- Run functional gates from [`../requirements/tms2_acceptance_matrix.md`](../requirements/tms2_acceptance_matrix.md).
