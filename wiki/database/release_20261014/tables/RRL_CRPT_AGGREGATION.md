# RRL_CRPT_AGGREGATION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `AGGREGATION_ID` | NUMBER | N |  |
| `SSCC` | VARCHAR2(32 bytes) | N |  |
| `PROD_BATCH_ID` | NUMBER | Y |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | Y |  |
| `PARENT_SSCC` | VARCHAR2(32 bytes) | Y |  |
| `AGGREGATION_LEVEL` | VARCHAR2(20 bytes) | Y |  |
| `AGGREGATION_STATUS` | VARCHAR2(30 bytes) | Y |  |
| `CRPT_DOCUMENT_ID` | VARCHAR2(100 bytes) | Y |  |
| `SENT_AT` | DATE | Y |  |
| `ACCEPTED_AT` | DATE | Y |  |
| `ERROR_TEXT` | VARCHAR2(4000 bytes) | Y |  |
| `CREATED_AT` | DATE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CRPT_AGGREGATION_PK | P | AGGREGATION_ID |  | ENABLED |
| RRL_CRPT_AGGREGATION_U1 | U | SSCC |  | ENABLED |
| SYS_C0014080 | C | AGGREGATION_ID |  | ENABLED |
| SYS_C0014081 | C | SSCC |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md), [RRL_PRODUCTION_API](../programs/RRL_PRODUCTION_API.md), [RRL_STOCK_MOVE_CORE](../programs/RRL_STOCK_MOVE_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CRPT_AGGREGATION` в файле соответствующего типа.
