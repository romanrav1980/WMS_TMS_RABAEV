# RRL_CRPT_AGGREGATION_ITEMS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `AGGREGATION_ID` | NUMBER | N |  |
| `CHILD_TYPE` | VARCHAR2(20 bytes) | N |  |
| `CHILD_CIS` | VARCHAR2(255 bytes) | Y |  |
| `CHILD_SSCC` | VARCHAR2(32 bytes) | Y |  |
| `GTIN` | VARCHAR2(14 bytes) | Y |  |
| `PROD_BATCH_ID` | NUMBER | Y |  |
| `CREATED_AT` | DATE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CRPT_AGG_ITEMS_C1 | C | CHILD_TYPE |  | ENABLED |
| SYS_C0014084 | C | AGGREGATION_ID |  | ENABLED |
| SYS_C0014085 | C | CHILD_TYPE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PRODUCTION_API](../programs/RRL_PRODUCTION_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CRPT_AGGREGATION_ITEMS` в файле соответствующего типа.
