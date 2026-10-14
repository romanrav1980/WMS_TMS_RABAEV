# RRL_IW_GROUP_FACT_GUARD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_HEAD | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| ASSERT_HEAD | P_PLAN | 2 | VARCHAR2 | IN | N |  |
| ASSERT_HEAD | P_UID | 3 | VARCHAR2 | IN | N |  |
| ASSERT_HEAD | P_WARE | 4 | NUMBER | IN | N |  |
| ASSERT_HEAD | P_ACTOR | 5 | VARCHAR2 | IN | N |  |
| ASSERT_HEAD | P_KIND | 6 | VARCHAR2 | IN | N |  |
| ASSERT_HEAD | P_CELL | 7 | VARCHAR2 | IN | Y |  |
| ASSERT_HEAD | P_UNLOAD | 8 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_IW_GROUP_FACT_GUARD](../programs/RRL_IW_GROUP_FACT_GUARD.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md)

## Кто использует

[RRL_IW_GROUP_FACT_GUARD](../programs/RRL_IW_GROUP_FACT_GUARD.md), [RRL_IW_GROUP_RECEIPT_GUARD](../programs/RRL_IW_GROUP_RECEIPT_GUARD.md), [RRL_IW_GROUP_UNLOAD_GUARD](../programs/RRL_IW_GROUP_UNLOAD_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_FACT_GUARD` в файле соответствующего типа.
