# RRL_WEIGHT_CHOICE_UNIT_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| SELECTED_UNITS |  |  | CLOB | OUT | N |  |
| SELECTED_UNITS | P_TASK | 1 | NUMBER | IN | N |  |
| SELECTED_UNITS | P_UID | 2 | VARCHAR2 | IN | N |  |
| SELECTED_UNITS | P_CELL | 3 | VARCHAR2 | IN | N |  |
| SELECTED_UNITS | P_QTY | 4 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WEIGHT_CHOICE](../tables/RRL_PICK_WEIGHT_CHOICE.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_WEIGHT_CHOICE_UNIT_READ](../programs/RRL_WEIGHT_CHOICE_UNIT_READ.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_WAVE_CMD](../programs/RRL_STOCK_WAVE_CMD.md), [RRL_STOCK_WAVE_LAUNCH_CMD](../programs/RRL_STOCK_WAVE_LAUNCH_CMD.md), [RRL_WEIGHT_CHOICE_UNIT_READ](../programs/RRL_WEIGHT_CHOICE_UNIT_READ.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WEIGHT_CHOICE_UNIT_READ` в файле соответствующего типа.
