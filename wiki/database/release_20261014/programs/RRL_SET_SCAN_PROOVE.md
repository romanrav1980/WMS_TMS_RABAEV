# RRL_SET_SCAN_PROOVE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_SET_SCAN_PROOVE |  |  | NUMBER | OUT | N |  |
| RRL_SET_SCAN_PROOVE | PALLET_UID1 | 1 | VARCHAR2 | IN | N |  |
| RRL_SET_SCAN_PROOVE | COUNT_OF_ERRORS1 | 2 | NUMBER | IN | N |  |
| RRL_SET_SCAN_PROOVE | PRIM1 | 3 | VARCHAR2 | IN | N |  |
| RRL_SET_SCAN_PROOVE | P_OPERATION_ID | 4 | VARCHAR2 | IN | Y |  |
| RRL_SET_SCAN_PROOVE | P_ACTOR | 5 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SET_SCAN_PROOVE_SP_OLD](../programs/RRL_SET_SCAN_PROOVE_SP_OLD.md), [RRL_STOCK_QUALITY_ENTRY](../programs/RRL_STOCK_QUALITY_ENTRY.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SET_SCAN_PROOVE` в файле соответствующего типа.
