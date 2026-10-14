# RRL_ORDERS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `ORD_NUMBER` | VARCHAR2(50 bytes) | N |  |
| `CREATE_DATE` | DATE | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ADDR` | VARCHAR2(255 bytes) | Y |  |
| `STATE` | VARCHAR2(50 bytes) | Y |  |
| `ORDDATE` | DATE | Y |  |
| `USER_ID` | VARCHAR2(50 bytes) | Y |  |
| `COND` | NUMBER | Y |  |
| `ORD1` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_ORDERS_PK | P | ID |  | ENABLED |
| SYS_C0013475 | C | ID |  | ENABLED |
| SYS_C0013476 | C | ORD_NUMBER |  | ENABLED |
| SYS_C0013477 | C | CREATE_DATE |  | ENABLED |
| SYS_C0013478 | C | WARE_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[COMPL](../programs/COMPL.md), [ORDERS](../programs/ORDERS.md), [RRL_CUSTOMER_ORDER_API](../programs/RRL_CUSTOMER_ORDER_API.md), [RRL_ORDERS_DELETE](../programs/RRL_ORDERS_DELETE.md), [RRL_ORDERS_TRG](../programs/RRL_ORDERS_TRG.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ORDERS` в файле соответствующего типа.
