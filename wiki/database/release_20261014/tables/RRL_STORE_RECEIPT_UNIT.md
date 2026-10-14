# RRL_STORE_RECEIPT_UNIT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PHYSICAL_UNIT_KEY` | VARCHAR2(64 bytes) | N |  |
| `UNIT_DISPOSITION` | VARCHAR2(20 bytes) | N |  |
| `BASE_QTY` | NUMBER(27,9) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `SOURCE_UNIT_VERSION` | NUMBER | N |  |
| `RECORDED_BY` | NVARCHAR2(100 bytes) | N |  |
| `RECORDED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STORE_RUNIT_FACT_FK | R | OPERATION_ID | RRL_STORE_RECEIPT_FACT (OPERATION_ID) | ENABLED |
| RRL_STORE_RUNIT_LOAD_FK | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| RRL_STORE_RUNIT_PK | P | OPERATION_ID, PHYSICAL_UNIT_KEY |  | ENABLED |
| RRL_STORE_RUNIT_QTY_CK | C | SOURCE_UNIT_VERSION, BASE_QTY |  | ENABLED |
| RRL_STORE_RUNIT_SOURCE_UK | U | LOAD_OPERATION_ID, PHYSICAL_UNIT_KEY |  | ENABLED |
| RRL_STORE_RUNIT_STATE_CK | C | UNIT_DISPOSITION |  | ENABLED |
| RRL_STORE_RUNIT_UNIT_FK | R | PHYSICAL_UNIT_KEY | RRL_WMS_RECEIPT_UNIT (PHYSICAL_UNIT_KEY) | ENABLED |
| SYS_C0017836 | C | OPERATION_ID |  | ENABLED |
| SYS_C0017837 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0017838 | C | PHYSICAL_UNIT_KEY |  | ENABLED |
| SYS_C0017839 | C | UNIT_DISPOSITION |  | ENABLED |
| SYS_C0017840 | C | BASE_QTY |  | ENABLED |
| SYS_C0017841 | C | BASE_UOM |  | ENABLED |
| SYS_C0017842 | C | SOURCE_UNIT_VERSION |  | ENABLED |
| SYS_C0017843 | C | RECORDED_BY |  | ENABLED |
| SYS_C0017844 | C | RECORDED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STORE_MARK_CORE](../programs/RRL_STORE_MARK_CORE.md), [RRL_STORE_RECEIPT_UNIT_GUARD](../programs/RRL_STORE_RECEIPT_UNIT_GUARD.md), [RRL_STORE_RETURN_UNIT_CORE](../programs/RRL_STORE_RETURN_UNIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RECEIPT_UNIT` в файле соответствующего типа.
