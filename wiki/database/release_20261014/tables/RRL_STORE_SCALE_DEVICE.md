# RRL_STORE_SCALE_DEVICE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `DEVICE_ID` | VARCHAR2(100 bytes) | N |  |
| `STORE_ADDR` | VARCHAR2(255 bytes) | N |  |
| `SENDER_ID` | NVARCHAR2(100 bytes) | N |  |
| `POLICY_VERSION` | NUMBER(10,0) | N |  |
| `ACTIVE_FLAG` | NUMBER(1,0) | N |  |
| `CAPACITY_KG` | NUMBER(27,9) | N |  |
| `RESOLUTION_KG` | NUMBER(27,9) | N |  |
| `CALIBRATION_REF` | VARCHAR2(100 bytes) | N |  |
| `CALIBRATED_UNTIL` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `CHANGED_BY` | VARCHAR2(50 bytes) | N |  |
| `CHANGED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016442 | C | STORE_ADDR |  | ENABLED |
| SYS_C0016443 | C | SENDER_ID |  | ENABLED |
| SYS_C0016444 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0016445 | C | ACTIVE_FLAG |  | ENABLED |
| SYS_C0016446 | C | CAPACITY_KG |  | ENABLED |
| SYS_C0016447 | C | RESOLUTION_KG |  | ENABLED |
| SYS_C0016448 | C | CALIBRATION_REF |  | ENABLED |
| SYS_C0016449 | C | CALIBRATED_UNTIL |  | ENABLED |
| SYS_C0016450 | C | CHANGED_BY |  | ENABLED |
| SYS_C0016451 | C | CHANGED_AT |  | ENABLED |
| SYS_C0016452 | C | ACTIVE_FLAG |  | ENABLED |
| SYS_C0016453 | C | CAPACITY_KG |  | ENABLED |
| SYS_C0016454 | C | RESOLUTION_KG |  | ENABLED |
| SYS_C0016455 | P | DEVICE_ID |  | ENABLED |
| SYS_C0016456 | R | STORE_ADDR | RRL_STORE_RECEIPT_POLICY (STORE_ADDR) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_WEIGHT_CORE](../programs/RRL_STOCK_STORE_WEIGHT_CORE.md), [RRL_STORE_SCALE_API](../programs/RRL_STORE_SCALE_API.md), [RRL_STORE_SCALE_DEVICE_GUARD](../programs/RRL_STORE_SCALE_DEVICE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_SCALE_DEVICE` в файле соответствующего типа.
