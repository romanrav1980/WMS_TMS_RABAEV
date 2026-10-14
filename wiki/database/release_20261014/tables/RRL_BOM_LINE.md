# RRL_BOM_LINE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `BOM_LINE_ID` | NUMBER | N |  |
| `BOM_ID` | NUMBER | N |  |
| `LINE_NO` | NUMBER | N |  |
| `COMPONENT_TYPE` | VARCHAR2(30 bytes) | N |  |
| `COMPONENT_ARTICUL` | VARCHAR2(40 bytes) | Y |  |
| `COMPONENT_MOD_ID` | NUMBER | Y |  |
| `COMPONENT_NAME` | VARCHAR2(255 bytes) | Y |  |
| `QTY_PER_BASE` | NUMBER | Y |  |
| `UNIT_CODE` | VARCHAR2(20 bytes) | Y |  |
| `LOSS_PERCENT` | NUMBER | N |  |
| `MIN_TOLERANCE_PCT` | NUMBER | Y |  |
| `MAX_TOLERANCE_PCT` | NUMBER | Y |  |
| `IS_REQUIRED` | NUMBER(1,0) | N |  |
| `SUBSTITUTION_GROUP` | VARCHAR2(100 bytes) | Y |  |
| `REPLACEMENT_RATIO` | NUMBER | Y |  |
| `COMMENT_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_BOM_LINE_CHK1 | C | COMPONENT_TYPE |  | ENABLED |
| RRL_BOM_LINE_CHK2 | C | QTY_PER_BASE |  | ENABLED |
| RRL_BOM_LINE_CHK3 | C | IS_REQUIRED |  | ENABLED |
| RRL_BOM_LINE_CHK4 | C | LOSS_PERCENT |  | ENABLED |
| RRL_BOM_LINE_FK1 | R | BOM_ID | RRL_BOM (BOM_ID) | ENABLED |
| RRL_BOM_LINE_PK | P | BOM_LINE_ID |  | ENABLED |
| RRL_BOM_LINE_U1 | U | BOM_ID, LINE_NO |  | ENABLED |
| SYS_C0014203 | C | BOM_LINE_ID |  | ENABLED |
| SYS_C0014204 | C | BOM_ID |  | ENABLED |
| SYS_C0014205 | C | LINE_NO |  | ENABLED |
| SYS_C0014206 | C | COMPONENT_TYPE |  | ENABLED |
| SYS_C0014207 | C | LOSS_PERCENT |  | ENABLED |
| SYS_C0014208 | C | IS_REQUIRED |  | ENABLED |
| SYS_C0014209 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_BOM_API](../programs/RRL_BOM_API.md), [RRL_MES_PRODUCTION_API](../programs/RRL_MES_PRODUCTION_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_BOM_LINE` в файле соответствующего типа.
