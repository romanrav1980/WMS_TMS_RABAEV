# RRL_STOCK_RELEASE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `RELEASE_ID` | NUMBER | N |  |
| `STATE` | VARCHAR2(20 bytes) | N |  |
| `BASELINE_ID` | VARCHAR2(100 bytes) | Y |  |
| `CHANGED_AT` | TIMESTAMP(6) | N |  |
| `CHANGED_BY` | VARCHAR2(50 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STOCK_RELEASE_ONE_CK | C | RELEASE_ID |  | ENABLED |
| RRL_STOCK_RELEASE_STATE_CK | C | STATE |  | ENABLED |
| SYS_C0016092 | C | STATE |  | ENABLED |
| SYS_C0016093 | C | CHANGED_AT |  | ENABLED |
| SYS_C0016094 | C | CHANGED_BY |  | ENABLED |
| SYS_C0016097 | P | RELEASE_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[ARTICULS](../programs/ARTICULS.md), [BIN$UX1xZvUbS6/gYw8CAAo/Yg==$0](../programs/BIN_UX1xZvUbS6_gYw8CAAo_Yg___0.md), [REMAINS](../programs/REMAINS.md), [REVIZION](../programs/REVIZION.md), [RRL_ACCEPT_ORDER2](../programs/RRL_ACCEPT_ORDER2.md), [RRL_ACCEPT_ORDER2_2](../programs/RRL_ACCEPT_ORDER2_2.md), [RRL_ACCEPT_ORDER2_3](../programs/RRL_ACCEPT_ORDER2_3.md), [RRL_ACCEPT_ORDER3](../programs/RRL_ACCEPT_ORDER3.md), [RRL_ADD_INV_LINE](../programs/RRL_ADD_INV_LINE.md), [RRL_CLOSE_OTHOD_NAKLAD](../programs/RRL_CLOSE_OTHOD_NAKLAD.md), [RRL_CLOSE_OTHOD_PALLET](../programs/RRL_CLOSE_OTHOD_PALLET.md), [RRL_INTERNAL_MOVE2](../programs/RRL_INTERNAL_MOVE2.md), [RRL_INTERNAL_MOVE3](../programs/RRL_INTERNAL_MOVE3.md), [RRL_INV_CREATE_LINE2](../programs/RRL_INV_CREATE_LINE2.md), [RRL_INV_CREATE_LINE3](../programs/RRL_INV_CREATE_LINE3.md), [RRL_INV_CREATE_LINE4](../programs/RRL_INV_CREATE_LINE4.md), [RRL_MES_PRODUCTION_API](../programs/RRL_MES_PRODUCTION_API.md), [RRL_MES_RAW_SUPPLY_API](../programs/RRL_MES_RAW_SUPPLY_API.md), [RRL_MES_RAW_SUPPLY_OLD](../programs/RRL_MES_RAW_SUPPLY_OLD.md), [RRL_OTKAT_ORDER2](../programs/RRL_OTKAT_ORDER2.md), [RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_PLAN_ADMISSION](../programs/RRL_PICK_PLAN_ADMISSION.md), [RRL_PICK_PLAN_CREATE_API](../programs/RRL_PICK_PLAN_CREATE_API.md), [RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_REVIZION_CELL](../programs/RRL_REVIZION_CELL.md), [RRL_REVIZION_CELL_KOR](../programs/RRL_REVIZION_CELL_KOR.md), [RRL_SET_SCAN_PROOVE](../programs/RRL_SET_SCAN_PROOVE.md), [RRL_SET_SCAN_PROOVE2](../programs/RRL_SET_SCAN_PROOVE2.md), [RRL_STOCK_CONFIG_API](../programs/RRL_STOCK_CONFIG_API.md), [RRL_STOCK_CTX_API](../programs/RRL_STOCK_CTX_API.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_STOCK_OPERATION_CORE](../programs/RRL_STOCK_OPERATION_CORE.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_SETTING_API](../programs/RRL_STOCK_SETTING_API.md), [RRL_STOCK_WRITE_GUARD](../programs/RRL_STOCK_WRITE_GUARD.md), [RRL_STORE_UNLOAD_API](../programs/RRL_STORE_UNLOAD_API.md), [RRL_STORNO_ORDER3](../programs/RRL_STORNO_ORDER3.md), [RRL_TRIAL_BY_WEIGHT](../programs/RRL_TRIAL_BY_WEIGHT.md), [RRL_TRIAL_BY_WEIGHT2](../programs/RRL_TRIAL_BY_WEIGHT2.md), [RRL_UPDATE_PALLET_ROW2](../programs/RRL_UPDATE_PALLET_ROW2.md), [RRL_UPDATE_PALLET_ROW3](../programs/RRL_UPDATE_PALLET_ROW3.md), [RRL_UPDATE_SBORKA_PALLET_ROWS2](../programs/RRL_UPDATE_SBORKA_PALLET_ROWS2.md), [RRL_WEIGHT_BOX_PLANNING_READ](../programs/RRL_WEIGHT_BOX_PLANNING_READ.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_RELEASE` в файле соответствующего типа.
