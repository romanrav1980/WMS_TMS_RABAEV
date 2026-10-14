# RRL_ARTICULS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ACTICUL` | VARCHAR2(160 bytes) | Y |  |
| `NORMA_UKLADKI` | NUMBER | N |  |
| `CELL` | VARCHAR2(200 bytes) | Y |  |
| `NAME` | VARCHAR2(1020 bytes) | Y |  |
| `UNIT_TYPE` | VARCHAR2(80 bytes) | Y |  |
| `BARCODE_SHT` | VARCHAR2(512 bytes) | N |  |
| `BARCODE_KOR` | VARCHAR2(512 bytes) | Y |  |
| `BARCODE_BL` | VARCHAR2(512 bytes) | Y |  |
| `WEIGHT_OF_KOR` | NUMBER | Y |  |
| `COUNT_IN_ROW` | NUMBER | Y |  |
| `ROWS_IN_PAL` | NUMBER | Y |  |
| `COUNT_SHT_IN_KOR` | NUMBER | Y |  |
| `COUNT_SHT_IN_BL` | NUMBER | Y |  |
| `PALLET_MULTIPLE` | NUMBER | Y |  |
| `CARTON_WEIGHT` | NUMBER | Y |  |
| `ETAJ_LIMIT` | NUMBER | Y | Исходный комментарий Oracle повреждён; требуется уточнение. |
| `BESTBEFOREDAYS` | NUMBER | Y |  |
| `SSP` | NUMBER | Y |  |
| `ABC_GROUP` | VARCHAR2(1 bytes) | Y |  |
| `XYZ_GROUP` | VARCHAR2(1 bytes) | Y |  |
| `ORDER_OF_COMP` | NUMBER | Y |  |
| `RCECOMPLECT` | NUMBER | Y |  |
| `FLOATING_WEIGHT` | NUMBER | Y |  |
| `TYPE_W` | NUMBER | Y |  |
| `WEIGHT_OF_SHT` | NUMBER | Y |  |
| `ROUND_TO` | NUMBER | Y |  |
| `DEF_PERC` | NUMBER | Y |  |
| `LAST_MOD_ID` | NUMBER | Y |  |
| `AUTHOR_ID` | VARCHAR2(50 bytes) | Y |  |
| `FAKE_PARTION_UID` | VARCHAR2(50 bytes) | Y |  |
| `DIMKOR_X` | NUMBER | Y |  |
| `DIMKOR_Y` | NUMBER | Y |  |
| `DIMKOR_Z` | NUMBER | Y |  |
| `BRUTTO_WEIGHT_OF_KOR` | NUMBER | Y |  |
| `LAST_PRICE` | NUMBER | Y |  |
| `LAST_USER_ID` | VARCHAR2(50 bytes) | Y |  |
| `UUZ` | NUMBER | Y |  |
| `SHIPMENT_AGING_HOURS` | NUMBER | Y |  |
| `SHIPMENT_AGING_COMMENT` | VARCHAR2(1000 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| BIN$UX1xZvSmS6/gYw8CAAo/Yg==$0 | C | NORMA_UKLADKI |  | ENABLED |
| BIN$UX1xZvSnS6/gYw8CAAo/Yg==$0 | C | BARCODE_SHT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[ARTICULS](../programs/ARTICULS.md), [ARTICULS_SP_OLD](../programs/ARTICULS_SP_OLD.md), [COMPL](../programs/COMPL.md), [CROSS_DOCKING](../programs/CROSS_DOCKING.md), [GOODS_TO_PICK](../programs/GOODS_TO_PICK.md), [ORDERS](../programs/ORDERS.md), [PALL_SPLITTER](../programs/PALL_SPLITTER.md), [REMAINS](../programs/REMAINS.md), [REVIZION](../programs/REVIZION.md), [REVIZION_SP_OLD](../programs/REVIZION_SP_OLD.md), [RRL_ABC_CALCULATE](../programs/RRL_ABC_CALCULATE.md), [RRL_ACCEPT_ORDER](../programs/RRL_ACCEPT_ORDER.md), [RRL_ACCEPT_ORDER2_2_SP_OLD](../programs/RRL_ACCEPT_ORDER2_2_SP_OLD.md), [RRL_ACCEPT_ORDER2_3_SP_OLD](../programs/RRL_ACCEPT_ORDER2_3_SP_OLD.md), [RRL_ACCEPT_ORDER2_SP_OLD](../programs/RRL_ACCEPT_ORDER2_SP_OLD.md), [RRL_CARTON_WEIGHT](../programs/RRL_CARTON_WEIGHT.md), [RRL_CARTON_WEIGHT2](../programs/RRL_CARTON_WEIGHT2.md), [RRL_CASE_SCALE_ADMISSION](../programs/RRL_CASE_SCALE_ADMISSION.md), [RRL_CLOSE_OTHOD_NAKLAD_SP_OLD](../programs/RRL_CLOSE_OTHOD_NAKLAD_SP_OLD.md), [RRL_CLOSE_OTHOD_PALLET_SP_OLD](../programs/RRL_CLOSE_OTHOD_PALLET_SP_OLD.md), [RRL_COUNT_KOR](../programs/RRL_COUNT_KOR.md), [RRL_COUNT_KOR2](../programs/RRL_COUNT_KOR2.md), [RRL_COUNT_KOR3](../programs/RRL_COUNT_KOR3.md), [RRL_COUNT_KOR4](../programs/RRL_COUNT_KOR4.md), [RRL_DAY_DISTRIBUTE_ENDS](../programs/RRL_DAY_DISTRIBUTE_ENDS.md), [RRL_GIVE_DESTINATION_CELL2](../programs/RRL_GIVE_DESTINATION_CELL2.md), [RRL_GIVE_POPOLNENIE2](../programs/RRL_GIVE_POPOLNENIE2.md), [RRL_INTERNAL_MOVE3_SP_OLD](../programs/RRL_INTERNAL_MOVE3_SP_OLD.md), [RRL_INV_CREATE_LINE](../programs/RRL_INV_CREATE_LINE.md), [RRL_INV_CREATE_LINE2_SP_OLD](../programs/RRL_INV_CREATE_LINE2_SP_OLD.md), [RRL_INV_CREATE_LINE3_SP_OLD](../programs/RRL_INV_CREATE_LINE3_SP_OLD.md), [RRL_INV_CREATE_LINE4_SP_OLD](../programs/RRL_INV_CREATE_LINE4_SP_OLD.md), [RRL_ORDER_WEIGHT_READ](../programs/RRL_ORDER_WEIGHT_READ.md), [RRL_OTHOD_PALLET_PODBOR_PARTII](../programs/RRL_OTHOD_PALLET_PODBOR_PARTII.md), [RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_RANGE_PROPOSAL_API](../programs/RRL_PICK_RANGE_PROPOSAL_API.md), [RRL_PRIEMPALLET_HEIGHT](../programs/RRL_PRIEMPALLET_HEIGHT.md), [RRL_PRIEMPALLET_WEIGHT](../programs/RRL_PRIEMPALLET_WEIGHT.md), [RRL_PRIHODPALLET_CHANGE](../programs/RRL_PRIHODPALLET_CHANGE.md), [RRL_PRIHODPALLET_CHANGE_COUNT](../programs/RRL_PRIHODPALLET_CHANGE_COUNT.md), [RRL_PRIHODPALLET_CHANGE_WEIGHT](../programs/RRL_PRIHODPALLET_CHANGE_WEIGHT.md), [RRL_PRIHOD_VERIFY](../programs/RRL_PRIHOD_VERIFY.md), [RRL_REVIZION_CELL_KOR_SP_OLD](../programs/RRL_REVIZION_CELL_KOR_SP_OLD.md), [RRL_SBORKA_CELL](../programs/RRL_SBORKA_CELL.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md), [RRL_STOCK_INTERNAL_CMD](../programs/RRL_STOCK_INTERNAL_CMD.md), [RRL_STOCK_INV_ENTRY](../programs/RRL_STOCK_INV_ENTRY.md), [RRL_STOCK_PALLET_UOM](../programs/RRL_STOCK_PALLET_UOM.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_ITEM](../programs/RRL_STOCK_QC_ITEM.md), [RRL_STOCK_REPL_ADMISSION](../programs/RRL_STOCK_REPL_ADMISSION.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_UOM_CONFIG](../programs/RRL_STOCK_UOM_CONFIG.md), [RRL_TOVAR_TYPE](../programs/RRL_TOVAR_TYPE.md), [RRL_TRG_PROD_BATCH_SHIP_READY](../programs/RRL_TRG_PROD_BATCH_SHIP_READY.md), [RRL_UPDATE_ARTICUL_EX](../programs/RRL_UPDATE_ARTICUL_EX.md), [RRL_UPDATE_PALLET_ROW3_SP_CALC](../programs/RRL_UPDATE_PALLET_ROW3_SP_CALC.md), [RRL_UPDATE_PALLET_ROW3_SP_OLD](../programs/RRL_UPDATE_PALLET_ROW3_SP_OLD.md), [RRL_UPDATE_SG](../programs/RRL_UPDATE_SG.md), [RRL_WEIGHT_BOX_READ](../programs/RRL_WEIGHT_BOX_READ.md), [RRL_WH_SCALE_API](../programs/RRL_WH_SCALE_API.md), [TRANSPORT_TASK](../programs/TRANSPORT_TASK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ARTICULS` в файле соответствующего типа.
