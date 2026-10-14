# RRL_STOCK_TARE_LOSS

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_COMMAND | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_DOMAIN | 5 | CLOB | OUT | N |  |
| EXECUTE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_TARE_BALANCE](../tables/RRL_TARE_BALANCE.md), [RRL_TARE_LOSS_CLAIM](../tables/RRL_TARE_LOSS_CLAIM.md), [RRL_TARE_LOSS_DECISION](../tables/RRL_TARE_LOSS_DECISION.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_TARE_LOSS](../programs/RRL_STOCK_TARE_LOSS.md), [RRL_TARE_BALANCE](../tables/RRL_TARE_BALANCE.md), [RRL_TARE_BALANCE_KEY](../programs/RRL_TARE_BALANCE_KEY.md), [RRL_TARE_DAMAGE_TRACE](../programs/RRL_TARE_DAMAGE_TRACE.md), [RRL_TARE_LOSS_CLAIM](../tables/RRL_TARE_LOSS_CLAIM.md), [RRL_TARE_LOSS_DECISION](../tables/RRL_TARE_LOSS_DECISION.md), [RRL_TARE_PARTICIPANT](../programs/RRL_TARE_PARTICIPANT.md), [RRL_TARE_PLANNING](../programs/RRL_TARE_PLANNING.md), [RRL_TARE_STORE_DEBT](../programs/RRL_TARE_STORE_DEBT.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_TARE_LOSS](../programs/RRL_STOCK_TARE_LOSS.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_TARE_LOSS` в файле соответствующего типа.
