# RRL_PICK_RANGE_STATUS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_FACE_ARTICUL_ID` | NUMBER | N |  |
| `MODE_CODE` | VARCHAR2(20 bytes) | N |  |
| `APPROVAL_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017536 | C | MODE_CODE |  | ENABLED |
| SYS_C0017537 | C | APPROVAL_OPERATION_ID |  | ENABLED |
| SYS_C0017538 | C | MODE_CODE |  | ENABLED |
| SYS_C0017539 | P | PICK_FACE_ARTICUL_ID |  | ENABLED |
| SYS_C0017540 | R | PICK_FACE_ARTICUL_ID | RRL_PICK_FACE_ARTICUL (PICK_FACE_ARTICUL_ID) | ENABLED |
| SYS_C0017541 | R | APPROVAL_OPERATION_ID | RRL_PICK_RANGE_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_RANGE_POLICY](../programs/RRL_PICK_RANGE_POLICY.md), [RRL_RA_STATUS_G](../programs/RRL_RA_STATUS_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_RANGE_STATUS` в файле соответствующего типа.
