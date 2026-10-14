# RRL_MES_COMPLETION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `COMPLETION_ID` | NUMBER | N |  |
| `PRODUCTION_ORDER_ID` | NUMBER | N |  |
| `PROD_BATCH_ID` | NUMBER | N |  |
| `IDEMPOTENCY_KEY` | VARCHAR2(100 bytes) | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `PAYLOAD_JSON` | CLOB | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_MES_COMPLETION_FK1 | R | PRODUCTION_ORDER_ID | RRL_PRODUCTION_ORDER (PRODUCTION_ORDER_ID) | ENABLED |
| RRL_MES_COMPLETION_PK | P | COMPLETION_ID |  | ENABLED |
| RRL_MES_COMPLETION_U1 | U | IDEMPOTENCY_KEY |  | ENABLED |
| SYS_C0014262 | C | COMPLETION_ID |  | ENABLED |
| SYS_C0014263 | C | PRODUCTION_ORDER_ID |  | ENABLED |
| SYS_C0014264 | C | PROD_BATCH_ID |  | ENABLED |
| SYS_C0014265 | C | STATUS |  | ENABLED |
| SYS_C0014266 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_MES_PRODUCTION_API](../programs/RRL_MES_PRODUCTION_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_MES_COMPLETION` в файле соответствующего типа.
