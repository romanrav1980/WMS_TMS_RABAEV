# RRL_BILL_ADD_TTBILL

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_BILL_ADD_TTBILL |  |  | NUMBER | OUT | N |  |
| RRL_BILL_ADD_TTBILL | ID1 | 1 | NUMBER | IN | N |  |
| RRL_BILL_ADD_TTBILL | NUM1 | 2 | VARCHAR2 | IN | N |  |
| RRL_BILL_ADD_TTBILL | COMPANY1 | 3 | VARCHAR2 | IN | N |  |
| RRL_BILL_ADD_TTBILL | DATEOFORDER1 | 4 | DATE | IN | N |  |
| RRL_BILL_ADD_TTBILL | DATEFROM1 | 5 | DATE | IN | N |  |
| RRL_BILL_ADD_TTBILL | DATETO1 | 6 | DATE | IN | N |  |
| RRL_BILL_ADD_TTBILL | NUM_PLAT1 | 7 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_BILL_ORDERS](../tables/RRL_BILL_ORDERS.md), `RRL_BILL_ORDERS_SEQ`

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_BILL_ADD_TTBILL` в файле соответствующего типа.
