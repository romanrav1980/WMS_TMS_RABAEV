# RRL_TT_ADD_PALL

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TT_ADD_PALL |  |  | VARCHAR2 | OUT | N |  |
| RRL_TT_ADD_PALL | TT_ID | 1 | NUMBER | IN | N |  |
| RRL_TT_ADD_PALL | ST_NUMBER1 | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_TT_MEMBERSHIP_CTX_API](../programs/RRL_TT_MEMBERSHIP_CTX_API.md), [RRL_TT_REGIONS](../programs/RRL_TT_REGIONS.md)

## Кто использует

[RRL_ST_DEFER_API](../programs/RRL_ST_DEFER_API.md), [RRL_TRANSPORT_PLAN_API](../programs/RRL_TRANSPORT_PLAN_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_ADD_PALL` в файле соответствующего типа.
