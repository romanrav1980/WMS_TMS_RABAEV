# RRL_TOPOLOGY_CELL_SLOT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CELL_SLOT_ID` | NUMBER | N |  |
| `TOPOLOGY_ID` | NUMBER | N |  |
| `TOPOLOGY_CELL_ID` | NUMBER | N |  |
| `PARENT_SLOT_LAYER_KIND` | VARCHAR2(30 bytes) | N |  |
| `SLOT_KIND` | VARCHAR2(30 bytes) | N |  |
| `SLOT_CODE` | VARCHAR2(100 bytes) | N |  |
| `SLOT_NAME` | VARCHAR2(200 bytes) | Y |  |
| `FRACTION_COUNT` | NUMBER | N |  |
| `FRACTION_INDEX` | NUMBER | N |  |
| `SUB_LEVEL_NO` | NUMBER | Y |  |
| `SUB_COLUMN_NO` | NUMBER | Y |  |
| `PICK_ORDER` | NUMBER | Y |  |
| `STORAGE_ORDER` | NUMBER | Y |  |
| `CAPACITY_QTY` | NUMBER | Y |  |
| `CAPACITY_VOLUME_M3` | NUMBER | Y |  |
| `CAPACITY_WEIGHT_KG` | NUMBER | Y |  |
| `X_OFFSET_M` | NUMBER | N |  |
| `Y_OFFSET_M` | NUMBER | N |  |
| `Z_OFFSET_M` | NUMBER | N |  |
| `WIDTH_M` | NUMBER | Y |  |
| `DEPTH_M` | NUMBER | Y |  |
| `HEIGHT_M` | NUMBER | Y |  |
| `CANVAS_OBJECT_ID` | NUMBER | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | N |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TOPO_CELL_SLOT_CHK_ACTIVE | C | ACTIVE |  | ENABLED |
| RRL_TOPO_CELL_SLOT_CHK_FRACT | C | FRACTION_COUNT, FRACTION_INDEX |  | ENABLED |
| RRL_TOPO_CELL_SLOT_CHK_KIND | C | SLOT_KIND, PARENT_SLOT_LAYER_KIND |  | ENABLED |
| RRL_TOPO_CELL_SLOT_CHK_ORD | C | STORAGE_ORDER, PICK_ORDER, SLOT_KIND |  | ENABLED |
| RRL_TOPO_CELL_SLOT_CHK_SIZE | C | CAPACITY_WEIGHT_KG, DEPTH_M, HEIGHT_M, WIDTH_M, CAPACITY_VOLUME_M3, CAPACITY_QTY |  | ENABLED |
| RRL_TOPO_CELL_SLOT_FK1 | R | TOPOLOGY_ID | RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID) | ENABLED |
| RRL_TOPO_CELL_SLOT_FK2 | R | TOPOLOGY_CELL_ID | RRL_TOPOLOGY_CELL (TOPOLOGY_CELL_ID) | ENABLED |
| RRL_TOPO_CELL_SLOT_FK_LAYER | R | TOPOLOGY_CELL_ID, PARENT_SLOT_LAYER_KIND | RRL_TOPOLOGY_CELL (TOPOLOGY_CELL_ID, SLOT_LAYER_KIND) | ENABLED |
| RRL_TOPO_CELL_SLOT_FK_OBJECT | R | CANVAS_OBJECT_ID | RRL_WAREHOUSE_MAP_OBJECT (MAP_OBJECT_ID) | ENABLED |
| RRL_TOPO_CELL_SLOT_PK | P | CELL_SLOT_ID |  | ENABLED |
| SYS_C0015320 | C | CELL_SLOT_ID |  | ENABLED |
| SYS_C0015321 | C | TOPOLOGY_ID |  | ENABLED |
| SYS_C0015322 | C | TOPOLOGY_CELL_ID |  | ENABLED |
| SYS_C0015323 | C | PARENT_SLOT_LAYER_KIND |  | ENABLED |
| SYS_C0015324 | C | SLOT_KIND |  | ENABLED |
| SYS_C0015325 | C | SLOT_CODE |  | ENABLED |
| SYS_C0015326 | C | FRACTION_COUNT |  | ENABLED |
| SYS_C0015327 | C | FRACTION_INDEX |  | ENABLED |
| SYS_C0015328 | C | X_OFFSET_M |  | ENABLED |
| SYS_C0015329 | C | Y_OFFSET_M |  | ENABLED |
| SYS_C0015330 | C | Z_OFFSET_M |  | ENABLED |
| SYS_C0015331 | C | ACTIVE |  | ENABLED |
| SYS_C0015332 | C | CREATED_AT |  | ENABLED |
| SYS_C0015333 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_HU_REPACK_CMD](../programs/RRL_STOCK_HU_REPACK_CMD.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_HU_SLOT_MOVE_CMD](../programs/RRL_STOCK_HU_SLOT_MOVE_CMD.md), [RRL_STOCK_HU_UNPACK_CMD](../programs/RRL_STOCK_HU_UNPACK_CMD.md), [RRL_STOCK_IW_PUT_CELL](../programs/RRL_STOCK_IW_PUT_CELL.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md), [RRL_WAREHOUSE_MAP_API](../programs/RRL_WAREHOUSE_MAP_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TOPOLOGY_CELL_SLOT` в файле соответствующего типа.
