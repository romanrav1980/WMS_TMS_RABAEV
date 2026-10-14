# RRL_SCALE_PACKET_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| UTC_STAMP |  |  | TIMESTAMP WITH TIME ZONE | OUT | N |  |
| UTC_STAMP | P_TEXT | 1 | VARCHAR2 | IN | N |  |
| VALIDATE_JSON |  |  | CLOB | OUT | N |  |
| VALIDATE_JSON | P_SOURCE | 1 | CLOB | IN | N |  |
| VALIDATE_JSON | P_CAPACITY | 2 | NUMBER | IN | N |  |
| VALIDATE_JSON | P_RESOLUTION | 3 | NUMBER | IN | N |  |
| VALIDATE_JSON | P_EXPECTED_BASIS | 4 | VARCHAR2 | IN | Y |  |
| VALIDATE_JSON | P_SAMPLE_FIELD | 5 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SCALE_PACKET_READ](../programs/RRL_SCALE_PACKET_READ.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md)

## Кто использует

[RRL_SCALE_PACKET_READ](../programs/RRL_SCALE_PACKET_READ.md), [RRL_STORE_SCALE_API](../programs/RRL_STORE_SCALE_API.md), [RRL_WH_SCALE_API](../programs/RRL_WH_SCALE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SCALE_PACKET_READ` в файле соответствующего типа.
