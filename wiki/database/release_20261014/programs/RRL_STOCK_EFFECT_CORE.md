# RRL_STOCK_EFFECT_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CONSUME | P_UID | 1 | VARCHAR2 | IN | N |  |
| CONSUME | P_CELL | 2 | VARCHAR2 | IN | N |  |
| CONSUME | P_QTY | 3 | NUMBER | IN | N |  |
| CONSUME | P_UOM | 4 | VARCHAR2 | IN | N |  |
| CONSUME | P_UOM_VERSION | 5 | NUMBER | IN | N |  |
| CONSUME | P_WAREHOUSE | 6 | NUMBER | IN | N |  |
| CONSUME | P_ACTOR | 7 | VARCHAR2 | IN | N |  |
| CONSUME | P_LINE | 8 | NUMBER | IN | N |  |
| CONSUME | P_RESERVATION | 9 | NUMBER | IN | Y |  |
| CONSUME | P_DOC_TYPE | 10 | VARCHAR2 | IN | Y |  |
| CONSUME | P_DOC_ID | 11 | NUMBER | IN | Y |  |
| CONSUME | P_UNITS | 12 | CLOB | IN | Y |  |
| CONSUME | P_OUTGOING_DOC | 13 | NUMBER | IN | Y |  |
| CONSUME | P_PALLET_ROW | 14 | NUMBER | IN | Y |  |
| CONSUME | P_SUPPLIER_RETURN_RECEIPT | 15 | VARCHAR2 | IN | Y |  |
| CONSUME | P_DISPOSAL_RECEIPT | 16 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_EFFECT_CORE](../programs/RRL_STOCK_EFFECT_CORE.md), [RRL_STOCK_LOCATION_CORE](../programs/RRL_STOCK_LOCATION_CORE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md), [RRL_STOCK_RETURN_DISPOSE](../programs/RRL_STOCK_RETURN_DISPOSE.md), [RRL_STOCK_SUP_RETURN](../programs/RRL_STOCK_SUP_RETURN.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md)

## Кто использует

[RRL_STOCK_EFFECT_CORE](../programs/RRL_STOCK_EFFECT_CORE.md), [RRL_STOCK_MES_MOVEMENT_CORE](../programs/RRL_STOCK_MES_MOVEMENT_CORE.md), [RRL_STOCK_RETURN_DISPOSE](../programs/RRL_STOCK_RETURN_DISPOSE.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_EFFECT_CORE` в файле соответствующего типа.
