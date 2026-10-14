# RRL_WAREHOUSE_MAP_CANVAS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Складские задания и топология.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CANVAS_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `TOPOLOGY_ID` | NUMBER | Y |  |
| `CANVAS_CODE` | VARCHAR2(80 bytes) | N |  |
| `CANVAS_NAME` | VARCHAR2(200 bytes) | Y |  |
| `VERSION_NO` | NUMBER | N |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `RENDERER_KIND` | VARCHAR2(20 bytes) | N |  |
| `UNIT_CODE` | VARCHAR2(20 bytes) | N |  |
| `GRID_CELL_WIDTH_M` | NUMBER | N |  |
| `GRID_CELL_DEPTH_M` | NUMBER | N |  |
| `LEVELS` | NUMBER | N |  |
| `VIEWPORT_JSON` | CLOB | Y |  |
| `RENDERER_STATE_JSON` | CLOB | Y |  |
| `SOURCE_CANVAS_ID` | NUMBER | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `COMMENT_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | N |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `PUBLISHED_AT` | DATE | Y |  |
| `PUBLISHED_BY` | VARCHAR2(50 bytes) | Y |  |
| `IDEMPOTENCY_KEY` | VARCHAR2(120 bytes) | Y |  |
| `PUBLISH_IDEMPOTENCY_KEY` | VARCHAR2(120 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WH_MAP_CANVAS_CHK_ACTIVE | C | ACTIVE |  | ENABLED |
| RRL_WH_MAP_CANVAS_CHK_RENDER | C | RENDERER_KIND |  | ENABLED |
| RRL_WH_MAP_CANVAS_CHK_SIZE | C | GRID_CELL_DEPTH_M, LEVELS, GRID_CELL_WIDTH_M |  | ENABLED |
| RRL_WH_MAP_CANVAS_CHK_STATUS | C | STATUS |  | ENABLED |
| RRL_WH_MAP_CANVAS_CHK_UNIT | C | UNIT_CODE |  | ENABLED |
| RRL_WH_MAP_CANVAS_CK_WARE_POS | C | WARE_ID |  | ENABLED |
| RRL_WH_MAP_CANVAS_FK1 | R | TOPOLOGY_ID | RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID) | ENABLED |
| RRL_WH_MAP_CANVAS_FK2 | R | SOURCE_CANVAS_ID | RRL_WAREHOUSE_MAP_CANVAS (CANVAS_ID) | ENABLED |
| RRL_WH_MAP_CANVAS_PK | P | CANVAS_ID |  | ENABLED |
| SYS_C0015206 | C | CANVAS_ID |  | ENABLED |
| SYS_C0015207 | C | WARE_ID |  | ENABLED |
| SYS_C0015208 | C | CANVAS_CODE |  | ENABLED |
| SYS_C0015209 | C | VERSION_NO |  | ENABLED |
| SYS_C0015210 | C | STATUS |  | ENABLED |
| SYS_C0015211 | C | RENDERER_KIND |  | ENABLED |
| SYS_C0015212 | C | UNIT_CODE |  | ENABLED |
| SYS_C0015213 | C | GRID_CELL_WIDTH_M |  | ENABLED |
| SYS_C0015214 | C | GRID_CELL_DEPTH_M |  | ENABLED |
| SYS_C0015215 | C | LEVELS |  | ENABLED |
| SYS_C0015216 | C | ACTIVE |  | ENABLED |
| SYS_C0015217 | C | CREATED_AT |  | ENABLED |
| SYS_C0015218 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_WAREHOUSE_MAP_API](../programs/RRL_WAREHOUSE_MAP_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WAREHOUSE_MAP_CANVAS` в файле соответствующего типа.
