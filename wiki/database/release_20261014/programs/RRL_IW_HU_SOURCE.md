# RRL_IW_HU_SOURCE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_CONTEXT | P_LOAD | 1 | VARCHAR2 | IN | N |  |
| ASSERT_CONTEXT | P_CONTEXT | 2 | CLOB | IN | N |  |
| CAPTURE_CONTEXT | P_LOAD | 1 | VARCHAR2 | IN | N |  |
| CAPTURE_CONTEXT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CAPTURE_CONTEXT | P_CONTEXT | 3 | CLOB | OUT | N |  |
| CONTEXT_JSON |  |  | CLOB | OUT | N |  |
| CONTEXT_JSON | P_LOAD | 1 | VARCHAR2 | IN | N |  |
| STOCK_UID |  |  | VARCHAR2 | OUT | N |  |
| STOCK_UID | P_LOAD | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_INTERWARE_UNIT_SOURCE](../programs/RRL_INTERWARE_UNIT_SOURCE.md), [RRL_IW_HU_SOURCE](../programs/RRL_IW_HU_SOURCE.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_TARE_BOOK](../tables/RRL_TARE_BOOK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md), `RRL_WMS_HU_LINK_SQ`

## Кто использует

[RRL_INTERWARE_PLAN_GUARD](../programs/RRL_INTERWARE_PLAN_GUARD.md), [RRL_IW_HU_SOURCE](../programs/RRL_IW_HU_SOURCE.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_HU_SOURCE` в файле соответствующего типа.
