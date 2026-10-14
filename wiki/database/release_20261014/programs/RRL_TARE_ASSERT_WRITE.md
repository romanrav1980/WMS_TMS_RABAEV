# RRL_TARE_ASSERT_WRITE

Тип: **PROCEDURE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TARE_ASSERT_WRITE | P_TABLE | 1 | VARCHAR2 | IN | N |  |
| RRL_TARE_ASSERT_WRITE | P_KEY | 2 | VARCHAR2 | IN | N |  |
| RRL_TARE_ASSERT_WRITE | P_KIND | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md)

## Кто использует

[RRL_TARE_ACCEPT_GUARD](../programs/RRL_TARE_ACCEPT_GUARD.md), [RRL_TARE_BALANCE_GUARD](../programs/RRL_TARE_BALANCE_GUARD.md), [RRL_TARE_BOOK_GUARD](../programs/RRL_TARE_BOOK_GUARD.md), [RRL_TARE_DAMAGE_TRACE](../programs/RRL_TARE_DAMAGE_TRACE.md), [RRL_TARE_DELIVERY_POLICY_GUARD](../programs/RRL_TARE_DELIVERY_POLICY_GUARD.md), [RRL_TARE_JOURNAL_GUARD](../programs/RRL_TARE_JOURNAL_GUARD.md), [RRL_TARE_LOAD_RECOVERY_GUARD](../programs/RRL_TARE_LOAD_RECOVERY_GUARD.md), [RRL_TARE_LOSS_CLAIM_GUARD](../programs/RRL_TARE_LOSS_CLAIM_GUARD.md), [RRL_TARE_LOSS_DEC_GUARD](../programs/RRL_TARE_LOSS_DEC_GUARD.md), [RRL_TARE_OFFER_BOOK_GUARD](../programs/RRL_TARE_OFFER_BOOK_GUARD.md), [RRL_TARE_OFFER_CANCEL_GUARD](../programs/RRL_TARE_OFFER_CANCEL_GUARD.md), [RRL_TARE_OFFER_GUARD](../programs/RRL_TARE_OFFER_GUARD.md), [RRL_TARE_RESOLUTION_GUARD](../programs/RRL_TARE_RESOLUTION_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_ASSERT_WRITE` в файле соответствующего типа.
