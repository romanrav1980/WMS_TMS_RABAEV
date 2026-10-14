# RRL_PALLET_FLOOR_TYPE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `PALLET_TYPE_ID` | NUMBER | N |  |
| `TYPE_VERSION` | NUMBER | N |  |
| `LAST_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `DECLARED_WARE_ID` | NUMBER | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PAL_FLOOR_OP_FK | R | LAST_OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| RRL_PAL_FLOOR_TYPE_FK | R | PALLET_TYPE_ID | RRL_PALLET_TYPE (PALLET_TYPE_ID) | ENABLED |
| RRL_PAL_FLOOR_UID_FK | R | UID_PALLET | RRL_PALLETS (UID_PALLET) | ENABLED |
| RRL_PAL_FLOOR_VERSION_CK | C | TYPE_VERSION |  | ENABLED |
| SYS_C0018820 | C | PALLET_TYPE_ID |  | ENABLED |
| SYS_C0018821 | C | TYPE_VERSION |  | ENABLED |
| SYS_C0018822 | C | LAST_OPERATION_ID |  | ENABLED |
| SYS_C0018823 | C | DECLARED_WARE_ID |  | ENABLED |
| SYS_C0018825 | P | UID_PALLET |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PALLET_FLOOR_GUARD](../programs/RRL_PALLET_FLOOR_GUARD.md), [RRL_PALLET_FLOOR_READ](../programs/RRL_PALLET_FLOOR_READ.md), [RRL_STOCK_LOAD_FLOOR](../programs/RRL_STOCK_LOAD_FLOOR.md), [RRL_STOCK_PALLET_TYPE_CMD](../programs/RRL_STOCK_PALLET_TYPE_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PALLET_FLOOR_TYPE` в файле соответствующего типа.
