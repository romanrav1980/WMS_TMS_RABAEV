# RRL_PICK_WAVE_REPLENISH_TASK

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_WAVE_REPLENISH_TASK_ID` | NUMBER | N |  |
| `PICK_WAVE_ID` | NUMBER | N |  |
| `PICK_TASK_ID` | NUMBER | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `PALLET_UID` | VARCHAR2(200 bytes) | Y |  |
| `SOURCE_CELL_CODE` | VARCHAR2(60 bytes) | Y |  |
| `TARGET_CELL_CODE` | VARCHAR2(60 bytes) | Y |  |
| `QTY` | NUMBER | N |  |
| `PICK_SEQUENCE` | NUMBER | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `REPLENISHMENT_METHOD` | VARCHAR2(20 bytes) | Y |  |
| `REPLENISHMENT_QTY_MODE` | VARCHAR2(20 bytes) | Y |  |
| `RELEASE_TRIGGER_QTY` | NUMBER | Y |  |
| `BOXES_PER_LAYER` | NUMBER | Y |  |
| `BOXES_PER_PALLET` | NUMBER | Y |  |
| `BOX_VOLUME_M3` | NUMBER | Y |  |
| `PICK_FACE_MAX_VOLUME` | NUMBER | Y |  |
| `WAIT_REASON` | VARCHAR2(200 bytes) | Y |  |
| `RELEASED_AT` | DATE | Y |  |
| `RELEASED_BY` | VARCHAR2(50 bytes) | Y |  |
| `SOURCE_RESERVATION_ID` | NUMBER | Y |  |
| `SOURCE_AVAILABLE_QTY` | NUMBER | Y |  |
| `SOURCE_PRODUCED_DATE` | DATE | Y |  |
| `SOURCE_EXPIRY_DATE` | DATE | Y |  |
| `MIN_SHELF_LIFE_DAYS` | NUMBER | Y |  |
| `MIN_SHELF_LIFE_PERCENT` | NUMBER | Y |  |
| `REPLENISHMENT_RELEASE_POLICY` | VARCHAR2(40 bytes) | Y |  |
| `SAFETY_LAYER_QTY` | NUMBER | Y |  |
| `PREDICTIVE_BUFFER_MIN` | NUMBER | Y |  |
| `PICK_RATE_SOURCE` | VARCHAR2(20 bytes) | Y |  |
| `RECHECK_ON_PICK_EVENT` | NUMBER(1,0) | Y |  |
| `DEMAND_BASE_QTY` | NUMBER | Y |  |
| `RESERVE_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `MINIMAX_CYCLE_ID` | NUMBER | Y |  |
| `MINIMAX_TARGET_BASE` | NUMBER | Y |  |
| `MINIMAX_FINISHED_AT` | TIMESTAMP(6) | Y |  |
| `PARENT_REPLENISH_TASK_ID` | NUMBER | Y |  |
| `RESERVE_REQUEST_JSON` | CLOB | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_WAVE_REPL_CHK1 | C | STATUS |  | ENABLED |
| RRL_PICK_WAVE_REPL_CHK2 | C | REPLENISHMENT_METHOD |  | ENABLED |
| RRL_PICK_WAVE_REPL_CHK3 | C | REPLENISHMENT_QTY_MODE |  | ENABLED |
| RRL_PICK_WAVE_REPL_FK1 | R | PICK_WAVE_ID | RRL_PICK_WAVE (PICK_WAVE_ID) | ENABLED |
| RRL_PICK_WAVE_REPL_PK | P | PICK_WAVE_REPLENISH_TASK_ID |  | ENABLED |
| SYS_C0014597 | C | PICK_WAVE_REPLENISH_TASK_ID |  | ENABLED |
| SYS_C0014598 | C | PICK_WAVE_ID |  | ENABLED |
| SYS_C0014599 | C | STATUS |  | ENABLED |
| SYS_C0014600 | C | ARTICUL |  | ENABLED |
| SYS_C0014601 | C | QTY |  | ENABLED |
| SYS_C0014602 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_RANGE_POLICY](../programs/RRL_PICK_RANGE_POLICY.md), [RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md), [RRL_REPL_RANGE_TARGET_G](../programs/RRL_REPL_RANGE_TARGET_G.md), [RRL_STOCK_DOC_RESERVE_CMD](../programs/RRL_STOCK_DOC_RESERVE_CMD.md), [RRL_STOCK_REPL_ADMISSION](../programs/RRL_STOCK_REPL_ADMISSION.md), [RRL_STOCK_REPL_BIND](../programs/RRL_STOCK_REPL_BIND.md), [RRL_STOCK_REPL_CAPACITY](../programs/RRL_STOCK_REPL_CAPACITY.md), [RRL_STOCK_REPL_CONTINUATION](../programs/RRL_STOCK_REPL_CONTINUATION.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_STOCK_TASK_DOMAIN](../programs/RRL_STOCK_TASK_DOMAIN.md), [RRL_STOCK_TASK_PLAN](../programs/RRL_STOCK_TASK_PLAN.md), [RRL_STOCK_WAVE_CMD](../programs/RRL_STOCK_WAVE_CMD.md), [RRL_STOCK_WAVE_FINISH_CMD](../programs/RRL_STOCK_WAVE_FINISH_CMD.md), [RRL_STOCK_WAVE_PICK_CMD](../programs/RRL_STOCK_WAVE_PICK_CMD.md), [RRL_STOCK_WAVE_READY](../programs/RRL_STOCK_WAVE_READY.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_WAVE_REPLENISH_TASK` в файле соответствующего типа.
