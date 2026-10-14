# RRL_PLANNER_APPLY_RESULT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PLAN_ID` | NUMBER | N |  |
| `SOURCE_HASH` | VARCHAR2(64 bytes) | N |  |
| `SHIPMENT_DATE` | DATE | N |  |
| `DOCK` | VARCHAR2(100 bytes) | Y |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `APPLIED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017462 | C | SOURCE_HASH |  | ENABLED |
| SYS_C0017463 | C | SHIPMENT_DATE |  | ENABLED |
| SYS_C0017464 | C | ACTOR |  | ENABLED |
| SYS_C0017465 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017466 | C | APPLIED_AT |  | ENABLED |
| SYS_C0017467 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017468 | P | PLAN_ID |  | ENABLED |
| SYS_C0017469 | R | PLAN_ID | RRL_PLANNER_PLANS (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PLANNER_APPLY_GUARD](../programs/RRL_PLANNER_APPLY_GUARD.md), [RRL_TRANSPORT_PLAN_API](../programs/RRL_TRANSPORT_PLAN_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PLANNER_APPLY_RESULT` в файле соответствующего типа.
