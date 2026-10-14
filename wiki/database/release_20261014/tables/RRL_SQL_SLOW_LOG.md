# RRL_SQL_SLOW_LOG

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `LOG_ID` | NUMBER | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `MODULE` | VARCHAR2(48 bytes) | Y |  |
| `ACTION` | VARCHAR2(200 bytes) | Y |  |
| `API_CALL_ID` | NUMBER | Y |  |
| `REQUEST_ID` | VARCHAR2(64 bytes) | Y |  |
| `API_METHOD` | VARCHAR2(10 bytes) | Y |  |
| `API_PATH` | VARCHAR2(500 bytes) | Y |  |
| `DB_USER` | VARCHAR2(128 bytes) | Y |  |
| `ELAPSED_MS` | NUMBER | N |  |
| `SQL_TEXT_HASH` | VARCHAR2(64 bytes) | N |  |
| `SQL_TEXT` | VARCHAR2(4000 bytes) | Y |  |
| `PARAMS_JSON` | VARCHAR2(4000 bytes) | Y |  |
| `ROW_COUNT` | NUMBER | Y |  |
| `ERROR_TEXT` | VARCHAR2(4000 bytes) | Y |  |
| `CLIENT_IDENTIFIER` | VARCHAR2(64 bytes) | Y |  |
| `OPERATION_KIND` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SQL_SLOW_LOG_PK | P | LOG_ID |  | ENABLED |
| SYS_C0014687 | C | LOG_ID |  | ENABLED |
| SYS_C0014688 | C | CREATED_AT |  | ENABLED |
| SYS_C0014689 | C | ELAPSED_MS |  | ENABLED |
| SYS_C0014690 | C | SQL_TEXT_HASH |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SQL_SLOW_LOG` в файле соответствующего типа.
