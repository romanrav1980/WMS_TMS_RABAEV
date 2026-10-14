# RRL_WAREHOUSE_TOPOLOGY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Складские задания и топология.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TOPOLOGY_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `TOPOLOGY_CODE` | VARCHAR2(80 bytes) | N |  |
| `TOPOLOGY_NAME` | VARCHAR2(200 bytes) | Y |  |
| `VERSION_NO` | NUMBER | N |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `VALID_FROM` | DATE | Y |  |
| `VALID_TO` | DATE | Y |  |
| `SOURCE_TOPOLOGY_ID` | NUMBER | Y |  |
| `COMMENT_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | N |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `PUBLISHED_AT` | DATE | Y |  |
| `PUBLISHED_BY` | VARCHAR2(50 bytes) | Y |  |
| `IDEMPOTENCY_KEY` | VARCHAR2(120 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WH_TOPOLOGY_CHK1 | C | STATUS |  | ENABLED |
| RRL_WH_TOPOLOGY_CK_WARE_POS | C | WARE_ID |  | ENABLED |
| RRL_WH_TOPOLOGY_PK | P | TOPOLOGY_ID |  | ENABLED |
| RRL_WH_TOPOLOGY_U1 | U | WARE_ID, TOPOLOGY_CODE |  | ENABLED |
| SYS_C0015064 | C | TOPOLOGY_ID |  | ENABLED |
| SYS_C0015065 | C | WARE_ID |  | ENABLED |
| SYS_C0015066 | C | TOPOLOGY_CODE |  | ENABLED |
| SYS_C0015067 | C | VERSION_NO |  | ENABLED |
| SYS_C0015068 | C | STATUS |  | ENABLED |
| SYS_C0015069 | C | CREATED_AT |  | ENABLED |
| SYS_C0015070 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_IW_PUT_CELL](../programs/RRL_STOCK_IW_PUT_CELL.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WAREHOUSE_TOPOLOGY` в файле соответствующего типа.
