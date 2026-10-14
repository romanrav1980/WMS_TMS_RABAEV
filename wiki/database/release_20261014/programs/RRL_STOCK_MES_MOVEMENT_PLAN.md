# RRL_STOCK_MES_MOVEMENT_PLAN

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_MOVEMENTS | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_MOVEMENTS | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_MOVEMENTS | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_MOVEMENTS | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_MOVEMENTS | P_DOMAIN | 5 | CLOB | OUT | N |  |
| SIGNATURE |  |  | VARCHAR2 | OUT | N |  |
| SIGNATURE | P_M | 1 | PL/SQL RECORD | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_MES_MOVEMENT](../tables/RRL_MES_MOVEMENT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PRODUCTION_ORDER](../tables/RRL_PRODUCTION_ORDER.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_MES_MOVEMENT_PLAN](../programs/RRL_STOCK_MES_MOVEMENT_PLAN.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), `RRL_STOCK_RESERVATION_SQ`, [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md)

## Кто использует

[RRL_STOCK_MES_MOVEMENT_CORE](../programs/RRL_STOCK_MES_MOVEMENT_CORE.md), [RRL_STOCK_MES_MOVEMENT_PLAN](../programs/RRL_STOCK_MES_MOVEMENT_PLAN.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_MES_MOVEMENT_PLAN` в файле соответствующего типа.
