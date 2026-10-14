# RRL_STOCK_CTX_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| BEGIN_EFFECT | P_KIND | 1 | VARCHAR2 | IN | N |  |
| BEGIN_EFFECT | P_UID | 2 | VARCHAR2 | IN | Y |  |
| BEGIN_EFFECT | P_CELL | 3 | VARCHAR2 | IN | Y |  |
| BEGIN_EFFECT | P_ROW_ID | 4 | NUMBER | IN | Y |  |
| BEGIN_STAGING | P_UID | 1 | VARCHAR2 | IN | N |  |
| BEGIN_STAGING | P_CELL | 2 | VARCHAR2 | IN | N |  |
| OPEN_CONFIGURATION | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| OPEN_CONFIGURATION | P_PERMISSION | 2 | VARCHAR2 | IN | N |  |
| OPEN_OPERATION | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| OPEN_OPERATION | P_MODE | 2 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_CTX_API](../programs/RRL_STOCK_CTX_API.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md)

## Кто использует

[RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_COMPOSITION_CORE](../programs/RRL_STOCK_COMPOSITION_CORE.md), [RRL_STOCK_CONFIG_API](../programs/RRL_STOCK_CONFIG_API.md), [RRL_STOCK_CTX_API](../programs/RRL_STOCK_CTX_API.md), [RRL_STOCK_DOC_RESERVE_CMD](../programs/RRL_STOCK_DOC_RESERVE_CMD.md), [RRL_STOCK_MES_CANCEL_CMD](../programs/RRL_STOCK_MES_CANCEL_CMD.md), [RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md), [RRL_STOCK_OPERATION_CORE](../programs/RRL_STOCK_OPERATION_CORE.md), [RRL_STOCK_POOL_CMD](../programs/RRL_STOCK_POOL_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_RESERVATION_CMD](../programs/RRL_STOCK_RESERVATION_CMD.md), [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md), [RRL_STOCK_SETTING_API](../programs/RRL_STOCK_SETTING_API.md), [RRL_STOCK_TRANSFER_CORE](../programs/RRL_STOCK_TRANSFER_CORE.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_CTX_API` в файле соответствующего типа.
