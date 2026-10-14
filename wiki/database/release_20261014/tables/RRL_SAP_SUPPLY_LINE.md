# RRL_SAP_SUPPLY_LINE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Интеграция SAP.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ORDER_ID` | VARCHAR2(32 bytes) | N |  |
| `LINE_NUMBER` | VARCHAR2(20 bytes) | N |  |
| `ROW_ID` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `PLANNED_QTY` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `SOURCE_QTY` | NUMBER | N |  |
| `SOURCE_UOM` | VARCHAR2(20 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_SUP_LINE_FK | R | ORDER_ID | RRL_SAP_SUPPLY_ORDER (ORDER_ID) | ENABLED |
| RRL_SAP_SUP_LINE_PK | P | ORDER_ID, LINE_NUMBER |  | ENABLED |
| RRL_SAP_SUP_QTY_CK | C | PLANNED_QTY, SOURCE_QTY |  | ENABLED |
| SYS_C0015890 | C | ORDER_ID |  | ENABLED |
| SYS_C0015891 | C | LINE_NUMBER |  | ENABLED |
| SYS_C0015892 | C | ROW_ID |  | ENABLED |
| SYS_C0015893 | C | ARTICUL |  | ENABLED |
| SYS_C0015894 | C | PLANNED_QTY |  | ENABLED |
| SYS_C0015895 | C | BASE_UOM |  | ENABLED |
| SYS_C0015896 | C | SOURCE_QTY |  | ENABLED |
| SYS_C0015897 | C | SOURCE_UOM |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_RECEIPT_CORE](../programs/RRL_STOCK_RECEIPT_CORE.md), [RRL_STOCK_RECEIPT_PLAN](../programs/RRL_STOCK_RECEIPT_PLAN.md), [RRL_STORE_ORDER_SCOPE](../programs/RRL_STORE_ORDER_SCOPE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_SUPPLY_LINE` в файле соответствующего типа.
