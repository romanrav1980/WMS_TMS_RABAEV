# RRL_RECEIPT_SKU_RULE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Приёмка.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `PICK_CELL` | VARCHAR2(60 bytes) | N |  |
| `TEMP_MIN` | NUMBER | Y |  |
| `TEMP_MAX` | NUMBER | Y |  |
| `MIN_SHELF_DAYS` | NUMBER | N |  |
| `SOURCE_PICK_MODE` | VARCHAR2(20 bytes) | N |  |
| `SHIP_FROM_STOCK` | NUMBER | Y |  |
| `STOCK_ALLOC_CLASS` | VARCHAR2(20 bytes) | N |  |
| `PICK_STEP_BASE` | NUMBER | N |  |
| `ALLOCATION_VERSION` | NUMBER | N |  |
| `ALLOW_PICK_BATCH_MIX` | NUMBER(1,0) | N |  |
| `QC_BASE_WEIGHT_KG` | NUMBER | Y |  |
| `QC_BOX_WEIGHT_KG` | NUMBER | Y |  |
| `QC_WEIGHT_VERSION` | NUMBER | N |  |
| `QC_WEIGHT_BASE_UOM` | VARCHAR2(20 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_ALLOCATION_RULE_CK | C | PICK_STEP_BASE, STOCK_ALLOC_CLASS, SHIP_FROM_STOCK, ALLOCATION_VERSION |  | ENABLED |
| RRL_RECEIPT_SOURCE_MODE_CK | C | SOURCE_PICK_MODE |  | ENABLED |
| RRL_REC_SKUR_PK | P | WARE_ID, ARTICUL |  | ENABLED |
| RRL_REC_SKUR_SHELF_CK | C | MIN_SHELF_DAYS |  | ENABLED |
| RRL_REC_SKUR_TEMP_CK | C | TEMP_MIN, TEMP_MAX |  | ENABLED |
| SYS_C0015983 | C | WARE_ID |  | ENABLED |
| SYS_C0015984 | C | ARTICUL |  | ENABLED |
| SYS_C0015985 | C | PICK_CELL |  | ENABLED |
| SYS_C0015986 | C | MIN_SHELF_DAYS |  | ENABLED |
| SYS_C0016198 | C | SOURCE_PICK_MODE |  | ENABLED |
| SYS_C0016230 | C | STOCK_ALLOC_CLASS |  | ENABLED |
| SYS_C0016231 | C | PICK_STEP_BASE |  | ENABLED |
| SYS_C0016232 | C | ALLOCATION_VERSION |  | ENABLED |
| SYS_C0016256 | C | ALLOW_PICK_BATCH_MIX |  | ENABLED |
| SYS_C0016257 | C | ALLOW_PICK_BATCH_MIX |  | ENABLED |
| SYS_C0016275 | C | QC_WEIGHT_VERSION |  | ENABLED |
| SYS_C0016276 | C | QC_BASE_WEIGHT_KG |  | ENABLED |
| SYS_C0016277 | C | QC_BOX_WEIGHT_KG |  | ENABLED |
| SYS_C0016278 | C | QC_WEIGHT_VERSION |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_DIRECT_RECEIVING_PICK](../programs/RRL_DIRECT_RECEIVING_PICK.md), [RRL_INTERWARE_THERMAL](../programs/RRL_INTERWARE_THERMAL.md), [RRL_IW_GROUP_THERMAL](../programs/RRL_IW_GROUP_THERMAL.md), [RRL_QC_MASS_POLICY_GUARD](../programs/RRL_QC_MASS_POLICY_GUARD.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_POOL_CMD](../programs/RRL_STOCK_POOL_CMD.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_WEIGHT](../programs/RRL_STOCK_QC_WEIGHT.md), [RRL_STOCK_REPL_ADMISSION](../programs/RRL_STOCK_REPL_ADMISSION.md), [RRL_STOCK_RETURN_REUSE](../programs/RRL_STOCK_RETURN_REUSE.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RECEIPT_SKU_RULE` в файле соответствующего типа.
