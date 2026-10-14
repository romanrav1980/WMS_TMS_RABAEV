# RRL_BOM

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `BOM_ID` | NUMBER | N |  |
| `BOM_CODE` | VARCHAR2(100 bytes) | N |  |
| `BOM_NAME` | VARCHAR2(255 bytes) | Y |  |
| `TARGET_ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `TARGET_MOD_ID` | NUMBER | Y |  |
| `TARGET_GTIN` | VARCHAR2(14 bytes) | Y |  |
| `BOM_KIND` | VARCHAR2(30 bytes) | N |  |
| `BASE_QTY` | NUMBER | N |  |
| `BASE_UNIT_CODE` | VARCHAR2(20 bytes) | N |  |
| `IS_PRIMARY` | NUMBER(1,0) | N |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `VALID_FROM` | DATE | N |  |
| `VALID_TO` | DATE | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `PRODUCTION_LINE` | VARCHAR2(100 bytes) | Y |  |
| `VERSION_NO` | NUMBER | N |  |
| `PARENT_BOM_ID` | NUMBER | Y |  |
| `COMMENT_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `APPROVED_AT` | DATE | Y |  |
| `APPROVED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_BOM_CHK1 | C | BOM_KIND |  | ENABLED |
| RRL_BOM_CHK2 | C | BASE_QTY |  | ENABLED |
| RRL_BOM_CHK3 | C | IS_PRIMARY |  | ENABLED |
| RRL_BOM_CHK4 | C | STATUS |  | ENABLED |
| RRL_BOM_CHK5 | C | VALID_FROM, VALID_TO |  | ENABLED |
| RRL_BOM_FK1 | R | PARENT_BOM_ID | RRL_BOM (BOM_ID) | ENABLED |
| RRL_BOM_PK | P | BOM_ID |  | ENABLED |
| RRL_BOM_U1 | U | BOM_CODE |  | ENABLED |
| SYS_C0014184 | C | BOM_ID |  | ENABLED |
| SYS_C0014185 | C | BOM_CODE |  | ENABLED |
| SYS_C0014186 | C | TARGET_ARTICUL |  | ENABLED |
| SYS_C0014187 | C | BOM_KIND |  | ENABLED |
| SYS_C0014188 | C | BASE_QTY |  | ENABLED |
| SYS_C0014189 | C | BASE_UNIT_CODE |  | ENABLED |
| SYS_C0014190 | C | IS_PRIMARY |  | ENABLED |
| SYS_C0014191 | C | STATUS |  | ENABLED |
| SYS_C0014192 | C | VALID_FROM |  | ENABLED |
| SYS_C0014193 | C | VERSION_NO |  | ENABLED |
| SYS_C0014194 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_BOM_API](../programs/RRL_BOM_API.md), [RRL_MES_PRODUCTION_API](../programs/RRL_MES_PRODUCTION_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_BOM` в файле соответствующего типа.
