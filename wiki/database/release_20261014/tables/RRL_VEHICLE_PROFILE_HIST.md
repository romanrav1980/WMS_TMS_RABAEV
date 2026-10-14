# RRL_VEHICLE_PROFILE_HIST

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортные средства.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `VEHICLE_ID` | NUMBER | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `VEHICLE_SIZE_CLASS` | VARCHAR2(40 bytes) | N |  |
| `CARGO_LENGTH_MM` | NUMBER(7,0) | N |  |
| `CARGO_WIDTH_MM` | NUMBER(7,0) | N |  |
| `CARGO_HEIGHT_MM` | NUMBER(7,0) | N |  |
| `SOURCE_JSON` | CLOB | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `OUTER_HEIGHT_MM` | NUMBER(7,0) | Y |  |
| `OUTER_LENGTH_MM` | NUMBER(7,0) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_VEH_OUTER_HEIGHT_CK | C | OUTER_HEIGHT_MM, CARGO_HEIGHT_MM |  | ENABLED |
| RRL_VEH_OUTER_LENGTH_CK | C | CARGO_LENGTH_MM, OUTER_LENGTH_MM |  | ENABLED |
| SYS_C0018685 | C | VEHICLE_ID |  | ENABLED |
| SYS_C0018686 | C | VERSION_NO |  | ENABLED |
| SYS_C0018687 | C | OPERATION_ID |  | ENABLED |
| SYS_C0018688 | C | ACTOR |  | ENABLED |
| SYS_C0018689 | C | VEHICLE_SIZE_CLASS |  | ENABLED |
| SYS_C0018690 | C | CARGO_LENGTH_MM |  | ENABLED |
| SYS_C0018691 | C | CARGO_WIDTH_MM |  | ENABLED |
| SYS_C0018692 | C | CARGO_HEIGHT_MM |  | ENABLED |
| SYS_C0018693 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018694 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018695 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018696 | C | CREATED_AT |  | ENABLED |
| SYS_C0018697 | C | VERSION_NO |  | ENABLED |
| SYS_C0018698 | C | CARGO_LENGTH_MM |  | ENABLED |
| SYS_C0018699 | C | CARGO_WIDTH_MM |  | ENABLED |
| SYS_C0018700 | C | CARGO_HEIGHT_MM |  | ENABLED |
| SYS_C0018701 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018702 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018703 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018704 | P | VEHICLE_ID, VERSION_NO |  | ENABLED |
| SYS_C0018705 | U | OPERATION_ID |  | ENABLED |
| SYS_C0018706 | R | VEHICLE_ID | RRL_VEHICLE_PROFILE_HEAD (VEHICLE_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_VEHICLE_PROFILE_API](../programs/RRL_VEHICLE_PROFILE_API.md), [RRL_VEH_PROFILE_HIST_GUARD](../programs/RRL_VEH_PROFILE_HIST_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_VEHICLE_PROFILE_HIST` в файле соответствующего типа.
