# RRL_SHIPMENT_PART

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SHIPMENT_PART_ID` | NUMBER | N |  |
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `PICK_PLAN_ID` | NUMBER | Y |  |
| `ROUTE_ID` | NUMBER | Y |  |
| `DOCK_ID` | NUMBER | Y |  |
| `VEHICLE_TYPE_ID` | NUMBER | Y |  |
| `PART_NO` | NUMBER | N |  |
| `PLANNED_PALLET_COUNT` | NUMBER | Y |  |
| `PLANNED_WEIGHT` | NUMBER | Y |  |
| `PLANNED_VOLUME` | NUMBER | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SHIPMENT_PART_CHK1 | C | STATUS |  | ENABLED |
| RRL_SHIPMENT_PART_CHK2 | C | PLANNED_PALLET_COUNT |  | ENABLED |
| RRL_SHIPMENT_PART_FK1 | R | CUSTOMER_ORDER_ID | RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID) | ENABLED |
| RRL_SHIPMENT_PART_FK2 | R | VEHICLE_TYPE_ID | RRL_VEHICLE_TYPE (VEHICLE_TYPE_ID) | ENABLED |
| RRL_SHIPMENT_PART_PK | P | SHIPMENT_PART_ID |  | ENABLED |
| RRL_SHIPMENT_PART_U1 | U | CUSTOMER_ORDER_ID, PART_NO |  | ENABLED |
| SYS_C0014388 | C | SHIPMENT_PART_ID |  | ENABLED |
| SYS_C0014389 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0014390 | C | PART_NO |  | ENABLED |
| SYS_C0014391 | C | STATUS |  | ENABLED |
| SYS_C0014392 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CUSTOMER_RULE_API](../programs/RRL_CUSTOMER_RULE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SHIPMENT_PART` в файле соответствующего типа.
