# RRL_INTERWARE_CUSTODY_PROOF

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `SOURCE_LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017231 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0017232 | C | SOURCE_LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0017233 | C | ACTOR |  | ENABLED |
| SYS_C0017234 | C | CREATED_AT |  | ENABLED |
| SYS_C0017235 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017236 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0017237 | U | SOURCE_LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0017238 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0017239 | R | RECEIPT_OPERATION_ID | RRL_INTERWARE_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0017240 | R | SOURCE_LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_INTERWARE_CUSTODY_GUARD](../programs/RRL_INTERWARE_CUSTODY_GUARD.md), [RRL_INTERWARE_ONWARD_BIND_GUARD](../programs/RRL_INTERWARE_ONWARD_BIND_GUARD.md), [RRL_STOCK_INTERWARE_CUSTODY](../programs/RRL_STOCK_INTERWARE_CUSTODY.md), [RRL_STOCK_INTERWARE_NEXT](../programs/RRL_STOCK_INTERWARE_NEXT.md), [RRL_STOCK_IW_RECOVERY_NEXT](../programs/RRL_STOCK_IW_RECOVERY_NEXT.md), [RRL_TT_HU_LOAD_FACT_GUARD](../programs/RRL_TT_HU_LOAD_FACT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_CUSTODY_PROOF` в файле соответствующего типа.
