# RRL_IW_GROUP_SOURCE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| SOURCE_JSON |  |  | CLOB | OUT | N |  |
| SOURCE_JSON | P_LOAD | 1 | VARCHAR2 | IN | N |  |
| SOURCE_JSON | P_ACTOR | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_INTERWARE_UNIT_SOURCE](../programs/RRL_INTERWARE_UNIT_SOURCE.md), [RRL_IW_GROUP_ARCHIVE](../programs/RRL_IW_GROUP_ARCHIVE.md), [RRL_IW_GROUP_SOURCE](../programs/RRL_IW_GROUP_SOURCE.md)

## Кто использует

[RRL_IW_GROUP_PLAN_GUARD](../programs/RRL_IW_GROUP_PLAN_GUARD.md), [RRL_IW_GROUP_SOURCE](../programs/RRL_IW_GROUP_SOURCE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_SOURCE` в файле соответствующего типа.
