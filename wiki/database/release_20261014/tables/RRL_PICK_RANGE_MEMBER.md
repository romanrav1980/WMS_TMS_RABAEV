# RRL_PICK_RANGE_MEMBER

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PROPOSAL_ID` | VARCHAR2(100 bytes) | N |  |
| `PICK_FACE_ARTICUL_ID` | NUMBER | N |  |
| `ROLE_CODE` | VARCHAR2(10 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017551 | C | PROPOSAL_ID |  | ENABLED |
| SYS_C0017552 | C | PICK_FACE_ARTICUL_ID |  | ENABLED |
| SYS_C0017553 | C | ROLE_CODE |  | ENABLED |
| SYS_C0017554 | C | ROLE_CODE |  | ENABLED |
| SYS_C0017555 | P | PROPOSAL_ID, PICK_FACE_ARTICUL_ID, ROLE_CODE |  | ENABLED |
| SYS_C0017556 | R | PROPOSAL_ID | RRL_PICK_RANGE_APPROVAL (PROPOSAL_ID) | ENABLED |
| SYS_C0017557 | R | PICK_FACE_ARTICUL_ID | RRL_PICK_FACE_ARTICUL (PICK_FACE_ARTICUL_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_RA_MEMBER_G](../programs/RRL_RA_MEMBER_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_RANGE_MEMBER` в файле соответствующего типа.
