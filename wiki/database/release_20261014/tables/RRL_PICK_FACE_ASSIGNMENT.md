# RRL_PICK_FACE_ASSIGNMENT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_FACE_ASSIGNMENT_ID` | NUMBER | N |  |
| `PICK_FACE_ID` | NUMBER | N |  |
| `CELL_CODE` | VARCHAR2(60 bytes) | N |  |
| `PICK_WAVE_ID` | NUMBER | N |  |
| `PICK_WAVE_REPLENISH_TASK_ID` | NUMBER | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `ASSIGNMENT_KIND` | VARCHAR2(20 bytes) | N |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `ASSIGNED_AT` | DATE | N |  |
| `ASSIGNED_BY` | VARCHAR2(50 bytes) | Y |  |
| `RELEASED_AT` | DATE | Y |  |
| `RELEASED_BY` | VARCHAR2(50 bytes) | Y |  |
| `RELEASE_REASON` | VARCHAR2(200 bytes) | Y |  |
| `UNIT_VOLUME_M3` | NUMBER | Y |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_FACE_ASSIGN_CHK1 | C | ASSIGNMENT_KIND |  | ENABLED |
| RRL_PICK_FACE_ASSIGN_CHK2 | C | STATUS |  | ENABLED |
| RRL_PICK_FACE_ASSIGN_FK1 | R | PICK_FACE_ID | RRL_PICK_FACE (PICK_FACE_ID) | ENABLED |
| RRL_PICK_FACE_ASSIGN_FK2 | R | PICK_WAVE_ID | RRL_PICK_WAVE (PICK_WAVE_ID) | ENABLED |
| RRL_PICK_FACE_ASSIGN_PK | P | PICK_FACE_ASSIGNMENT_ID |  | ENABLED |
| SYS_C0014801 | C | PICK_FACE_ASSIGNMENT_ID |  | ENABLED |
| SYS_C0014802 | C | PICK_FACE_ID |  | ENABLED |
| SYS_C0014803 | C | CELL_CODE |  | ENABLED |
| SYS_C0014804 | C | PICK_WAVE_ID |  | ENABLED |
| SYS_C0014805 | C | ARTICUL |  | ENABLED |
| SYS_C0014806 | C | ASSIGNMENT_KIND |  | ENABLED |
| SYS_C0014807 | C | STATUS |  | ENABLED |
| SYS_C0014808 | C | ASSIGNED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_REPL_CAPACITY](../programs/RRL_STOCK_REPL_CAPACITY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_FACE_ASSIGNMENT` в файле соответствующего типа.
