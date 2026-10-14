# RRL_PICK_SHORTAGE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_SHORTAGE_ID` | NUMBER | N |  |
| `PICK_PLAN_ID` | NUMBER | N |  |
| `PICK_PLAN_LINE_ID` | NUMBER | Y |  |
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `CUSTOMER_ORDER_ROW_ID` | NUMBER | Y |  |
| `CUSTOMER_ID` | NUMBER | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `REQUESTED_QTY` | NUMBER | N |  |
| `AVAILABLE_QTY` | NUMBER | N |  |
| `RESERVED_BY_OTHER_QTY` | NUMBER | N |  |
| `PLANNED_QTY` | NUMBER | N |  |
| `SHORTAGE_QTY` | NUMBER | N |  |
| `REASON_CODE` | VARCHAR2(50 bytes) | Y |  |
| `REASON_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_SHORTAGE_FK1 | R | PICK_PLAN_ID | RRL_PICK_PLAN (PICK_PLAN_ID) | ENABLED |
| RRL_PICK_SHORTAGE_FK2 | R | PICK_PLAN_LINE_ID | RRL_PICK_PLAN_LINE (PICK_PLAN_LINE_ID) | ENABLED |
| RRL_PICK_SHORTAGE_FK3 | R | CUSTOMER_ORDER_ID | RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID) | ENABLED |
| RRL_PICK_SHORTAGE_PK | P | PICK_SHORTAGE_ID |  | ENABLED |
| SYS_C0014462 | C | PICK_SHORTAGE_ID |  | ENABLED |
| SYS_C0014463 | C | PICK_PLAN_ID |  | ENABLED |
| SYS_C0014464 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0014465 | C | ARTICUL |  | ENABLED |
| SYS_C0014466 | C | REQUESTED_QTY |  | ENABLED |
| SYS_C0014467 | C | AVAILABLE_QTY |  | ENABLED |
| SYS_C0014468 | C | RESERVED_BY_OTHER_QTY |  | ENABLED |
| SYS_C0014469 | C | PLANNED_QTY |  | ENABLED |
| SYS_C0014470 | C | SHORTAGE_QTY |  | ENABLED |
| SYS_C0014471 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_SHORTAGE` в файле соответствующего типа.
