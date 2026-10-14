# RRL_STOCK_REPL_ADMISSION

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_TARGET | P_UID | 1 | VARCHAR2 | IN | N |  |
| ASSERT_TARGET | P_TARGET | 2 | VARCHAR2 | IN | N |  |
| ASSERT_TARGET | P_WARE | 3 | NUMBER | IN | N |  |
| ASSERT_TARGET | P_ARTICLE | 4 | VARCHAR2 | IN | N |  |
| LOT_KEY |  |  | VARCHAR2 | OUT | N |  |
| LOT_KEY | P_UID | 1 | VARCHAR2 | IN | N |  |
| MODE_FOR |  |  | VARCHAR2 | OUT | N |  |
| MODE_FOR | P_TASK | 1 | NUMBER | IN | N |  |
| POLICY_SIGNATURE |  |  | VARCHAR2 | OUT | N |  |
| POLICY_SIGNATURE | P_TASK | 1 | NUMBER | IN | N |  |
| REASON |  |  | VARCHAR2 | OUT | N |  |
| REASON | P_UID | 1 | VARCHAR2 | IN | N |  |
| REASON | P_TARGET | 2 | VARCHAR2 | IN | N |  |
| REASON | P_WARE | 3 | NUMBER | IN | N |  |
| REASON | P_ARTICLE | 4 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CASE_PICK_SHORT](../tables/RRL_CASE_PICK_SHORT.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md), [RRL_RECEIPT_SKU_RULE](../tables/RRL_RECEIPT_SKU_RULE.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SAP_PALLET_RECEIPT](../tables/RRL_SAP_PALLET_RECEIPT.md), [RRL_STOCK_REPL_ADMISSION](../programs/RRL_STOCK_REPL_ADMISSION.md)

## Кто использует

[RRL_STOCK_REPL_ADMISSION](../programs/RRL_STOCK_REPL_ADMISSION.md), [RRL_STOCK_RETURN_REUSE](../programs/RRL_STOCK_RETURN_REUSE.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_WAVE_CMD](../programs/RRL_STOCK_WAVE_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_REPL_ADMISSION` в файле соответствующего типа.
