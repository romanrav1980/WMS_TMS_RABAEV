# RRL_BOX_ASSEMBLY_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CLOCKS_JSON |  |  | CLOB | OUT | N |  |
| CLOCKS_JSON | P_TREE | 1 | CLOB | IN | N |  |
| CLOCKS_JSON | P_WARE | 2 | NUMBER | IN | N |  |
| CLOCKS_JSON | P_REGION | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_BOX_ASSEMBLY_READ](../programs/RRL_BOX_ASSEMBLY_READ.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_HU_PACK_CYCLE](../tables/RRL_HU_PACK_CYCLE.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md)

## Кто использует

[RRL_BOX_ASSEMBLY_READ](../programs/RRL_BOX_ASSEMBLY_READ.md), [RRL_LOG_COST_LINE_GUARD](../programs/RRL_LOG_COST_LINE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_BOX_ASSEMBLY_READ` в файле соответствующего типа.
