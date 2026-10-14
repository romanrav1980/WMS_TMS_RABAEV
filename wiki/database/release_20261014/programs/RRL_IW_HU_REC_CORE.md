# RRL_IW_HU_REC_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DECLARE_ROWS | P_DOMAIN | 1 | OBJECT | IN | N |  |
| DECLARE_ROWS | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| DECLARE_ROWS | P_RESOURCES | 3 | OBJECT | IN/OUT | N |  |
| RESTORE | P_DOMAIN | 1 | OBJECT | IN | N |  |
| RESTORE | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| RESTORE | P_ACTOR | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_IW_HU_REC_CORE](../programs/RRL_IW_HU_REC_CORE.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

## Кто использует

[RRL_IW_HU_REC_CORE](../programs/RRL_IW_HU_REC_CORE.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_HU_REC_CORE` в файле соответствующего типа.
