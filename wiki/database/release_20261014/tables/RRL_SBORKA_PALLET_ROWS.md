# RRL_SBORKA_PALLET_ROWS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | Y |  |
| `PALLET_UID` | VARCHAR2(50 bytes) | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | Y |  |
| `SHORTNAME` | VARCHAR2(255 bytes) | Y |  |
| `SHTRIHKOD` | VARCHAR2(4000 bytes) | Y |  |
| `EI` | VARCHAR2(40 bytes) | Y |  |
| `TAREWEIGHT` | NUMBER | Y |  |
| `ORDER_WEIGHT` | NUMBER | Y |  |
| `TARESIZE` | NUMBER | Y |  |
| `QUANTITY` | NUMBER | Y |  |
| `SORTFIELD` | NUMBER | Y |  |
| `AUCTION` | VARCHAR2(255 bytes) | Y |  |
| `DOCID` | VARCHAR2(15 bytes) | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `PATH` | VARCHAR2(50 bytes) | Y |  |
| `PACK_COUNT` | NUMBER | Y |  |
| `ORIGINAL_QUANTITY` | NUMBER | Y |  |
| `ORIGINAL_ORDER_WEIGHT` | NUMBER | Y |  |
| `TIME_OF_CHECKING` | DATE | Y |  |
| `CURRENT_MOD_ID` | NUMBER | Y |  |
| `SELECTED` | NUMBER | Y |  |
| `VYCHERK_USER_ID` | VARCHAR2(50 bytes) | Y |  |
| `PRIHOD_PALLET_UID` | VARCHAR2(50 bytes) | Y |  |
| `SOBRANO` | NUMBER | Y |  |
| `EXPIRY_DATE` | DATE | Y |  |
| `PRIHOD_PALLET_UID_COUNT` | NUMBER | Y |  |
| `PROD_BATCH_ID` | NUMBER | Y |  |
| `SSCC` | VARCHAR2(32 bytes) | Y |  |
| `CRPT_TRANSFER_MODE` | VARCHAR2(20 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[COMPL](../programs/COMPL.md), [CROSS_DOCKING](../programs/CROSS_DOCKING.md), [GOODS_TO_PICK](../programs/GOODS_TO_PICK.md), [ORDERS](../programs/ORDERS.md), [PALL_SPLITTER](../programs/PALL_SPLITTER.md), [REMAINS](../programs/REMAINS.md), [RRL_ABC_CALCULATE](../programs/RRL_ABC_CALCULATE.md), [RRL_CLOSE_OTHOD_PALLET_SP_OLD](../programs/RRL_CLOSE_OTHOD_PALLET_SP_OLD.md), [RRL_COPY_PALLET_ROW2](../programs/RRL_COPY_PALLET_ROW2.md), [RRL_CUSTOMER_ORDER_API](../programs/RRL_CUSTOMER_ORDER_API.md), [RRL_DELETE_OP2](../programs/RRL_DELETE_OP2.md), [RRL_DELETE_OPALLET](../programs/RRL_DELETE_OPALLET.md), [RRL_DELETE_ST](../programs/RRL_DELETE_ST.md), [RRL_GET_PALLET_ROWS_COUNT](../programs/RRL_GET_PALLET_ROWS_COUNT.md), [RRL_INTERWARE_ONWARD_ROW_GUARD](../programs/RRL_INTERWARE_ONWARD_ROW_GUARD.md), [RRL_OP_WEIGHT](../programs/RRL_OP_WEIGHT.md), [RRL_OP_WEIGHT2](../programs/RRL_OP_WEIGHT2.md), [RRL_OTHOD_PALLET_PODBOR_PARTII](../programs/RRL_OTHOD_PALLET_PODBOR_PARTII.md), [RRL_PALLET_HAS_MODS](../programs/RRL_PALLET_HAS_MODS.md), [RRL_PALLET_WEIGHT](../programs/RRL_PALLET_WEIGHT.md), [RRL_PALLET_WEIGHT2](../programs/RRL_PALLET_WEIGHT2.md), [RRL_PAL_KOR_COUNT](../programs/RRL_PAL_KOR_COUNT.md), [RRL_PAL_ROW_COUNT](../programs/RRL_PAL_ROW_COUNT.md), [RRL_PAL_VOLUME](../programs/RRL_PAL_VOLUME.md), [RRL_PAL_WEIGHT](../programs/RRL_PAL_WEIGHT.md), [RRL_QC_ROWS_INSERT](../programs/RRL_QC_ROWS_INSERT.md), [RRL_QC_ROWS_INVALIDATE](../programs/RRL_QC_ROWS_INVALIDATE.md), [RRL_SBORKA_PALLETS_ADD](../programs/RRL_SBORKA_PALLETS_ADD.md), [RRL_SBORKA_PALLETS_ADD2](../programs/RRL_SBORKA_PALLETS_ADD2.md), [RRL_SBORKA_PALLET_ROWS_ADD](../programs/RRL_SBORKA_PALLET_ROWS_ADD.md), [RRL_SBORKA_PALLET_ROWS_ADD2](../programs/RRL_SBORKA_PALLET_ROWS_ADD2.md), [RRL_SBORKA_PALLET_ROWS_ADD3](../programs/RRL_SBORKA_PALLET_ROWS_ADD3.md), [RRL_SBORKA_PALLET_ROWS_ADD4](../programs/RRL_SBORKA_PALLET_ROWS_ADD4.md), [RRL_STOCK_FULLPAL_BIND_CMD](../programs/RRL_STOCK_FULLPAL_BIND_CMD.md), [RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_STOCK_ST_ROW_CMD](../programs/RRL_STOCK_ST_ROW_CMD.md), [RRL_ST_DEFER_API](../programs/RRL_ST_DEFER_API.md), [RRL_ST_DEFER_PLACE_READ](../programs/RRL_ST_DEFER_PLACE_READ.md), [RRL_ST_LAYOUT_READ](../programs/RRL_ST_LAYOUT_READ.md), [RRL_ST_ROW_COUNT](../programs/RRL_ST_ROW_COUNT.md), [RRL_ST_UNIQPCOUNT](../programs/RRL_ST_UNIQPCOUNT.md), [RRL_ST_VOLUME](../programs/RRL_ST_VOLUME.md), [RRL_ST_WEIGHT](../programs/RRL_ST_WEIGHT.md), [RRL_SUP_RETURN_ROWS_SOURCE_GUARD](../programs/RRL_SUP_RETURN_ROWS_SOURCE_GUARD.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md), [RRL_TT_VOLUME](../programs/RRL_TT_VOLUME.md), [RRL_TT_WEIGHT](../programs/RRL_TT_WEIGHT.md), [RRL_UPDATE_PALLET_ROW](../programs/RRL_UPDATE_PALLET_ROW.md), [RRL_UPDATE_PALLET_ROW2_SP_CALC](../programs/RRL_UPDATE_PALLET_ROW2_SP_CALC.md), [RRL_UPDATE_PALLET_ROW2_SP_OLD](../programs/RRL_UPDATE_PALLET_ROW2_SP_OLD.md), [RRL_UPDATE_PALLET_ROW3_SP_CALC](../programs/RRL_UPDATE_PALLET_ROW3_SP_CALC.md), [RRL_UPDATE_PALLET_ROW3_SP_OLD](../programs/RRL_UPDATE_PALLET_ROW3_SP_OLD.md), [RRL_UPDATE_SBORKA_PALLET_ROWS2](../programs/RRL_UPDATE_SBORKA_PALLET_ROWS2.md), [RRL_V_AVAILABLE_STS](../programs/RRL_V_AVAILABLE_STS.md), [TRANSPORT_TASK](../programs/TRANSPORT_TASK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SBORKA_PALLET_ROWS` в файле соответствующего типа.
