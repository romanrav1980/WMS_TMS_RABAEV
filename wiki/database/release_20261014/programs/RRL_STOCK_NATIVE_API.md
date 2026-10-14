# RRL_STOCK_NATIVE_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| POST | P_REQUEST | 1 | CLOB | IN | N |  |
| POST | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| POST | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_NATIVE_API](../programs/RRL_STOCK_NATIVE_API.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Кто использует

[REMAINS](../programs/REMAINS.md), [RRL_ADD_INV_LINE](../programs/RRL_ADD_INV_LINE.md), [RRL_CLOSE_OTHOD_NAKLAD](../programs/RRL_CLOSE_OTHOD_NAKLAD.md), [RRL_CLOSE_OTHOD_PALLET](../programs/RRL_CLOSE_OTHOD_PALLET.md), [RRL_INTERNAL_MOVE2](../programs/RRL_INTERNAL_MOVE2.md), [RRL_MES_PRODUCTION_API](../programs/RRL_MES_PRODUCTION_API.md), [RRL_MES_RAW_SUPPLY_API](../programs/RRL_MES_RAW_SUPPLY_API.md), [RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_STOCK_INV_ENTRY](../programs/RRL_STOCK_INV_ENTRY.md), [RRL_STOCK_NATIVE_API](../programs/RRL_STOCK_NATIVE_API.md), [RRL_STOCK_QUALITY_ENTRY](../programs/RRL_STOCK_QUALITY_ENTRY.md), [RRL_STOCK_REVISION_ENTRY](../programs/RRL_STOCK_REVISION_ENTRY.md), [RRL_STORNO_ORDER3](../programs/RRL_STORNO_ORDER3.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_NATIVE_API` в файле соответствующего типа.
