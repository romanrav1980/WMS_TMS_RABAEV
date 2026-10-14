# RRL_INTERWARE_DEPART_GATE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_READY | P_PROMISES | 1 | CLOB | IN | N |  |
| PROMISES |  |  | CLOB | OUT | N |  |
| PROMISES | P_TRIP | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_INTERWARE_DECISION](../tables/RRL_INTERWARE_DECISION.md), [RRL_INTERWARE_DEPART_GATE](../programs/RRL_INTERWARE_DEPART_GATE.md), [RRL_INTERWARE_ONWARD_BIND](../tables/RRL_INTERWARE_ONWARD_BIND.md), [RRL_INTERWARE_ONWARD_DISPATCH](../tables/RRL_INTERWARE_ONWARD_DISPATCH.md), [RRL_INTERWARE_PLAN](../tables/RRL_INTERWARE_PLAN.md), [RRL_INTERWARE_RECEIPT](../tables/RRL_INTERWARE_RECEIPT.md), [RRL_INTERWARE_ROUTING](../programs/RRL_INTERWARE_ROUTING.md), [RRL_INTERWARE_SHORTAGE_FACT](../tables/RRL_INTERWARE_SHORTAGE_FACT.md), [RRL_INTERWARE_THERMAL](../programs/RRL_INTERWARE_THERMAL.md), [RRL_IW_GROUP_PLAN](../tables/RRL_IW_GROUP_PLAN.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md)

## Кто использует

[RRL_INTERWARE_DEPART_GATE](../programs/RRL_INTERWARE_DEPART_GATE.md), [RRL_STOCK_TRIP_DEPART_CMD](../programs/RRL_STOCK_TRIP_DEPART_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_DEPART_GATE` в файле соответствующего типа.
