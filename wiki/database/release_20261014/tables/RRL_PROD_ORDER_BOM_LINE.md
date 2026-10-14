# RRL_PROD_ORDER_BOM_LINE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ORDER_LINE_ID` | NUMBER | N |  |
| `PRODUCTION_ORDER_ID` | NUMBER | N |  |
| `BOM_ID` | NUMBER | N |  |
| `BOM_LINE_ID` | NUMBER | Y |  |
| `LINE_NO` | NUMBER | N |  |
| `COMPONENT_TYPE` | VARCHAR2(30 bytes) | N |  |
| `COMPONENT_ARTICUL` | VARCHAR2(40 bytes) | Y |  |
| `COMPONENT_MOD_ID` | NUMBER | Y |  |
| `COMPONENT_NAME` | VARCHAR2(255 bytes) | Y |  |
| `PLANNED_QTY` | NUMBER | Y |  |
| `UNIT_CODE` | VARCHAR2(20 bytes) | Y |  |
| `LOSS_PERCENT` | NUMBER | N |  |
| `IS_REQUIRED` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PROD_ORDER_BOM_LINE_CHK1 | C | PLANNED_QTY |  | ENABLED |
| RRL_PROD_ORDER_BOM_LINE_FK1 | R | PRODUCTION_ORDER_ID | RRL_PRODUCTION_ORDER (PRODUCTION_ORDER_ID) | ENABLED |
| RRL_PROD_ORDER_BOM_LINE_FK2 | R | BOM_ID | RRL_BOM (BOM_ID) | ENABLED |
| RRL_PROD_ORDER_BOM_LINE_PK | P | ORDER_LINE_ID |  | ENABLED |
| RRL_PROD_ORDER_BOM_LINE_U1 | U | PRODUCTION_ORDER_ID, LINE_NO |  | ENABLED |
| SYS_C0014237 | C | ORDER_LINE_ID |  | ENABLED |
| SYS_C0014238 | C | PRODUCTION_ORDER_ID |  | ENABLED |
| SYS_C0014239 | C | BOM_ID |  | ENABLED |
| SYS_C0014240 | C | LINE_NO |  | ENABLED |
| SYS_C0014241 | C | COMPONENT_TYPE |  | ENABLED |
| SYS_C0014242 | C | LOSS_PERCENT |  | ENABLED |
| SYS_C0014243 | C | IS_REQUIRED |  | ENABLED |
| SYS_C0014244 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_MES_PRODUCTION_API](../programs/RRL_MES_PRODUCTION_API.md), [RRL_MES_RAW_SUPPLY_OLD](../programs/RRL_MES_RAW_SUPPLY_OLD.md), [RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PROD_ORDER_BOM_LINE` в файле соответствующего типа.
