# RRL_IW_GROUP_PUT

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DECLARE_ROWS | P_DOMAIN | 1 | OBJECT | IN | N |  |
| DECLARE_ROWS | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| DECLARE_ROWS | P_RESOURCES | 3 | OBJECT | IN/OUT | N |  |
| DESCRIBE_RECEIPT | P_RECEIPT | 1 | VARCHAR2 | IN | N |  |
| DESCRIBE_RECEIPT | P_TARGET | 2 | VARCHAR2 | IN | N |  |
| DESCRIBE_RECEIPT | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| DESCRIBE_RECEIPT | P_TASK | 4 | NUMBER | IN | N |  |
| DESCRIBE_RECEIPT | P_DOMAIN | 5 | OBJECT | OUT | N |  |
| RECORD_COMPLETE | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| RECORD_COMPLETE | P_TASK | 2 | NUMBER | IN | N |  |
| RECORD_COMPLETE | P_DOMAIN | 3 | OBJECT | IN | N |  |
| RECORD_COMPLETE | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| RECORD_PLAN | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| RECORD_PLAN | P_TASK | 2 | NUMBER | IN | N |  |
| RECORD_PLAN | P_DOMAIN | 3 | OBJECT | IN | N |  |
| RECORD_PLAN | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| VALIDATE_RECEIPT | P_DOMAIN | 1 | OBJECT | IN | N |  |
| VALIDATE_RECEIPT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| VALIDATE_RECEIPT | P_TASK | 3 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_IW_GROUP_PLACEMENT](../tables/RRL_IW_GROUP_PLACEMENT.md), [RRL_IW_GROUP_PUT_PLAN](../tables/RRL_IW_GROUP_PUT_PLAN.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_IW_GROUP_PLACEMENT](../tables/RRL_IW_GROUP_PLACEMENT.md), [RRL_IW_GROUP_PUT](../programs/RRL_IW_GROUP_PUT.md), [RRL_IW_GROUP_PUT_PLAN](../tables/RRL_IW_GROUP_PUT_PLAN.md), [RRL_IW_GROUP_RECEIPT](../tables/RRL_IW_GROUP_RECEIPT.md), [RRL_IW_GROUP_RECEIPT_LINE](../tables/RRL_IW_GROUP_RECEIPT_LINE.md), [RRL_IW_GROUP_THERMAL](../programs/RRL_IW_GROUP_THERMAL.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_IW_GROUP_PUT](../programs/RRL_IW_GROUP_PUT.md), [RRL_STOCK_HU_TASK](../programs/RRL_STOCK_HU_TASK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_PUT` в файле соответствующего типа.
