# RRL_CLOSE_OTHOD_PALLET

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_CLOSE_OTHOD_PALLET |  |  | VARCHAR2 | OUT | N |  |
| RRL_CLOSE_OTHOD_PALLET | PALLET_ID1 | 1 | VARCHAR2 | IN | N |  |
| RRL_CLOSE_OTHOD_PALLET | ISER_ID21 | 2 | VARCHAR2 | IN | N |  |
| RRL_CLOSE_OTHOD_PALLET | P_OPERATION_ID | 3 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CLOSE_OTHOD_PALLET_SP_OLD](../programs/RRL_CLOSE_OTHOD_PALLET_SP_OLD.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_NATIVE_API](../programs/RRL_STOCK_NATIVE_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md)

## Кто использует

[REMAINS](../programs/REMAINS.md), [RRL_SET_SCAN_PROOVE2_SP_OLD](../programs/RRL_SET_SCAN_PROOVE2_SP_OLD.md), [RRL_SET_SCAN_PROOVE_SP_OLD](../programs/RRL_SET_SCAN_PROOVE_SP_OLD.md), [RRL_TRIAL_BY_WEIGHT2_SP_OLD](../programs/RRL_TRIAL_BY_WEIGHT2_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CLOSE_OTHOD_PALLET` в файле соответствующего типа.
