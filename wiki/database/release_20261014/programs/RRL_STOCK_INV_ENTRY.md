# RRL_STOCK_INV_ENTRY

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COUNT_LOT |  |  | VARCHAR2 | OUT | N |  |
| COUNT_LOT | P_CELL | 1 | VARCHAR2 | IN | N |  |
| COUNT_LOT | P_UID | 2 | VARCHAR2 | IN | N |  |
| COUNT_LOT | P_QUANTITY | 3 | VARCHAR2 | IN | N |  |
| COUNT_LOT | P_UNIT | 4 | VARCHAR2 | IN | N |  |
| COUNT_LOT | P_DOCUMENT | 5 | NUMBER | IN | N |  |
| COUNT_LOT | P_ACTOR | 6 | VARCHAR2 | IN | N |  |
| COUNT_LOT | P_OPERATION | 7 | VARCHAR2 | IN | N |  |
| COUNT_LOT | P_REASON | 8 | VARCHAR2 | IN | N |  |
| REGISTER_LINE |  |  | VARCHAR2 | OUT | N |  |
| REGISTER_LINE | P_CELL | 1 | VARCHAR2 | IN | N |  |
| REGISTER_LINE | P_BARCODE | 2 | VARCHAR2 | IN | N |  |
| REGISTER_LINE | P_ARTICLE_PART | 3 | VARCHAR2 | IN | N |  |
| REGISTER_LINE | P_QTY | 4 | NUMBER | IN | N |  |
| REGISTER_LINE | P_DOCUMENT | 5 | NUMBER | IN | N |  |
| REGISTER_LINE | P_EXPIRY | 6 | DATE | IN | N |  |
| REGISTER_LINE | P_ACTOR | 7 | VARCHAR2 | IN | N |  |
| REGISTER_LINE | P_OPERATION | 8 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_GIVE_NEXT_CELL](../programs/RRL_GIVE_NEXT_CELL.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_INV_ENTRY](../programs/RRL_STOCK_INV_ENTRY.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_NATIVE_API](../programs/RRL_STOCK_NATIVE_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md)

## Кто использует

[RRL_INV_CREATE_LINE2](../programs/RRL_INV_CREATE_LINE2.md), [RRL_INV_CREATE_LINE3](../programs/RRL_INV_CREATE_LINE3.md), [RRL_INV_CREATE_LINE4](../programs/RRL_INV_CREATE_LINE4.md), [RRL_REVIZION_CELL](../programs/RRL_REVIZION_CELL.md), [RRL_REVIZION_CELL_KOR](../programs/RRL_REVIZION_CELL_KOR.md), [RRL_STOCK_INV_ENTRY](../programs/RRL_STOCK_INV_ENTRY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_INV_ENTRY` в файле соответствующего типа.
