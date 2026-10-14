# RRL_STOCK_LOAD_RECONCILE_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| PREVIEW_JSON |  |  | CLOB | OUT | N |  |
| PREVIEW_JSON | P_ORIGINAL | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_LOAD_RECONCILE_READ](../programs/RRL_STOCK_LOAD_RECONCILE_READ.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_TT_LOAD_RECONCILE](../tables/RRL_TT_LOAD_RECONCILE.md)

## Кто использует

[RRL_STOCK_LOAD_RECONCILE_READ](../programs/RRL_STOCK_LOAD_RECONCILE_READ.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_LOAD_RECONCILE_READ` в файле соответствующего типа.
