# RRL_TARE_DAMAGE_TRACE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Маркировка и агрегация.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CHECK_TRANSFER | P_DAMAGE | 1 | VARCHAR2 | IN | N |  |
| CHECK_TRANSFER | P_KEY | 2 | RAW | IN | N |  |
| CHECK_TRANSFER | P_QUANTITY | 3 | NUMBER | IN | N |  |
| CHECK_TRANSFER | P_PHYSICAL | 4 | NUMBER | IN | N |  |
| OFFER_ORIGIN |  |  | VARCHAR2 | OUT | N |  |
| OFFER_ORIGIN | P_OFFER | 1 | VARCHAR2 | IN | N |  |
| ORIGIN_EXISTS |  |  | PL/SQL BOOLEAN | OUT | N |  |
| ORIGIN_EXISTS | P_DAMAGE | 1 | VARCHAR2 | IN | N |  |
| RECORD_OFFER | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| RECORD_OFFER | P_DAMAGE | 2 | VARCHAR2 | IN | N |  |
| RECORD_TRANSFER | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| RECORD_TRANSFER | P_DAMAGE | 2 | VARCHAR2 | IN | N |  |
| RECORD_TRANSFER | P_FROM | 3 | RAW | IN | N |  |
| RECORD_TRANSFER | P_TO | 4 | RAW | IN | N |  |
| RECORD_TRANSFER | P_QUANTITY | 5 | NUMBER | IN | N |  |
| RECORD_WRITEOFF | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| RECORD_WRITEOFF | P_DAMAGE | 2 | VARCHAR2 | IN | N |  |
| RECORD_WRITEOFF | P_KEY | 3 | RAW | IN | N |  |
| RECORD_WRITEOFF | P_QUANTITY | 4 | NUMBER | IN | N |  |
| REGISTER_DAMAGE | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| REGISTER_DAMAGE | P_KEY | 2 | RAW | IN | N |  |
| REGISTER_DAMAGE | P_QUANTITY | 3 | NUMBER | IN | N |  |
| TRACKED_QUANTITY |  |  | NUMBER | OUT | N |  |
| TRACKED_QUANTITY | P_KEY | 1 | RAW | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TARE_DAMAGE_MOVE](../tables/RRL_TARE_DAMAGE_MOVE.md), [RRL_TARE_DAMAGE_OFFER](../tables/RRL_TARE_DAMAGE_OFFER.md), [RRL_TARE_DAMAGE_ORIGIN](../tables/RRL_TARE_DAMAGE_ORIGIN.md), [RRL_TARE_DAMAGE_POSITION](../tables/RRL_TARE_DAMAGE_POSITION.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_TARE_ASSERT_WRITE](../programs/RRL_TARE_ASSERT_WRITE.md), [RRL_TARE_DAMAGE_MOVE](../tables/RRL_TARE_DAMAGE_MOVE.md), [RRL_TARE_DAMAGE_OFFER](../tables/RRL_TARE_DAMAGE_OFFER.md), [RRL_TARE_DAMAGE_ORIGIN](../tables/RRL_TARE_DAMAGE_ORIGIN.md), [RRL_TARE_DAMAGE_POSITION](../tables/RRL_TARE_DAMAGE_POSITION.md), [RRL_TARE_DAMAGE_TRACE](../programs/RRL_TARE_DAMAGE_TRACE.md), [RRL_TARE_PLANNING](../programs/RRL_TARE_PLANNING.md)

## Кто использует

[RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_LOSS](../programs/RRL_STOCK_TARE_LOSS.md), [RRL_STOCK_TARE_RESOLVE](../programs/RRL_STOCK_TARE_RESOLVE.md), [RRL_TARE_DAMAGE_TRACE](../programs/RRL_TARE_DAMAGE_TRACE.md), [RRL_TARE_DMOVE_GUARD](../programs/RRL_TARE_DMOVE_GUARD.md), [RRL_TARE_DOFFER_GUARD](../programs/RRL_TARE_DOFFER_GUARD.md), [RRL_TARE_DORIGIN_GUARD](../programs/RRL_TARE_DORIGIN_GUARD.md), [RRL_TARE_DPOSITION_GUARD](../programs/RRL_TARE_DPOSITION_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_DAMAGE_TRACE` в файле соответствующего типа.
