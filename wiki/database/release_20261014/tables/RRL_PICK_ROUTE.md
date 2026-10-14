# RRL_PICK_ROUTE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_ROUTE_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ROUTE_CODE` | VARCHAR2(50 bytes) | N |  |
| `ROUTE_NAME` | VARCHAR2(255 bytes) | Y |  |
| `ROUTE_KIND` | VARCHAR2(20 bytes) | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `TOPOLOGY_ID` | NUMBER | Y |  |
| `ROUTE_PATTERN` | VARCHAR2(30 bytes) | N |  |
| `START_POINT_CODE` | VARCHAR2(80 bytes) | Y |  |
| `END_POINT_CODE` | VARCHAR2(80 bytes) | Y |  |
| `STRICT_SEQUENCE` | NUMBER(1,0) | N |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `PUBLISHED_AT` | DATE | Y |  |
| `PUBLISHED_BY` | VARCHAR2(50 bytes) | Y |  |
| `COMMENT_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `ZONE_CODE` | VARCHAR2(40 bytes) | Y |  |
| `IDEMPOTENCY_KEY` | VARCHAR2(120 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_ROUTE_CHK1 | C | ROUTE_KIND |  | ENABLED |
| RRL_PICK_ROUTE_CHK2 | C | ACTIVE |  | ENABLED |
| RRL_PICK_ROUTE_CK_WARE_POS | C | WARE_ID |  | ENABLED |
| RRL_PICK_ROUTE_PK | P | PICK_ROUTE_ID |  | ENABLED |
| SYS_C0014483 | C | PICK_ROUTE_ID |  | ENABLED |
| SYS_C0014484 | C | WARE_ID |  | ENABLED |
| SYS_C0014485 | C | ROUTE_CODE |  | ENABLED |
| SYS_C0014486 | C | ROUTE_KIND |  | ENABLED |
| SYS_C0014487 | C | ACTIVE |  | ENABLED |
| SYS_C0014488 | C | CREATED_AT |  | ENABLED |
| SYS_C0015144 | C | ROUTE_PATTERN |  | ENABLED |
| SYS_C0015145 | C | STRICT_SEQUENCE |  | ENABLED |
| SYS_C0015146 | C | STATUS |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_TOPOLOGY_API](../programs/RRL_PICK_TOPOLOGY_API.md), [RRL_WAREHOUSE_MAP_API](../programs/RRL_WAREHOUSE_MAP_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_ROUTE` в файле соответствующего типа.
