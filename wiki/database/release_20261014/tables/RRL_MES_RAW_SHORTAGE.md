# RRL_MES_RAW_SHORTAGE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SHORTAGE_ID` | NUMBER | N |  |
| `PRODUCTION_ORDER_ID` | NUMBER | N |  |
| `DEMAND_ID` | NUMBER | Y |  |
| `RAW_ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `REQUIRED_QTY` | NUMBER | N |  |
| `ISSUED_QTY` | NUMBER | N |  |
| `AVAILABLE_QTY` | NUMBER | N |  |
| `SHORTAGE_QTY` | NUMBER | N |  |
| `UNIT_CODE` | VARCHAR2(20 bytes) | Y |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `RESOLVED_AT` | TIMESTAMP(6) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_MES_RAW_SHORTAGE_CHK1 | C | STATUS |  | ENABLED |
| RRL_MES_RAW_SHORTAGE_CHK2 | C | REQUIRED_QTY, ISSUED_QTY, AVAILABLE_QTY, SHORTAGE_QTY |  | ENABLED |
| RRL_MES_RAW_SHORTAGE_PK | P | SHORTAGE_ID |  | ENABLED |
| SYS_C0014733 | C | SHORTAGE_ID |  | ENABLED |
| SYS_C0014734 | C | PRODUCTION_ORDER_ID |  | ENABLED |
| SYS_C0014735 | C | RAW_ARTICUL |  | ENABLED |
| SYS_C0014736 | C | REQUIRED_QTY |  | ENABLED |
| SYS_C0014737 | C | ISSUED_QTY |  | ENABLED |
| SYS_C0014738 | C | AVAILABLE_QTY |  | ENABLED |
| SYS_C0014739 | C | SHORTAGE_QTY |  | ENABLED |
| SYS_C0014740 | C | STATUS |  | ENABLED |
| SYS_C0014741 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_MES_RAW_SUPPLY_OLD](../programs/RRL_MES_RAW_SUPPLY_OLD.md), [RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_MES_RAW_SHORTAGE` в файле соответствующего типа.
