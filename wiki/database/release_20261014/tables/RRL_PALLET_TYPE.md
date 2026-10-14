# RRL_PALLET_TYPE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PALLET_TYPE_ID` | NUMBER | N |  |
| `PALLET_TYPE_CODE` | VARCHAR2(50 bytes) | N |  |
| `PALLET_TYPE_NAME` | VARCHAR2(160 bytes) | N |  |
| `LOAD_UNIT_CLASS` | VARCHAR2(20 bytes) | N |  |
| `DEFAULT_VOLUME_M3` | NUMBER | Y |  |
| `DEFAULT_WEIGHT_KG` | NUMBER | Y |  |
| `LENGTH_MM` | NUMBER | Y |  |
| `WIDTH_MM` | NUMBER | Y |  |
| `HEIGHT_MM` | NUMBER | Y |  |
| `DEFAULT_MAX_CLIENT_PALLETS` | NUMBER | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `FINAL_WEIGHT_REQUIRED` | NUMBER(1,0) | N |  |
| `TYPE_VERSION` | NUMBER(10,0) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PALLET_TYPE_CHK1 | C | LOAD_UNIT_CLASS |  | ENABLED |
| RRL_PALLET_TYPE_CHK2 | C | ACTIVE |  | ENABLED |
| RRL_PALLET_TYPE_PK | P | PALLET_TYPE_ID |  | ENABLED |
| RRL_PALLET_TYPE_U1 | U | PALLET_TYPE_CODE |  | ENABLED |
| RRL_PT_FINAL_WEIGHT_CK | C | FINAL_WEIGHT_REQUIRED |  | ENABLED |
| RRL_PT_VERSION_CK | C | TYPE_VERSION |  | ENABLED |
| SYS_C0014893 | C | PALLET_TYPE_ID |  | ENABLED |
| SYS_C0014894 | C | PALLET_TYPE_CODE |  | ENABLED |
| SYS_C0014895 | C | PALLET_TYPE_NAME |  | ENABLED |
| SYS_C0014896 | C | LOAD_UNIT_CLASS |  | ENABLED |
| SYS_C0014897 | C | DEFAULT_MAX_CLIENT_PALLETS |  | ENABLED |
| SYS_C0014898 | C | ACTIVE |  | ENABLED |
| SYS_C0014899 | C | CREATED_AT |  | ENABLED |
| SYS_C0017708 | C | FINAL_WEIGHT_REQUIRED |  | ENABLED |
| SYS_C0017710 | C | TYPE_VERSION |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_PALLET_TYPE_READ](../programs/RRL_CASE_PALLET_TYPE_READ.md), [RRL_CASE_SCALE_ADMISSION](../programs/RRL_CASE_SCALE_ADMISSION.md), [RRL_CASE_SSCC_API](../programs/RRL_CASE_SSCC_API.md), [RRL_PALLET_FLOOR_READ](../programs/RRL_PALLET_FLOOR_READ.md), [RRL_PALLET_TYPE_API](../programs/RRL_PALLET_TYPE_API.md), [RRL_PALLET_TYPE_FINAL_GUARD](../programs/RRL_PALLET_TYPE_FINAL_GUARD.md), [RRL_RECIPIENT_PALLET_POLICY](../programs/RRL_RECIPIENT_PALLET_POLICY.md), [RRL_STOCK_CASE_TYPE_CMD](../programs/RRL_STOCK_CASE_TYPE_CMD.md), [RRL_STOCK_LOAD_FLOOR](../programs/RRL_STOCK_LOAD_FLOOR.md), [RRL_STOCK_PALLET_TYPE_CMD](../programs/RRL_STOCK_PALLET_TYPE_CMD.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_POLICY](../programs/RRL_STOCK_QC_POLICY.md), [RRL_STOCK_TARE_BOOK_CMD](../programs/RRL_STOCK_TARE_BOOK_CMD.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_RESOLVE](../programs/RRL_STOCK_TARE_RESOLVE.md), [RRL_VEHICLE_PROFILE_API](../programs/RRL_VEHICLE_PROFILE_API.md), [RRL_WH_FINAL_SCALE_ADMISSION](../programs/RRL_WH_FINAL_SCALE_ADMISSION.md), [RRL_WH_SCALE_API](../programs/RRL_WH_SCALE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PALLET_TYPE` в файле соответствующего типа.
