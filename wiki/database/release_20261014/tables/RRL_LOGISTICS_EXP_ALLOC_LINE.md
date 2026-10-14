# RRL_LOGISTICS_EXP_ALLOC_LINE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `ARTICLE` | VARCHAR2(160 bytes) | N |  |
| `BASE_QTY` | NUMBER(27,9) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `WEIGHT_KG` | NUMBER(27,9) | Y |  |
| `BASIS_VALUE` | NUMBER(27,9) | N |  |
| `AMOUNT` | NUMBER(27,2) | N |  |
| `CURRENCY` | VARCHAR2(3 bytes) | N |  |
| `WEIGHT_SOURCE` | VARCHAR2(30 bytes) | N |  |
| `WEIGHT_BOX_UID` | VARCHAR2(200 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017111 | C | OPERATION_ID |  | ENABLED |
| SYS_C0017112 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0017113 | C | UID_PALLET |  | ENABLED |
| SYS_C0017114 | C | ARTICLE |  | ENABLED |
| SYS_C0017115 | C | BASE_QTY |  | ENABLED |
| SYS_C0017116 | C | BASE_UOM |  | ENABLED |
| SYS_C0017117 | C | BASIS_VALUE |  | ENABLED |
| SYS_C0017118 | C | AMOUNT |  | ENABLED |
| SYS_C0017119 | C | CURRENCY |  | ENABLED |
| SYS_C0017120 | C | BASE_QTY |  | ENABLED |
| SYS_C0017121 | C | BASIS_VALUE |  | ENABLED |
| SYS_C0017122 | C | AMOUNT |  | ENABLED |
| SYS_C0017123 | P | OPERATION_ID, LOAD_OPERATION_ID, UID_PALLET |  | ENABLED |
| SYS_C0017124 | R | OPERATION_ID | RRL_LOGISTICS_EXP_ALLOCATION (OPERATION_ID) | ENABLED |
| SYS_C0017125 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| SYS_C0017126 | C | WEIGHT_SOURCE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOG_EXP_ALLOC_LINE_GUARD](../programs/RRL_LOG_EXP_ALLOC_LINE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_LOGISTICS_EXP_ALLOC_LINE` в файле соответствующего типа.
