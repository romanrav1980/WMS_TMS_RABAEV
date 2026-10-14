# RRL_PICK_RANGE_DRAIN_CLOSE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PICK_FACE_ARTICUL_ID` | NUMBER | N |  |
| `FROM_APPROVAL_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017558 | C | PICK_FACE_ARTICUL_ID |  | ENABLED |
| SYS_C0017559 | C | FROM_APPROVAL_OPERATION_ID |  | ENABLED |
| SYS_C0017560 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017561 | R | OPERATION_ID | RRL_PICK_RANGE_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0017562 | R | PICK_FACE_ARTICUL_ID | RRL_PICK_FACE_ARTICUL (PICK_FACE_ARTICUL_ID) | ENABLED |
| SYS_C0017563 | R | FROM_APPROVAL_OPERATION_ID | RRL_PICK_RANGE_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_RA_DRAIN_CLOSE_G](../programs/RRL_RA_DRAIN_CLOSE_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_RANGE_DRAIN_CLOSE` в файле соответствующего типа.
