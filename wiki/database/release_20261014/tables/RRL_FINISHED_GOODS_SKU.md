# RRL_FINISHED_GOODS_SKU

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `IS_FINISHED_GOODS` | NUMBER(1,0) | N |  |
| `PRODUCT_GROUP` | VARCHAR2(100 bytes) | Y |  |
| `GTIN` | VARCHAR2(14 bytes) | Y |  |
| `CRPT_REQUIRED` | NUMBER(1,0) | N |  |
| `AGGREGATION_REQUIRED` | NUMBER(1,0) | N |  |
| `SSCC_REQUIRED` | NUMBER(1,0) | N |  |
| `PALLET_LABEL_REQUIRED` | NUMBER(1,0) | N |  |
| `QUALITY_HOLD_REQUIRED` | NUMBER(1,0) | N |  |
| `DEFAULT_PALLET_CASE_QTY` | NUMBER | Y |  |
| `DEFAULT_LAYER_QTY` | NUMBER | Y |  |
| `DEFAULT_LAYER_COUNT` | NUMBER | Y |  |
| `TECHNOLOGIST_COMMENT` | VARCHAR2(1000 bytes) | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_FINISHED_GOODS_SKU_CHK1 | C | IS_FINISHED_GOODS |  | ENABLED |
| RRL_FINISHED_GOODS_SKU_CHK2 | C | CRPT_REQUIRED |  | ENABLED |
| RRL_FINISHED_GOODS_SKU_CHK3 | C | AGGREGATION_REQUIRED |  | ENABLED |
| RRL_FINISHED_GOODS_SKU_CHK4 | C | SSCC_REQUIRED |  | ENABLED |
| RRL_FINISHED_GOODS_SKU_CHK5 | C | PALLET_LABEL_REQUIRED |  | ENABLED |
| RRL_FINISHED_GOODS_SKU_CHK6 | C | QUALITY_HOLD_REQUIRED |  | ENABLED |
| RRL_FINISHED_GOODS_SKU_CHK7 | C | ACTIVE |  | ENABLED |
| RRL_FINISHED_GOODS_SKU_PK | P | ARTICUL |  | ENABLED |
| SYS_C0014670 | C | ARTICUL |  | ENABLED |
| SYS_C0014671 | C | IS_FINISHED_GOODS |  | ENABLED |
| SYS_C0014672 | C | CRPT_REQUIRED |  | ENABLED |
| SYS_C0014673 | C | AGGREGATION_REQUIRED |  | ENABLED |
| SYS_C0014674 | C | SSCC_REQUIRED |  | ENABLED |
| SYS_C0014675 | C | PALLET_LABEL_REQUIRED |  | ENABLED |
| SYS_C0014676 | C | QUALITY_HOLD_REQUIRED |  | ENABLED |
| SYS_C0014677 | C | ACTIVE |  | ENABLED |
| SYS_C0014678 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_SCALE_ADMISSION](../programs/RRL_CASE_SCALE_ADMISSION.md), [RRL_INTERWARE_MARK_SCAN](../programs/RRL_INTERWARE_MARK_SCAN.md), [RRL_INTERWARE_UNIT_SOURCE](../programs/RRL_INTERWARE_UNIT_SOURCE.md), [RRL_STOCK_CASE_CLOSE](../programs/RRL_STOCK_CASE_CLOSE.md), [RRL_STOCK_INTERWARE_NEXT](../programs/RRL_STOCK_INTERWARE_NEXT.md), [RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_STOCK_INVENTORY_BIRTH](../programs/RRL_STOCK_INVENTORY_BIRTH.md), [RRL_STOCK_INVENTORY_CMD](../programs/RRL_STOCK_INVENTORY_CMD.md), [RRL_STOCK_IW_RECOVERY_NEXT](../programs/RRL_STOCK_IW_RECOVERY_NEXT.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_MARK](../programs/RRL_STOCK_QC_MARK.md), [RRL_STOCK_RETURN_DISPOSE](../programs/RRL_STOCK_RETURN_DISPOSE.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STOCK_SUP_RETURN](../programs/RRL_STOCK_SUP_RETURN.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_WH_SCALE_API](../programs/RRL_WH_SCALE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_FINISHED_GOODS_SKU` в файле соответствующего типа.
