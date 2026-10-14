# RRL_MES_RAW_SUPPLY_CANDIDATE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CANDIDATE_ID` | NUMBER | N |  |
| `DEMAND_ID` | NUMBER | N |  |
| `PRODUCTION_ORDER_ID` | NUMBER | N |  |
| `RAW_ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `UID_PALLET` | VARCHAR2(128 bytes) | Y |  |
| `BATCH_ID` | VARCHAR2(100 bytes) | Y |  |
| `RAW_BATCH_ID` | NUMBER | Y |  |
| `SSCC` | VARCHAR2(64 bytes) | Y |  |
| `FROM_WARE_ID` | NUMBER | Y |  |
| `FROM_CELL` | VARCHAR2(80 bytes) | Y |  |
| `PHYSICAL_QTY` | NUMBER | N |  |
| `HARD_RESERVED_QTY` | NUMBER | N |  |
| `AVAILABLE_QTY` | NUMBER | N |  |
| `SUGGESTED_QTY` | NUMBER | N |  |
| `EXPIRY_DATE` | DATE | Y |  |
| `QUALITY_STATUS` | VARCHAR2(30 bytes) | Y |  |
| `SORT_ORDER` | NUMBER | Y |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_MES_RAW_SUPPLY_CAND_CHK1 | C | PHYSICAL_QTY, SUGGESTED_QTY, HARD_RESERVED_QTY, AVAILABLE_QTY |  | ENABLED |
| RRL_MES_RAW_SUPPLY_CAND_PK | P | CANDIDATE_ID |  | ENABLED |
| SYS_C0014722 | C | CANDIDATE_ID |  | ENABLED |
| SYS_C0014723 | C | DEMAND_ID |  | ENABLED |
| SYS_C0014724 | C | PRODUCTION_ORDER_ID |  | ENABLED |
| SYS_C0014725 | C | RAW_ARTICUL |  | ENABLED |
| SYS_C0014726 | C | PHYSICAL_QTY |  | ENABLED |
| SYS_C0014727 | C | HARD_RESERVED_QTY |  | ENABLED |
| SYS_C0014728 | C | AVAILABLE_QTY |  | ENABLED |
| SYS_C0014729 | C | SUGGESTED_QTY |  | ENABLED |
| SYS_C0014730 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_MES_RAW_SUPPLY_OLD](../programs/RRL_MES_RAW_SUPPLY_OLD.md), [RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_MES_RAW_SUPPLY_CANDIDATE` в файле соответствующего типа.
