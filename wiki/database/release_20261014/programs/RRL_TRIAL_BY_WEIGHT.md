# RRL_TRIAL_BY_WEIGHT

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TRIAL_BY_WEIGHT |  |  | NUMBER | OUT | N |  |
| RRL_TRIAL_BY_WEIGHT | PALLET_UID1 | 1 | VARCHAR2 | IN | N |  |
| RRL_TRIAL_BY_WEIGHT | TRIAL_WEIGHT1 | 2 | VARCHAR2 | IN | N |  |
| RRL_TRIAL_BY_WEIGHT | WOOD_WEIGHT1 | 3 | VARCHAR2 | IN | N |  |
| RRL_TRIAL_BY_WEIGHT | USER_ID1 | 4 | VARCHAR2 | IN | N |  |
| RRL_TRIAL_BY_WEIGHT | P_OPERATION_ID | 5 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_QUALITY_ENTRY](../programs/RRL_STOCK_QUALITY_ENTRY.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md), [RRL_TRIAL_BY_WEIGHT_SP_OLD](../programs/RRL_TRIAL_BY_WEIGHT_SP_OLD.md)

## Кто использует

[REMAINS](../programs/REMAINS.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRIAL_BY_WEIGHT` в файле соответствующего типа.
