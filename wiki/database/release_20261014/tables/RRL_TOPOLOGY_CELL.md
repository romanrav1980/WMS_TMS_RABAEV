# RRL_TOPOLOGY_CELL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TOPOLOGY_CELL_ID` | NUMBER | N |  |
| `TOPOLOGY_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `CELL_CODE` | VARCHAR2(80 bytes) | N |  |
| `LEGACY_CELL_CODE` | VARCHAR2(80 bytes) | Y |  |
| `ZONE_CODE` | VARCHAR2(40 bytes) | Y |  |
| `SECTION_CODE` | VARCHAR2(40 bytes) | Y |  |
| `AISLE_CODE` | VARCHAR2(40 bytes) | Y |  |
| `RACK_CODE` | VARCHAR2(40 bytes) | Y |  |
| `BAY_NO` | NUMBER | Y |  |
| `LEVEL_NO` | NUMBER | Y |  |
| `POSITION_NO` | NUMBER | Y |  |
| `SIDE_CODE` | VARCHAR2(20 bytes) | N |  |
| `CELL_KIND` | VARCHAR2(40 bytes) | N |  |
| `ACCESS_LEVEL` | NUMBER | Y |  |
| `STORAGE_AREA_CODE` | VARCHAR2(40 bytes) | Y |  |
| `RESOURCE_AREA_CODE` | VARCHAR2(40 bytes) | Y |  |
| `CELL_SIZE_CODE` | VARCHAR2(40 bytes) | Y |  |
| `MAX_VOLUME_M3` | NUMBER | Y |  |
| `MAX_WEIGHT_KG` | NUMBER | Y |  |
| `X` | NUMBER | N |  |
| `Y` | NUMBER | N |  |
| `Z` | NUMBER | N |  |
| `WIDTH` | NUMBER | N |  |
| `DEPTH` | NUMBER | N |  |
| `HEIGHT` | NUMBER | N |  |
| `ANGLE_DEG` | NUMBER | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | N |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `SLOT_LAYER_KIND` | VARCHAR2(30 bytes) | Y |  |
| `WAREHOUSE_MAP_CAMERA_ID` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TOPOLOGY_CELL_CHK1 | C | SIDE_CODE |  | ENABLED |
| RRL_TOPOLOGY_CELL_CHK2 | C | ACTIVE |  | ENABLED |
| RRL_TOPOLOGY_CELL_FK1 | R | TOPOLOGY_ID | RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID) | ENABLED |
| RRL_TOPOLOGY_CELL_FK_MAP_CAM | R | WAREHOUSE_MAP_CAMERA_ID | RRL_WAREHOUSE_MAP_CAMERA (CAMERA_ID) | ENABLED |
| RRL_TOPOLOGY_CELL_PK | P | TOPOLOGY_CELL_ID |  | ENABLED |
| RRL_TOPOLOGY_CELL_U1 | U | TOPOLOGY_ID, CELL_CODE |  | ENABLED |
| RRL_TOPO_CELL_CHK_SLOT_LAYER | C | SLOT_LAYER_KIND |  | ENABLED |
| RRL_TOPO_CELL_CK_WARE_POS | C | WARE_ID |  | ENABLED |
| RRL_TOPO_CELL_UK_SLOT_LAYER | U | TOPOLOGY_CELL_ID, SLOT_LAYER_KIND |  | ENABLED |
| SYS_C0015108 | C | TOPOLOGY_CELL_ID |  | ENABLED |
| SYS_C0015109 | C | TOPOLOGY_ID |  | ENABLED |
| SYS_C0015110 | C | WARE_ID |  | ENABLED |
| SYS_C0015111 | C | CELL_CODE |  | ENABLED |
| SYS_C0015112 | C | SIDE_CODE |  | ENABLED |
| SYS_C0015113 | C | CELL_KIND |  | ENABLED |
| SYS_C0015114 | C | X |  | ENABLED |
| SYS_C0015115 | C | Y |  | ENABLED |
| SYS_C0015116 | C | Z |  | ENABLED |
| SYS_C0015117 | C | WIDTH |  | ENABLED |
| SYS_C0015118 | C | DEPTH |  | ENABLED |
| SYS_C0015119 | C | HEIGHT |  | ENABLED |
| SYS_C0015120 | C | ANGLE_DEG |  | ENABLED |
| SYS_C0015121 | C | ACTIVE |  | ENABLED |
| SYS_C0015122 | C | CREATED_AT |  | ENABLED |
| SYS_C0015123 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_IW_PUT_CELL](../programs/RRL_STOCK_IW_PUT_CELL.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md), [RRL_WAREHOUSE_MAP_API](../programs/RRL_WAREHOUSE_MAP_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TOPOLOGY_CELL` в файле соответствующего типа.
