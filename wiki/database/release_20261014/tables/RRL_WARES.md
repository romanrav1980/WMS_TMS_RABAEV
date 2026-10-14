# RRL_WARES

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | Y |  |
| `NAME` | VARCHAR2(50 bytes) | Y |  |
| `OVERFLOW_CELL_NAME` | VARCHAR2(50 bytes) | Y |  |
| `PREFIX` | VARCHAR2(3 bytes) | Y |  |
| `FAKE_ROWS` | NUMBER | Y |  |
| `FAKE_ART` | VARCHAR2(40 bytes) | Y |  |
| `BLOCK_IF_NO_PROOVE` | NUMBER | Y |  |
| `VERIFY_VYCHERK` | NUMBER | Y |  |
| `WRITE_BOTH_EXPIRYANDBEST` | NUMBER | Y |  |
| `SPIS_IF_HRAN_NO_EMPTY` | VARCHAR2(10 bytes) | Y | Исходный комментарий Oracle повреждён; требуется уточнение. |
| `ALLOW_HALF_VYCHERK` | NUMBER | Y |  |
| `SPIS_OTBOR_ON_SCAN_OPALL` | NUMBER | Y |  |
| `SPIS_OTBOR_ON_WPROOVE_OPALL` | NUMBER | Y |  |
| `TIME_COEFF` | NUMBER | Y |  |
| `XYZ_XCOV` | NUMBER | Y | Исходный комментарий Oracle повреждён; требуется уточнение. |
| `XYZ_YCOV` | NUMBER | Y | Исходный комментарий Oracle повреждён; требуется уточнение. |
| `ABC_A` | NUMBER | Y |  |
| `ABC_B` | NUMBER | Y |  |
| `ABC_XYZ_TIME_EDGES_IN_DAYS` | NUMBER(30,0) | Y |  |
| `VERIFY_VYCHERK_IN_OTBOR` | NUMBER | Y |  |
| `PRINT_EXPIRY_DATE_OP` | NUMBER | Y |  |
| `COUNT_OF_PRINTS` | NUMBER | Y |  |
| `WEIGHT_LIMIT_WARNING` | NUMBER | Y |  |
| `WEIGHT_LIMIT_STOP` | NUMBER | Y |  |
| `PARENT_WARE_ID` | NUMBER | Y |  |
| `ORD2` | NUMBER | Y |  |
| `COUNT_WEIGHT_AUTORECALC` | NUMBER | Y |  |
| `AUTO_PLAN_DOCK` | NUMBER | Y |  |
| `FLAG_RAW_MATERIAL` | NUMBER(1,0) | Y |  |
| `FLAG_PRODUCTION` | NUMBER(1,0) | Y |  |
| `FLAG_PRODUCTION_BUFFER` | NUMBER(1,0) | Y |  |
| `FLAG_FINISHED_GOODS` | NUMBER(1,0) | Y |  |
| `MES_ENABLED` | NUMBER(1,0) | Y |  |
| `DEFAULT_RECEIVE_CELL` | VARCHAR2(20 bytes) | Y |  |
| `DEFAULT_ISSUE_CELL` | VARCHAR2(20 bytes) | Y |  |
| `WARE_COMMENT` | VARCHAR2(1000 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WARES_CK_ID_POS | C | ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[DOCK_PLANNING](../programs/DOCK_PLANNING.md), [RRL_ABC_CALCULATE](../programs/RRL_ABC_CALCULATE.md), [RRL_DAY_INSPECT_API](../programs/RRL_DAY_INSPECT_API.md), [RRL_DAY_REVIEW_API](../programs/RRL_DAY_REVIEW_API.md), [RRL_INTERNAL_MOVE3_SP_OLD](../programs/RRL_INTERNAL_MOVE3_SP_OLD.md), [RRL_LOG_COST_PERIOD_HISTORY_G](../programs/RRL_LOG_COST_PERIOD_HISTORY_G.md), [RRL_LOG_RATE_HEAD_GUARD](../programs/RRL_LOG_RATE_HEAD_GUARD.md), [RRL_MES_RAW_SUPPLY_OLD](../programs/RRL_MES_RAW_SUPPLY_OLD.md), [RRL_PALLET_FLOOR_READ](../programs/RRL_PALLET_FLOOR_READ.md), [RRL_PRIHODPALLET_CHANGE_COUNT](../programs/RRL_PRIHODPALLET_CHANGE_COUNT.md), [RRL_PRIHODPALLET_CHANGE_WEIGHT](../programs/RRL_PRIHODPALLET_CHANGE_WEIGHT.md), [RRL_QC_SCOPE_READ](../programs/RRL_QC_SCOPE_READ.md), [RRL_QC_SCOPE_RULE_GUARD](../programs/RRL_QC_SCOPE_RULE_GUARD.md), [RRL_SET_SCAN_PROOVE2_SP_OLD](../programs/RRL_SET_SCAN_PROOVE2_SP_OLD.md), [RRL_SET_SCAN_PROOVE_SP_OLD](../programs/RRL_SET_SCAN_PROOVE_SP_OLD.md), [RRL_SKLADNAME_BY_ID](../programs/RRL_SKLADNAME_BY_ID.md), [RRL_STOCK_INTERNAL_CMD](../programs/RRL_STOCK_INTERNAL_CMD.md), [RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md), [RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_POLICY](../programs/RRL_STOCK_QC_POLICY.md), [RRL_STOCK_STORE_RETURN_SAP_CMD](../programs/RRL_STOCK_STORE_RETURN_SAP_CMD.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_RESOLVE](../programs/RRL_STOCK_TARE_RESOLVE.md), [RRL_STORE_CALENDAR_API](../programs/RRL_STORE_CALENDAR_API.md), [RRL_STORE_RETURN_WARE_GUARD](../programs/RRL_STORE_RETURN_WARE_GUARD.md), [RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md), [RRL_TRANSPORT_NORM_API](../programs/RRL_TRANSPORT_NORM_API.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md), [RRL_TRIAL_BY_WEIGHT2_SP_OLD](../programs/RRL_TRIAL_BY_WEIGHT2_SP_OLD.md), [RRL_TT_PLAN_DOCK](../programs/RRL_TT_PLAN_DOCK.md), [RRL_WARE_DEPOT_API](../programs/RRL_WARE_DEPOT_API.md), [RRL_WORKLOAD_CONFIG_API](../programs/RRL_WORKLOAD_CONFIG_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WARES` в файле соответствующего типа.
