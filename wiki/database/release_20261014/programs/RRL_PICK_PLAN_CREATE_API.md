# RRL_PICK_PLAN_CREATE_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_WRITE | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| CACHED_PLAN |  |  | NUMBER | OUT | N |  |
| CREATE_COMMAND |  |  | NUMBER | OUT | N |  |
| CREATE_COMMAND | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| CREATE_COMMAND | P_ORDER | 2 | NUMBER | IN | N |  |
| CREATE_COMMAND | P_STRATEGY | 3 | VARCHAR2 | IN | N |  |
| CREATE_COMMAND | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| CURRENT_OPERATION |  |  | VARCHAR2 | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_PICK_PLAN_CREATE_OP](../tables/RRL_PICK_PLAN_CREATE_OP.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_PLAN_CREATE_API](../programs/RRL_PICK_PLAN_CREATE_API.md), [RRL_PICK_PLAN_CREATE_OP](../tables/RRL_PICK_PLAN_CREATE_OP.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_CREATE_OP_GUARD](../programs/RRL_PICK_CREATE_OP_GUARD.md), [RRL_PICK_PLAN_ADMISSION](../programs/RRL_PICK_PLAN_ADMISSION.md), [RRL_PICK_PLAN_CREATE_API](../programs/RRL_PICK_PLAN_CREATE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_PLAN_CREATE_API` в файле соответствующего типа.
