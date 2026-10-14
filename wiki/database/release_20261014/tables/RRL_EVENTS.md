# RRL_EVENTS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID_EVENT` | NUMBER | Y |  |
| `CELL_FROM` | VARCHAR2(60 bytes) | Y |  |
| `CELL_TO` | VARCHAR2(60 bytes) | Y |  |
| `DATE_EVENT` | DATE | N |  |
| `DATE_OF_ORDER` | DATE | Y |  |
| `COUNT_EVENT` | NUMBER | Y |  |
| `TYPE_EVENT` | NUMBER(38,0) | N |  |
| `UID_POLETA` | VARCHAR2(200 bytes) | Y |  |
| `USER_ID` | VARCHAR2(50 bytes) | N |  |
| `PRIHOD_NAKL_ID` | NUMBER | Y |  |
| `OTHOD_NAKL_ID` | NUMBER | Y |  |
| `PALLET_ROW_ID` | NUMBER | Y |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `LINE_NO` | NUMBER | Y |  |
| `LEG_NO` | NUMBER | Y |  |
| `BASE_QTY` | NUMBER | Y |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | Y |  |
| `UOM_POLICY_VERSION` | NUMBER | Y |  |
| `ORIGINAL_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| BIN$UX1xZvUVS6/gYw8CAAo/Yg==$0 | C | DATE_EVENT |  | ENABLED |
| BIN$UX1xZvUWS6/gYw8CAAo/Yg==$0 | C | TYPE_EVENT |  | ENABLED |
| BIN$UX1xZvUXS6/gYw8CAAo/Yg==$0 | C | USER_ID |  | ENABLED |
| RRL_EVENTS_OPERATION_UK | U | OPERATION_ID, LINE_NO, LEG_NO |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[ARTICULS_SP_OLD](../programs/ARTICULS_SP_OLD.md), [BIN$UX1xZvUbS6/gYw8CAAo/Yg==$0](../programs/BIN_UX1xZvUbS6_gYw8CAAo_Yg___0.md), [REVIZION_SP_OLD](../programs/REVIZION_SP_OLD.md), [RRL_ACCEPT_ORDER2_2_SP_OLD](../programs/RRL_ACCEPT_ORDER2_2_SP_OLD.md), [RRL_ACCEPT_ORDER2_SP_OLD](../programs/RRL_ACCEPT_ORDER2_SP_OLD.md), [RRL_ACCEPT_ORDER3_SP_OLD](../programs/RRL_ACCEPT_ORDER3_SP_OLD.md), [RRL_ADD_INV_LINE_SP_OLD](../programs/RRL_ADD_INV_LINE_SP_OLD.md), [RRL_CLOSE_OTHOD_NAKLAD_SP_OLD](../programs/RRL_CLOSE_OTHOD_NAKLAD_SP_OLD.md), [RRL_CLOSE_OTHOD_PALLET_SP_OLD](../programs/RRL_CLOSE_OTHOD_PALLET_SP_OLD.md), [RRL_INTERNAL_MOVE2_SP_OLD](../programs/RRL_INTERNAL_MOVE2_SP_OLD.md), [RRL_INTERNAL_MOVE3_SP_OLD](../programs/RRL_INTERNAL_MOVE3_SP_OLD.md), [RRL_INTERWARE_INCIDENT_API](../programs/RRL_INTERWARE_INCIDENT_API.md), [RRL_INTERWARE_RECEIPT_GUARD](../programs/RRL_INTERWARE_RECEIPT_GUARD.md), [RRL_INV_CREATE_LINE2_SP_OLD](../programs/RRL_INV_CREATE_LINE2_SP_OLD.md), [RRL_INV_CREATE_LINE3_SP_OLD](../programs/RRL_INV_CREATE_LINE3_SP_OLD.md), [RRL_INV_CREATE_LINE4_SP_OLD](../programs/RRL_INV_CREATE_LINE4_SP_OLD.md), [RRL_IW_GROUP_REC_LINE_GUARD](../programs/RRL_IW_GROUP_REC_LINE_GUARD.md), [RRL_MES_PRODUCTION_API](../programs/RRL_MES_PRODUCTION_API.md), [RRL_OTKAT_ORDER2_SP_OLD](../programs/RRL_OTKAT_ORDER2_SP_OLD.md), [RRL_REVIZION_CELL_KOR_SP_OLD](../programs/RRL_REVIZION_CELL_KOR_SP_OLD.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_INVARIANT_CORE](../programs/RRL_STOCK_INVARIANT_CORE.md), [RRL_STOCK_JOURNAL_GUARD](../programs/RRL_STOCK_JOURNAL_GUARD.md), [RRL_STOCK_RECEIPT_REVERSE](../programs/RRL_STOCK_RECEIPT_REVERSE.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_STORNO_ORDER3_SP_OLD](../programs/RRL_STORNO_ORDER3_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_EVENTS` в файле соответствующего типа.
