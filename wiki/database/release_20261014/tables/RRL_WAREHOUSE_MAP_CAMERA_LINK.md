# RRL_WAREHOUSE_MAP_CAMERA_LINK

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Складские задания и топология.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CAMERA_LINK_ID` | NUMBER | N |  |
| `CANVAS_ID` | NUMBER | N |  |
| `FROM_CAMERA_ID` | NUMBER | N |  |
| `TO_CAMERA_ID` | NUMBER | N |  |
| `LINK_CODE` | VARCHAR2(80 bytes) | N |  |
| `LINK_KIND` | VARCHAR2(40 bytes) | N |  |
| `FROM_POINT_X_M` | NUMBER | N |  |
| `FROM_POINT_Y_M` | NUMBER | N |  |
| `FROM_POINT_Z_M` | NUMBER | N |  |
| `TO_POINT_X_M` | NUMBER | N |  |
| `TO_POINT_Y_M` | NUMBER | N |  |
| `TO_POINT_Z_M` | NUMBER | N |  |
| `DISTANCE_M` | NUMBER | N |  |
| `TRAVEL_TIME_SEC` | NUMBER | Y |  |
| `DIRECTION_CODE` | VARCHAR2(20 bytes) | N |  |
| `ALLOWED_RESOURCE_MASK` | VARCHAR2(200 bytes) | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | N |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WH_MAP_CAMERA_LINK_FK1 | R | CANVAS_ID | RRL_WAREHOUSE_MAP_CANVAS (CANVAS_ID) | ENABLED |
| RRL_WH_MAP_CAMERA_LINK_FK2 | R | FROM_CAMERA_ID | RRL_WAREHOUSE_MAP_CAMERA (CAMERA_ID) | ENABLED |
| RRL_WH_MAP_CAMERA_LINK_FK3 | R | TO_CAMERA_ID | RRL_WAREHOUSE_MAP_CAMERA (CAMERA_ID) | ENABLED |
| RRL_WH_MAP_CAMERA_LINK_PK | P | CAMERA_LINK_ID |  | ENABLED |
| RRL_WH_MAP_LINK_CHK_ACTIVE | C | ACTIVE |  | ENABLED |
| RRL_WH_MAP_LINK_CHK_DIR | C | DIRECTION_CODE |  | ENABLED |
| RRL_WH_MAP_LINK_CHK_KIND | C | LINK_KIND |  | ENABLED |
| RRL_WH_MAP_LINK_CHK_SIZE | C | FROM_CAMERA_ID, TRAVEL_TIME_SEC, DISTANCE_M, TO_CAMERA_ID |  | ENABLED |
| SYS_C0015292 | C | CAMERA_LINK_ID |  | ENABLED |
| SYS_C0015293 | C | CANVAS_ID |  | ENABLED |
| SYS_C0015294 | C | FROM_CAMERA_ID |  | ENABLED |
| SYS_C0015295 | C | TO_CAMERA_ID |  | ENABLED |
| SYS_C0015296 | C | LINK_CODE |  | ENABLED |
| SYS_C0015297 | C | LINK_KIND |  | ENABLED |
| SYS_C0015298 | C | FROM_POINT_X_M |  | ENABLED |
| SYS_C0015299 | C | FROM_POINT_Y_M |  | ENABLED |
| SYS_C0015300 | C | FROM_POINT_Z_M |  | ENABLED |
| SYS_C0015301 | C | TO_POINT_X_M |  | ENABLED |
| SYS_C0015302 | C | TO_POINT_Y_M |  | ENABLED |
| SYS_C0015303 | C | TO_POINT_Z_M |  | ENABLED |
| SYS_C0015304 | C | DISTANCE_M |  | ENABLED |
| SYS_C0015305 | C | DIRECTION_CODE |  | ENABLED |
| SYS_C0015306 | C | ACTIVE |  | ENABLED |
| SYS_C0015307 | C | CREATED_AT |  | ENABLED |
| SYS_C0015308 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WAREHOUSE_MAP_CAMERA_LINK` в файле соответствующего типа.
