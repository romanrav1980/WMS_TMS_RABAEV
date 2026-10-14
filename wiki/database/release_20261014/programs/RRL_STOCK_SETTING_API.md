# RRL_STOCK_SETTING_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| SET_COMPATIBILITY | P_VALUE | 1 | VARCHAR2 | IN | N |  |
| SET_COMPATIBILITY | P_REASON | 2 | VARCHAR2 | IN | N |  |
| SET_COMPATIBILITY | P_ACTOR | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_STOCK_SETTING_AUDIT](../tables/RRL_STOCK_SETTING_AUDIT.md), [RRL_SYSTEM_SETTINGS](../tables/RRL_SYSTEM_SETTINGS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_STOCK_CTX_API](../programs/RRL_STOCK_CTX_API.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md), [RRL_STOCK_SETTING_API](../programs/RRL_STOCK_SETTING_API.md), [RRL_STOCK_SETTING_AUDIT](../tables/RRL_STOCK_SETTING_AUDIT.md), [RRL_SYSTEM_SETTINGS](../tables/RRL_SYSTEM_SETTINGS.md)

## Кто использует

[RRL_STOCK_SETTING_API](../programs/RRL_STOCK_SETTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_SETTING_API` в файле соответствующего типа.
