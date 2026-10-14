# RRL_SSCC_ALLOCATOR

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ALLOCATE |  |  | VARCHAR2 | OUT | N |  |
| ALLOCATE | P_WARE | 1 | NUMBER | IN | N |  |
| ALLOCATE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| ALLOCATE | P_PERMISSION | 3 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_WARE | 1 | NUMBER | IN | N |  |
| ASSERT_SCOPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_PERMISSION | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CASE_SSCC_LABEL](../tables/RRL_CASE_SSCC_LABEL.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_RECEIPT_LABEL](../tables/RRL_RECEIPT_LABEL.md), `RRL_RECEIPT_SSCC_SQ`, [RRL_RECEIPT_WARE_SETTINGS](../tables/RRL_RECEIPT_WARE_SETTINGS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SSCC_ALLOCATOR](../programs/RRL_SSCC_ALLOCATOR.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_CASE_SSCC_API](../programs/RRL_CASE_SSCC_API.md), [RRL_SSCC_ALLOCATOR](../programs/RRL_SSCC_ALLOCATOR.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SSCC_ALLOCATOR` в файле соответствующего типа.
