# RRL_UPDATE_TT_ZONE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_UPDATE_TT_ZONE |  |  | NUMBER | OUT | N |  |
| RRL_UPDATE_TT_ZONE | ZONE1 | 1 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_TT_ZONE | SUB_ZONE1 | 2 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_TT_ZONE | DOCK1 | 3 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_TT_ZONE | X1 | 4 | NUMBER | IN | N |  |
| RRL_UPDATE_TT_ZONE | Y1 | 5 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TT_ZONES](../tables/RRL_TT_ZONES.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TT_ZONES](../tables/RRL_TT_ZONES.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_UPDATE_TT_ZONE` в файле соответствующего типа.
