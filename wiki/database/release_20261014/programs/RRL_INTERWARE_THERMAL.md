# RRL_INTERWARE_THERMAL

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_CELL | P_MODE | 1 | CLOB | IN | N |  |
| ASSERT_CELL | P_WARE | 2 | NUMBER | IN | N |  |
| ASSERT_CELL | P_CELL | 3 | VARCHAR2 | IN | N |  |
| ASSERT_RELEASE | P_PLAN | 1 | VARCHAR2 | IN | N |  |
| MODE_JSON |  |  | CLOB | OUT | N |  |
| MODE_JSON | P_PLAN | 1 | VARCHAR2 | IN | N |  |
| RECORD_DECISION | P_REQUEST | 1 | CLOB | IN | N |  |
| RECORD_DECISION | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| RECORD_DECISION | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_INTERWARE_THERMAL_FACT](../tables/RRL_INTERWARE_THERMAL_FACT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_INTERWARE_PLAN](../tables/RRL_INTERWARE_PLAN.md), [RRL_INTERWARE_ROUTING](../programs/RRL_INTERWARE_ROUTING.md), [RRL_INTERWARE_THERMAL](../programs/RRL_INTERWARE_THERMAL.md), [RRL_INTERWARE_THERMAL_FACT](../tables/RRL_INTERWARE_THERMAL_FACT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_RECEIPT_CELL_RULE](../tables/RRL_RECEIPT_CELL_RULE.md), [RRL_RECEIPT_SKU_RULE](../tables/RRL_RECEIPT_SKU_RULE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_INTERWARE_DEPART_GATE](../programs/RRL_INTERWARE_DEPART_GATE.md), [RRL_INTERWARE_THERMAL](../programs/RRL_INTERWARE_THERMAL.md), [RRL_IW_GROUP_THERMAL](../programs/RRL_IW_GROUP_THERMAL.md), [RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md), [RRL_STOCK_IW_RECOVERY_PUT](../programs/RRL_STOCK_IW_RECOVERY_PUT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_THERMAL` в файле соответствующего типа.
