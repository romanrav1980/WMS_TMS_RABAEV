# RRL_STOCK_EVENT_BRIDGE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| AFTER_EVENT | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| AFTER_EVENT | P_LINE | 2 | NUMBER | IN | N |  |
| AFTER_EVENT | P_LEG | 3 | NUMBER | IN | N |  |
| AFTER_EVENT | P_UID | 4 | VARCHAR2 | IN | N |  |
| AFTER_EVENT | P_FROM | 5 | VARCHAR2 | IN | N |  |
| AFTER_EVENT | P_TO | 6 | VARCHAR2 | IN | N |  |
| AFTER_EVENT | P_QTY | 7 | NUMBER | IN | N |  |
| AFTER_EVENT | P_UOM | 8 | VARCHAR2 | IN | N |  |
| AFTER_EVENT | P_UOM_VERSION | 9 | NUMBER | IN | N |  |
| AFTER_EVENT | P_TYPE | 10 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_EVENT_BRIDGE](../programs/RRL_STOCK_EVENT_BRIDGE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_SYSTEM_SETTINGS](../tables/RRL_SYSTEM_SETTINGS.md)

## Кто использует

[BIN$UX1xZvUbS6/gYw8CAAo/Yg==$0](../programs/BIN_UX1xZvUbS6_gYw8CAAo_Yg___0.md), [RRL_STOCK_EVENT_BRIDGE](../programs/RRL_STOCK_EVENT_BRIDGE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_EVENT_BRIDGE` в файле соответствующего типа.
