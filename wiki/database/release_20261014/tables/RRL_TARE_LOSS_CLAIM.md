# RRL_TARE_LOSS_CLAIM

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `BALANCE_KEY` | RAW(32 bytes) | N |  |
| `OWNER_WARE_ID` | NUMBER | N |  |
| `PALLET_TYPE_ID` | NUMBER | N |  |
| `CONDITION_CODE` | VARCHAR2(10 bytes) | N |  |
| `QUANTITY` | NUMBER(18,0) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `SOURCE_CLAIM_ID` | VARCHAR2(100 bytes) | Y |  |
| `TRANSPORT_TASK_ID` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016867 | C | BALANCE_KEY |  | ENABLED |
| SYS_C0016868 | C | OWNER_WARE_ID |  | ENABLED |
| SYS_C0016869 | C | PALLET_TYPE_ID |  | ENABLED |
| SYS_C0016870 | C | CONDITION_CODE |  | ENABLED |
| SYS_C0016871 | C | QUANTITY |  | ENABLED |
| SYS_C0016872 | C | REASON_TEXT |  | ENABLED |
| SYS_C0016873 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0016874 | C | ACTOR |  | ENABLED |
| SYS_C0016875 | C | CREATED_AT |  | ENABLED |
| SYS_C0016876 | C | CONDITION_CODE |  | ENABLED |
| SYS_C0016877 | C | QUANTITY |  | ENABLED |
| SYS_C0016878 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016879 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016880 | R | BALANCE_KEY | RRL_TARE_BALANCE (BALANCE_KEY) | ENABLED |
| SYS_C0016892 | R | SOURCE_CLAIM_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016893 | R | TRANSPORT_TASK_ID | RRL_TRANSPORT_TASK (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_TARE_LOSS](../programs/RRL_STOCK_TARE_LOSS.md), [RRL_TARE_LOSS_CLAIM_GUARD](../programs/RRL_TARE_LOSS_CLAIM_GUARD.md), [RRL_TARE_LOSS_DEC_GUARD](../programs/RRL_TARE_LOSS_DEC_GUARD.md), [RRL_TARE_LOSS_PENDING](../programs/RRL_TARE_LOSS_PENDING.md), [RRL_TARE_STORE_DEBT](../programs/RRL_TARE_STORE_DEBT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_LOSS_CLAIM` в файле соответствующего типа.
