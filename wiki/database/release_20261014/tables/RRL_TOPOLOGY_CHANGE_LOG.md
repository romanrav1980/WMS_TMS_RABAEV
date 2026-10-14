# RRL_TOPOLOGY_CHANGE_LOG

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CHANGE_ID` | NUMBER | N |  |
| `TOPOLOGY_ID` | NUMBER | N |  |
| `ENTITY_KIND` | VARCHAR2(40 bytes) | N |  |
| `ENTITY_ID` | NUMBER | Y |  |
| `CHANGE_KIND` | VARCHAR2(40 bytes) | N |  |
| `OLD_VALUE_JSON` | CLOB | Y |  |
| `NEW_VALUE_JSON` | CLOB | Y |  |
| `REASON_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TOPO_CHANGE_LOG_PK | P | CHANGE_ID |  | ENABLED |
| SYS_C0015138 | C | CHANGE_ID |  | ENABLED |
| SYS_C0015139 | C | TOPOLOGY_ID |  | ENABLED |
| SYS_C0015140 | C | ENTITY_KIND |  | ENABLED |
| SYS_C0015141 | C | CHANGE_KIND |  | ENABLED |
| SYS_C0015142 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TOPOLOGY_CHANGE_LOG` в файле соответствующего типа.
