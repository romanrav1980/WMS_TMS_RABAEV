# RRL_PRIHOD_MAY_STORNO

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_PRIHOD_MAY_STORNO |  |  | NUMBER | OUT | N |  |
| RRL_PRIHOD_MAY_STORNO | ORDER_ID1 | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md)

## Кто использует

[RRL_STORNO_ORDER3_SP_OLD](../programs/RRL_STORNO_ORDER3_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PRIHOD_MAY_STORNO` в файле соответствующего типа.
