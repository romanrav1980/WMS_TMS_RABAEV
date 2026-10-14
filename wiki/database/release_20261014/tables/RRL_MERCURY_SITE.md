# RRL_MERCURY_SITE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `MERCURY_SITE_ID` | NUMBER | N |  |
| `SITE_CODE` | VARCHAR2(100 bytes) | N |  |
| `SITE_NAME` | VARCHAR2(255 bytes) | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `ENTERPRISE_GUID` | VARCHAR2(64 bytes) | Y |  |
| `ENTERPRISE_UUID` | VARCHAR2(64 bytes) | Y |  |
| `BUSINESS_GUID` | VARCHAR2(64 bytes) | Y |  |
| `BUSINESS_UUID` | VARCHAR2(64 bytes) | Y |  |
| `ADDRESS_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | Y |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_MERCURY_SITE_PK | P | MERCURY_SITE_ID |  | ENABLED |
| RRL_MERCURY_SITE_U1 | U | SITE_CODE |  | ENABLED |
| SYS_C0014099 | C | MERCURY_SITE_ID |  | ENABLED |
| SYS_C0014100 | C | SITE_CODE |  | ENABLED |
| SYS_C0014101 | C | ACTIVE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_REGULATORY_API](../programs/RRL_REGULATORY_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_MERCURY_SITE` в файле соответствующего типа.
