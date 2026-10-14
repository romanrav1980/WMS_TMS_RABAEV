# RRL_STORE_RETURN_HANDOVER

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `TRANSPORT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PALLET_IDENTIFIER` | VARCHAR2(200 bytes) | N |  |
| `GROSS_WEIGHT_KG` | NUMBER(27,9) | N |  |
| `PHYSICAL_PLACES` | NUMBER(10,0) | N |  |
| `HANDED_BY` | NVARCHAR2(100 bytes) | N |  |
| `HANDED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016645 | C | TRANSPORT_OPERATION_ID |  | ENABLED |
| SYS_C0016646 | C | PALLET_IDENTIFIER |  | ENABLED |
| SYS_C0016647 | C | GROSS_WEIGHT_KG |  | ENABLED |
| SYS_C0016648 | C | PHYSICAL_PLACES |  | ENABLED |
| SYS_C0016649 | C | HANDED_BY |  | ENABLED |
| SYS_C0016650 | C | HANDED_AT |  | ENABLED |
| SYS_C0016651 | C | GROSS_WEIGHT_KG |  | ENABLED |
| SYS_C0016652 | C | PHYSICAL_PLACES |  | ENABLED |
| SYS_C0016653 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016654 | U | TRANSPORT_OPERATION_ID |  | ENABLED |
| SYS_C0016655 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016656 | R | TRANSPORT_OPERATION_ID | RRL_STORE_RETURN_TRANSPORT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_RETURN_CUST_CMD](../programs/RRL_STOCK_STORE_RETURN_CUST_CMD.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STORE_RETURN_HAND_GUARD](../programs/RRL_STORE_RETURN_HAND_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RETURN_HANDOVER` в файле соответствующего типа.
