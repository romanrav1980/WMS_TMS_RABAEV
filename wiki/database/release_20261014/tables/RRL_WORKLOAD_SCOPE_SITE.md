# RRL_WORKLOAD_SCOPE_SITE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `WORK_SCOPE` | VARCHAR2(30 bytes) | N |  |
| `SITE_CODE` | VARCHAR2(50 bytes) | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `REASON` | NVARCHAR2(1000 bytes) | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `CREATED_BY` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WORK_SCOPE_ACTIVE_CK | C | ACTIVE |  | ENABLED |
| RRL_WORK_SCOPE_KIND_CK | C | WORK_SCOPE |  | ENABLED |
| RRL_WORK_SCOPE_VERSION_CK | C | VERSION_NO |  | ENABLED |
| SYS_C0018880 | C | WARE_ID |  | ENABLED |
| SYS_C0018881 | C | WORK_SCOPE |  | ENABLED |
| SYS_C0018882 | C | SITE_CODE |  | ENABLED |
| SYS_C0018883 | C | VERSION_NO |  | ENABLED |
| SYS_C0018884 | C | ACTIVE |  | ENABLED |
| SYS_C0018885 | C | REASON |  | ENABLED |
| SYS_C0018886 | C | OPERATION_ID |  | ENABLED |
| SYS_C0018887 | C | CREATED_BY |  | ENABLED |
| SYS_C0018888 | C | CREATED_AT |  | ENABLED |
| SYS_C0018892 | P | WARE_ID, WORK_SCOPE, VERSION_NO |  | ENABLED |
| SYS_C0018893 | U | OPERATION_ID |  | ENABLED |
| SYS_C0018894 | R | OPERATION_ID | RRL_WORKLOAD_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_WORKLOAD_CONFIG_API](../programs/RRL_WORKLOAD_CONFIG_API.md), [RRL_WORKLOAD_SCOPE_SITE_G](../programs/RRL_WORKLOAD_SCOPE_SITE_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WORKLOAD_SCOPE_SITE` в файле соответствующего типа.
