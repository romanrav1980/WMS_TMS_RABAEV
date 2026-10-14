# RRL_SET_SCAN_PROOVE2_SP_OLD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_SET_SCAN_PROOVE2_SP_OLD |  |  | NUMBER | OUT | N |  |
| RRL_SET_SCAN_PROOVE2_SP_OLD | PALLET_UID1 | 1 | VARCHAR2 | IN | N |  |
| RRL_SET_SCAN_PROOVE2_SP_OLD | COUNT_OF_ERRORS1 | 2 | NUMBER | IN | N |  |
| RRL_SET_SCAN_PROOVE2_SP_OLD | PRIM1 | 3 | VARCHAR2 | IN | N |  |
| RRL_SET_SCAN_PROOVE2_SP_OLD | SBORSHIK1 | 4 | VARCHAR2 | IN | N |  |
| RRL_SET_SCAN_PROOVE2_SP_OLD | KLADOVSHIK1 | 5 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CLOSE_OTHOD_PALLET](../programs/RRL_CLOSE_OTHOD_PALLET.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_WARES](../tables/RRL_WARES.md)

## Кто использует

[RRL_SET_SCAN_PROOVE2](../programs/RRL_SET_SCAN_PROOVE2.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SET_SCAN_PROOVE2_SP_OLD` в файле соответствующего типа.
