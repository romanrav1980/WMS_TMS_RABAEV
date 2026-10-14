# RRL_TT_VEHICLE_SOURCE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TT_ID` | NUMBER | N |  |
| `DEPARTURE_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `VEHICLE_ID` | NUMBER | N |  |
| `PROFILE_VERSION` | NUMBER(19,0) | Y |  |
| `SOURCE_STATE` | VARCHAR2(24 bytes) | N |  |
| `SOURCE_JSON` | CLOB | N |  |
| `CAPTURED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018707 | C | DEPARTURE_OPERATION_ID |  | ENABLED |
| SYS_C0018708 | C | VEHICLE_ID |  | ENABLED |
| SYS_C0018709 | C | SOURCE_STATE |  | ENABLED |
| SYS_C0018710 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018711 | C | CAPTURED_AT |  | ENABLED |
| SYS_C0018712 | C | SOURCE_STATE |  | ENABLED |
| SYS_C0018713 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018714 | P | TT_ID |  | ENABLED |
| SYS_C0018715 | U | DEPARTURE_OPERATION_ID |  | ENABLED |
| SYS_C0018716 | R | TT_ID | RRL_TRANSPORT_TASK (ID) | ENABLED |
| SYS_C0018717 | R | DEPARTURE_OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0018718 | R | VEHICLE_ID | RRL_TR_VEHICLE (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md), [RRL_TT_VEH_SOURCE_GUARD](../programs/RRL_TT_VEH_SOURCE_GUARD.md), [RRL_VEH_DEPART_SOURCE](../programs/RRL_VEH_DEPART_SOURCE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_VEHICLE_SOURCE` в файле соответствующего типа.
