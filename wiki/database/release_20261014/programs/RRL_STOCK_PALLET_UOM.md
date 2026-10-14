# RRL_STOCK_PALLET_UOM

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RESOLVE_QUANTITY | P_UID | 1 | VARCHAR2 | IN | N |  |
| RESOLVE_QUANTITY | P_INPUT | 2 | VARCHAR2 | IN | N |  |
| RESOLVE_QUANTITY | P_QUANTITY | 3 | VARCHAR2 | IN | N |  |
| RESOLVE_QUANTITY | P_BASE | 4 | VARCHAR2 | OUT | N |  |
| RESOLVE_QUANTITY | P_QUANTITY_BASE | 5 | NUMBER | OUT | N |  |
| RESOLVE_QUANTITY | P_VERSION | 6 | NUMBER | OUT | N |  |
| RESOLVE_QUANTITY | P_SIGNATURE | 7 | VARCHAR2 | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_ARTICUL_MODS](../tables/RRL_ARTICUL_MODS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PALLET_UOM](../programs/RRL_STOCK_PALLET_UOM.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md)

## Кто использует

[RRL_STOCK_INTERNAL_CMD](../programs/RRL_STOCK_INTERNAL_CMD.md), [RRL_STOCK_INVENTORY_CMD](../programs/RRL_STOCK_INVENTORY_CMD.md), [RRL_STOCK_PALLET_UOM](../programs/RRL_STOCK_PALLET_UOM.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TASK_PLAN](../programs/RRL_STOCK_TASK_PLAN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_PALLET_UOM` в файле соответствующего типа.
