# RRL_WMS_HU_LINK

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Грузовые единицы и вложенность.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `HU_LINK_ID` | NUMBER | N |  |
| `PARENT_UID` | VARCHAR2(200 bytes) | N |  |
| `CHILD_PALLET_UID` | VARCHAR2(200 bytes) | Y |  |
| `CHILD_CASE_TASK_ID` | NUMBER | Y |  |
| `ACTIVE_FLAG` | NUMBER | N |  |
| `LINK_VERSION` | NUMBER | N |  |
| `LINKED_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LINKED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `LINKED_BY` | VARCHAR2(50 bytes) | N |  |
| `UNLINKED_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `UNLINKED_AT` | TIMESTAMP(6) WITH TIME ZONE | Y |  |
| `UNLINKED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_HU_CHILD_CASE_FK | R | CHILD_CASE_TASK_ID | RRL_CASE_PICK_TASK (CASE_PICK_TASK_ID) | ENABLED |
| RRL_HU_CHILD_PALLET_FK | R | CHILD_PALLET_UID | RRL_PALLETS (UID_PALLET) | ENABLED |
| RRL_HU_LINK_CK | C | ACTIVE_FLAG, CHILD_CASE_TASK_ID, CHILD_PALLET_UID, PARENT_UID, LINK_VERSION |  | ENABLED |
| RRL_HU_PARENT_FK | R | PARENT_UID | RRL_PALLETS (UID_PALLET) | ENABLED |
| SYS_C0016262 | C | PARENT_UID |  | ENABLED |
| SYS_C0016263 | C | ACTIVE_FLAG |  | ENABLED |
| SYS_C0016264 | C | LINK_VERSION |  | ENABLED |
| SYS_C0016265 | C | LINKED_OPERATION_ID |  | ENABLED |
| SYS_C0016266 | C | LINKED_AT |  | ENABLED |
| SYS_C0016267 | C | LINKED_BY |  | ENABLED |
| SYS_C0016269 | P | HU_LINK_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_PALLET_TYPE_READ](../programs/RRL_CASE_PALLET_TYPE_READ.md), [RRL_CASE_SSCC_API](../programs/RRL_CASE_SSCC_API.md), [RRL_HU_LINK_WRITE_GUARD](../programs/RRL_HU_LINK_WRITE_GUARD.md), [RRL_HU_PACK_CLOCK](../programs/RRL_HU_PACK_CLOCK.md), [RRL_HU_TARE_LINK_GUARD](../programs/RRL_HU_TARE_LINK_GUARD.md), [RRL_IW_GROUP_ARCHIVE](../programs/RRL_IW_GROUP_ARCHIVE.md), [RRL_IW_GROUP_REC](../programs/RRL_IW_GROUP_REC.md), [RRL_IW_HU_REC_CORE](../programs/RRL_IW_HU_REC_CORE.md), [RRL_IW_HU_SOURCE](../programs/RRL_IW_HU_SOURCE.md), [RRL_PALLET_FLOOR_READ](../programs/RRL_PALLET_FLOOR_READ.md), [RRL_RETURN_PALLET_IDENTITY](../programs/RRL_RETURN_PALLET_IDENTITY.md), [RRL_STOCK_CASE_RETURN_CMD](../programs/RRL_STOCK_CASE_RETURN_CMD.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_HU_CMD](../programs/RRL_STOCK_HU_CMD.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md), [RRL_STOCK_HU_SHIP_CMD](../programs/RRL_STOCK_HU_SHIP_CMD.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_LOAD_RECONCILE_CMD](../programs/RRL_STOCK_LOAD_RECONCILE_CMD.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_QC_CASE](../programs/RRL_STOCK_QC_CASE.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_RETURN_DISPOSE](../programs/RRL_STOCK_RETURN_DISPOSE.md), [RRL_STOCK_SUP_RETURN](../programs/RRL_STOCK_SUP_RETURN.md), [RRL_STOCK_TARE_BOOK_CMD](../programs/RRL_STOCK_TARE_BOOK_CMD.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_PHYSICAL](../programs/RRL_ST_DEFER_PHYSICAL.md), [RRL_ST_DEFER_PLACE_READ](../programs/RRL_ST_DEFER_PLACE_READ.md), [RRL_TARE_LOAD_RECOVERY_API](../programs/RRL_TARE_LOAD_RECOVERY_API.md), [RRL_TARE_PLANNING](../programs/RRL_TARE_PLANNING.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WMS_HU_LINK` в файле соответствующего типа.
