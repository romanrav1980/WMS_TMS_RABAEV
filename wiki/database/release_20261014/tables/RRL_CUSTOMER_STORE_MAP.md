# RRL_CUSTOMER_STORE_MAP

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CUSTOMER_STORE_MAP_ID` | NUMBER | N |  |
| `CUSTOMER_ID` | NUMBER | N |  |
| `LEGACY_ADDR` | VARCHAR2(255 bytes) | Y |  |
| `LEGACY_ADDR_KEY` | VARCHAR2(255 bytes) | N |  |
| `STORE_CODE` | VARCHAR2(100 bytes) | Y |  |
| `STORE_NAME` | VARCHAR2(255 bytes) | Y |  |
| `ADDRESS_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CITY` | VARCHAR2(100 bytes) | Y |  |
| `REGION` | VARCHAR2(100 bytes) | Y |  |
| `GLN` | VARCHAR2(32 bytes) | Y |  |
| `EDI_ID` | VARCHAR2(100 bytes) | Y |  |
| `DEFAULT_ROUTE_ID` | NUMBER | Y |  |
| `DEFAULT_DOCK_ID` | NUMBER | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CUSTOMER_STORE_MAP_CHK1 | C | ACTIVE |  | ENABLED |
| RRL_CUSTOMER_STORE_MAP_FK1 | R | CUSTOMER_ID | RRL_CUSTOMER (CUSTOMER_ID) | ENABLED |
| RRL_CUSTOMER_STORE_MAP_PK | P | CUSTOMER_STORE_MAP_ID |  | ENABLED |
| RRL_CUSTOMER_STORE_MAP_U1 | U | LEGACY_ADDR_KEY |  | ENABLED |
| SYS_C0014293 | C | CUSTOMER_STORE_MAP_ID |  | ENABLED |
| SYS_C0014294 | C | CUSTOMER_ID |  | ENABLED |
| SYS_C0014295 | C | LEGACY_ADDR_KEY |  | ENABLED |
| SYS_C0014296 | C | ACTIVE |  | ENABLED |
| SYS_C0014297 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CUSTOMER_ORDER_API](../programs/RRL_CUSTOMER_ORDER_API.md), [RRL_STOCK_TARE_POLICY](../programs/RRL_STOCK_TARE_POLICY.md), [RRL_STORE_CALENDAR_API](../programs/RRL_STORE_CALENDAR_API.md), [RRL_TARE_POLICY_GUARD](../programs/RRL_TARE_POLICY_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CUSTOMER_STORE_MAP` в файле соответствующего типа.
