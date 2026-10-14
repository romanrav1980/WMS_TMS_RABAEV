# RRL_SET_SCAN_PROOVE2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_SET_SCAN_PROOVE2 |  |  | NUMBER | OUT | N |  |
| RRL_SET_SCAN_PROOVE2 | PALLET_UID1 | 1 | VARCHAR2 | IN | N |  |
| RRL_SET_SCAN_PROOVE2 | COUNT_OF_ERRORS1 | 2 | NUMBER | IN | N |  |
| RRL_SET_SCAN_PROOVE2 | PRIM1 | 3 | VARCHAR2 | IN | N |  |
| RRL_SET_SCAN_PROOVE2 | SBORSHIK1 | 4 | VARCHAR2 | IN | N |  |
| RRL_SET_SCAN_PROOVE2 | KLADOVSHIK1 | 5 | VARCHAR2 | IN | N |  |
| RRL_SET_SCAN_PROOVE2 | P_OPERATION_ID | 6 | VARCHAR2 | IN | Y |  |
| RRL_SET_SCAN_PROOVE2 | P_ACTOR | 7 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SET_SCAN_PROOVE2_SP_OLD](../programs/RRL_SET_SCAN_PROOVE2_SP_OLD.md), [RRL_STOCK_QUALITY_ENTRY](../programs/RRL_STOCK_QUALITY_ENTRY.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md)

## Кто использует

[REMAINS](../programs/REMAINS.md), [RRL_UPDATE_PALLET_ROW2_SP_OLD](../programs/RRL_UPDATE_PALLET_ROW2_SP_OLD.md), [RRL_UPDATE_PALLET_ROW3_SP_OLD](../programs/RRL_UPDATE_PALLET_ROW3_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SET_SCAN_PROOVE2` в файле соответствующего типа.
