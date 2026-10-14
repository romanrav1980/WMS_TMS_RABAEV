# RRL_STORE_RECEIPT_WEIGHT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `CAPTURE_KEY` | VARCHAR2(64 bytes) | N |  |
| `SHIPPING_GROSS_KG` | NUMBER(27,9) | N |  |
| `OBSERVED_GROSS_KG` | NUMBER(27,9) | N |  |
| `TOLERANCE_KG` | NUMBER(28,10) | N |  |
| `DELTA_KG` | NUMBER(27,9) | N |  |
| `IN_TOLERANCE` | NUMBER(1,0) | N |  |
| `ACT_CONFIRMED` | NUMBER(1,0) | N |  |
| `PHOTOS_JSON` | CLOB | N |  |
| `RECORDED_BY` | VARCHAR2(50 bytes) | N |  |
| `RECORDED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016499 | C | CAPTURE_KEY |  | ENABLED |
| SYS_C0016500 | C | SHIPPING_GROSS_KG |  | ENABLED |
| SYS_C0016501 | C | OBSERVED_GROSS_KG |  | ENABLED |
| SYS_C0016502 | C | TOLERANCE_KG |  | ENABLED |
| SYS_C0016503 | C | DELTA_KG |  | ENABLED |
| SYS_C0016504 | C | IN_TOLERANCE |  | ENABLED |
| SYS_C0016505 | C | ACT_CONFIRMED |  | ENABLED |
| SYS_C0016506 | C | PHOTOS_JSON |  | ENABLED |
| SYS_C0016507 | C | RECORDED_BY |  | ENABLED |
| SYS_C0016508 | C | RECORDED_AT |  | ENABLED |
| SYS_C0016509 | C | TOLERANCE_KG |  | ENABLED |
| SYS_C0016510 | C | IN_TOLERANCE |  | ENABLED |
| SYS_C0016511 | C | ACT_CONFIRMED |  | ENABLED |
| SYS_C0016512 | C | PHOTOS_JSON |  | ENABLED |
| SYS_C0016513 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016514 | R | OPERATION_ID | RRL_STORE_RECEIPT_FACT (OPERATION_ID) | ENABLED |
| SYS_C0016515 | R | CAPTURE_KEY | RRL_STORE_SCALE_CAPTURE (CAPTURE_KEY) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_WEIGHT_CORE](../programs/RRL_STOCK_STORE_WEIGHT_CORE.md), [RRL_STORE_RECEIPT_WEIGHT_GUARD](../programs/RRL_STORE_RECEIPT_WEIGHT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RECEIPT_WEIGHT` в файле соответствующего типа.
