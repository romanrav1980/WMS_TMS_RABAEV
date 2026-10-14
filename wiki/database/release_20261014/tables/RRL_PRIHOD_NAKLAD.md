# RRL_PRIHOD_NAKLAD

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `NAKLAD_NUMBER` | VARCHAR2(80 bytes) | Y |  |
| `DATE_OF_NAKLAD` | DATE | Y |  |
| `DATE_OF_ACCEPT` | DATE | Y |  |
| `POSTAVSHIK_NAME` | VARCHAR2(200 bytes) | Y |  |
| `SM_NAKLAD_NUMBER` | VARCHAR2(200 bytes) | Y |  |
| `CONDITION` | NUMBER | Y |  |
| `ID` | NUMBER | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `ZAKAZ_NUMBER` | VARCHAR2(20 bytes) | Y |  |
| `PROOVED` | NUMBER | Y |  |
| `DOCK` | VARCHAR2(50 bytes) | Y |  |
| `VECHILE_NUMBER` | VARCHAR2(50 bytes) | Y |  |
| `VODITEL_NAME` | VARCHAR2(255 bytes) | Y |  |
| `VODITEL_PHONE_NUMB` | VARCHAR2(50 bytes) | Y |  |
| `CHECKING_TIME` | DATE | Y |  |
| `PRIORITY1` | NUMBER | Y |  |
| `PLANNING_ACCEPT_TIME` | DATE | Y |  |
| `INVITE_TIME` | DATE | Y |  |
| `OHRANA_KPP` | VARCHAR2(50 bytes) | Y |  |
| `DOCUMENT_KIND` | VARCHAR2(30 bytes) | N |  |
| `RETURN_APPROVAL_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `RETURN_DOCUMENT_REFERENCE` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PRIHOD_RETURN_APPROVAL_FK | R | RETURN_APPROVAL_OPERATION_ID | RRL_STORE_RETURN_APPROVAL (OPERATION_ID) | ENABLED |
| RRL_PRIHOD_RETURN_KIND_CHECK | C | RETURN_DOCUMENT_REFERENCE, RETURN_APPROVAL_OPERATION_ID, DOCUMENT_KIND |  | ENABLED |
| SYS_C0016710 | C | DOCUMENT_KIND |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[ADD_RRL_PRIH_NAKLAD](../programs/ADD_RRL_PRIH_NAKLAD.md), [ADD_RRL_PRIH_NAKLAD2](../programs/ADD_RRL_PRIH_NAKLAD2.md), [BIN$UX1xZvSxS6/gYw8CAAo/Yg==$0](../programs/BIN_UX1xZvSxS6_gYw8CAAo_Yg___0.md), [DELETE_RRL_PRIH_NAKLAD_ROW](../programs/DELETE_RRL_PRIH_NAKLAD_ROW.md), [PRIHOD](../programs/PRIHOD.md), [REVIZION](../programs/REVIZION.md), [REVIZION_SP_OLD](../programs/REVIZION_SP_OLD.md), [RRL_ACCEPT_ORDER](../programs/RRL_ACCEPT_ORDER.md), [RRL_ACCEPT_ORDER2_2_SP_OLD](../programs/RRL_ACCEPT_ORDER2_2_SP_OLD.md), [RRL_ACCEPT_ORDER2_3_SP_OLD](../programs/RRL_ACCEPT_ORDER2_3_SP_OLD.md), [RRL_ACCEPT_ORDER2_SP_OLD](../programs/RRL_ACCEPT_ORDER2_SP_OLD.md), [RRL_ACCEPT_ORDER3_SP_OLD](../programs/RRL_ACCEPT_ORDER3_SP_OLD.md), [RRL_CLEAR_PRIH_NAKLAD_ROWS](../programs/RRL_CLEAR_PRIH_NAKLAD_ROWS.md), [RRL_INTERNAL_MOVE2_SP_OLD](../programs/RRL_INTERNAL_MOVE2_SP_OLD.md), [RRL_INTERNAL_MOVE3_SP_OLD](../programs/RRL_INTERNAL_MOVE3_SP_OLD.md), [RRL_OTKAT_ORDER2_SP_OLD](../programs/RRL_OTKAT_ORDER2_SP_OLD.md), [RRL_PRIHODPALLET_CHANGE_COUNT](../programs/RRL_PRIHODPALLET_CHANGE_COUNT.md), [RRL_PRIHODPALLET_CHANGE_WEIGHT](../programs/RRL_PRIHODPALLET_CHANGE_WEIGHT.md), [RRL_PRIHOD_RETURN_SOURCE_GUARD](../programs/RRL_PRIHOD_RETURN_SOURCE_GUARD.md), [RRL_STOCK_INTERNAL_CMD](../programs/RRL_STOCK_INTERNAL_CMD.md), [RRL_STOCK_RECEIPT_CORE](../programs/RRL_STOCK_RECEIPT_CORE.md), [RRL_STOCK_RECEIPT_REVERSE](../programs/RRL_STOCK_RECEIPT_REVERSE.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TASK_DOMAIN](../programs/RRL_STOCK_TASK_DOMAIN.md), [RRL_STORNO_ORDER3_SP_OLD](../programs/RRL_STORNO_ORDER3_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PRIHOD_NAKLAD` в файле соответствующего типа.
