# RRL_PICK_FACE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_FACE_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `CELL_CODE` | VARCHAR2(60 bytes) | N |  |
| `PICK_FACE_CODE` | VARCHAR2(100 bytes) | Y |  |
| `PICK_FACE_TYPE` | VARCHAR2(20 bytes) | N |  |
| `PICK_ROUTE_ID` | NUMBER | Y |  |
| `PICK_ROUTE_CELL_ID` | NUMBER | Y |  |
| `PICK_SEQUENCE` | NUMBER | Y |  |
| `MIN_CASE_QTY` | NUMBER | Y |  |
| `MAX_CASE_QTY` | NUMBER | Y |  |
| `REPLENISHMENT_TRIGGER_QTY` | NUMBER | Y |  |
| `MAX_WEIGHT` | NUMBER | Y |  |
| `MAX_VOLUME` | NUMBER | Y |  |
| `ALLOW_DYNAMIC_ASSIGNMENT` | NUMBER(1,0) | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `COMMENT_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_FACE_CHK1 | C | PICK_FACE_TYPE |  | ENABLED |
| RRL_PICK_FACE_CHK2 | C | ALLOW_DYNAMIC_ASSIGNMENT |  | ENABLED |
| RRL_PICK_FACE_CHK3 | C | ACTIVE |  | ENABLED |
| RRL_PICK_FACE_FK1 | R | PICK_ROUTE_ID | RRL_PICK_ROUTE (PICK_ROUTE_ID) | ENABLED |
| RRL_PICK_FACE_FK2 | R | PICK_ROUTE_CELL_ID | RRL_PICK_ROUTE_CELL (PICK_ROUTE_CELL_ID) | ENABLED |
| RRL_PICK_FACE_PK | P | PICK_FACE_ID |  | ENABLED |
| SYS_C0014502 | C | PICK_FACE_ID |  | ENABLED |
| SYS_C0014503 | C | WARE_ID |  | ENABLED |
| SYS_C0014504 | C | CELL_CODE |  | ENABLED |
| SYS_C0014505 | C | PICK_FACE_TYPE |  | ENABLED |
| SYS_C0014506 | C | ALLOW_DYNAMIC_ASSIGNMENT |  | ENABLED |
| SYS_C0014507 | C | ACTIVE |  | ENABLED |
| SYS_C0014508 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_RANGE_POLICY](../programs/RRL_PICK_RANGE_POLICY.md), [RRL_PICK_TOPOLOGY_API](../programs/RRL_PICK_TOPOLOGY_API.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_REPL_CAPACITY](../programs/RRL_STOCK_REPL_CAPACITY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_FACE` в файле соответствующего типа.
