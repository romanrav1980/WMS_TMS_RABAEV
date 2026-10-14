# RRL_STORE_UNLOAD_FACT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `START_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `STORE_ADDR` | VARCHAR2(255 bytes) | N |  |
| `METHOD` | VARCHAR2(20 bytes) | N |  |
| `ROLLING_DIFFICULT` | NUMBER(1,0) | N |  |
| `LOADER_PRESENT` | NUMBER(1,0) | N |  |
| `EVIDENCE_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `FINISHED_AT_INSTANT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `PAYLOAD_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018627 | C | START_OPERATION_ID |  | ENABLED |
| SYS_C0018628 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018629 | C | STORE_ADDR |  | ENABLED |
| SYS_C0018630 | C | METHOD |  | ENABLED |
| SYS_C0018631 | C | ROLLING_DIFFICULT |  | ENABLED |
| SYS_C0018632 | C | LOADER_PRESENT |  | ENABLED |
| SYS_C0018633 | C | EVIDENCE_REFERENCE |  | ENABLED |
| SYS_C0018634 | C | ACTOR |  | ENABLED |
| SYS_C0018635 | C | FINISHED_AT_INSTANT |  | ENABLED |
| SYS_C0018636 | C | PAYLOAD_JSON |  | ENABLED |
| SYS_C0018637 | C | METHOD |  | ENABLED |
| SYS_C0018638 | C | ROLLING_DIFFICULT |  | ENABLED |
| SYS_C0018639 | C | LOADER_PRESENT |  | ENABLED |
| SYS_C0018640 | C | PAYLOAD_JSON |  | ENABLED |
| SYS_C0018641 | P | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018642 | U | START_OPERATION_ID |  | ENABLED |
| SYS_C0018643 | U | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018644 | R | RECEIPT_OPERATION_ID | RRL_STORE_RECEIPT_FACT (OPERATION_ID) | ENABLED |
| SYS_C0018645 | R | START_OPERATION_ID | RRL_STORE_UNLOAD_START (OPERATION_ID) | ENABLED |
| SYS_C0018646 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STORE_UNLOAD_CORE](../programs/RRL_STORE_UNLOAD_CORE.md), [RRL_STORE_UNLOAD_FACT_G](../programs/RRL_STORE_UNLOAD_FACT_G.md), [RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_UNLOAD_FACT` в файле соответствующего типа.
