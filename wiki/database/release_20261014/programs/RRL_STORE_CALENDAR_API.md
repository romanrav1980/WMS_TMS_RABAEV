# RRL_STORE_CALENDAR_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CONFIGURE | P_WARE | 1 | NUMBER | IN | N |  |
| CONFIGURE | P_STORE | 2 | VARCHAR2 | IN | N |  |
| CONFIGURE | P_BODY | 3 | CLOB | IN | N |  |
| CONFIGURE | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| CONFIGURE | P_RESULT | 5 | CLOB | OUT | N |  |
| CONFIG_WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |
| CONTEXT | P_WARE | 1 | NUMBER | IN | N |  |
| CONTEXT | P_STORE | 2 | VARCHAR2 | IN | N |  |
| CONTEXT | P_DAY | 3 | VARCHAR2 | IN | N |  |
| CONTEXT | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| CONTEXT | P_RESULT | 5 | CLOB | OUT | N |  |
| DELIVERY_RULE | P_WARE | 1 | NUMBER | IN | N |  |
| DELIVERY_RULE | P_STORE_ID | 2 | NUMBER | IN | N |  |
| DELIVERY_RULE | P_DAY | 3 | DATE | IN | N |  |
| DELIVERY_RULE | P_OFFSET | 4 | NUMBER | OUT | N |  |
| DELIVERY_RULE | P_ALLOWED | 5 | NUMBER | OUT | N |  |
| DELIVERY_RULE | P_PROOF | 6 | CLOB | OUT | N |  |
| SET_EXCEPTION | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| SET_EXCEPTION | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| SET_EXCEPTION | P_BODY | 3 | CLOB | IN | N |  |
| SET_EXCEPTION | P_RESULT | 4 | CLOB | OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |
| WRITE_ALLOWED | P_OPERATION | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SAP_STORE_CALENDAR](../tables/RRL_SAP_STORE_CALENDAR.md), [RRL_SAP_STORE_CAL_EXCEPTION](../tables/RRL_SAP_STORE_CAL_EXCEPTION.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER](../tables/RRL_CUSTOMER.md), [RRL_CUSTOMER_STORE_MAP](../tables/RRL_CUSTOMER_STORE_MAP.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_SAP_STORE_CALENDAR](../tables/RRL_SAP_STORE_CALENDAR.md), [RRL_SAP_STORE_CAL_EXCEPTION](../tables/RRL_SAP_STORE_CAL_EXCEPTION.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_STORE_CALENDAR_API](../programs/RRL_STORE_CALENDAR_API.md), [RRL_WARES](../tables/RRL_WARES.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_SAP_CAL_EX_GUARD](../programs/RRL_SAP_CAL_EX_GUARD.md), [RRL_SAP_CAL_WRITE_GUARD](../programs/RRL_SAP_CAL_WRITE_GUARD.md), [RRL_SAP_STORE_ADMISSION_API](../programs/RRL_SAP_STORE_ADMISSION_API.md), [RRL_SAP_STORE_PICK_GUARD](../programs/RRL_SAP_STORE_PICK_GUARD.md), [RRL_STORE_CALENDAR_API](../programs/RRL_STORE_CALENDAR_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_CALENDAR_API` в файле соответствующего типа.
