# RRL_STORE_PROFILE_CHANGE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `STORE_ADDR` | VARCHAR2(255 bytes) | N |  |
| `PROFILE_VERSION` | NUMBER | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(4000 bytes) | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STORE_PROFILE_CHANGE_U1 | U | STORE_ADDR, PROFILE_VERSION |  | ENABLED |
| SYS_C0018966 | C | STORE_ADDR |  | ENABLED |
| SYS_C0018967 | C | PROFILE_VERSION |  | ENABLED |
| SYS_C0018968 | C | ACTOR |  | ENABLED |
| SYS_C0018969 | C | REASON_TEXT |  | ENABLED |
| SYS_C0018970 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0018971 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018972 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018973 | C | CREATED_AT |  | ENABLED |
| SYS_C0018974 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018975 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018976 | P | OPERATION_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STORE_PROFILE_CHANGE_GUARD](../programs/RRL_STORE_PROFILE_CHANGE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_PROFILE_CHANGE` в файле соответствующего типа.
