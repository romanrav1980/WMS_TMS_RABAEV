# RRL_WMS_RECEIPT_CODE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Приёмка.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SYSTEM_CODE` | VARCHAR2(40 bytes) | N |  |
| `CODE_HASH` | VARCHAR2(64 bytes) | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `UNIT_ID` | VARCHAR2(100 bytes) | N |  |
| `RAW_CODE` | CLOB | N |  |
| `PROFILES_JSON` | CLOB | N |  |
| `CANONICAL_CODE` | VARCHAR2(4000 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WMS_REC_CODE_FK | R | UID_PALLET, UNIT_ID | RRL_WMS_RECEIPT_UNIT (UID_PALLET, UNIT_ID) | ENABLED |
| RRL_WMS_REC_CODE_JSON | C | PROFILES_JSON |  | ENABLED |
| RRL_WMS_REC_CODE_PK | P | SYSTEM_CODE, CODE_HASH |  | ENABLED |
| SYS_C0015954 | C | SYSTEM_CODE |  | ENABLED |
| SYS_C0015955 | C | CODE_HASH |  | ENABLED |
| SYS_C0015956 | C | UID_PALLET |  | ENABLED |
| SYS_C0015957 | C | UNIT_ID |  | ENABLED |
| SYS_C0015958 | C | RAW_CODE |  | ENABLED |
| SYS_C0015959 | C | PROFILES_JSON |  | ENABLED |
| SYS_C0016035 | C | CANONICAL_CODE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_INTERWARE_MARK_SCAN](../programs/RRL_INTERWARE_MARK_SCAN.md), [RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md), [RRL_IW_GROUP_REC](../programs/RRL_IW_GROUP_REC.md), [RRL_REGULATORY_STOCK_OUTBOX](../programs/RRL_REGULATORY_STOCK_OUTBOX.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_MARK](../programs/RRL_STOCK_QC_MARK.md), [RRL_STORE_AGG_SCAN](../programs/RRL_STORE_AGG_SCAN.md), [RRL_STORE_MARK_CORE](../programs/RRL_STORE_MARK_CORE.md), [RRL_STORE_RETURN_UNIT_CORE](../programs/RRL_STORE_RETURN_UNIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WMS_RECEIPT_CODE` в файле соответствующего типа.
