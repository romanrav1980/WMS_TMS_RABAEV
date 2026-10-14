# RRL_STOCK_LOADING_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_SCOPE | P_IDENTIFIER | 1 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| DESCRIBE_SOURCE | P_IDENTIFIER | 1 | VARCHAR2 | IN | N |  |
| DESCRIBE_SOURCE | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| DESCRIBE_SOURCE | P_POLICIES | 3 | CLOB | OUT | N |  |
| DESCRIBE_SOURCE | P_RESOURCES | 4 | CLOB | OUT | N |  |
| DESCRIBE_SOURCE | P_DOMAIN | 5 | CLOB | OUT | N |  |
| DESCRIBE_SOURCE | P_SNAPSHOT | 6 | CLOB | OUT | N |  |
| PREVIEW_JSON |  |  | CLOB | OUT | N |  |
| PREVIEW_JSON | P_IDENTIFIER | 1 | VARCHAR2 | IN | N |  |
| PREVIEW_JSON | P_ACTOR | 2 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md), [RRL_STOCK_LOADING_READ](../programs/RRL_STOCK_LOADING_READ.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_LOADING_READ](../programs/RRL_STOCK_LOADING_READ.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_SINGLE_LOAD_CMD](../programs/RRL_STOCK_SINGLE_LOAD_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_LOADING_READ` в файле соответствующего типа.
