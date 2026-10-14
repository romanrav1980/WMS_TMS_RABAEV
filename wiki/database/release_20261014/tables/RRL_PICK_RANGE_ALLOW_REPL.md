# RRL_PICK_RANGE_ALLOW_REPL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_FACE_ARTICUL_ID` | NUMBER | N |  |
| `DRAIN_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `REPLENISH_TASK_ID` | NUMBER | N |  |
| `MAX_ORIGINAL_QTY` | NUMBER | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017542 | C | PICK_FACE_ARTICUL_ID |  | ENABLED |
| SYS_C0017543 | C | DRAIN_OPERATION_ID |  | ENABLED |
| SYS_C0017544 | C | REPLENISH_TASK_ID |  | ENABLED |
| SYS_C0017545 | C | MAX_ORIGINAL_QTY |  | ENABLED |
| SYS_C0017546 | C | MAX_ORIGINAL_QTY |  | ENABLED |
| SYS_C0017547 | P | PICK_FACE_ARTICUL_ID, DRAIN_OPERATION_ID, REPLENISH_TASK_ID |  | ENABLED |
| SYS_C0017548 | R | PICK_FACE_ARTICUL_ID | RRL_PICK_FACE_ARTICUL (PICK_FACE_ARTICUL_ID) | ENABLED |
| SYS_C0017549 | R | DRAIN_OPERATION_ID | RRL_PICK_RANGE_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0017550 | R | REPLENISH_TASK_ID | RRL_PICK_WAVE_REPLENISH_TASK (PICK_WAVE_REPLENISH_TASK_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_RANGE_POLICY](../programs/RRL_PICK_RANGE_POLICY.md), [RRL_RA_ALLOW_REPL_G](../programs/RRL_RA_ALLOW_REPL_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_RANGE_ALLOW_REPL` в файле соответствующего типа.
