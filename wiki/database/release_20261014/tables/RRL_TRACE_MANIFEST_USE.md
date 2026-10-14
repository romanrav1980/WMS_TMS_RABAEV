# RRL_TRACE_MANIFEST_USE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Маркировка и агрегация.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `MANIFEST_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `STOCK_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017325 | C | STOCK_OPERATION_ID |  | ENABLED |
| SYS_C0017326 | C | UID_PALLET |  | ENABLED |
| SYS_C0017327 | C | ACTOR |  | ENABLED |
| SYS_C0017328 | C | CREATED_AT |  | ENABLED |
| SYS_C0017329 | P | MANIFEST_OPERATION_ID |  | ENABLED |
| SYS_C0017330 | R | MANIFEST_OPERATION_ID | RRL_TRACE_SENDER_MANIFEST (OPERATION_ID) | ENABLED |
| SYS_C0017331 | R | STOCK_OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md), [RRL_TRACE_AGG_LIFECYCLE](../programs/RRL_TRACE_AGG_LIFECYCLE.md), [RRL_TRACE_MANIFEST_USE_GUARD](../programs/RRL_TRACE_MANIFEST_USE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRACE_MANIFEST_USE` в файле соответствующего типа.
