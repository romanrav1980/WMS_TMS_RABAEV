# RRL_STORE_RETURN_SUP_DISPATCH

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `BIND_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ST_ID` | NUMBER | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `BASE_QTY` | NUMBER(27,9) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `SUPPLIER_INN` | VARCHAR2(255 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016922 | C | BIND_OPERATION_ID |  | ENABLED |
| SYS_C0016923 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0016924 | C | ST_ID |  | ENABLED |
| SYS_C0016925 | C | UID_PALLET |  | ENABLED |
| SYS_C0016926 | C | BASE_QTY |  | ENABLED |
| SYS_C0016927 | C | BASE_UOM |  | ENABLED |
| SYS_C0016928 | C | SUPPLIER_INN |  | ENABLED |
| SYS_C0016929 | C | ACTOR |  | ENABLED |
| SYS_C0016930 | C | CREATED_AT |  | ENABLED |
| SYS_C0016931 | C | BASE_QTY |  | ENABLED |
| SYS_C0016932 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016933 | U | BIND_OPERATION_ID |  | ENABLED |
| SYS_C0016934 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0016935 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016936 | R | BIND_OPERATION_ID | RRL_STORE_RETURN_SUP_BIND (OPERATION_ID) | ENABLED |
| SYS_C0016937 | R | RECEIPT_OPERATION_ID | RRL_STORE_RETURN_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0016938 | R | ST_ID | RRL_SBORKA_PALLETS (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_SUP_RETURN](../programs/RRL_STOCK_SUP_RETURN.md), [RRL_SUP_CONFIRM_GUARD](../programs/RRL_SUP_CONFIRM_GUARD.md), [RRL_SUP_HANDOVER_GUARD](../programs/RRL_SUP_HANDOVER_GUARD.md), [RRL_SUP_RETURN_DISPATCH_GUARD](../programs/RRL_SUP_RETURN_DISPATCH_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RETURN_SUP_DISPATCH` в файле соответствующего типа.
