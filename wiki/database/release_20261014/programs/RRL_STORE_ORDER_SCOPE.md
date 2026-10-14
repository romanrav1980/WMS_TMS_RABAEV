# RRL_STORE_ORDER_SCOPE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ACTOR_SCOPE | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| ACTOR_SCOPE | P_PERMISSION | 2 | VARCHAR2 | IN | N |  |
| ACTOR_SCOPE | P_WARE | 3 | NUMBER | OUT | N |  |
| ACTOR_SCOPE | P_GLOBAL | 4 | NUMBER | OUT | N |  |
| ASSERT_SCOPE | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_PERMISSION | 2 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_WARE | 3 | NUMBER | IN | N |  |
| BEGIN_SOURCE | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| BEGIN_SOURCE | P_PERMISSION | 2 | VARCHAR2 | IN | N |  |
| BEGIN_SOURCE | P_WARE | 3 | NUMBER | IN | N |  |
| BEGIN_SOURCE | P_ORDER | 4 | NUMBER | IN | Y |  |
| BEGIN_SUPPLY | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| BEGIN_SUPPLY | P_WARE | 2 | NUMBER | IN | N |  |
| BEGIN_SUPPLY | P_SENDER | 3 | VARCHAR2 | IN | N |  |
| BEGIN_SUPPLY | P_ORDER | 4 | VARCHAR2 | IN | N |  |
| BEGIN_SUPPLY | P_MESSAGE | 5 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_SAP_SUPPLY_LINE](../tables/RRL_SAP_SUPPLY_LINE.md), [RRL_SAP_SUPPLY_ORDER](../tables/RRL_SAP_SUPPLY_ORDER.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STORE_ORDER_SCOPE](../programs/RRL_STORE_ORDER_SCOPE.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_SAP_STORE_ADMISSION_API](../programs/RRL_SAP_STORE_ADMISSION_API.md), [RRL_STORE_ORDER_SCOPE](../programs/RRL_STORE_ORDER_SCOPE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_ORDER_SCOPE` в файле соответствующего типа.
