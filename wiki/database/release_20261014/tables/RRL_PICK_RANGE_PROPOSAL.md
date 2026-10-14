# RRL_PICK_RANGE_PROPOSAL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PROPOSAL_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ARTICLE` | VARCHAR2(40 bytes) | N |  |
| `SOURCE_SIGNATURE` | VARCHAR2(64 bytes) | N |  |
| `SOURCE_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017514 | C | WARE_ID |  | ENABLED |
| SYS_C0017515 | C | ARTICLE |  | ENABLED |
| SYS_C0017516 | C | SOURCE_SIGNATURE |  | ENABLED |
| SYS_C0017517 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0017518 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0017519 | P | PROPOSAL_ID |  | ENABLED |
| SYS_C0017520 | R | PROPOSAL_ID | RRL_PICK_RANGE_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_RANGE_PROPOSAL_API](../programs/RRL_PICK_RANGE_PROPOSAL_API.md), [RRL_PR_PROPOSAL_G](../programs/RRL_PR_PROPOSAL_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_RANGE_PROPOSAL` в файле соответствующего типа.
