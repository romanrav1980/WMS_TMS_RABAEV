# RRL_TARE_PARTICIPANT

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| HOLDER_ACTOR | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| HOLDER_ACTOR | P_KIND | 2 | VARCHAR2 | IN | N |  |
| HOLDER_ACTOR | P_ID | 3 | VARCHAR2 | IN | N |  |
| HOLDER_ACTOR | P_OWNER | 4 | NUMBER | IN | N |  |
| HOLDER_ACTOR | P_TRIP | 5 | PL/SQL RECORD | IN | N |  |
| HOLDER_ACTOR | P_RIGHT | 6 | VARCHAR2 | IN | N |  |
| WAREHOUSE_ACTOR | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| WAREHOUSE_ACTOR | P_OWNER | 2 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_STOCK_STORE_RECEIPT_READ](../programs/RRL_STOCK_STORE_RECEIPT_READ.md), [RRL_TARE_PARTICIPANT](../programs/RRL_TARE_PARTICIPANT.md), [RRL_TRANSPORT_DRIVER_USER](../tables/RRL_TRANSPORT_DRIVER_USER.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_TARE_BOOK_CMD](../programs/RRL_STOCK_TARE_BOOK_CMD.md), [RRL_STOCK_TARE_CANCEL_CMD](../programs/RRL_STOCK_TARE_CANCEL_CMD.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_LOSS](../programs/RRL_STOCK_TARE_LOSS.md), [RRL_STOCK_TARE_RESOLVE](../programs/RRL_STOCK_TARE_RESOLVE.md), [RRL_TARE_LOAD_RECOVERY_API](../programs/RRL_TARE_LOAD_RECOVERY_API.md), [RRL_TARE_PARTICIPANT](../programs/RRL_TARE_PARTICIPANT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_PARTICIPANT` в файле соответствующего типа.
