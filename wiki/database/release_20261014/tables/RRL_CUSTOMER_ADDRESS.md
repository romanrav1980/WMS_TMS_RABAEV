# RRL_CUSTOMER_ADDRESS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CUSTOMER_ADDRESS_ID` | NUMBER | N |  |
| `CUSTOMER_ID` | NUMBER | N |  |
| `ADDRESS_TYPE` | VARCHAR2(30 bytes) | N |  |
| `ADDRESS_TEXT` | VARCHAR2(1000 bytes) | N |  |
| `CITY` | VARCHAR2(100 bytes) | Y |  |
| `REGION` | VARCHAR2(100 bytes) | Y |  |
| `POSTAL_CODE` | VARCHAR2(20 bytes) | Y |  |
| `GLN` | VARCHAR2(32 bytes) | Y |  |
| `LATITUDE` | NUMBER | Y |  |
| `LONGITUDE` | NUMBER | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `VEHICLE_TYPE_ID` | NUMBER | Y |  |
| `MAX_PALLET_COUNT` | NUMBER | Y |  |
| `MAX_WEIGHT` | NUMBER | Y |  |
| `MAX_VOLUME` | NUMBER | Y |  |
| `SPLIT_ORDER_BY_CAPACITY` | NUMBER(1,0) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CUSTOMER_ADDRESS_CHK1 | C | ADDRESS_TYPE |  | ENABLED |
| RRL_CUSTOMER_ADDRESS_CHK2 | C | ACTIVE |  | ENABLED |
| RRL_CUSTOMER_ADDRESS_CHK3 | C | SPLIT_ORDER_BY_CAPACITY |  | ENABLED |
| RRL_CUSTOMER_ADDRESS_FK1 | R | CUSTOMER_ID | RRL_CUSTOMER (CUSTOMER_ID) | ENABLED |
| RRL_CUSTOMER_ADDRESS_FK2 | R | VEHICLE_TYPE_ID | RRL_VEHICLE_TYPE (VEHICLE_TYPE_ID) | ENABLED |
| RRL_CUSTOMER_ADDRESS_PK | P | CUSTOMER_ADDRESS_ID |  | ENABLED |
| SYS_C0014283 | C | CUSTOMER_ADDRESS_ID |  | ENABLED |
| SYS_C0014284 | C | CUSTOMER_ID |  | ENABLED |
| SYS_C0014285 | C | ADDRESS_TYPE |  | ENABLED |
| SYS_C0014286 | C | ADDRESS_TEXT |  | ENABLED |
| SYS_C0014287 | C | ACTIVE |  | ENABLED |
| SYS_C0014288 | C | CREATED_AT |  | ENABLED |
| SYS_C0014634 | C | SPLIT_ORDER_BY_CAPACITY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CUSTOMER_ORDER_API](../programs/RRL_CUSTOMER_ORDER_API.md), [RRL_CUSTOMER_RULE_API](../programs/RRL_CUSTOMER_RULE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CUSTOMER_ADDRESS` в файле соответствующего типа.
