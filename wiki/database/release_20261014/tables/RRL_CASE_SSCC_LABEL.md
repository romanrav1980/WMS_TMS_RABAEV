# RRL_CASE_SSCC_LABEL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Сборка CASE.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `CASE_PICK_TASK_ID` | NUMBER | N |  |
| `SSCC` | VARCHAR2(18 bytes) | N |  |
| `ORIGINAL_CARRIER` | VARCHAR2(64 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `PALLET_TYPE_ID` | NUMBER | N |  |
| `REQUESTED_VERSION` | NUMBER | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CONFIRMED_AT` | TIMESTAMP(6) WITH TIME ZONE | Y |  |
| `CONFIRMED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CASE_SSCC_LABEL_CASE_U | U | CASE_PICK_TASK_ID |  | ENABLED |
| RRL_CASE_SSCC_LABEL_CONF_C | C | CONFIRMED_BY, CONFIRMED_AT |  | ENABLED |
| RRL_CASE_SSCC_LABEL_DIGIT_C | C | SSCC |  | ENABLED |
| RRL_CASE_SSCC_LABEL_SSCC_U | U | SSCC |  | ENABLED |
| SYS_C0017712 | C | CASE_PICK_TASK_ID |  | ENABLED |
| SYS_C0017713 | C | SSCC |  | ENABLED |
| SYS_C0017714 | C | ORIGINAL_CARRIER |  | ENABLED |
| SYS_C0017715 | C | WARE_ID |  | ENABLED |
| SYS_C0017716 | C | PALLET_TYPE_ID |  | ENABLED |
| SYS_C0017717 | C | REQUESTED_VERSION |  | ENABLED |
| SYS_C0017718 | C | CREATED_BY |  | ENABLED |
| SYS_C0017719 | C | CREATED_AT |  | ENABLED |
| SYS_C0017720 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0017721 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017722 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0017723 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017726 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017729 | R | CASE_PICK_TASK_ID | RRL_CASE_PICK_TASK (CASE_PICK_TASK_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_SSCC_API](../programs/RRL_CASE_SSCC_API.md), [RRL_CASE_SSCC_ID_GUARD](../programs/RRL_CASE_SSCC_ID_GUARD.md), [RRL_CASE_SSCC_LABEL_GUARD](../programs/RRL_CASE_SSCC_LABEL_GUARD.md), [RRL_SSCC_ALLOCATOR](../programs/RRL_SSCC_ALLOCATOR.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CASE_SSCC_LABEL` в файле соответствующего типа.
