# RRL_STOCK_TARE_CMD

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

[RRL_TARE_ACCEPT](../tables/RRL_TARE_ACCEPT.md), [RRL_TARE_BALANCE](../tables/RRL_TARE_BALANCE.md), [RRL_TARE_JOURNAL](../tables/RRL_TARE_JOURNAL.md), [RRL_TARE_OFFER](../tables/RRL_TARE_OFFER.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_HANDOVER](../programs/RRL_STOCK_TARE_HANDOVER.md), [RRL_STOCK_TARE_POLICY](../programs/RRL_STOCK_TARE_POLICY.md), [RRL_TARE_ACCEPT](../tables/RRL_TARE_ACCEPT.md), [RRL_TARE_BALANCE](../tables/RRL_TARE_BALANCE.md), [RRL_TARE_BALANCE_KEY](../programs/RRL_TARE_BALANCE_KEY.md), [RRL_TARE_DAMAGE_TRACE](../programs/RRL_TARE_DAMAGE_TRACE.md), [RRL_TARE_JOURNAL](../tables/RRL_TARE_JOURNAL.md), [RRL_TARE_OFFER](../tables/RRL_TARE_OFFER.md), [RRL_TARE_OFFER_CANCEL](../tables/RRL_TARE_OFFER_CANCEL.md), [RRL_TARE_PARTICIPANT](../programs/RRL_TARE_PARTICIPANT.md), [RRL_TARE_PLANNING](../programs/RRL_TARE_PLANNING.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RRL_TR_VODITEL](../tables/RRL_TR_VODITEL.md), [RRL_WARES](../tables/RRL_WARES.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_TARE_CMD` в файле соответствующего типа.
