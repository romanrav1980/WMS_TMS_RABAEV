# RRL_PICK_FACE_ARTICUL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_FACE_ARTICUL_ID` | NUMBER | N |  |
| `PICK_FACE_ID` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `PRIORITY` | NUMBER | N |  |
| `MIN_QTY` | NUMBER | Y |  |
| `MAX_QTY` | NUMBER | Y |  |
| `CASE_PICK_ENABLED` | NUMBER(1,0) | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `VALID_FROM` | DATE | N |  |
| `VALID_TO` | DATE | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `REPLENISHMENT_METHOD` | VARCHAR2(20 bytes) | N |  |
| `REPLENISHMENT_QTY_MODE` | VARCHAR2(20 bytes) | N |  |
| `MIN_TRIGGER_BOX_QTY` | NUMBER | Y |  |
| `MIN_TRIGGER_LAYER_QTY` | NUMBER | Y |  |
| `BOXES_PER_LAYER` | NUMBER | Y |  |
| `BOXES_PER_PALLET` | NUMBER | Y |  |
| `BOX_VOLUME_M3` | NUMBER | Y |  |
| `ALLOW_PARTIAL_PALLET` | NUMBER(1,0) | N |  |
| `USE_ARTICUL_REPLENISH_RULE` | NUMBER(1,0) | N |  |
| `REPLENISHMENT_RELEASE_POLICY` | VARCHAR2(40 bytes) | N |  |
| `SAFETY_LAYER_QTY` | NUMBER | Y |  |
| `PREDICTIVE_BUFFER_MIN` | NUMBER | Y |  |
| `PICK_RATE_SOURCE` | VARCHAR2(20 bytes) | N |  |
| `RECHECK_ON_PICK_EVENT` | NUMBER(1,0) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_FACE_ARTICUL_CHK1 | C | CASE_PICK_ENABLED |  | ENABLED |
| RRL_PICK_FACE_ARTICUL_CHK2 | C | ACTIVE |  | ENABLED |
| RRL_PICK_FACE_ARTICUL_FK1 | R | PICK_FACE_ID | RRL_PICK_FACE (PICK_FACE_ID) | ENABLED |
| RRL_PICK_FACE_ARTICUL_PK | P | PICK_FACE_ARTICUL_ID |  | ENABLED |
| RRL_PICK_FACE_ART_CHK3 | C | REPLENISHMENT_METHOD |  | ENABLED |
| RRL_PICK_FACE_ART_CHK4 | C | REPLENISHMENT_QTY_MODE |  | ENABLED |
| RRL_PICK_FACE_ART_CHK5 | C | ALLOW_PARTIAL_PALLET |  | ENABLED |
| SYS_C0014515 | C | PICK_FACE_ARTICUL_ID |  | ENABLED |
| SYS_C0014516 | C | PICK_FACE_ID |  | ENABLED |
| SYS_C0014517 | C | ARTICUL |  | ENABLED |
| SYS_C0014518 | C | PRIORITY |  | ENABLED |
| SYS_C0014519 | C | CASE_PICK_ENABLED |  | ENABLED |
| SYS_C0014520 | C | ACTIVE |  | ENABLED |
| SYS_C0014521 | C | VALID_FROM |  | ENABLED |
| SYS_C0014522 | C | CREATED_AT |  | ENABLED |
| SYS_C0014791 | C | REPLENISHMENT_METHOD |  | ENABLED |
| SYS_C0014792 | C | REPLENISHMENT_QTY_MODE |  | ENABLED |
| SYS_C0014793 | C | ALLOW_PARTIAL_PALLET |  | ENABLED |
| SYS_C0015036 | C | USE_ARTICUL_REPLENISH_RULE |  | ENABLED |
| SYS_C0015037 | C | REPLENISHMENT_RELEASE_POLICY |  | ENABLED |
| SYS_C0015038 | C | PICK_RATE_SOURCE |  | ENABLED |
| SYS_C0015039 | C | RECHECK_ON_PICK_EVENT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_RANGE_POLICY](../programs/RRL_PICK_RANGE_POLICY.md), [RRL_PICK_TOPOLOGY_API](../programs/RRL_PICK_TOPOLOGY_API.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_REPL_CAPACITY](../programs/RRL_STOCK_REPL_CAPACITY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_FACE_ARTICUL` в файле соответствующего типа.
