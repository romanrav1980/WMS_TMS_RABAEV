# RRL_TT_ROUTE_INPUT

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
| `DRIVE_MIN` | NUMBER(8,2) | N |  |
| `DRIVE_BACK_MIN` | NUMBER(8,2) | N |  |
| `SOURCE_REFERENCE` | NVARCHAR2(1000 bytes) | N |  |
| `REASON` | NVARCHAR2(1000 bytes) | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TT_ROUTE_INPUT_MIN_CK | C | DRIVE_MIN, DRIVE_BACK_MIN |  | ENABLED |
| RRL_TT_ROUTE_INPUT_PK | P | TT_ID, VERSION_NO |  | ENABLED |
| RRL_TT_ROUTE_INPUT_VER_CK | C | VERSION_NO |  | ENABLED |
| SYS_C0017936 | C | TT_ID |  | ENABLED |
| SYS_C0017937 | C | VERSION_NO |  | ENABLED |
| SYS_C0017938 | C | OPERATION_ID |  | ENABLED |
| SYS_C0017939 | C | ACTOR |  | ENABLED |
| SYS_C0017940 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0017941 | C | SOURCE_HASH |  | ENABLED |
| SYS_C0017942 | C | DRIVE_MIN |  | ENABLED |
| SYS_C0017943 | C | DRIVE_BACK_MIN |  | ENABLED |
| SYS_C0017944 | C | SOURCE_REFERENCE |  | ENABLED |
| SYS_C0017945 | C | REASON |  | ENABLED |
| SYS_C0017946 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017947 | C | CREATED_AT |  | ENABLED |
| SYS_C0017948 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017952 | U | OPERATION_ID |  | ENABLED |
| SYS_C0017953 | R | TT_ID | RRL_TRANSPORT_TASK (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TT_ROUTE_API](../programs/RRL_TT_ROUTE_API.md), [RRL_TT_ROUTE_INPUT_GUARD](../programs/RRL_TT_ROUTE_INPUT_GUARD.md), [RRL_TT_ROUTE_SOURCE](../programs/RRL_TT_ROUTE_SOURCE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_ROUTE_INPUT` в файле соответствующего типа.
