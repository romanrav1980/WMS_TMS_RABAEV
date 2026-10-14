# RRL_SAP_STORE_CALENDAR

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `CUSTOMER_STORE_MAP_ID` | NUMBER | N |  |
| `UTC_OFFSET_MINUTES` | NUMBER | N |  |
| `DELIVERY_WEEKDAYS` | VARCHAR2(20 bytes) | N |  |
| `ALLOW_SAME_DAY` | NUMBER | N |  |
| `UPDATED_AT` | TIMESTAMP(6) | N |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_STORE_CAL_CK | C | ALLOW_SAME_DAY, UTC_OFFSET_MINUTES |  | ENABLED |
| RRL_SAP_STORE_CAL_FK | R | CUSTOMER_STORE_MAP_ID | RRL_CUSTOMER_STORE_MAP (CUSTOMER_STORE_MAP_ID) | ENABLED |
| RRL_SAP_STORE_CAL_PK | P | WARE_ID, CUSTOMER_STORE_MAP_ID |  | ENABLED |
| SYS_C0016038 | C | WARE_ID |  | ENABLED |
| SYS_C0016039 | C | CUSTOMER_STORE_MAP_ID |  | ENABLED |
| SYS_C0016040 | C | UTC_OFFSET_MINUTES |  | ENABLED |
| SYS_C0016041 | C | DELIVERY_WEEKDAYS |  | ENABLED |
| SYS_C0016042 | C | ALLOW_SAME_DAY |  | ENABLED |
| SYS_C0016043 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_SAP_CAL_WRITE_GUARD](../programs/RRL_SAP_CAL_WRITE_GUARD.md), [RRL_STORE_CALENDAR_API](../programs/RRL_STORE_CALENDAR_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_STORE_CALENDAR` в файле соответствующего типа.
