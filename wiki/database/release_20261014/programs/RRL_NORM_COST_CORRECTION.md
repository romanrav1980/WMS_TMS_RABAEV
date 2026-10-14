# RRL_NORM_COST_CORRECTION

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Затраты.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CONFIRMED_TOTAL |  |  | NUMBER | OUT | N |  |
| CONFIRMED_TOTAL | P_COST | 1 | VARCHAR2 | IN | N |  |
| VALIDATE_DECISION | P_EXPENSE | 1 | VARCHAR2 | IN | N |  |
| VALIDATE_DECISION | P_PHASE | 2 | VARCHAR2 | IN | N |  |
| VALIDATE_DECISION | P_OUTCOME | 3 | VARCHAR2 | IN | N |  |
| VALIDATE_REPORT | P_COST | 1 | VARCHAR2 | IN | N |  |
| VALIDATE_REPORT | P_WARE | 2 | NUMBER | IN | N |  |
| VALIDATE_REPORT | P_KIND | 3 | VARCHAR2 | IN | N |  |
| VALIDATE_REPORT | P_OBJECT | 4 | NUMBER | IN | N |  |
| VALIDATE_REPORT | P_CURRENCY | 5 | VARCHAR2 | IN | N |  |
| VALIDATE_REPORT | P_DELTA | 6 | NUMBER | IN | N |  |
| VALIDATE_REPORT | P_EXPECTED | 7 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_LOGISTICS_COST_RUN](../tables/RRL_LOGISTICS_COST_RUN.md), [RRL_LOGISTICS_EXPENSE](../tables/RRL_LOGISTICS_EXPENSE.md), [RRL_LOGISTICS_EXP_DECISION](../tables/RRL_LOGISTICS_EXP_DECISION.md), [RRL_NORM_COST_CORRECTION](../programs/RRL_NORM_COST_CORRECTION.md), [RRL_TRANSPORT_COST_CLAIM](../tables/RRL_TRANSPORT_COST_CLAIM.md)

## Кто использует

[RRL_LOG_EXPENSE_GUARD](../programs/RRL_LOG_EXPENSE_GUARD.md), [RRL_LOG_EXP_DECISION_GUARD](../programs/RRL_LOG_EXP_DECISION_GUARD.md), [RRL_NORM_COST_CORRECTION](../programs/RRL_NORM_COST_CORRECTION.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_NORM_COST_CORRECTION` в файле соответствующего типа.
