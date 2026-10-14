# RRL_ORDER_ROWS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `ORDER_ID` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `SHORTNAME` | VARCHAR2(255 bytes) | Y |  |
| `EI` | VARCHAR2(40 bytes) | Y |  |
| `ORDER_WEIGHT` | NUMBER | Y |  |
| `QUANTITY` | NUMBER | N |  |
| `SORTFIELD` | NUMBER | Y |  |
| `WARE_ID` | NUMBER | N |  |
| `PACK_COUNT` | NUMBER | Y |  |
| `ORIGINAL_QUANTITY` | NUMBER | Y |  |
| `ORIGINAL_ORDER_WEIGHT` | NUMBER | Y |  |
| `CONDITION` | NUMBER | Y |  |
| `TARESIZE` | NUMBER | Y |  |
| `TAREWEIGHT` | NUMBER | Y |  |
| `MOD_ID` | NUMBER | Y |  |
| `QUANTITY_PLANNED` | NUMBER | Y |  |
| `PARTIONPLANNED` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_ORDER_ROWS_PK | P | ID |  | ENABLED |
| SYS_C0013469 | C | ID |  | ENABLED |
| SYS_C0013470 | C | ORDER_ID |  | ENABLED |
| SYS_C0013471 | C | ARTICUL |  | ENABLED |
| SYS_C0013472 | C | QUANTITY |  | ENABLED |
| SYS_C0013473 | C | WARE_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[COMPL](../programs/COMPL.md), [ORDERS](../programs/ORDERS.md), [RRL_CUSTOMER_ORDER_API](../programs/RRL_CUSTOMER_ORDER_API.md), [RRL_ORDERS_DELETE](../programs/RRL_ORDERS_DELETE.md), [RRL_ORDER_ROWS_TRG](../programs/RRL_ORDER_ROWS_TRG.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ORDER_ROWS` в файле соответствующего типа.
