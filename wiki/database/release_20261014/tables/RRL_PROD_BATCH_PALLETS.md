# RRL_PROD_BATCH_PALLETS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PROD_BATCH_ID` | NUMBER | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `PALLET_NO` | NUMBER | Y |  |
| `QUANTITY` | NUMBER | Y |  |
| `PACK_COUNT` | NUMBER | Y |  |
| `NET_WEIGHT` | NUMBER | Y |  |
| `GROSS_WEIGHT` | NUMBER | Y |  |
| `SSCC` | VARCHAR2(32 bytes) | Y |  |
| `AGGREGATION_STATUS` | VARCHAR2(30 bytes) | Y |  |
| `CREATED_AT` | DATE | Y |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PROD_BATCH_PALLETS_PK | P | PROD_BATCH_ID, UID_PALLET |  | ENABLED |
| SYS_C0014065 | C | PROD_BATCH_ID |  | ENABLED |
| SYS_C0014066 | C | UID_PALLET |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_MES_PRODUCTION_API](../programs/RRL_MES_PRODUCTION_API.md), [RRL_PRODUCTION_API](../programs/RRL_PRODUCTION_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PROD_BATCH_PALLETS` в файле соответствующего типа.
