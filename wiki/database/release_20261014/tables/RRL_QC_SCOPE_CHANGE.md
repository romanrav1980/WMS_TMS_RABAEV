# RRL_QC_SCOPE_CHANGE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Контроль качества.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018916 | C | ACTOR |  | ENABLED |
| SYS_C0018917 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0018918 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018919 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018920 | C | CREATED_AT |  | ENABLED |
| SYS_C0018921 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018922 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018923 | P | OPERATION_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_QC_SCOPE_CHANGE_GUARD](../programs/RRL_QC_SCOPE_CHANGE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_QC_SCOPE_CHANGE` в файле соответствующего типа.
