# RRL_PICK_WAVE_ORDER

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_WAVE_ORDER_ID` | NUMBER | N |  |
| `PICK_WAVE_ID` | NUMBER | N |  |
| `PICK_PLAN_ID` | NUMBER | N |  |
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `CUSTOMER_ID` | NUMBER | Y |  |
| `ORDER_NO` | VARCHAR2(100 bytes) | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_WAVE_ORDER_CHK1 | C | STATUS |  | ENABLED |
| RRL_PICK_WAVE_ORDER_FK1 | R | PICK_WAVE_ID | RRL_PICK_WAVE (PICK_WAVE_ID) | ENABLED |
| RRL_PICK_WAVE_ORDER_FK2 | R | PICK_PLAN_ID | RRL_PICK_PLAN (PICK_PLAN_ID) | ENABLED |
| RRL_PICK_WAVE_ORDER_FK3 | R | CUSTOMER_ORDER_ID | RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID) | ENABLED |
| RRL_PICK_WAVE_ORDER_PK | P | PICK_WAVE_ORDER_ID |  | ENABLED |
| SYS_C0014548 | C | PICK_WAVE_ORDER_ID |  | ENABLED |
| SYS_C0014549 | C | PICK_WAVE_ID |  | ENABLED |
| SYS_C0014550 | C | PICK_PLAN_ID |  | ENABLED |
| SYS_C0014551 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0014552 | C | STATUS |  | ENABLED |
| SYS_C0014553 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_DIRECT_RECEIVING_PICK](../programs/RRL_DIRECT_RECEIVING_PICK.md), [RRL_PICK_PLAN_ADMISSION](../programs/RRL_PICK_PLAN_ADMISSION.md), [RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md), [RRL_STOCK_DOC_RESERVE_CMD](../programs/RRL_STOCK_DOC_RESERVE_CMD.md), [RRL_STOCK_POOL_CMD](../programs/RRL_STOCK_POOL_CMD.md), [RRL_STOCK_WAVE_FINISH_CMD](../programs/RRL_STOCK_WAVE_FINISH_CMD.md), [RRL_STOCK_WAVE_LAUNCH_CMD](../programs/RRL_STOCK_WAVE_LAUNCH_CMD.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_WAVE_ORDER` в файле соответствующего типа.
