# RRL_ARTICUL_REPLENISH_RULE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ARTICUL_REPLENISH_RULE_ID` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(80 bytes) | N |  |
| `REPLENISHMENT_METHOD` | VARCHAR2(20 bytes) | N |  |
| `REPLENISHMENT_RELEASE_POLICY` | VARCHAR2(40 bytes) | N |  |
| `REPLENISHMENT_QTY_MODE` | VARCHAR2(20 bytes) | N |  |
| `MIN_TRIGGER_BOX_QTY` | NUMBER | Y |  |
| `MIN_TRIGGER_LAYER_QTY` | NUMBER | Y |  |
| `SAFETY_LAYER_QTY` | NUMBER | Y |  |
| `BOXES_PER_LAYER` | NUMBER | Y |  |
| `BOXES_PER_PALLET` | NUMBER | Y |  |
| `BOX_VOLUME_M3` | NUMBER | Y |  |
| `ALLOW_PARTIAL_PALLET` | NUMBER(1,0) | N |  |
| `PREDICTIVE_BUFFER_MIN` | NUMBER | Y |  |
| `PICK_RATE_SOURCE` | VARCHAR2(20 bytes) | N |  |
| `RECHECK_ON_PICK_EVENT` | NUMBER(1,0) | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `COMMENT_TEXT` | VARCHAR2(500 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | N |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_ART_REPL_RULE_CHK1 | C | REPLENISHMENT_METHOD |  | ENABLED |
| RRL_ART_REPL_RULE_CHK2 | C | REPLENISHMENT_RELEASE_POLICY |  | ENABLED |
| RRL_ART_REPL_RULE_CHK3 | C | REPLENISHMENT_QTY_MODE |  | ENABLED |
| RRL_ART_REPL_RULE_CHK4 | C | ALLOW_PARTIAL_PALLET |  | ENABLED |
| RRL_ART_REPL_RULE_CHK5 | C | PICK_RATE_SOURCE |  | ENABLED |
| RRL_ART_REPL_RULE_CHK6 | C | RECHECK_ON_PICK_EVENT |  | ENABLED |
| RRL_ART_REPL_RULE_CHK7 | C | ACTIVE |  | ENABLED |
| RRL_ART_REPL_RULE_PK | P | ARTICUL_REPLENISH_RULE_ID |  | ENABLED |
| RRL_ART_REPL_RULE_U1 | U | ARTICUL |  | ENABLED |
| SYS_C0015016 | C | ARTICUL_REPLENISH_RULE_ID |  | ENABLED |
| SYS_C0015017 | C | ARTICUL |  | ENABLED |
| SYS_C0015018 | C | REPLENISHMENT_METHOD |  | ENABLED |
| SYS_C0015019 | C | REPLENISHMENT_RELEASE_POLICY |  | ENABLED |
| SYS_C0015020 | C | REPLENISHMENT_QTY_MODE |  | ENABLED |
| SYS_C0015021 | C | ALLOW_PARTIAL_PALLET |  | ENABLED |
| SYS_C0015022 | C | PICK_RATE_SOURCE |  | ENABLED |
| SYS_C0015023 | C | RECHECK_ON_PICK_EVENT |  | ENABLED |
| SYS_C0015024 | C | ACTIVE |  | ENABLED |
| SYS_C0015025 | C | CREATED_AT |  | ENABLED |
| SYS_C0015026 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_STOCK_REPL_CAPACITY](../programs/RRL_STOCK_REPL_CAPACITY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ARTICUL_REPLENISH_RULE` в файле соответствующего типа.
