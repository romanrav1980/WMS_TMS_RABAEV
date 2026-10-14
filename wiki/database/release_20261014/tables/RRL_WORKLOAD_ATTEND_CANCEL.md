# RRL_WORKLOAD_ATTEND_CANCEL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PLAN_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `CANCEL_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `REASON` | NVARCHAR2(1000 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017456 | C | CANCEL_OPERATION_ID |  | ENABLED |
| SYS_C0017457 | C | REASON |  | ENABLED |
| SYS_C0017458 | P | PLAN_OPERATION_ID |  | ENABLED |
| SYS_C0017459 | U | CANCEL_OPERATION_ID |  | ENABLED |
| SYS_C0017460 | R | PLAN_OPERATION_ID | RRL_WORKLOAD_ATTENDANCE (PLAN_OPERATION_ID) | ENABLED |
| SYS_C0017461 | R | CANCEL_OPERATION_ID | RRL_WORKLOAD_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_WORKLOAD_CANCEL_G](../programs/RRL_WORKLOAD_CANCEL_G.md), [RRL_WORKLOAD_CONFIG_API](../programs/RRL_WORKLOAD_CONFIG_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WORKLOAD_ATTEND_CANCEL` в файле соответствующего типа.
