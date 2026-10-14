# RRL_PICK_RANGE_POLICY

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| NEW_TARGET_ALLOWED |  |  | NUMBER | OUT | N |  |
| NEW_TARGET_ALLOWED | P_CELL | 1 | VARCHAR2 | IN | N |  |
| NEW_TARGET_ALLOWED | P_ARTICLE | 2 | VARCHAR2 | IN | N |  |
| NEW_TARGET_ALLOWED | P_EXCLUDE_REPL | 3 | NUMBER | IN | Y |  |
| TARGET_WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |
| TARGET_WRITE_ALLOWED | P_CELL | 1 | VARCHAR2 | IN | N |  |
| TARGET_WRITE_ALLOWED | P_ARTICLE | 2 | VARCHAR2 | IN | N |  |
| TARGET_WRITE_ALLOWED | P_REPL | 3 | NUMBER | IN | N |  |
| TARGET_WRITE_ALLOWED | P_QUANTITY | 4 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_PICK_FACE](../tables/RRL_PICK_FACE.md), [RRL_PICK_FACE_ARTICUL](../tables/RRL_PICK_FACE_ARTICUL.md), [RRL_PICK_RANGE_ALLOW_REPL](../tables/RRL_PICK_RANGE_ALLOW_REPL.md), [RRL_PICK_RANGE_POLICY](../programs/RRL_PICK_RANGE_POLICY.md), [RRL_PICK_RANGE_STATUS](../tables/RRL_PICK_RANGE_STATUS.md), [RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md)

## Кто использует

[RRL_PICK_RANGE_POLICY](../programs/RRL_PICK_RANGE_POLICY.md), [RRL_PICK_TOPOLOGY_API](../programs/RRL_PICK_TOPOLOGY_API.md), [RRL_REPL_RANGE_TARGET_G](../programs/RRL_REPL_RANGE_TARGET_G.md), [RRL_STOCK_REPL_CAPACITY](../programs/RRL_STOCK_REPL_CAPACITY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_RANGE_POLICY` в файле соответствующего типа.
