# RRL_WAREHOUSE_MAP_PASSAGE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Складские задания и топология.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PASSAGE_ID` | NUMBER | N |  |
| `CANVAS_ID` | NUMBER | N |  |
| `CAMERA_ID` | NUMBER | N |  |
| `PASSAGE_CODE` | VARCHAR2(80 bytes) | N |  |
| `PASSAGE_NAME` | VARCHAR2(200 bytes) | Y |  |
| `PASSAGE_KIND` | VARCHAR2(40 bytes) | N |  |
| `X1_M` | NUMBER | N |  |
| `Y1_M` | NUMBER | N |  |
| `Z1_M` | NUMBER | N |  |
| `X2_M` | NUMBER | N |  |
| `Y2_M` | NUMBER | N |  |
| `Z2_M` | NUMBER | N |  |
| `WIDTH_M` | NUMBER | N |  |
| `AISLE_SPACING_M` | NUMBER | Y |  |
| `GEOMETRY_JSON` | CLOB | Y |  |
| `ALLOWED_RESOURCE_MASK` | VARCHAR2(200 bytes) | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | N |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WH_MAP_PASSAGE_CHK_ACTIVE | C | ACTIVE |  | ENABLED |
| RRL_WH_MAP_PASSAGE_CHK_KIND | C | PASSAGE_KIND |  | ENABLED |
| RRL_WH_MAP_PASSAGE_CHK_SIZE | C | WIDTH_M, AISLE_SPACING_M |  | ENABLED |
| RRL_WH_MAP_PASSAGE_FK1 | R | CANVAS_ID | RRL_WAREHOUSE_MAP_CANVAS (CANVAS_ID) | ENABLED |
| RRL_WH_MAP_PASSAGE_FK2 | R | CAMERA_ID | RRL_WAREHOUSE_MAP_CAMERA (CAMERA_ID) | ENABLED |
| RRL_WH_MAP_PASSAGE_PK | P | PASSAGE_ID |  | ENABLED |
| SYS_C0015271 | C | PASSAGE_ID |  | ENABLED |
| SYS_C0015272 | C | CANVAS_ID |  | ENABLED |
| SYS_C0015273 | C | CAMERA_ID |  | ENABLED |
| SYS_C0015274 | C | PASSAGE_CODE |  | ENABLED |
| SYS_C0015275 | C | PASSAGE_KIND |  | ENABLED |
| SYS_C0015276 | C | X1_M |  | ENABLED |
| SYS_C0015277 | C | Y1_M |  | ENABLED |
| SYS_C0015278 | C | Z1_M |  | ENABLED |
| SYS_C0015279 | C | X2_M |  | ENABLED |
| SYS_C0015280 | C | Y2_M |  | ENABLED |
| SYS_C0015281 | C | Z2_M |  | ENABLED |
| SYS_C0015282 | C | WIDTH_M |  | ENABLED |
| SYS_C0015283 | C | ACTIVE |  | ENABLED |
| SYS_C0015284 | C | CREATED_AT |  | ENABLED |
| SYS_C0015285 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_WAREHOUSE_MAP_API](../programs/RRL_WAREHOUSE_MAP_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WAREHOUSE_MAP_PASSAGE` в файле соответствующего типа.
