# RRL_CCTV_VIEWPOINT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `CELL_CODE` | VARCHAR2(60 bytes) | N |  |
| `VIEWPOINT_CODE` | VARCHAR2(80 bytes) | N |  |
| `ARCHIVE_URI_TEMPLATE` | VARCHAR2(2000 bytes) | N |  |
| `STORED_TIME_OFFSET` | VARCHAR2(6 bytes) | N |  |
| `BEFORE_SECONDS` | NUMBER | N |  |
| `AFTER_SECONDS` | NUMBER | N |  |
| `ACTIVE` | NUMBER | N |  |
| `POLICY_VERSION` | NUMBER | N |  |
| `UPDATED_AT` | TIMESTAMP(6) | N |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CCTV_ACTIVE_C | C | ACTIVE |  | ENABLED |
| RRL_CCTV_VERSION_C | C | POLICY_VERSION |  | ENABLED |
| RRL_CCTV_VIEWPOINT_PK | P | WARE_ID, CELL_CODE, VIEWPOINT_CODE |  | ENABLED |
| RRL_CCTV_WINDOW_C | C | BEFORE_SECONDS, AFTER_SECONDS |  | ENABLED |
| SYS_C0016241 | C | WARE_ID |  | ENABLED |
| SYS_C0016242 | C | CELL_CODE |  | ENABLED |
| SYS_C0016243 | C | VIEWPOINT_CODE |  | ENABLED |
| SYS_C0016244 | C | ARCHIVE_URI_TEMPLATE |  | ENABLED |
| SYS_C0016245 | C | STORED_TIME_OFFSET |  | ENABLED |
| SYS_C0016246 | C | BEFORE_SECONDS |  | ENABLED |
| SYS_C0016247 | C | AFTER_SECONDS |  | ENABLED |
| SYS_C0016248 | C | ACTIVE |  | ENABLED |
| SYS_C0016249 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0016250 | C | UPDATED_AT |  | ENABLED |
| SYS_C0016251 | C | UPDATED_BY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CCTV_VIEWPOINT` в файле соответствующего типа.
