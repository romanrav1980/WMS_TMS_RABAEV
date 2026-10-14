# RRL_HU_PACK_CYCLE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Грузовые единицы и вложенность.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PARENT_UID` | VARCHAR2(200 bytes) | N |  |
| `START_CONTENT_VERSION` | NUMBER(19,0) | N |  |
| `START_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `STARTED_AT_INSTANT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018578 | C | PARENT_UID |  | ENABLED |
| SYS_C0018579 | C | START_CONTENT_VERSION |  | ENABLED |
| SYS_C0018580 | C | START_OPERATION_ID |  | ENABLED |
| SYS_C0018581 | C | WARE_ID |  | ENABLED |
| SYS_C0018582 | C | ACTOR |  | ENABLED |
| SYS_C0018583 | C | STARTED_AT_INSTANT |  | ENABLED |
| SYS_C0018584 | C | START_CONTENT_VERSION |  | ENABLED |
| SYS_C0018585 | P | PARENT_UID, START_CONTENT_VERSION |  | ENABLED |
| SYS_C0018586 | U | PARENT_UID, START_OPERATION_ID |  | ENABLED |
| SYS_C0018587 | R | PARENT_UID | RRL_PALLETS (UID_PALLET) | ENABLED |
| SYS_C0018588 | R | START_OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_BOX_ASSEMBLY_READ](../programs/RRL_BOX_ASSEMBLY_READ.md), [RRL_HU_PACK_CLOCK](../programs/RRL_HU_PACK_CLOCK.md), [RRL_HU_PACK_CYCLE_GUARD](../programs/RRL_HU_PACK_CYCLE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_HU_PACK_CYCLE` в файле соответствующего типа.
