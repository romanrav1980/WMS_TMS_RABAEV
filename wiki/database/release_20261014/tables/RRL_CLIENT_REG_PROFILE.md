# RRL_CLIENT_REG_PROFILE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CLIENT_ID` | VARCHAR2(100 bytes) | N |  |
| `CLIENT_NAME` | VARCHAR2(255 bytes) | Y |  |
| `INN` | VARCHAR2(20 bytes) | Y |  |
| `KPP` | VARCHAR2(20 bytes) | Y |  |
| `GLN` | VARCHAR2(32 bytes) | Y |  |
| `ACCEPTS_CRPT_AGGREGATION` | NUMBER(1,0) | N |  |
| `CRPT_ACCEPTANCE_MODE` | VARCHAR2(20 bytes) | N |  |
| `REQUIRES_MERCURY_VSD` | NUMBER(1,0) | N |  |
| `EDI_CHANNEL` | VARCHAR2(50 bytes) | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | Y |  |
| `UPDATED_AT` | DATE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CLIENT_REG_PROFILE_M1 | C | CRPT_ACCEPTANCE_MODE |  | ENABLED |
| RRL_CLIENT_REG_PROFILE_PK | P | CLIENT_ID |  | ENABLED |
| SYS_C0014051 | C | CLIENT_ID |  | ENABLED |
| SYS_C0014052 | C | ACCEPTS_CRPT_AGGREGATION |  | ENABLED |
| SYS_C0014053 | C | CRPT_ACCEPTANCE_MODE |  | ENABLED |
| SYS_C0014054 | C | REQUIRES_MERCURY_VSD |  | ENABLED |
| SYS_C0014055 | C | ACTIVE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CLIENT_REG_PROFILE` в файле соответствующего типа.
