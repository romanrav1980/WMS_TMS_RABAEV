# RRL_WH_SCALE_DEVICE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `DEVICE_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `POST_CELL` | VARCHAR2(60 bytes) | N |  |
| `SENDER_ID` | NVARCHAR2(100 bytes) | N |  |
| `POLICY_VERSION` | NUMBER(10,0) | N |  |
| `ACTIVE_FLAG` | NUMBER(1,0) | N |  |
| `DEVICE_MODE` | VARCHAR2(10 bytes) | N |  |
| `MEASUREMENT_BASIS` | VARCHAR2(5 bytes) | N |  |
| `CAPACITY_KG` | NUMBER(27,9) | N |  |
| `RESOLUTION_KG` | NUMBER(27,9) | N |  |
| `CALIBRATION_REF` | VARCHAR2(100 bytes) | N |  |
| `CALIBRATED_UNTIL` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `CHANGED_BY` | VARCHAR2(50 bytes) | N |  |
| `CHANGED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017571 | C | WARE_ID |  | ENABLED |
| SYS_C0017572 | C | POST_CELL |  | ENABLED |
| SYS_C0017573 | C | SENDER_ID |  | ENABLED |
| SYS_C0017574 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0017575 | C | ACTIVE_FLAG |  | ENABLED |
| SYS_C0017576 | C | DEVICE_MODE |  | ENABLED |
| SYS_C0017577 | C | MEASUREMENT_BASIS |  | ENABLED |
| SYS_C0017578 | C | CAPACITY_KG |  | ENABLED |
| SYS_C0017579 | C | RESOLUTION_KG |  | ENABLED |
| SYS_C0017580 | C | CALIBRATION_REF |  | ENABLED |
| SYS_C0017581 | C | CALIBRATED_UNTIL |  | ENABLED |
| SYS_C0017582 | C | CHANGED_BY |  | ENABLED |
| SYS_C0017583 | C | CHANGED_AT |  | ENABLED |
| SYS_C0017584 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0017585 | C | ACTIVE_FLAG |  | ENABLED |
| SYS_C0017586 | C | DEVICE_MODE |  | ENABLED |
| SYS_C0017587 | C | MEASUREMENT_BASIS |  | ENABLED |
| SYS_C0017588 | C | CAPACITY_KG |  | ENABLED |
| SYS_C0017589 | C | RESOLUTION_KG |  | ENABLED |
| SYS_C0017590 | P | DEVICE_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_SCALE_ADMISSION](../programs/RRL_CASE_SCALE_ADMISSION.md), [RRL_WH_FINAL_SCALE_ADMISSION](../programs/RRL_WH_FINAL_SCALE_ADMISSION.md), [RRL_WH_SCALE_API](../programs/RRL_WH_SCALE_API.md), [RRL_WH_SCALE_DEVICE_GUARD](../programs/RRL_WH_SCALE_DEVICE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WH_SCALE_DEVICE` в файле соответствующего типа.
