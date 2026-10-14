# RRL_PICK_ROUTE_CELL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_ROUTE_CELL_ID` | NUMBER | N |  |
| `PICK_ROUTE_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `CELL_CODE` | VARCHAR2(60 bytes) | N |  |
| `PICK_SEQUENCE` | NUMBER | N |  |
| `ZONE_CODE` | VARCHAR2(50 bytes) | Y |  |
| `AISLE_CODE` | VARCHAR2(50 bytes) | Y |  |
| `SIDE_CODE` | VARCHAR2(20 bytes) | Y |  |
| `LEVEL_NO` | NUMBER | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `TOPOLOGY_CELL_ID` | NUMBER | Y |  |
| `SECTION_CODE` | VARCHAR2(40 bytes) | Y |  |
| `BAY_NO` | NUMBER | Y |  |
| `DIRECTION_CODE` | VARCHAR2(20 bytes) | Y |  |
| `VISIT_GROUP_NO` | NUMBER | Y |  |
| `PATH_SEGMENT_NO` | NUMBER | Y |  |
| `DISTANCE_FROM_PREV_M` | NUMBER | Y |  |
| `TURN_COST_SEC` | NUMBER | Y |  |
| `CELL_SLOT_ID` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_ROUTE_CELL_CHK1 | C | ACTIVE |  | ENABLED |
| RRL_PICK_ROUTE_CELL_CK_WARE_POS | C | WARE_ID |  | ENABLED |
| RRL_PICK_ROUTE_CELL_FK1 | R | PICK_ROUTE_ID | RRL_PICK_ROUTE (PICK_ROUTE_ID) | ENABLED |
| RRL_PICK_ROUTE_CELL_FK_SLOT | R | CELL_SLOT_ID | RRL_TOPOLOGY_CELL_SLOT (CELL_SLOT_ID) | ENABLED |
| RRL_PICK_ROUTE_CELL_PK | P | PICK_ROUTE_CELL_ID |  | ENABLED |
| SYS_C0014492 | C | PICK_ROUTE_CELL_ID |  | ENABLED |
| SYS_C0014493 | C | PICK_ROUTE_ID |  | ENABLED |
| SYS_C0014494 | C | WARE_ID |  | ENABLED |
| SYS_C0014495 | C | CELL_CODE |  | ENABLED |
| SYS_C0014496 | C | PICK_SEQUENCE |  | ENABLED |
| SYS_C0014497 | C | ACTIVE |  | ENABLED |
| SYS_C0014498 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_TOPOLOGY_API](../programs/RRL_PICK_TOPOLOGY_API.md), [RRL_WAREHOUSE_MAP_API](../programs/RRL_WAREHOUSE_MAP_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_ROUTE_CELL` в файле соответствующего типа.
