# RRL_COPY_PALLET_ROW2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_COPY_PALLET_ROW2 |  |  | NUMBER | OUT | N |  |
| RRL_COPY_PALLET_ROW2 | ROW_ID2 | 1 | NUMBER | IN | N |  |
| RRL_COPY_PALLET_ROW2 | COUNT1 | 2 | NUMBER | IN | N |  |
| RRL_COPY_PALLET_ROW2 | PALLET_UID_NEW | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), `RRL_SBORKA_PALLET_ROWS_SQ`

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_COPY_PALLET_ROW2` в файле соответствующего типа.
