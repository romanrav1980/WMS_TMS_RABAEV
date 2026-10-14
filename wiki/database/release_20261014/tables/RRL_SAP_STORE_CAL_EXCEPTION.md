# RRL_SAP_STORE_CAL_EXCEPTION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `CUSTOMER_STORE_MAP_ID` | NUMBER | N |  |
| `DELIVERY_DATE` | DATE | N |  |
| `VERSION_NO` | NUMBER | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTOR` | VARCHAR2(50 bytes) | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `DAY_STATE` | VARCHAR2(10 bytes) | N |  |
| `SOURCE_REFERENCE` | NVARCHAR2(1000 bytes) | N |  |
| `REASON` | NVARCHAR2(1000 bytes) | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_CAL_EX_DATE_CK | C | VERSION_NO, DELIVERY_DATE |  | ENABLED |
| RRL_SAP_CAL_EX_PK | P | WARE_ID, CUSTOMER_STORE_MAP_ID, DELIVERY_DATE, VERSION_NO |  | ENABLED |
| RRL_SAP_CAL_EX_STATE_CK | C | DAY_STATE |  | ENABLED |
| SYS_C0017972 | C | WARE_ID |  | ENABLED |
| SYS_C0017973 | C | CUSTOMER_STORE_MAP_ID |  | ENABLED |
| SYS_C0017974 | C | DELIVERY_DATE |  | ENABLED |
| SYS_C0017975 | C | VERSION_NO |  | ENABLED |
| SYS_C0017976 | C | OPERATION_ID |  | ENABLED |
| SYS_C0017977 | C | ACTOR |  | ENABLED |
| SYS_C0017978 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0017979 | C | DAY_STATE |  | ENABLED |
| SYS_C0017980 | C | SOURCE_REFERENCE |  | ENABLED |
| SYS_C0017981 | C | REASON |  | ENABLED |
| SYS_C0017982 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017983 | C | CREATED_AT |  | ENABLED |
| SYS_C0017984 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017988 | U | OPERATION_ID |  | ENABLED |
| SYS_C0017989 | R | CUSTOMER_STORE_MAP_ID | RRL_CUSTOMER_STORE_MAP (CUSTOMER_STORE_MAP_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_SAP_CAL_EX_GUARD](../programs/RRL_SAP_CAL_EX_GUARD.md), [RRL_STORE_CALENDAR_API](../programs/RRL_STORE_CALENDAR_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_STORE_CAL_EXCEPTION` в файле соответствующего типа.
