# RRL_PICK_RANGE_APPROVAL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PROPOSAL_ID` | VARCHAR2(100 bytes) | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ARTICLE` | VARCHAR2(40 bytes) | N |  |
| `PROOF_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017527 | C | OPERATION_ID |  | ENABLED |
| SYS_C0017528 | C | WARE_ID |  | ENABLED |
| SYS_C0017529 | C | ARTICLE |  | ENABLED |
| SYS_C0017530 | C | PROOF_JSON |  | ENABLED |
| SYS_C0017531 | C | PROOF_JSON |  | ENABLED |
| SYS_C0017532 | P | PROPOSAL_ID |  | ENABLED |
| SYS_C0017533 | U | OPERATION_ID |  | ENABLED |
| SYS_C0017534 | R | PROPOSAL_ID | RRL_PICK_RANGE_PROPOSAL (PROPOSAL_ID) | ENABLED |
| SYS_C0017535 | R | OPERATION_ID | RRL_PICK_RANGE_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_RANGE_PROPOSAL_API](../programs/RRL_PICK_RANGE_PROPOSAL_API.md), [RRL_RA_APPROVAL_G](../programs/RRL_RA_APPROVAL_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_RANGE_APPROVAL` в файле соответствующего типа.
