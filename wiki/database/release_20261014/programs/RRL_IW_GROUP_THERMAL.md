# RRL_IW_GROUP_THERMAL

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_CELL | P_WARE | 1 | NUMBER | IN | N |  |
| ASSERT_CELL | P_ARTICLE | 2 | VARCHAR2 | IN | N |  |
| ASSERT_CELL | P_CELL | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_INTERWARE_THERMAL](../programs/RRL_INTERWARE_THERMAL.md), [RRL_IW_GROUP_THERMAL](../programs/RRL_IW_GROUP_THERMAL.md), [RRL_RECEIPT_SKU_RULE](../tables/RRL_RECEIPT_SKU_RULE.md)

## Кто использует

[RRL_IW_GROUP_NEXT](../programs/RRL_IW_GROUP_NEXT.md), [RRL_IW_GROUP_PUT](../programs/RRL_IW_GROUP_PUT.md), [RRL_IW_GROUP_REC](../programs/RRL_IW_GROUP_REC.md), [RRL_IW_GROUP_THERMAL](../programs/RRL_IW_GROUP_THERMAL.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_THERMAL` в файле соответствующего типа.
