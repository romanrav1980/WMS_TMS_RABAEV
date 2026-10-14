# RRL_PICK_PLAN_ACCESS

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_SCOPE | P_ORDER | 1 | NUMBER | IN | N |  |
| ASSERT_SCOPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_PERMISSION | 3 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PICK_PLAN_ACCESS](../programs/RRL_PICK_PLAN_ACCESS.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_PICK_PLAN_ACCESS](../programs/RRL_PICK_PLAN_ACCESS.md), [RRL_PICK_PLAN_ADMISSION](../programs/RRL_PICK_PLAN_ADMISSION.md), [RRL_WEIGHT_BOX_CHOICE_API](../programs/RRL_WEIGHT_BOX_CHOICE_API.md), [RRL_WEIGHT_BOX_PLANNING_READ](../programs/RRL_WEIGHT_BOX_PLANNING_READ.md), [RRL_WEIGHT_PLAN_BIND](../programs/RRL_WEIGHT_PLAN_BIND.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_PLAN_ACCESS` в файле соответствующего типа.
