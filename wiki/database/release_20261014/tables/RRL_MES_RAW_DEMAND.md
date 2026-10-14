# RRL_MES_RAW_DEMAND

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `DEMAND_ID` | NUMBER | N |  |
| `PRODUCTION_ORDER_ID` | NUMBER | N |  |
| `ORDER_LINE_ID` | NUMBER | Y |  |
| `BOM_ID` | NUMBER | Y |  |
| `BOM_LINE_ID` | NUMBER | Y |  |
| `RAW_ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `REQUIRED_QTY` | NUMBER | N |  |
| `ISSUED_QTY` | NUMBER | N |  |
| `OPEN_QTY` | NUMBER | N |  |
| `UNIT_CODE` | VARCHAR2(20 bytes) | Y |  |
| `SOFT_RESERVATION_ID` | NUMBER | Y |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `CALCULATED_AT` | TIMESTAMP(6) | N |  |
| `CALCULATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_MES_RAW_DEMAND_CHK1 | C | STATUS |  | ENABLED |
| RRL_MES_RAW_DEMAND_CHK2 | C | OPEN_QTY, ISSUED_QTY, REQUIRED_QTY |  | ENABLED |
| RRL_MES_RAW_DEMAND_PK | P | DEMAND_ID |  | ENABLED |
| SYS_C0014711 | C | DEMAND_ID |  | ENABLED |
| SYS_C0014712 | C | PRODUCTION_ORDER_ID |  | ENABLED |
| SYS_C0014713 | C | RAW_ARTICUL |  | ENABLED |
| SYS_C0014714 | C | REQUIRED_QTY |  | ENABLED |
| SYS_C0014715 | C | ISSUED_QTY |  | ENABLED |
| SYS_C0014716 | C | OPEN_QTY |  | ENABLED |
| SYS_C0014717 | C | STATUS |  | ENABLED |
| SYS_C0014718 | C | CALCULATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_MES_RAW_SUPPLY_OLD](../programs/RRL_MES_RAW_SUPPLY_OLD.md), [RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_MES_RAW_DEMAND` в файле соответствующего типа.
