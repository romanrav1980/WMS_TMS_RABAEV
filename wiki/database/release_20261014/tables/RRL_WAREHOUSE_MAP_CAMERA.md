# RRL_WAREHOUSE_MAP_CAMERA

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Складские задания и топология.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CAMERA_ID` | NUMBER | N |  |
| `CANVAS_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `CAMERA_CODE` | VARCHAR2(80 bytes) | N |  |
| `CAMERA_NAME` | VARCHAR2(200 bytes) | N |  |
| `CAMERA_KIND` | VARCHAR2(30 bytes) | N |  |
| `ORIGIN_X_M` | NUMBER | N |  |
| `ORIGIN_Y_M` | NUMBER | N |  |
| `ORIGIN_Z_M` | NUMBER | N |  |
| `WIDTH_M` | NUMBER | N |  |
| `DEPTH_M` | NUMBER | N |  |
| `HEIGHT_M` | NUMBER | N |  |
| `GRID_CELL_WIDTH_M` | NUMBER | N |  |
| `GRID_CELL_DEPTH_M` | NUMBER | N |  |
| `LEVELS` | NUMBER | N |  |
| `BOUNDARY_JSON` | CLOB | Y |  |
| `DEFAULT_PASSAGE_WIDTH_M` | NUMBER | N |  |
| `DEFAULT_AISLE_SPACING_M` | NUMBER | Y |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | N |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WH_MAP_CAMERA_CHK_ACTIVE | C | ACTIVE |  | ENABLED |
| RRL_WH_MAP_CAMERA_CHK_KIND | C | CAMERA_KIND |  | ENABLED |
| RRL_WH_MAP_CAMERA_CHK_SIZE | C | GRID_CELL_WIDTH_M, WIDTH_M, DEPTH_M, HEIGHT_M, GRID_CELL_DEPTH_M, DEFAULT_AISLE_SPACING_M, DEFAULT_PASSAGE_WIDTH_M, LEVELS |  | ENABLED |
| RRL_WH_MAP_CAMERA_CHK_STATUS | C | STATUS |  | ENABLED |
| RRL_WH_MAP_CAMERA_CK_WARE_POS | C | WARE_ID |  | ENABLED |
| RRL_WH_MAP_CAMERA_FK1 | R | CANVAS_ID | RRL_WAREHOUSE_MAP_CANVAS (CANVAS_ID) | ENABLED |
| RRL_WH_MAP_CAMERA_PK | P | CAMERA_ID |  | ENABLED |
| SYS_C0015227 | C | CAMERA_ID |  | ENABLED |
| SYS_C0015228 | C | CANVAS_ID |  | ENABLED |
| SYS_C0015229 | C | WARE_ID |  | ENABLED |
| SYS_C0015230 | C | CAMERA_CODE |  | ENABLED |
| SYS_C0015231 | C | CAMERA_NAME |  | ENABLED |
| SYS_C0015232 | C | CAMERA_KIND |  | ENABLED |
| SYS_C0015233 | C | ORIGIN_X_M |  | ENABLED |
| SYS_C0015234 | C | ORIGIN_Y_M |  | ENABLED |
| SYS_C0015235 | C | ORIGIN_Z_M |  | ENABLED |
| SYS_C0015236 | C | WIDTH_M |  | ENABLED |
| SYS_C0015237 | C | DEPTH_M |  | ENABLED |
| SYS_C0015238 | C | HEIGHT_M |  | ENABLED |
| SYS_C0015239 | C | GRID_CELL_WIDTH_M |  | ENABLED |
| SYS_C0015240 | C | GRID_CELL_DEPTH_M |  | ENABLED |
| SYS_C0015241 | C | LEVELS |  | ENABLED |
| SYS_C0015242 | C | DEFAULT_PASSAGE_WIDTH_M |  | ENABLED |
| SYS_C0015243 | C | STATUS |  | ENABLED |
| SYS_C0015244 | C | ACTIVE |  | ENABLED |
| SYS_C0015245 | C | CREATED_AT |  | ENABLED |
| SYS_C0015246 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_WAREHOUSE_MAP_API](../programs/RRL_WAREHOUSE_MAP_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WAREHOUSE_MAP_CAMERA` в файле соответствующего типа.
