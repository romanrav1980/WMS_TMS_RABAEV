# RRL_STOCK_QUALITY_ENTRY

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| SCAN |  |  | NUMBER | OUT | N |  |
| SCAN | P_PALLET | 1 | VARCHAR2 | IN | N |  |
| SCAN | P_ERRORS | 2 | NUMBER | IN | N |  |
| SCAN | P_NOTE | 3 | VARCHAR2 | IN | N |  |
| SCAN | P_PICKER | 4 | VARCHAR2 | IN | N |  |
| SCAN | P_ACTOR | 5 | VARCHAR2 | IN | N |  |
| SCAN | P_OPERATION | 6 | VARCHAR2 | IN | N |  |
| WEIGHT |  |  | NUMBER | OUT | N |  |
| WEIGHT | P_KIND | 1 | VARCHAR2 | IN | N |  |
| WEIGHT | P_PALLET | 2 | VARCHAR2 | IN | N |  |
| WEIGHT | P_GROSS | 3 | VARCHAR2 | IN | N |  |
| WEIGHT | P_WOOD | 4 | VARCHAR2 | IN | N |  |
| WEIGHT | P_ACTOR | 5 | VARCHAR2 | IN | N |  |
| WEIGHT | P_OPERATION | 6 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_NATIVE_API](../programs/RRL_STOCK_NATIVE_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_QUALITY_ENTRY](../programs/RRL_STOCK_QUALITY_ENTRY.md)

## Кто использует

[RRL_SET_SCAN_PROOVE](../programs/RRL_SET_SCAN_PROOVE.md), [RRL_SET_SCAN_PROOVE2](../programs/RRL_SET_SCAN_PROOVE2.md), [RRL_STOCK_QUALITY_ENTRY](../programs/RRL_STOCK_QUALITY_ENTRY.md), [RRL_TRIAL_BY_WEIGHT](../programs/RRL_TRIAL_BY_WEIGHT.md), [RRL_TRIAL_BY_WEIGHT2](../programs/RRL_TRIAL_BY_WEIGHT2.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_QUALITY_ENTRY` в файле соответствующего типа.
