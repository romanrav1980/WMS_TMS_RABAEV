# RRL_TARE_LOSS_DECISION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `CLAIM_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `OUTCOME` | VARCHAR2(12 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016881 | C | CLAIM_OPERATION_ID |  | ENABLED |
| SYS_C0016882 | C | OUTCOME |  | ENABLED |
| SYS_C0016883 | C | REASON_TEXT |  | ENABLED |
| SYS_C0016884 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0016885 | C | ACTOR |  | ENABLED |
| SYS_C0016886 | C | CREATED_AT |  | ENABLED |
| SYS_C0016887 | C | OUTCOME |  | ENABLED |
| SYS_C0016888 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016889 | U | CLAIM_OPERATION_ID |  | ENABLED |
| SYS_C0016890 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016891 | R | CLAIM_OPERATION_ID | RRL_TARE_LOSS_CLAIM (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_TARE_LOSS](../programs/RRL_STOCK_TARE_LOSS.md), [RRL_TARE_LOSS_DEC_GUARD](../programs/RRL_TARE_LOSS_DEC_GUARD.md), [RRL_TARE_LOSS_PENDING](../programs/RRL_TARE_LOSS_PENDING.md), [RRL_TARE_STORE_DEBT](../programs/RRL_TARE_STORE_DEBT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_LOSS_DECISION` в файле соответствующего типа.
