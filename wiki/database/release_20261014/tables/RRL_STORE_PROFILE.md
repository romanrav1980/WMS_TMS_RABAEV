# RRL_STORE_PROFILE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `STORE_ADDR` | VARCHAR2(255 bytes) | N |  |
| `PROFILE_VERSION` | NUMBER | N |  |
| `RECEIVING_WINDOW_MODE` | VARCHAR2(12 bytes) | N |  |
| `TIMEZONE_REGION` | VARCHAR2(64 bytes) | Y |  |
| `BACKROOM_FLAG` | NUMBER(1,0) | Y |  |
| `BACKROOM_PALLETS` | NUMBER(6,0) | Y |  |
| `BACKROOM_ROLLS` | NUMBER(6,0) | Y |  |
| `UNATTENDED_DROP_FLAG` | NUMBER(1,0) | Y |  |
| `STORAGE_TEMP_CLASS` | VARCHAR2(10 bytes) | Y |  |
| `RAMP_FLAG` | NUMBER(1,0) | Y |  |
| `RAMP_HEIGHT_MM` | NUMBER(6,0) | Y |  |
| `MAX_VEHICLE_OUTER_HEIGHT_MM` | NUMBER(6,0) | Y |  |
| `MAX_VEHICLE_OUTER_LENGTH_MM` | NUMBER(6,0) | Y |  |
| `DEFAULT_UNLOAD_METHOD` | VARCHAR2(10 bytes) | Y |  |
| `LOADER_REQUIRED` | NUMBER(1,0) | Y |  |
| `ACCESS_NOTE` | VARCHAR2(4000 bytes) | Y |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | N |  |
| `UPDATED_AT` | TIMESTAMP(6) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STORE_PROFILE_BACKROOM_CK | C | BACKROOM_FLAG, BACKROOM_PALLETS, BACKROOM_ROLLS |  | ENABLED |
| RRL_STORE_PROFILE_PK | P | STORE_ADDR |  | ENABLED |
| RRL_STORE_PROFILE_RAMP_CK | C | RAMP_HEIGHT_MM, RAMP_FLAG |  | ENABLED |
| RRL_STORE_PROFILE_TZ_CK | C | TIMEZONE_REGION, RECEIVING_WINDOW_MODE |  | ENABLED |
| SYS_C0018934 | C | STORE_ADDR |  | ENABLED |
| SYS_C0018935 | C | PROFILE_VERSION |  | ENABLED |
| SYS_C0018936 | C | RECEIVING_WINDOW_MODE |  | ENABLED |
| SYS_C0018937 | C | UPDATED_BY |  | ENABLED |
| SYS_C0018938 | C | UPDATED_AT |  | ENABLED |
| SYS_C0018939 | C | PROFILE_VERSION |  | ENABLED |
| SYS_C0018940 | C | RECEIVING_WINDOW_MODE |  | ENABLED |
| SYS_C0018941 | C | BACKROOM_FLAG |  | ENABLED |
| SYS_C0018942 | C | BACKROOM_PALLETS |  | ENABLED |
| SYS_C0018943 | C | BACKROOM_ROLLS |  | ENABLED |
| SYS_C0018944 | C | UNATTENDED_DROP_FLAG |  | ENABLED |
| SYS_C0018945 | C | STORAGE_TEMP_CLASS |  | ENABLED |
| SYS_C0018946 | C | RAMP_FLAG |  | ENABLED |
| SYS_C0018947 | C | RAMP_HEIGHT_MM |  | ENABLED |
| SYS_C0018948 | C | MAX_VEHICLE_OUTER_HEIGHT_MM |  | ENABLED |
| SYS_C0018949 | C | MAX_VEHICLE_OUTER_LENGTH_MM |  | ENABLED |
| SYS_C0018950 | C | DEFAULT_UNLOAD_METHOD |  | ENABLED |
| SYS_C0018951 | C | LOADER_REQUIRED |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STORE_ACCESS_RULES](../programs/RRL_STORE_ACCESS_RULES.md), [RRL_STORE_PROFILE_GUARD](../programs/RRL_STORE_PROFILE_GUARD.md), [RRL_STORE_RECEIVING_WINDOW_GUARD](../programs/RRL_STORE_RECEIVING_WINDOW_GUARD.md), [RRL_STORE_WINDOW_RULES](../programs/RRL_STORE_WINDOW_RULES.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_PROFILE` в файле соответствующего типа.
