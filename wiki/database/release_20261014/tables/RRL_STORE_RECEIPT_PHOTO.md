# RRL_STORE_RECEIPT_PHOTO

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PHOTO_ID` | VARCHAR2(64 bytes) | N |  |
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `STORE_ADDR` | VARCHAR2(255 bytes) | N |  |
| `VIEW_CODE` | VARCHAR2(10 bytes) | N |  |
| `ASSET_SHA256` | VARCHAR2(64 bytes) | N |  |
| `RECORDED_BY` | VARCHAR2(50 bytes) | N |  |
| `RECORDED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STORE_PHOTO_SOURCE_UK | U | LOAD_OPERATION_ID, STORE_ADDR, VIEW_CODE, ASSET_SHA256 |  | ENABLED |
| SYS_C0016408 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0016409 | C | STORE_ADDR |  | ENABLED |
| SYS_C0016410 | C | VIEW_CODE |  | ENABLED |
| SYS_C0016411 | C | ASSET_SHA256 |  | ENABLED |
| SYS_C0016412 | C | RECORDED_BY |  | ENABLED |
| SYS_C0016413 | C | RECORDED_AT |  | ENABLED |
| SYS_C0016414 | C | VIEW_CODE |  | ENABLED |
| SYS_C0016415 | P | PHOTO_ID |  | ENABLED |
| SYS_C0016417 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| SYS_C0016418 | R | STORE_ADDR | RRL_STORE_RECEIPT_POLICY (STORE_ADDR) | ENABLED |
| SYS_C0016419 | R | ASSET_SHA256 | RRL_STORE_MEDIA_ASSET (SHA256) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_WEIGHT_CORE](../programs/RRL_STOCK_STORE_WEIGHT_CORE.md), [RRL_STORE_EVIDENCE_API](../programs/RRL_STORE_EVIDENCE_API.md), [RRL_STORE_PHOTO_SOURCE_GUARD](../programs/RRL_STORE_PHOTO_SOURCE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RECEIPT_PHOTO` в файле соответствующего типа.
