# RRL_TT_HU_LOAD_ST

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `SBORKA_PALLET_ID` | NUMBER | N |  |
| `ACTIVE_FLAG` | NUMBER(1,0) | N |  |
| `DESTINATION_ADDR` | VARCHAR2(255 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TT_HU_LOAD_ST_PK | P | LOAD_OPERATION_ID, SBORKA_PALLET_ID |  | ENABLED |
| SYS_C0016331 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0016332 | C | SBORKA_PALLET_ID |  | ENABLED |
| SYS_C0016333 | C | ACTIVE_FLAG |  | ENABLED |
| SYS_C0016334 | C | ACTIVE_FLAG |  | ENABLED |
| SYS_C0016336 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| SYS_C0016337 | R | SBORKA_PALLET_ID | RRL_SBORKA_PALLETS (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_INTERWARE_DEPART_GATE](../programs/RRL_INTERWARE_DEPART_GATE.md), [RRL_INTERWARE_ONWARD_BIND_GUARD](../programs/RRL_INTERWARE_ONWARD_BIND_GUARD.md), [RRL_INTERWARE_PLAN_GUARD](../programs/RRL_INTERWARE_PLAN_GUARD.md), [RRL_IW_GROUP_ARCHIVE](../programs/RRL_IW_GROUP_ARCHIVE.md), [RRL_IW_GROUP_ST_BIND_GUARD](../programs/RRL_IW_GROUP_ST_BIND_GUARD.md), [RRL_STOCK_CASE_BIND_MOVE](../programs/RRL_STOCK_CASE_BIND_MOVE.md), [RRL_STOCK_HU_LOAD_CORE](../programs/RRL_STOCK_HU_LOAD_CORE.md), [RRL_STOCK_STORE_RECEIPT_READ](../programs/RRL_STOCK_STORE_RECEIPT_READ.md), [RRL_STOCK_TRIP_DEPART_CMD](../programs/RRL_STOCK_TRIP_DEPART_CMD.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_STORE_SCALE_API](../programs/RRL_STORE_SCALE_API.md), [RRL_STORE_SUPPLIER_CARGO_GUARD](../programs/RRL_STORE_SUPPLIER_CARGO_GUARD.md), [RRL_ST_DEFER_API](../programs/RRL_ST_DEFER_API.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md), [RRL_ST_LAYOUT_READ](../programs/RRL_ST_LAYOUT_READ.md), [RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md), [RRL_TRANSPORT_PLAN_API](../programs/RRL_TRANSPORT_PLAN_API.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md), [RRL_TT_ADD_PALL](../programs/RRL_TT_ADD_PALL.md), [RRL_TT_HU_LOAD_ST_GUARD](../programs/RRL_TT_HU_LOAD_ST_GUARD.md), [RRL_TT_LOADED_ST_ASSIGN_GUARD](../programs/RRL_TT_LOADED_ST_ASSIGN_GUARD.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_HU_LOAD_ST` в файле соответствующего типа.
