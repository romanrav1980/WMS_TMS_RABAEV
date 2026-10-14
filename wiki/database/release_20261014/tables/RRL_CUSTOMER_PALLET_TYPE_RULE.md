# RRL_CUSTOMER_PALLET_TYPE_RULE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CUSTOMER_PALLET_TYPE_RULE_ID` | NUMBER | N |  |
| `CUSTOMER_ID` | NUMBER | N |  |
| `CUSTOMER_ADDRESS_ID` | NUMBER | Y |  |
| `CUSTOMER_STORE_MAP_ID` | NUMBER | Y |  |
| `PALLET_TYPE_ID` | NUMBER | N |  |
| `IS_DEFAULT` | NUMBER(1,0) | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `VALID_FROM` | DATE | N |  |
| `VALID_TO` | DATE | Y |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CUST_PALLET_RULE_CHK1 | C | IS_DEFAULT |  | ENABLED |
| RRL_CUST_PALLET_RULE_CHK2 | C | ACTIVE |  | ENABLED |
| RRL_CUST_PALLET_RULE_CHK3 | C | VALID_FROM, VALID_TO |  | ENABLED |
| RRL_CUST_PALLET_RULE_FK1 | R | CUSTOMER_ID | RRL_CUSTOMER (CUSTOMER_ID) | ENABLED |
| RRL_CUST_PALLET_RULE_FK2 | R | CUSTOMER_ADDRESS_ID | RRL_CUSTOMER_ADDRESS (CUSTOMER_ADDRESS_ID) | ENABLED |
| RRL_CUST_PALLET_RULE_FK3 | R | CUSTOMER_STORE_MAP_ID | RRL_CUSTOMER_STORE_MAP (CUSTOMER_STORE_MAP_ID) | ENABLED |
| RRL_CUST_PALLET_RULE_FK4 | R | PALLET_TYPE_ID | RRL_PALLET_TYPE (PALLET_TYPE_ID) | ENABLED |
| RRL_CUST_PALLET_RULE_PK | P | CUSTOMER_PALLET_TYPE_RULE_ID |  | ENABLED |
| SYS_C0014904 | C | CUSTOMER_PALLET_TYPE_RULE_ID |  | ENABLED |
| SYS_C0014905 | C | CUSTOMER_ID |  | ENABLED |
| SYS_C0014906 | C | PALLET_TYPE_ID |  | ENABLED |
| SYS_C0014907 | C | IS_DEFAULT |  | ENABLED |
| SYS_C0014908 | C | ACTIVE |  | ENABLED |
| SYS_C0014909 | C | VALID_FROM |  | ENABLED |
| SYS_C0014910 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_RECIPIENT_PALLET_POLICY](../programs/RRL_RECIPIENT_PALLET_POLICY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CUSTOMER_PALLET_TYPE_RULE` в файле соответствующего типа.
