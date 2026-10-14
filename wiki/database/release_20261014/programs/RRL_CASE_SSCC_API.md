# RRL_CASE_SSCC_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Сборка CASE.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_READY | P_TASK | 1 | NUMBER | IN | N |  |
| CONFIRM_LABEL | P_TASK | 1 | NUMBER | IN | N |  |
| CONFIRM_LABEL | P_SSCC | 2 | VARCHAR2 | IN | N |  |
| CONFIRM_LABEL | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| CONFIRM_LABEL | P_RESULT | 4 | CLOB | OUT | N |  |
| ISSUE | P_TASK | 1 | NUMBER | IN | N |  |
| ISSUE | P_REQUEST | 2 | CLOB | IN | N |  |
| ISSUE | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| ISSUE | P_RESULT | 4 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CASE_SSCC_LABEL](../tables/RRL_CASE_SSCC_LABEL.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CASE_SSCC_API](../programs/RRL_CASE_SSCC_API.md), [RRL_CASE_SSCC_LABEL](../tables/RRL_CASE_SSCC_LABEL.md), [RRL_CASE_TASK_ACCESS](../programs/RRL_CASE_TASK_ACCESS.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_SSCC_ALLOCATOR](../programs/RRL_SSCC_ALLOCATOR.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

## Кто использует

[RRL_CASE_SSCC_API](../programs/RRL_CASE_SSCC_API.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md), [RRL_WH_SCALE_API](../programs/RRL_WH_SCALE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CASE_SSCC_API` в файле соответствующего типа.
