# RRL_STOCK_CHANGE_AUDIT

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DIFFERENCES |  |  | CLOB | OUT | N |  |
| DIFFERENCES | P_BEFORE | 1 | CLOB | IN | N |  |
| DIFFERENCES | P_AFTER | 2 | CLOB | IN | N |  |
| SNAPSHOT |  |  | CLOB | OUT | N |  |
| SNAPSHOT | P_RESOURCES | 1 | CLOB | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_CHANGE_AUDIT](../programs/RRL_STOCK_CHANGE_AUDIT.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_CHANGE_AUDIT](../programs/RRL_STOCK_CHANGE_AUDIT.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_CHANGE_AUDIT` в файле соответствующего типа.
