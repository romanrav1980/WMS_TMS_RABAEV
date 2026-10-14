# RRL_CUSTOMER_VEHICLE_RULE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортные средства.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CUSTOMER_VEHICLE_RULE_ID` | NUMBER | N |  |
| `CUSTOMER_ID` | NUMBER | N |  |
| `CUSTOMER_STORE_MAP_ID` | NUMBER | Y |  |
| `VEHICLE_TYPE_ID` | NUMBER | N |  |
| `MAX_PALLET_COUNT` | NUMBER | Y |  |
| `MAX_WEIGHT` | NUMBER | Y |  |
| `MAX_VOLUME` | NUMBER | Y |  |
| `SPLIT_ORDER_BY_CAPACITY` | NUMBER(1,0) | N |  |
| `RULE_PRIORITY` | NUMBER | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `VALID_FROM` | DATE | N |  |
| `VALID_TO` | DATE | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CVR_CHK1 | C | ACTIVE |  | ENABLED |
| RRL_CVR_CHK2 | C | SPLIT_ORDER_BY_CAPACITY |  | ENABLED |
| RRL_CVR_CHK3 | C | VALID_FROM, VALID_TO |  | ENABLED |
| RRL_CVR_FK1 | R | CUSTOMER_ID | RRL_CUSTOMER (CUSTOMER_ID) | ENABLED |
| RRL_CVR_FK2 | R | CUSTOMER_STORE_MAP_ID | RRL_CUSTOMER_STORE_MAP (CUSTOMER_STORE_MAP_ID) | ENABLED |
| RRL_CVR_FK3 | R | VEHICLE_TYPE_ID | RRL_VEHICLE_TYPE (VEHICLE_TYPE_ID) | ENABLED |
| RRL_CVR_PK | P | CUSTOMER_VEHICLE_RULE_ID |  | ENABLED |
| SYS_C0014373 | C | CUSTOMER_VEHICLE_RULE_ID |  | ENABLED |
| SYS_C0014374 | C | CUSTOMER_ID |  | ENABLED |
| SYS_C0014375 | C | VEHICLE_TYPE_ID |  | ENABLED |
| SYS_C0014376 | C | SPLIT_ORDER_BY_CAPACITY |  | ENABLED |
| SYS_C0014377 | C | RULE_PRIORITY |  | ENABLED |
| SYS_C0014378 | C | ACTIVE |  | ENABLED |
| SYS_C0014379 | C | VALID_FROM |  | ENABLED |
| SYS_C0014380 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CUSTOMER_RULE_API](../programs/RRL_CUSTOMER_RULE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CUSTOMER_VEHICLE_RULE` в файле соответствующего типа.
