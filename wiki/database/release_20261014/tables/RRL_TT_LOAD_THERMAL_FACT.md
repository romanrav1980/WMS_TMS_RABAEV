# RRL_TT_LOAD_THERMAL_FACT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `VEHICLE_ID` | NUMBER | N |  |
| `PROFILE_VERSION` | NUMBER(19,0) | N |  |
| `OBSERVED_C` | NUMBER(9,3) | N |  |
| `OBSERVATION_REFERENCE` | NVARCHAR2(200 bytes) | N |  |
| `OBSERVATION_BASIS` | VARCHAR2(24 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `RECORDED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `SENSOR_VERIFIED` | NUMBER(1,0) | N |  |
| `CONFIRMATION_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018791 | C | VEHICLE_ID |  | ENABLED |
| SYS_C0018792 | C | PROFILE_VERSION |  | ENABLED |
| SYS_C0018793 | C | OBSERVED_C |  | ENABLED |
| SYS_C0018794 | C | OBSERVATION_REFERENCE |  | ENABLED |
| SYS_C0018795 | C | OBSERVATION_BASIS |  | ENABLED |
| SYS_C0018796 | C | ACTOR |  | ENABLED |
| SYS_C0018797 | C | RECORDED_AT |  | ENABLED |
| SYS_C0018798 | C | SENSOR_VERIFIED |  | ENABLED |
| SYS_C0018799 | C | CONFIRMATION_JSON |  | ENABLED |
| SYS_C0018800 | C | OBSERVATION_BASIS |  | ENABLED |
| SYS_C0018801 | C | SENSOR_VERIFIED |  | ENABLED |
| SYS_C0018802 | C | CONFIRMATION_JSON |  | ENABLED |
| SYS_C0018803 | P | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018804 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| SYS_C0018805 | R | VEHICLE_ID, PROFILE_VERSION | RRL_VEHICLE_PROFILE_HIST (VEHICLE_ID, VERSION_NO) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOAD_THERMAL_FACT_GUARD](../programs/RRL_LOAD_THERMAL_FACT_GUARD.md), [RRL_STOCK_LOAD_THERMAL](../programs/RRL_STOCK_LOAD_THERMAL.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_LOAD_THERMAL_FACT` в файле соответствующего типа.
