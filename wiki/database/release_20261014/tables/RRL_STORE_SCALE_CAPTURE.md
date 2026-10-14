# RRL_STORE_SCALE_CAPTURE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CAPTURE_KEY` | VARCHAR2(64 bytes) | N |  |
| `DEVICE_ID` | VARCHAR2(100 bytes) | N |  |
| `CAPTURE_ID` | VARCHAR2(100 bytes) | N |  |
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `STORE_ADDR` | VARCHAR2(255 bytes) | N |  |
| `DEVICE_POLICY_VERSION` | NUMBER(10,0) | N |  |
| `DEVICE_CALIBRATION_REF` | VARCHAR2(100 bytes) | N |  |
| `CAPACITY_KG` | NUMBER(27,9) | N |  |
| `RESOLUTION_KG` | NUMBER(27,9) | N |  |
| `GROSS_WEIGHT_KG` | NUMBER(27,9) | N |  |
| `SAMPLE_MIN_KG` | NUMBER(27,9) | N |  |
| `SAMPLE_MAX_KG` | NUMBER(27,9) | N |  |
| `SAMPLE_COUNT` | NUMBER(3,0) | N |  |
| `SPAN_MS` | NUMBER(6,0) | N |  |
| `MEASURED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `ZERO_CHECK_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RECEIVED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RECORDED_BY` | VARCHAR2(50 bytes) | N |  |
| `SOURCE_SHA256` | VARCHAR2(64 bytes) | N |  |
| `SOURCE_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016457 | C | DEVICE_ID |  | ENABLED |
| SYS_C0016458 | C | CAPTURE_ID |  | ENABLED |
| SYS_C0016459 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0016460 | C | STORE_ADDR |  | ENABLED |
| SYS_C0016461 | C | DEVICE_POLICY_VERSION |  | ENABLED |
| SYS_C0016462 | C | DEVICE_CALIBRATION_REF |  | ENABLED |
| SYS_C0016463 | C | CAPACITY_KG |  | ENABLED |
| SYS_C0016464 | C | RESOLUTION_KG |  | ENABLED |
| SYS_C0016465 | C | GROSS_WEIGHT_KG |  | ENABLED |
| SYS_C0016466 | C | SAMPLE_MIN_KG |  | ENABLED |
| SYS_C0016467 | C | SAMPLE_MAX_KG |  | ENABLED |
| SYS_C0016468 | C | SAMPLE_COUNT |  | ENABLED |
| SYS_C0016469 | C | SPAN_MS |  | ENABLED |
| SYS_C0016470 | C | MEASURED_AT |  | ENABLED |
| SYS_C0016471 | C | ZERO_CHECK_AT |  | ENABLED |
| SYS_C0016472 | C | RECEIVED_AT |  | ENABLED |
| SYS_C0016473 | C | RECORDED_BY |  | ENABLED |
| SYS_C0016474 | C | SOURCE_SHA256 |  | ENABLED |
| SYS_C0016475 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0016476 | C | RESULT_JSON |  | ENABLED |
| SYS_C0016477 | C | GROSS_WEIGHT_KG |  | ENABLED |
| SYS_C0016478 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0016479 | C | RESULT_JSON |  | ENABLED |
| SYS_C0016480 | P | CAPTURE_KEY |  | ENABLED |
| SYS_C0016481 | U | DEVICE_ID, CAPTURE_ID |  | ENABLED |
| SYS_C0016482 | R | DEVICE_ID | RRL_STORE_SCALE_DEVICE (DEVICE_ID) | ENABLED |
| SYS_C0016483 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| SYS_C0016484 | R | STORE_ADDR | RRL_STORE_RECEIPT_POLICY (STORE_ADDR) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_WEIGHT_CORE](../programs/RRL_STOCK_STORE_WEIGHT_CORE.md), [RRL_STORE_SCALE_API](../programs/RRL_STORE_SCALE_API.md), [RRL_STORE_SCALE_CAPTURE_GUARD](../programs/RRL_STORE_SCALE_CAPTURE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_SCALE_CAPTURE` в файле соответствующего типа.
