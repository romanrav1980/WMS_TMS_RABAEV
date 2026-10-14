# RRL_RECEIPT_WARE_SETTINGS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Приёмка.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `COMPANY_PREFIX` | VARCHAR2(12 bytes) | Y |  |
| `EXTENSION_DIGIT` | NUMBER(1,0) | N |  |
| `COORDINATE_UNIT_M` | NUMBER | N |  |
| `REACHTRUCK_MPS` | NUMBER | N |  |
| `LIFT_MPS` | NUMBER | N |  |
| `PLACEMENT_METRIC` | VARCHAR2(20 bytes) | N |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |
| `HU_CELL_HEIGHT_UNIT` | VARCHAR2(2 bytes) | Y |  |
| `OUTGOING_QC_MODE` | VARCHAR2(10 bytes) | Y |  |
| `OUTGOING_QC_INDEPENDENT` | NUMBER | N |  |
| `OUTGOING_QC_SAMPLE_PERCENT` | NUMBER | N |  |
| `DEFER_WAIT_CELL` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_REC_WSET_EXT_CK | C | EXTENSION_DIGIT |  | ENABLED |
| RRL_REC_WSET_METRIC_CK | C | PLACEMENT_METRIC |  | ENABLED |
| RRL_REC_WSET_PK | P | WARE_ID |  | ENABLED |
| RRL_REC_WSET_SPEED_CK | C | COORDINATE_UNIT_M, REACHTRUCK_MPS, LIFT_MPS |  | ENABLED |
| SYS_C0015973 | C | WARE_ID |  | ENABLED |
| SYS_C0015974 | C | EXTENSION_DIGIT |  | ENABLED |
| SYS_C0015975 | C | COORDINATE_UNIT_M |  | ENABLED |
| SYS_C0015976 | C | REACHTRUCK_MPS |  | ENABLED |
| SYS_C0015977 | C | LIFT_MPS |  | ENABLED |
| SYS_C0015978 | C | PLACEMENT_METRIC |  | ENABLED |
| SYS_C0016274 | C | HU_CELL_HEIGHT_UNIT |  | ENABLED |
| SYS_C0016283 | C | OUTGOING_QC_INDEPENDENT |  | ENABLED |
| SYS_C0016284 | C | OUTGOING_QC_MODE |  | ENABLED |
| SYS_C0016285 | C | OUTGOING_QC_INDEPENDENT |  | ENABLED |
| SYS_C0016293 | C | OUTGOING_QC_SAMPLE_PERCENT |  | ENABLED |
| SYS_C0016294 | C | OUTGOING_QC_SAMPLE_PERCENT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_DEFER_WAIT_CELL_GUARD](../programs/RRL_DEFER_WAIT_CELL_GUARD.md), [RRL_QC_SCOPE_READ](../programs/RRL_QC_SCOPE_READ.md), [RRL_QC_WARE_POLICY_GUARD](../programs/RRL_QC_WARE_POLICY_GUARD.md), [RRL_SSCC_ALLOCATOR](../programs/RRL_SSCC_ALLOCATOR.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_QC_POLICY](../programs/RRL_STOCK_QC_POLICY.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_PHYSICAL](../programs/RRL_ST_DEFER_PHYSICAL.md), [RRL_ST_DEFER_PLACE_READ](../programs/RRL_ST_DEFER_PLACE_READ.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RECEIPT_WARE_SETTINGS` в файле соответствующего типа.
