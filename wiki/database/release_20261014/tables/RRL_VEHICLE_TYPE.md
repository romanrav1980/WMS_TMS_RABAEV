# RRL_VEHICLE_TYPE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортные средства.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `VEHICLE_TYPE_ID` | NUMBER | N |  |
| `VEHICLE_TYPE_CODE` | VARCHAR2(50 bytes) | N |  |
| `VEHICLE_TYPE_NAME` | VARCHAR2(255 bytes) | N |  |
| `MAX_PALLET_COUNT` | NUMBER | Y |  |
| `MAX_WEIGHT` | NUMBER | Y |  |
| `MAX_VOLUME` | NUMBER | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_VEHICLE_TYPE_CHK1 | C | ACTIVE |  | ENABLED |
| RRL_VEHICLE_TYPE_PK | P | VEHICLE_TYPE_ID |  | ENABLED |
| RRL_VEHICLE_TYPE_U1 | U | VEHICLE_TYPE_CODE |  | ENABLED |
| SYS_C0014365 | C | VEHICLE_TYPE_ID |  | ENABLED |
| SYS_C0014366 | C | VEHICLE_TYPE_CODE |  | ENABLED |
| SYS_C0014367 | C | VEHICLE_TYPE_NAME |  | ENABLED |
| SYS_C0014368 | C | ACTIVE |  | ENABLED |
| SYS_C0014369 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CUSTOMER_RULE_API](../programs/RRL_CUSTOMER_RULE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_VEHICLE_TYPE` в файле соответствующего типа.
