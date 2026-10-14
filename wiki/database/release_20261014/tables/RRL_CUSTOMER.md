# RRL_CUSTOMER

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CUSTOMER_ID` | NUMBER | N |  |
| `CUSTOMER_CODE` | VARCHAR2(100 bytes) | N |  |
| `CUSTOMER_NAME` | VARCHAR2(255 bytes) | N |  |
| `CUSTOMER_TYPE` | VARCHAR2(30 bytes) | N |  |
| `INN` | VARCHAR2(20 bytes) | Y |  |
| `KPP` | VARCHAR2(20 bytes) | Y |  |
| `GLN` | VARCHAR2(32 bytes) | Y |  |
| `EDI_ID` | VARCHAR2(100 bytes) | Y |  |
| `DEFAULT_VEHICLE_TYPE_ID` | NUMBER | Y |  |
| `SPLIT_ORDER_BY_VEHICLE_CAPACITY` | NUMBER(1,0) | N |  |
| `DEFAULT_MIN_SHELF_LIFE_DAYS` | NUMBER | Y |  |
| `DEFAULT_MIN_SHELF_LIFE_PERCENT` | NUMBER | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CUSTOMER_CHK1 | C | CUSTOMER_TYPE |  | ENABLED |
| RRL_CUSTOMER_CHK2 | C | ACTIVE |  | ENABLED |
| RRL_CUSTOMER_CHK3 | C | SPLIT_ORDER_BY_VEHICLE_CAPACITY |  | ENABLED |
| RRL_CUSTOMER_CHK4 | C | DEFAULT_MIN_SHELF_LIFE_PERCENT |  | ENABLED |
| RRL_CUSTOMER_PK | P | CUSTOMER_ID |  | ENABLED |
| RRL_CUSTOMER_U1 | U | CUSTOMER_CODE |  | ENABLED |
| SYS_C0014270 | C | CUSTOMER_ID |  | ENABLED |
| SYS_C0014271 | C | CUSTOMER_CODE |  | ENABLED |
| SYS_C0014272 | C | CUSTOMER_NAME |  | ENABLED |
| SYS_C0014273 | C | CUSTOMER_TYPE |  | ENABLED |
| SYS_C0014274 | C | SPLIT_ORDER_BY_VEHICLE_CAPACITY |  | ENABLED |
| SYS_C0014275 | C | ACTIVE |  | ENABLED |
| SYS_C0014276 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CUSTOMER_ORDER_API](../programs/RRL_CUSTOMER_ORDER_API.md), [RRL_CUSTOMER_RULE_API](../programs/RRL_CUSTOMER_RULE_API.md), [RRL_STORE_CALENDAR_API](../programs/RRL_STORE_CALENDAR_API.md), [RRL_TARE_POLICY_GUARD](../programs/RRL_TARE_POLICY_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CUSTOMER` в файле соответствующего типа.
