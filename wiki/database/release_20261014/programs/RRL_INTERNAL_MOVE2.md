# RRL_INTERNAL_MOVE2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_INTERNAL_MOVE2 |  |  | VARCHAR2 | OUT | N |  |
| RRL_INTERNAL_MOVE2 | PALLET_ID | 1 | VARCHAR2 | IN | N |  |
| RRL_INTERNAL_MOVE2 | CELL_TO | 2 | VARCHAR2 | IN | N |  |
| RRL_INTERNAL_MOVE2 | COUNT1 | 3 | NUMBER | IN | N |  |
| RRL_INTERNAL_MOVE2 | USER_ID1 | 4 | VARCHAR2 | IN | N |  |
| RRL_INTERNAL_MOVE2 | P_OPERATION_ID | 5 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_INTERNAL_MOVE2_SP_OLD](../programs/RRL_INTERNAL_MOVE2_SP_OLD.md), [RRL_STOCK_NATIVE_API](../programs/RRL_STOCK_NATIVE_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md)

## Кто использует

[REVIZION_SP_OLD](../programs/REVIZION_SP_OLD.md), [RRL_INTERNAL_MOVE3](../programs/RRL_INTERNAL_MOVE3.md), [RRL_INTERNAL_MOVE3_SP_OLD](../programs/RRL_INTERNAL_MOVE3_SP_OLD.md), [RRL_REVIZION_CELL_KOR_SP_OLD](../programs/RRL_REVIZION_CELL_KOR_SP_OLD.md), [RRL_REVIZION_CELL_SP_OLD](../programs/RRL_REVIZION_CELL_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERNAL_MOVE2` в файле соответствующего типа.
