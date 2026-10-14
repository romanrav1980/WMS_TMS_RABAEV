# RRL_TT_LOAD_FLOOR_FACT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `VEHICLE_ID` | NUMBER | N |  |
| `PROFILE_VERSION` | NUMBER | N |  |
| `PALLET_TYPE_ID` | NUMBER | N |  |
| `TYPE_ORIGIN` | VARCHAR2(24 bytes) | N |  |
| `SOURCE_REFERENCE` | VARCHAR2(200 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `RECORDED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `CONFIRMATION_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_LOAD_FLOOR_JSON_CK | C | CONFIRMATION_JSON |  | ENABLED |
| RRL_LOAD_FLOOR_LOAD_FK | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| RRL_LOAD_FLOOR_ORIGIN_CK | C | TYPE_ORIGIN |  | ENABLED |
| RRL_LOAD_FLOOR_PROFILE_FK | R | VEHICLE_ID, PROFILE_VERSION | RRL_VEHICLE_PROFILE_HIST (VEHICLE_ID, VERSION_NO) | ENABLED |
| RRL_LOAD_FLOOR_TYPE_FK | R | PALLET_TYPE_ID | RRL_PALLET_TYPE (PALLET_TYPE_ID) | ENABLED |
| SYS_C0018806 | C | VEHICLE_ID |  | ENABLED |
| SYS_C0018807 | C | PROFILE_VERSION |  | ENABLED |
| SYS_C0018808 | C | PALLET_TYPE_ID |  | ENABLED |
| SYS_C0018809 | C | TYPE_ORIGIN |  | ENABLED |
| SYS_C0018810 | C | SOURCE_REFERENCE |  | ENABLED |
| SYS_C0018811 | C | ACTOR |  | ENABLED |
| SYS_C0018812 | C | RECORDED_AT |  | ENABLED |
| SYS_C0018813 | C | CONFIRMATION_JSON |  | ENABLED |
| SYS_C0018816 | P | LOAD_OPERATION_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOAD_FLOOR_FACT_GUARD](../programs/RRL_LOAD_FLOOR_FACT_GUARD.md), [RRL_STOCK_LOAD_FLOOR](../programs/RRL_STOCK_LOAD_FLOOR.md), [RRL_STORE_UNLOAD_CORE](../programs/RRL_STORE_UNLOAD_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_LOAD_FLOOR_FACT` в файле соответствующего типа.
