# RRL_CUSTOMER_SHELF_LIFE_RULE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SHELF_LIFE_RULE_ID` | NUMBER | N |  |
| `CUSTOMER_ID` | NUMBER | N |  |
| `CUSTOMER_STORE_MAP_ID` | NUMBER | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | Y |  |
| `PRODUCT_GROUP` | VARCHAR2(100 bytes) | Y |  |
| `MIN_SHELF_LIFE_DAYS` | NUMBER | Y |  |
| `MIN_SHELF_LIFE_PERCENT` | NUMBER | Y |  |
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
| RRL_CSL_RULE_CHK1 | C | ACTIVE |  | ENABLED |
| RRL_CSL_RULE_CHK2 | C | MIN_SHELF_LIFE_PERCENT |  | ENABLED |
| RRL_CSL_RULE_CHK3 | C | VALID_FROM, VALID_TO |  | ENABLED |
| RRL_CSL_RULE_FK1 | R | CUSTOMER_ID | RRL_CUSTOMER (CUSTOMER_ID) | ENABLED |
| RRL_CSL_RULE_FK2 | R | CUSTOMER_STORE_MAP_ID | RRL_CUSTOMER_STORE_MAP (CUSTOMER_STORE_MAP_ID) | ENABLED |
| RRL_CSL_RULE_PK | P | SHELF_LIFE_RULE_ID |  | ENABLED |
| SYS_C0014338 | C | SHELF_LIFE_RULE_ID |  | ENABLED |
| SYS_C0014339 | C | CUSTOMER_ID |  | ENABLED |
| SYS_C0014340 | C | RULE_PRIORITY |  | ENABLED |
| SYS_C0014341 | C | ACTIVE |  | ENABLED |
| SYS_C0014342 | C | VALID_FROM |  | ENABLED |
| SYS_C0014343 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CUSTOMER_SHELF_LIFE_RULE` в файле соответствующего типа.
