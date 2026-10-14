# RRL_CASE_CARRIER_LOT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Сборка CASE.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `LOT_UID` | VARCHAR2(150 bytes) | N |  |
| `CASE_PICK_TASK_ID` | NUMBER | N |  |
| `CASE_PICK_LINE_ID` | NUMBER | N |  |
| `CREATED_OPERATION` | VARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016179 | C | CASE_PICK_TASK_ID |  | ENABLED |
| SYS_C0016180 | C | CASE_PICK_LINE_ID |  | ENABLED |
| SYS_C0016181 | C | CREATED_OPERATION |  | ENABLED |
| SYS_C0016182 | C | CREATED_AT |  | ENABLED |
| SYS_C0016183 | C | CREATED_BY |  | ENABLED |
| SYS_C0016184 | P | LOT_UID |  | ENABLED |
| SYS_C0016185 | R | CASE_PICK_TASK_ID | RRL_CASE_PICK_TASK (CASE_PICK_TASK_ID) | ENABLED |
| SYS_C0016186 | R | CASE_PICK_LINE_ID | RRL_CASE_PICK_LINE (CASE_PICK_LINE_ID) | ENABLED |
| SYS_C0016187 | R | CREATED_OPERATION | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_CARRIER_LOT_GUARD](../programs/RRL_CASE_CARRIER_LOT_GUARD.md), [RRL_CASE_PALLET_TYPE_READ](../programs/RRL_CASE_PALLET_TYPE_READ.md), [RRL_FORECAST_SOURCE_RULES](../programs/RRL_FORECAST_SOURCE_RULES.md), [RRL_INTERWARE_UNIT_SOURCE](../programs/RRL_INTERWARE_UNIT_SOURCE.md), [RRL_PALLET_FLOOR_READ](../programs/RRL_PALLET_FLOOR_READ.md), [RRL_RETURN_PALLET_IDENTITY](../programs/RRL_RETURN_PALLET_IDENTITY.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md), [RRL_STOCK_CASE_RETURN_CMD](../programs/RRL_STOCK_CASE_RETURN_CMD.md), [RRL_STOCK_CASE_SHORT_CMD](../programs/RRL_STOCK_CASE_SHORT_CMD.md), [RRL_STOCK_COMPOSITION_CORE](../programs/RRL_STOCK_COMPOSITION_CORE.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_POLICY](../programs/RRL_STOCK_QC_POLICY.md), [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_STOCK_TARE_BOOK_CMD](../programs/RRL_STOCK_TARE_BOOK_CMD.md), [RRL_STOCK_TRANSFER_CORE](../programs/RRL_STOCK_TRANSFER_CORE.md), [RRL_STOCK_WAVE_READY](../programs/RRL_STOCK_WAVE_READY.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_PHYSICAL](../programs/RRL_ST_DEFER_PHYSICAL.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CASE_CARRIER_LOT` в файле соответствующего типа.
