# RRL_PICK_WAVE_RESERVATION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_WAVE_RESERVATION_ID` | NUMBER | N |  |
| `PICK_WAVE_ID` | NUMBER | N |  |
| `PICK_RESERVATION_ID` | NUMBER | N |  |
| `PICK_TASK_ID` | NUMBER | Y |  |
| `PICK_PLAN_ID` | NUMBER | N |  |
| `PICK_PLAN_LINE_ID` | NUMBER | Y |  |
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `CUSTOMER_ID` | NUMBER | Y |  |
| `RESERVATION_STATUS` | VARCHAR2(20 bytes) | N |  |
| `PALLET_UID` | VARCHAR2(200 bytes) | Y |  |
| `SSCC` | VARCHAR2(50 bytes) | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `SOURCE_CELL_CODE` | VARCHAR2(60 bytes) | Y |  |
| `RESERVED_QTY` | NUMBER | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `RELEASED_AT` | DATE | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_WAVE_RES_CHK1 | C | RESERVATION_STATUS |  | ENABLED |
| RRL_PICK_WAVE_RES_FK1 | R | PICK_WAVE_ID | RRL_PICK_WAVE (PICK_WAVE_ID) | ENABLED |
| RRL_PICK_WAVE_RES_FK2 | R | PICK_RESERVATION_ID | RRL_PICK_RESERVATION (PICK_RESERVATION_ID) | ENABLED |
| RRL_PICK_WAVE_RES_PK | P | PICK_WAVE_RESERVATION_ID |  | ENABLED |
| SYS_C0014575 | C | PICK_WAVE_RESERVATION_ID |  | ENABLED |
| SYS_C0014576 | C | PICK_WAVE_ID |  | ENABLED |
| SYS_C0014577 | C | PICK_RESERVATION_ID |  | ENABLED |
| SYS_C0014578 | C | PICK_PLAN_ID |  | ENABLED |
| SYS_C0014579 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0014580 | C | RESERVATION_STATUS |  | ENABLED |
| SYS_C0014581 | C | ARTICUL |  | ENABLED |
| SYS_C0014582 | C | RESERVED_QTY |  | ENABLED |
| SYS_C0014583 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md), [RRL_STOCK_DOC_RESERVE_CMD](../programs/RRL_STOCK_DOC_RESERVE_CMD.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_WAVE_RESERVATION` в файле соответствующего типа.
