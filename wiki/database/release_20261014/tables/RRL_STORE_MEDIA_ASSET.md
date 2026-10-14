# RRL_STORE_MEDIA_ASSET

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SHA256` | VARCHAR2(64 bytes) | N |  |
| `MIME_TYPE` | VARCHAR2(20 bytes) | N |  |
| `BYTE_COUNT` | NUMBER | N |  |
| `WIDTH_PX` | NUMBER | N |  |
| `HEIGHT_PX` | NUMBER | N |  |
| `CONTENT_BYTES` | BLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STORE_MEDIA_PIXELS_CK | C | HEIGHT_PX, WIDTH_PX |  | ENABLED |
| SYS_C0016396 | C | MIME_TYPE |  | ENABLED |
| SYS_C0016397 | C | BYTE_COUNT |  | ENABLED |
| SYS_C0016398 | C | WIDTH_PX |  | ENABLED |
| SYS_C0016399 | C | HEIGHT_PX |  | ENABLED |
| SYS_C0016400 | C | CONTENT_BYTES |  | ENABLED |
| SYS_C0016401 | C | CREATED_AT |  | ENABLED |
| SYS_C0016402 | C | MIME_TYPE |  | ENABLED |
| SYS_C0016403 | C | BYTE_COUNT |  | ENABLED |
| SYS_C0016404 | C | WIDTH_PX |  | ENABLED |
| SYS_C0016405 | C | HEIGHT_PX |  | ENABLED |
| SYS_C0016407 | P | SHA256 |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STORE_EVIDENCE_API](../programs/RRL_STORE_EVIDENCE_API.md), [RRL_STORE_MEDIA_ASSET_GUARD](../programs/RRL_STORE_MEDIA_ASSET_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_MEDIA_ASSET` в файле соответствующего типа.
