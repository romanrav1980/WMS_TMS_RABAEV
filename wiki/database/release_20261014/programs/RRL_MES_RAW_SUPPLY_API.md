# RRL_MES_RAW_SUPPLY_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RELEASE_TO_PRODUCTION |  |  | NUMBER | OUT | N |  |
| RELEASE_TO_PRODUCTION | P_PRODUCTION_ORDER_ID | 1 | NUMBER | IN | N |  |
| RELEASE_TO_PRODUCTION | P_TO_WARE_ID | 2 | NUMBER | IN | Y |  |
| RELEASE_TO_PRODUCTION | P_TO_CELL | 3 | VARCHAR2 | IN | Y |  |
| RELEASE_TO_PRODUCTION | P_ALLOW_PARTIAL | 4 | NUMBER | IN | Y |  |
| RELEASE_TO_PRODUCTION | P_CREATED_BY | 5 | VARCHAR2 | IN | Y |  |
| RELEASE_TO_PRODUCTION | P_OPERATION_ID | 6 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_MES_RAW_SUPPLY_API](../programs/RRL_MES_RAW_SUPPLY_API.md), [RRL_MES_RAW_SUPPLY_OLD](../programs/RRL_MES_RAW_SUPPLY_OLD.md), [RRL_STOCK_NATIVE_API](../programs/RRL_STOCK_NATIVE_API.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md)

## Кто использует

[RRL_MES_RAW_SUPPLY_API](../programs/RRL_MES_RAW_SUPPLY_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_MES_RAW_SUPPLY_API` в файле соответствующего типа.
