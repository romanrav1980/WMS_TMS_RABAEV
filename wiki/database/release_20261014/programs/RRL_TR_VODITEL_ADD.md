# RRL_TR_VODITEL_ADD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TR_VODITEL_ADD |  |  | NUMBER | OUT | N |  |
| RRL_TR_VODITEL_ADD | P_NAME | 1 | VARCHAR2 | IN | N |  |
| RRL_TR_VODITEL_ADD | P_PHONE | 2 | VARCHAR2 | IN | Y |  |
| RRL_TR_VODITEL_ADD | P_LICENSE_NUMBER | 3 | VARCHAR2 | IN | Y |  |
| RRL_TR_VODITEL_ADD | P_COMPANY | 4 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TR_VODITEL](../tables/RRL_TR_VODITEL.md), `SEQ_TR_VODITEL`

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TR_VODITEL_ADD` в файле соответствующего типа.
