# RRL_STORE_UNLOAD_START

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `STORE_ADDR` | VARCHAR2(255 bytes) | N |  |
| `ROOT_KEY` | VARCHAR2(200 bytes) | N |  |
| `COMPOSITION_SIGNATURE` | VARCHAR2(64 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `STARTED_AT_INSTANT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018614 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018615 | C | STORE_ADDR |  | ENABLED |
| SYS_C0018616 | C | ROOT_KEY |  | ENABLED |
| SYS_C0018617 | C | COMPOSITION_SIGNATURE |  | ENABLED |
| SYS_C0018618 | C | ACTOR |  | ENABLED |
| SYS_C0018619 | C | STARTED_AT_INSTANT |  | ENABLED |
| SYS_C0018620 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018621 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018622 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018623 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018624 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018625 | U | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018626 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STORE_UNLOAD_API](../programs/RRL_STORE_UNLOAD_API.md), [RRL_STORE_UNLOAD_CORE](../programs/RRL_STORE_UNLOAD_CORE.md), [RRL_STORE_UNLOAD_START_G](../programs/RRL_STORE_UNLOAD_START_G.md), [RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_UNLOAD_START` в файле соответствующего типа.
