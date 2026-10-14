# RRL_TRANSPORT_COST_DETAIL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `COST_CODE` | VARCHAR2(40 bytes) | N |  |
| `QUANTITY` | NUMBER(19,0) | N |  |
| `RATE_VALUE` | NUMBER(27,9) | N |  |
| `AMOUNT` | NUMBER(27,2) | N |  |
| `BASIS` | VARCHAR2(20 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TRAN_COST_AMOUNT_CK | C | RATE_VALUE, AMOUNT, QUANTITY |  | ENABLED |
| SYS_C0018727 | C | OPERATION_ID |  | ENABLED |
| SYS_C0018728 | C | COST_CODE |  | ENABLED |
| SYS_C0018729 | C | QUANTITY |  | ENABLED |
| SYS_C0018730 | C | RATE_VALUE |  | ENABLED |
| SYS_C0018731 | C | AMOUNT |  | ENABLED |
| SYS_C0018732 | C | BASIS |  | ENABLED |
| SYS_C0018733 | C | QUANTITY |  | ENABLED |
| SYS_C0018734 | C | RATE_VALUE |  | ENABLED |
| SYS_C0018735 | C | AMOUNT |  | ENABLED |
| SYS_C0018736 | C | BASIS |  | ENABLED |
| SYS_C0018738 | P | OPERATION_ID, COST_CODE |  | ENABLED |
| SYS_C0018739 | R | OPERATION_ID | RRL_LOGISTICS_COST_RUN (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md), [RRL_TRAN_COST_DETAIL_GUARD](../programs/RRL_TRAN_COST_DETAIL_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_COST_DETAIL` в файле соответствующего типа.
