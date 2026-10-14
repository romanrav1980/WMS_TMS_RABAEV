# RRL_TOPOLOGY_RECOMMENDATION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `RECOMMENDATION_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `TOPOLOGY_ID` | NUMBER | Y |  |
| `PICK_ROUTE_ID` | NUMBER | Y |  |
| `PERIOD_FROM` | DATE | Y |  |
| `PERIOD_TO` | DATE | Y |  |
| `RECOMMENDATION_KIND` | VARCHAR2(60 bytes) | N |  |
| `SEVERITY` | VARCHAR2(20 bytes) | N |  |
| `TITLE` | VARCHAR2(200 bytes) | N |  |
| `DETAIL_TEXT` | VARCHAR2(2000 bytes) | Y |  |
| `EVIDENCE_JSON` | CLOB | Y |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `DECIDED_AT` | DATE | Y |  |
| `DECIDED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TOPO_REC_CHK1 | C | STATUS |  | ENABLED |
| RRL_TOPO_REC_CK_WARE_POS | C | WARE_ID |  | ENABLED |
| RRL_TOPO_REC_PK | P | RECOMMENDATION_ID |  | ENABLED |
| SYS_C0015129 | C | RECOMMENDATION_ID |  | ENABLED |
| SYS_C0015130 | C | WARE_ID |  | ENABLED |
| SYS_C0015131 | C | RECOMMENDATION_KIND |  | ENABLED |
| SYS_C0015132 | C | SEVERITY |  | ENABLED |
| SYS_C0015133 | C | TITLE |  | ENABLED |
| SYS_C0015134 | C | STATUS |  | ENABLED |
| SYS_C0015135 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TOPOLOGY_RECOMMENDATION` в файле соответствующего типа.
