# RRL_STORE_RETURN_UNIT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `APPROVAL_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PHYSICAL_UNIT_KEY` | VARCHAR2(64 bytes) | N |  |
| `ORIGINAL_UID` | VARCHAR2(150 bytes) | N |  |
| `SOURCE_CELL` | VARCHAR2(60 bytes) | N |  |
| `BASE_QTY` | NUMBER(27,9) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `SOURCE_UNIT_VERSION` | NUMBER | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STORE_RETUNIT_APP_FK | R | APPROVAL_OPERATION_ID | RRL_STORE_RETURN_APPROVAL (OPERATION_ID) | ENABLED |
| RRL_STORE_RETUNIT_FACT_FK | R | RECEIPT_OPERATION_ID | RRL_STORE_RECEIPT_FACT (OPERATION_ID) | ENABLED |
| RRL_STORE_RETUNIT_PK | P | APPROVAL_OPERATION_ID, PHYSICAL_UNIT_KEY |  | ENABLED |
| RRL_STORE_RETUNIT_QTY_CK | C | BASE_QTY, SOURCE_UNIT_VERSION |  | ENABLED |
| RRL_STORE_RETUNIT_SOURCE_UK | U | RECEIPT_OPERATION_ID, PHYSICAL_UNIT_KEY |  | ENABLED |
| RRL_STORE_RETUNIT_UNIT_FK | R | PHYSICAL_UNIT_KEY | RRL_WMS_RECEIPT_UNIT (PHYSICAL_UNIT_KEY) | ENABLED |
| SYS_C0017852 | C | APPROVAL_OPERATION_ID |  | ENABLED |
| SYS_C0017853 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0017854 | C | PHYSICAL_UNIT_KEY |  | ENABLED |
| SYS_C0017855 | C | ORIGINAL_UID |  | ENABLED |
| SYS_C0017856 | C | SOURCE_CELL |  | ENABLED |
| SYS_C0017857 | C | BASE_QTY |  | ENABLED |
| SYS_C0017858 | C | BASE_UOM |  | ENABLED |
| SYS_C0017859 | C | SOURCE_UNIT_VERSION |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_RETURN_PALLET_IDENTITY](../programs/RRL_RETURN_PALLET_IDENTITY.md), [RRL_STOCK_RETURN_DISPOSE](../programs/RRL_STOCK_RETURN_DISPOSE.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STOCK_SUP_RETURN](../programs/RRL_STOCK_SUP_RETURN.md), [RRL_STORE_RETURN_UNIT_CORE](../programs/RRL_STORE_RETURN_UNIT_CORE.md), [RRL_STORE_RETURN_UNIT_GUARD](../programs/RRL_STORE_RETURN_UNIT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RETURN_UNIT` в файле соответствующего типа.
