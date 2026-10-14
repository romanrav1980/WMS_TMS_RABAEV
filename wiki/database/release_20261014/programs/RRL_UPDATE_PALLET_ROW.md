# RRL_UPDATE_PALLET_ROW

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_UPDATE_PALLET_ROW |  |  | VARCHAR2 | OUT | N |  |
| RRL_UPDATE_PALLET_ROW | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_PALLET_ROW | PALLET_UID1 | 2 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_PALLET_ROW | COUNT1 | 3 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW | USER_ID1 | 4 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_UPDATE_PALLET_ROW` в файле соответствующего типа.
