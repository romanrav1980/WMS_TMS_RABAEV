# RRL_CUSTOMER_PRODUCT_RULE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CUSTOMER_PRODUCT_RULE_ID` | NUMBER | N |  |
| `CUSTOMER_ID` | NUMBER | N |  |
| `CUSTOMER_STORE_MAP_ID` | NUMBER | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | Y |  |
| `PRODUCT_GROUP` | VARCHAR2(100 bytes) | Y |  |
| `MIN_SHELF_LIFE_DAYS` | NUMBER | Y |  |
| `MIN_SHELF_LIFE_PERCENT` | NUMBER | Y |  |
| `PALLET_CASE_QTY` | NUMBER | Y |  |
| `PALLET_LAYER_QTY` | NUMBER | Y |  |
| `PALLET_LAYER_COUNT` | NUMBER | Y |  |
| `MAX_PALLET_WEIGHT` | NUMBER | Y |  |
| `MAX_PALLET_VOLUME` | NUMBER | Y |  |
| `MAX_PALLET_HEIGHT` | NUMBER | Y |  |
| `PALLET_TYPE` | VARCHAR2(50 bytes) | Y |  |
| `ALLOW_TOP_STACKING` | NUMBER(1,0) | N |  |
| `MUST_BE_SEPARATE_PALLET` | NUMBER(1,0) | N |  |
| `STACK_COMPATIBILITY_GROUP` | VARCHAR2(100 bytes) | Y |  |
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
| RRL_CUSTOMER_PRODUCT_RULE_CHK1 | C | ACTIVE |  | ENABLED |
| RRL_CUSTOMER_PRODUCT_RULE_CHK2 | C | ALLOW_TOP_STACKING |  | ENABLED |
| RRL_CUSTOMER_PRODUCT_RULE_CHK3 | C | MUST_BE_SEPARATE_PALLET |  | ENABLED |
| RRL_CUSTOMER_PRODUCT_RULE_CHK4 | C | MIN_SHELF_LIFE_PERCENT |  | ENABLED |
| RRL_CUSTOMER_PRODUCT_RULE_CHK5 | C | VALID_FROM, VALID_TO |  | ENABLED |
| RRL_CUSTOMER_PRODUCT_RULE_FK1 | R | CUSTOMER_ID | RRL_CUSTOMER (CUSTOMER_ID) | ENABLED |
| RRL_CUSTOMER_PRODUCT_RULE_FK2 | R | CUSTOMER_STORE_MAP_ID | RRL_CUSTOMER_STORE_MAP (CUSTOMER_STORE_MAP_ID) | ENABLED |
| RRL_CUSTOMER_PRODUCT_RULE_PK | P | CUSTOMER_PRODUCT_RULE_ID |  | ENABLED |
| SYS_C0014637 | C | CUSTOMER_PRODUCT_RULE_ID |  | ENABLED |
| SYS_C0014638 | C | CUSTOMER_ID |  | ENABLED |
| SYS_C0014639 | C | ALLOW_TOP_STACKING |  | ENABLED |
| SYS_C0014640 | C | MUST_BE_SEPARATE_PALLET |  | ENABLED |
| SYS_C0014641 | C | RULE_PRIORITY |  | ENABLED |
| SYS_C0014642 | C | ACTIVE |  | ENABLED |
| SYS_C0014643 | C | VALID_FROM |  | ENABLED |
| SYS_C0014644 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CUSTOMER_PRODUCT_RULE` в файле соответствующего типа.
