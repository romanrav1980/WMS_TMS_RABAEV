# RRL_WMS_RECEIPT_AGG

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Приёмка.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SYSTEM_CODE` | VARCHAR2(40 bytes) | N |  |
| `CODE_HASH` | VARCHAR2(64 bytes) | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `PROFILE_CODE` | VARCHAR2(80 bytes) | N |  |
| `AGG_LEVEL` | VARCHAR2(10 bytes) | N |  |
| `RAW_CODE` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WMS_REC_AGG_FK | R | UID_PALLET | RRL_PALLETS (UID_PALLET) | ENABLED |
| RRL_WMS_REC_AGG_LVL | C | AGG_LEVEL |  | ENABLED |
| RRL_WMS_REC_AGG_PK | P | SYSTEM_CODE, CODE_HASH |  | ENABLED |
| SYS_C0015963 | C | SYSTEM_CODE |  | ENABLED |
| SYS_C0015964 | C | CODE_HASH |  | ENABLED |
| SYS_C0015965 | C | UID_PALLET |  | ENABLED |
| SYS_C0015966 | C | PROFILE_CODE |  | ENABLED |
| SYS_C0015967 | C | AGG_LEVEL |  | ENABLED |
| SYS_C0015968 | C | RAW_CODE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WMS_RECEIPT_AGG` в файле соответствующего типа.
