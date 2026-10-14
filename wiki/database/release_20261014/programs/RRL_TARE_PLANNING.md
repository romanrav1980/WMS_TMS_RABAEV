# RRL_TARE_PLANNING

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_AVAILABLE | P_KEY | 1 | RAW | IN | N |  |
| ASSERT_AVAILABLE | P_PHYSICAL | 2 | NUMBER | IN | N |  |
| ASSERT_AVAILABLE | P_REQUIRED | 3 | NUMBER | IN | N |  |
| CASE_BOOKING |  |  | VARCHAR2 | OUT | N |  |
| CASE_BOOKING | P_TASK | 1 | NUMBER | IN | N |  |
| CASE_BOOKING | P_WARE | 2 | NUMBER | IN | N |  |
| CASE_BOOKING | P_TYPE | 3 | NUMBER | IN | N |  |
| HELD_QUANTITY |  |  | NUMBER | OUT | N |  |
| HELD_QUANTITY | P_KEY | 1 | RAW | IN | N |  |
| REQUIRE_CASE | P_TASK | 1 | NUMBER | IN | N |  |
| REQUIRE_CASE | P_WARE | 2 | NUMBER | IN | N |  |
| REQUIRE_CASE | P_TYPE | 3 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TARE_BOOK](../tables/RRL_TARE_BOOK.md), [RRL_TARE_LOSS_PENDING](../programs/RRL_TARE_LOSS_PENDING.md), [RRL_TARE_PLANNING](../programs/RRL_TARE_PLANNING.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

## Кто использует

[RRL_CASE_TARE_START_GUARD](../programs/RRL_CASE_TARE_START_GUARD.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_LOSS](../programs/RRL_STOCK_TARE_LOSS.md), [RRL_STOCK_TARE_RESOLVE](../programs/RRL_STOCK_TARE_RESOLVE.md), [RRL_TARE_DAMAGE_TRACE](../programs/RRL_TARE_DAMAGE_TRACE.md), [RRL_TARE_PLANNING](../programs/RRL_TARE_PLANNING.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_PLANNING` в файле соответствующего типа.
