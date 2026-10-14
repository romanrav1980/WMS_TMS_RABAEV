# RRL_WAREHOUSE_MAP_OBJECT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Складские задания и топология.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `MAP_OBJECT_ID` | NUMBER | N |  |
| `CANVAS_ID` | NUMBER | N |  |
| `CAMERA_ID` | NUMBER | N |  |
| `TOPOLOGY_CELL_ID` | NUMBER | Y |  |
| `OBJECT_CODE` | VARCHAR2(100 bytes) | Y |  |
| `OBJECT_KIND` | VARCHAR2(40 bytes) | N |  |
| `OBJECT_NAME` | VARCHAR2(200 bytes) | Y |  |
| `LEVEL_NO` | NUMBER | Y |  |
| `X_M` | NUMBER | N |  |
| `Y_M` | NUMBER | N |  |
| `Z_M` | NUMBER | N |  |
| `WIDTH_M` | NUMBER | Y |  |
| `DEPTH_M` | NUMBER | Y |  |
| `HEIGHT_M` | NUMBER | Y |  |
| `ANGLE_DEG` | NUMBER | N |  |
| `GEOMETRY_JSON` | CLOB | Y |  |
| `STYLE_JSON` | CLOB | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | N |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WH_MAP_OBJECT_CHK_ACTIVE | C | ACTIVE |  | ENABLED |
| RRL_WH_MAP_OBJECT_CHK_KIND | C | OBJECT_KIND |  | ENABLED |
| RRL_WH_MAP_OBJECT_CHK_SIZE | C | HEIGHT_M, DEPTH_M, WIDTH_M |  | ENABLED |
| RRL_WH_MAP_OBJECT_FK1 | R | CANVAS_ID | RRL_WAREHOUSE_MAP_CANVAS (CANVAS_ID) | ENABLED |
| RRL_WH_MAP_OBJECT_FK2 | R | CAMERA_ID | RRL_WAREHOUSE_MAP_CAMERA (CAMERA_ID) | ENABLED |
| RRL_WH_MAP_OBJECT_FK_CELL | R | TOPOLOGY_CELL_ID | RRL_TOPOLOGY_CELL (TOPOLOGY_CELL_ID) | ENABLED |
| RRL_WH_MAP_OBJECT_PK | P | MAP_OBJECT_ID |  | ENABLED |
| SYS_C0015253 | C | MAP_OBJECT_ID |  | ENABLED |
| SYS_C0015254 | C | CANVAS_ID |  | ENABLED |
| SYS_C0015255 | C | CAMERA_ID |  | ENABLED |
| SYS_C0015256 | C | OBJECT_KIND |  | ENABLED |
| SYS_C0015257 | C | X_M |  | ENABLED |
| SYS_C0015258 | C | Y_M |  | ENABLED |
| SYS_C0015259 | C | Z_M |  | ENABLED |
| SYS_C0015260 | C | ANGLE_DEG |  | ENABLED |
| SYS_C0015261 | C | ACTIVE |  | ENABLED |
| SYS_C0015262 | C | CREATED_AT |  | ENABLED |
| SYS_C0015263 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WAREHOUSE_MAP_OBJECT` в файле соответствующего типа.
