# RRL_PICK_DECISION_LOG

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_DECISION_ID` | NUMBER | N |  |
| `PICK_PLAN_ID` | NUMBER | N |  |
| `PICK_PLAN_LINE_ID` | NUMBER | Y |  |
| `DECISION_TYPE` | VARCHAR2(50 bytes) | N |  |
| `MESSAGE_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `PAYLOAD_JSON` | CLOB | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_DECISION_LOG_FK1 | R | PICK_PLAN_ID | RRL_PICK_PLAN (PICK_PLAN_ID) | ENABLED |
| RRL_PICK_DECISION_LOG_FK2 | R | PICK_PLAN_LINE_ID | RRL_PICK_PLAN_LINE (PICK_PLAN_LINE_ID) | ENABLED |
| RRL_PICK_DECISION_LOG_PK | P | PICK_DECISION_ID |  | ENABLED |
| SYS_C0014476 | C | PICK_DECISION_ID |  | ENABLED |
| SYS_C0014477 | C | PICK_PLAN_ID |  | ENABLED |
| SYS_C0014478 | C | DECISION_TYPE |  | ENABLED |
| SYS_C0014479 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICKING_API](../programs/RRL_PICKING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_DECISION_LOG` в файле соответствующего типа.
