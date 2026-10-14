# RRL_PICK_WAVE_LINE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_WAVE_LINE_ID` | NUMBER | N |  |
| `PICK_WAVE_ID` | NUMBER | N |  |
| `PICK_WAVE_ORDER_ID` | NUMBER | N |  |
| `PICK_PLAN_ID` | NUMBER | N |  |
| `PICK_PLAN_LINE_ID` | NUMBER | N |  |
| `CUSTOMER_ORDER_ROW_ID` | NUMBER | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `REQUESTED_QTY` | NUMBER | N |  |
| `PLANNED_QTY` | NUMBER | N |  |
| `SHORTAGE_QTY` | NUMBER | N |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_WAVE_LINE_FK1 | R | PICK_WAVE_ID | RRL_PICK_WAVE (PICK_WAVE_ID) | ENABLED |
| RRL_PICK_WAVE_LINE_FK2 | R | PICK_WAVE_ORDER_ID | RRL_PICK_WAVE_ORDER (PICK_WAVE_ORDER_ID) | ENABLED |
| RRL_PICK_WAVE_LINE_FK3 | R | PICK_PLAN_ID | RRL_PICK_PLAN (PICK_PLAN_ID) | ENABLED |
| RRL_PICK_WAVE_LINE_FK4 | R | PICK_PLAN_LINE_ID | RRL_PICK_PLAN_LINE (PICK_PLAN_LINE_ID) | ENABLED |
| RRL_PICK_WAVE_LINE_PK | P | PICK_WAVE_LINE_ID |  | ENABLED |
| SYS_C0014559 | C | PICK_WAVE_LINE_ID |  | ENABLED |
| SYS_C0014560 | C | PICK_WAVE_ID |  | ENABLED |
| SYS_C0014561 | C | PICK_WAVE_ORDER_ID |  | ENABLED |
| SYS_C0014562 | C | PICK_PLAN_ID |  | ENABLED |
| SYS_C0014563 | C | PICK_PLAN_LINE_ID |  | ENABLED |
| SYS_C0014564 | C | ARTICUL |  | ENABLED |
| SYS_C0014565 | C | REQUESTED_QTY |  | ENABLED |
| SYS_C0014566 | C | PLANNED_QTY |  | ENABLED |
| SYS_C0014567 | C | SHORTAGE_QTY |  | ENABLED |
| SYS_C0014568 | C | STATUS |  | ENABLED |
| SYS_C0014569 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_WAVE_LINE` в файле соответствующего типа.
