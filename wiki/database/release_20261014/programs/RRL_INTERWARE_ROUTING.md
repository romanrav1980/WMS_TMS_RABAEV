# RRL_INTERWARE_ROUTING

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| OUTBOUND_DOCK |  |  | VARCHAR2 | OUT | N |  |
| OUTBOUND_DOCK | P_PLAN | 1 | VARCHAR2 | IN | N |  |
| READY_DUE |  |  | TIMESTAMP WITH TIME ZONE | OUT | N |  |
| READY_DUE | P_PLAN | 1 | VARCHAR2 | IN | N |  |
| RECORD_DECISION | P_REQUEST | 1 | CLOB | IN | N |  |
| RECORD_DECISION | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| RECORD_DECISION | P_RESULT | 3 | CLOB | OUT | N |  |
| RESOLVED |  |  | PL/SQL RECORD | OUT | N |  |
| RESOLVED | P_PLAN | 1 | PL/SQL RECORD | IN | N |  |
| TARGET_TRIP |  |  | NUMBER | OUT | N |  |
| TARGET_TRIP | P_PLAN | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_INTERWARE_DECISION](../tables/RRL_INTERWARE_DECISION.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_INTERWARE_DECISION](../tables/RRL_INTERWARE_DECISION.md), [RRL_INTERWARE_PLAN](../tables/RRL_INTERWARE_PLAN.md), [RRL_INTERWARE_RECEIPT](../tables/RRL_INTERWARE_RECEIPT.md), [RRL_INTERWARE_ROUTING](../programs/RRL_INTERWARE_ROUTING.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_DOCK](../tables/RRL_TT_DOCK.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_INTERWARE_DEPART_GATE](../programs/RRL_INTERWARE_DEPART_GATE.md), [RRL_INTERWARE_ONWARD_BIND_GUARD](../programs/RRL_INTERWARE_ONWARD_BIND_GUARD.md), [RRL_INTERWARE_ROUTING](../programs/RRL_INTERWARE_ROUTING.md), [RRL_INTERWARE_THERMAL](../programs/RRL_INTERWARE_THERMAL.md), [RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_STOCK_IW_RECOVERY_PUT](../programs/RRL_STOCK_IW_RECOVERY_PUT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_ROUTING` в файле соответствующего типа.
