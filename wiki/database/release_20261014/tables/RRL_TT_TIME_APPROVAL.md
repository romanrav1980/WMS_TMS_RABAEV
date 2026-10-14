# RRL_TT_TIME_APPROVAL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TT_ID` | NUMBER | N |  |
| `VERSION_NO` | NUMBER | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTOR` | VARCHAR2(50 bytes) | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `SOURCE_HASH` | VARCHAR2(64 bytes) | N |  |
| `TIME_ZONE` | VARCHAR2(50 bytes) | N |  |
| `REASON` | NVARCHAR2(1000 bytes) | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TT_TIME_APPROVAL_PK | P | TT_ID, VERSION_NO |  | ENABLED |
| RRL_TT_TIME_APPROVAL_TZ_CK | C | TIME_ZONE |  | ENABLED |
| RRL_TT_TIME_APPROVAL_VER_CK | C | VERSION_NO |  | ENABLED |
| SYS_C0017920 | C | TT_ID |  | ENABLED |
| SYS_C0017921 | C | VERSION_NO |  | ENABLED |
| SYS_C0017922 | C | OPERATION_ID |  | ENABLED |
| SYS_C0017923 | C | ACTOR |  | ENABLED |
| SYS_C0017924 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0017925 | C | SOURCE_HASH |  | ENABLED |
| SYS_C0017926 | C | TIME_ZONE |  | ENABLED |
| SYS_C0017927 | C | REASON |  | ENABLED |
| SYS_C0017928 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017929 | C | CREATED_AT |  | ENABLED |
| SYS_C0017930 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017934 | U | OPERATION_ID |  | ENABLED |
| SYS_C0017935 | R | TT_ID | RRL_TRANSPORT_TASK (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md), [RRL_TT_TIME_APPROVAL_GUARD](../programs/RRL_TT_TIME_APPROVAL_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_TIME_APPROVAL` в файле соответствующего типа.
