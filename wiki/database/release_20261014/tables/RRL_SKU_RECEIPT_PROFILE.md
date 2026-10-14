# RRL_SKU_RECEIPT_PROFILE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Приёмка.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `SYSTEM_CODE` | VARCHAR2(40 bytes) | N |  |
| `PROFILE_CODE` | VARCHAR2(80 bytes) | N |  |
| `PROFILE_VERSION` | VARCHAR2(40 bytes) | N |  |
| `SCAN_MODE` | VARCHAR2(40 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SKU_RPROF_FK | R | ARTICUL | RRL_SKU_RECEIPT_POLICY (ARTICUL) | ENABLED |
| RRL_SKU_RPROF_PK | P | ARTICUL, SYSTEM_CODE, PROFILE_CODE |  | ENABLED |
| RRL_SKU_RPROF_SCAN_CK | C | SCAN_MODE |  | ENABLED |
| SYS_C0015839 | C | ARTICUL |  | ENABLED |
| SYS_C0015840 | C | SYSTEM_CODE |  | ENABLED |
| SYS_C0015841 | C | PROFILE_CODE |  | ENABLED |
| SYS_C0015842 | C | PROFILE_VERSION |  | ENABLED |
| SYS_C0015843 | C | SCAN_MODE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_SCALE_ADMISSION](../programs/RRL_CASE_SCALE_ADMISSION.md), [RRL_INTERWARE_MARK_SCAN](../programs/RRL_INTERWARE_MARK_SCAN.md), [RRL_INTERWARE_UNIT_SOURCE](../programs/RRL_INTERWARE_UNIT_SOURCE.md), [RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md), [RRL_IW_GROUP_ARCHIVE](../programs/RRL_IW_GROUP_ARCHIVE.md), [RRL_IW_GROUP_REC](../programs/RRL_IW_GROUP_REC.md), [RRL_STOCK_CASE_CLOSE](../programs/RRL_STOCK_CASE_CLOSE.md), [RRL_STOCK_HU_SHIP_CMD](../programs/RRL_STOCK_HU_SHIP_CMD.md), [RRL_STOCK_INTERWARE_NEXT](../programs/RRL_STOCK_INTERWARE_NEXT.md), [RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_STOCK_INVENTORY_BIRTH](../programs/RRL_STOCK_INVENTORY_BIRTH.md), [RRL_STOCK_INVENTORY_CMD](../programs/RRL_STOCK_INVENTORY_CMD.md), [RRL_STOCK_IW_RECOVERY_NEXT](../programs/RRL_STOCK_IW_RECOVERY_NEXT.md), [RRL_STOCK_IW_RECOVERY_PUT](../programs/RRL_STOCK_IW_RECOVERY_PUT.md), [RRL_STOCK_MOVE_CORE](../programs/RRL_STOCK_MOVE_CORE.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_MARK](../programs/RRL_STOCK_QC_MARK.md), [RRL_STOCK_RETURN_DISPOSE](../programs/RRL_STOCK_RETURN_DISPOSE.md), [RRL_STOCK_STORE_RECEIPT_READ](../programs/RRL_STOCK_STORE_RECEIPT_READ.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STOCK_SUP_RETURN](../programs/RRL_STOCK_SUP_RETURN.md), [RRL_STOCK_TASK_SCAN](../programs/RRL_STOCK_TASK_SCAN.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_STORE_MARK_CORE](../programs/RRL_STORE_MARK_CORE.md), [RRL_STORE_RETURN_UNIT_CORE](../programs/RRL_STORE_RETURN_UNIT_CORE.md), [RRL_TRACE_SENDER_AGG_GUARD](../programs/RRL_TRACE_SENDER_AGG_GUARD.md), [RRL_TRACE_SENDER_MANIFEST_GUARD](../programs/RRL_TRACE_SENDER_MANIFEST_GUARD.md), [RRL_WH_SCALE_API](../programs/RRL_WH_SCALE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SKU_RECEIPT_PROFILE` в файле соответствующего типа.
