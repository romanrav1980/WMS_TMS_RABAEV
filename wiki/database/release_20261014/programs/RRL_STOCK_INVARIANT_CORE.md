# RRL_STOCK_INVARIANT_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| SNAPSHOT_STOCK |  |  | CLOB | OUT | N |  |
| SNAPSHOT_STOCK | P_RESOURCES | 1 | CLOB | IN | N |  |
| STOCK_UID |  |  | VARCHAR2 | OUT | N |  |
| STOCK_UID | P_KEY | 1 | RAW | IN | N |  |
| VERIFY_POSTING | P_RESOURCES | 1 | CLOB | IN | N |  |
| VERIFY_POSTING | P_BEFORE | 2 | CLOB | IN | N |  |
| VERIFY_POSTING | P_OPERATION | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_EVENTS](../tables/RRL_EVENTS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_INVARIANT_CORE](../programs/RRL_STOCK_INVARIANT_CORE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_COMPOSITION_CORE](../programs/RRL_STOCK_COMPOSITION_CORE.md), [RRL_STOCK_INVARIANT_CORE](../programs/RRL_STOCK_INVARIANT_CORE.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_INVARIANT_CORE` в файле соответствующего типа.
