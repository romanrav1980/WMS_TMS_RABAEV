# RRL_RETURN_DISPOSAL_FACT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Возвраты.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `REQUEST_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `BASE_QTY` | NUMBER(27,9) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `LOSS_STORE_ADDR` | VARCHAR2(255 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016976 | C | REQUEST_OPERATION_ID |  | ENABLED |
| SYS_C0016977 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0016978 | C | UID_PALLET |  | ENABLED |
| SYS_C0016979 | C | BASE_QTY |  | ENABLED |
| SYS_C0016980 | C | BASE_UOM |  | ENABLED |
| SYS_C0016981 | C | LOSS_STORE_ADDR |  | ENABLED |
| SYS_C0016982 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0016983 | C | ACTOR |  | ENABLED |
| SYS_C0016984 | C | CREATED_AT |  | ENABLED |
| SYS_C0016985 | C | BASE_QTY |  | ENABLED |
| SYS_C0016986 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016987 | U | REQUEST_OPERATION_ID |  | ENABLED |
| SYS_C0016988 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0016989 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016990 | R | REQUEST_OPERATION_ID | RRL_RETURN_DISPOSAL_REQUEST (OPERATION_ID) | ENABLED |
| SYS_C0016991 | R | RECEIPT_OPERATION_ID | RRL_STORE_RETURN_RECEIPT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_DISPOSAL_FACT_GUARD](../programs/RRL_DISPOSAL_FACT_GUARD.md), [RRL_STOCK_RETURN_DISPOSE](../programs/RRL_STOCK_RETURN_DISPOSE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RETURN_DISPOSAL_FACT` в файле соответствующего типа.
