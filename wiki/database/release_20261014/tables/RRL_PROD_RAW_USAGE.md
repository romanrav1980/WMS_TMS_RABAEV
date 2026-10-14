# RRL_PROD_RAW_USAGE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `RAW_USAGE_ID` | NUMBER | N |  |
| `PROD_BATCH_ID` | NUMBER | Y |  |
| `PRODUCTION_ORDER_ID` | NUMBER | Y |  |
| `RAW_BATCH_ID` | NUMBER | Y |  |
| `RAW_ARTICUL` | VARCHAR2(40 bytes) | Y |  |
| `QUANTITY_PLANNED` | NUMBER | Y |  |
| `QUANTITY_FACT` | NUMBER | Y |  |
| `UNIT_CODE` | VARCHAR2(20 bytes) | Y |  |
| `USED_AT` | DATE | Y |  |
| `USED_BY` | VARCHAR2(50 bytes) | Y |  |
| `MERCURY_RAW_LINE_NO` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PROD_RAW_USAGE_PK | P | RAW_USAGE_ID |  | ENABLED |
| SYS_C0014072 | C | RAW_USAGE_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PRODUCTION_API](../programs/RRL_PRODUCTION_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PROD_RAW_USAGE` в файле соответствующего типа.
