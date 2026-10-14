# RRL_RAW_MATERIAL_SKU

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `IS_RAW_MATERIAL` | NUMBER(1,0) | N |  |
| `RAW_GROUP` | VARCHAR2(100 bytes) | Y |  |
| `MERCURY_REQUIRED` | NUMBER(1,0) | N |  |
| `LOT_REQUIRED` | NUMBER(1,0) | N |  |
| `EXPIRY_REQUIRED` | NUMBER(1,0) | N |  |
| `MIN_STOCK_QTY` | NUMBER | Y |  |
| `TARGET_STOCK_QTY` | NUMBER | Y |  |
| `ALLOWED_WARE_IDS` | VARCHAR2(1000 bytes) | Y |  |
| `ALLOWED_ZONE_CODES` | VARCHAR2(1000 bytes) | Y |  |
| `TECHNOLOGIST_COMMENT` | VARCHAR2(1000 bytes) | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_RAW_MATERIAL_SKU_CHK1 | C | IS_RAW_MATERIAL |  | ENABLED |
| RRL_RAW_MATERIAL_SKU_CHK2 | C | MERCURY_REQUIRED |  | ENABLED |
| RRL_RAW_MATERIAL_SKU_CHK3 | C | LOT_REQUIRED |  | ENABLED |
| RRL_RAW_MATERIAL_SKU_CHK4 | C | EXPIRY_REQUIRED |  | ENABLED |
| RRL_RAW_MATERIAL_SKU_CHK5 | C | ACTIVE |  | ENABLED |
| RRL_RAW_MATERIAL_SKU_PK | P | ARTICUL |  | ENABLED |
| SYS_C0014653 | C | ARTICUL |  | ENABLED |
| SYS_C0014654 | C | IS_RAW_MATERIAL |  | ENABLED |
| SYS_C0014655 | C | MERCURY_REQUIRED |  | ENABLED |
| SYS_C0014656 | C | LOT_REQUIRED |  | ENABLED |
| SYS_C0014657 | C | EXPIRY_REQUIRED |  | ENABLED |
| SYS_C0014658 | C | ACTIVE |  | ENABLED |
| SYS_C0014659 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RAW_MATERIAL_SKU` в файле соответствующего типа.
