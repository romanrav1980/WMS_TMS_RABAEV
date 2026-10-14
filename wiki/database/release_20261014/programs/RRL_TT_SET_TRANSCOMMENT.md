# RRL_TT_SET_TRANSCOMMENT

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TT_SET_TRANSCOMMENT |  |  | VARCHAR2 | OUT | N |  |
| RRL_TT_SET_TRANSCOMMENT | TRANS | 1 | VARCHAR2 | IN | N |  |
| RRL_TT_SET_TRANSCOMMENT | TTID1 | 2 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ADDR](../tables/RRL_ADDR.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_SET_TRANSCOMMENT` в файле соответствующего типа.
