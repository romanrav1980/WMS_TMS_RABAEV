# RRL_WAREHOUSE_MAP_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Складские задания и топология.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| PUBLISH_DRAFT | P_CANVAS_ID | 1 | NUMBER | IN | N |  |
| PUBLISH_DRAFT | P_PICK_ROUTE_ID | 2 | NUMBER | IN | Y |  |
| PUBLISH_DRAFT | P_PUBLISHED_BY | 3 | VARCHAR2 | IN | Y |  |
| VALIDATE_DRAFT |  |  | CLOB | OUT | N |  |
| VALIDATE_DRAFT | P_CANVAS_ID | 1 | NUMBER | IN | N |  |
| VALIDATE_DRAFT | P_PICK_ROUTE_ID | 2 | NUMBER | IN | Y |  |

## Потенциальные записи по тексту SQL

[RRL_PICK_ROUTE](../tables/RRL_PICK_ROUTE.md), [RRL_WAREHOUSE_MAP_CANVAS](../tables/RRL_WAREHOUSE_MAP_CANVAS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_PICK_ROUTE](../tables/RRL_PICK_ROUTE.md), [RRL_PICK_ROUTE_CELL](../tables/RRL_PICK_ROUTE_CELL.md), [RRL_TOPOLOGY_CELL](../tables/RRL_TOPOLOGY_CELL.md), [RRL_TOPOLOGY_CELL_SLOT](../tables/RRL_TOPOLOGY_CELL_SLOT.md), [RRL_WAREHOUSE_MAP_API](../programs/RRL_WAREHOUSE_MAP_API.md), [RRL_WAREHOUSE_MAP_CAMERA](../tables/RRL_WAREHOUSE_MAP_CAMERA.md), [RRL_WAREHOUSE_MAP_CANVAS](../tables/RRL_WAREHOUSE_MAP_CANVAS.md), [RRL_WAREHOUSE_MAP_PASSAGE](../tables/RRL_WAREHOUSE_MAP_PASSAGE.md)

## Кто использует

[RRL_WAREHOUSE_MAP_API](../programs/RRL_WAREHOUSE_MAP_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WAREHOUSE_MAP_API` в файле соответствующего типа.
