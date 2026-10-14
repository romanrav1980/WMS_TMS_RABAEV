# RRL_PICK_RANGE_CANCEL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PROPOSAL_ID` | VARCHAR2(100 bytes) | N |  |
| `CANCEL_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `REASON` | VARCHAR2(2000 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017521 | C | CANCEL_OPERATION_ID |  | ENABLED |
| SYS_C0017522 | C | REASON |  | ENABLED |
| SYS_C0017523 | P | PROPOSAL_ID |  | ENABLED |
| SYS_C0017524 | U | CANCEL_OPERATION_ID |  | ENABLED |
| SYS_C0017525 | R | PROPOSAL_ID | RRL_PICK_RANGE_PROPOSAL (PROPOSAL_ID) | ENABLED |
| SYS_C0017526 | R | CANCEL_OPERATION_ID | RRL_PICK_RANGE_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_RANGE_PROPOSAL_API](../programs/RRL_PICK_RANGE_PROPOSAL_API.md), [RRL_PR_CANCEL_G](../programs/RRL_PR_CANCEL_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_RANGE_CANCEL` в файле соответствующего типа.
