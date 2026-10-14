# RRL_PICK_WAVE_DEMAND

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_WAVE_DEMAND_ID` | NUMBER | N |  |
| `PICK_WAVE_ID` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `TASK_TYPE` | VARCHAR2(30 bytes) | N |  |
| `TARGET_CELL_CODE` | VARCHAR2(60 bytes) | Y |  |
| `PICK_FACE_ID` | NUMBER | Y |  |
| `PICK_ROUTE_CELL_ID` | NUMBER | Y |  |
| `DEMAND_QTY` | NUMBER | N |  |
| `TASK_COUNT` | NUMBER | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `PICK_FACE_FREE_QTY` | NUMBER | Y |  |
| `REPLENISH_QTY` | NUMBER | Y |  |
| `REPLENISHMENT_METHOD` | VARCHAR2(20 bytes) | Y |  |
| `REPLENISHMENT_QTY_MODE` | VARCHAR2(20 bytes) | Y |  |
| `MIN_SHELF_LIFE_DAYS` | NUMBER | Y |  |
| `MIN_SHELF_LIFE_PERCENT` | NUMBER | Y |  |
| `REPLENISHMENT_RELEASE_POLICY` | VARCHAR2(40 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_WAVE_DEMAND_FK1 | R | PICK_WAVE_ID | RRL_PICK_WAVE (PICK_WAVE_ID) | ENABLED |
| RRL_PICK_WAVE_DEMAND_PK | P | PICK_WAVE_DEMAND_ID |  | ENABLED |
| SYS_C0014588 | C | PICK_WAVE_DEMAND_ID |  | ENABLED |
| SYS_C0014589 | C | PICK_WAVE_ID |  | ENABLED |
| SYS_C0014590 | C | ARTICUL |  | ENABLED |
| SYS_C0014591 | C | TASK_TYPE |  | ENABLED |
| SYS_C0014592 | C | DEMAND_QTY |  | ENABLED |
| SYS_C0014593 | C | TASK_COUNT |  | ENABLED |
| SYS_C0014594 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_WAVE_DEMAND` в файле соответствующего типа.
