# RRL_REVIZION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `CREATE_DATE` | DATE | N |  |
| `CONDITION` | NUMBER | Y |  |
| `USER_ID` | VARCHAR2(50 bytes) | N |  |
| `REV_NAKLAD_ID` | NUMBER | Y |  |
| `SNAPSHOT_BEFORE` | NUMBER | Y |  |
| `SNAPSHOT_AFTER` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_REVIZION_PK | P | ID |  | ENABLED |
| SYS_C0013506 | C | ID |  | ENABLED |
| SYS_C0013507 | C | WARE_ID |  | ENABLED |
| SYS_C0013508 | C | CREATE_DATE |  | ENABLED |
| SYS_C0013509 | C | USER_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[REVIZION](../programs/REVIZION.md), [REVIZION_SP_OLD](../programs/REVIZION_SP_OLD.md), [RRL_REVIZION_TRG](../programs/RRL_REVIZION_TRG.md), [RRL_STOCK_INVENTORY_BIRTH](../programs/RRL_STOCK_INVENTORY_BIRTH.md), [RRL_STOCK_INVENTORY_CMD](../programs/RRL_STOCK_INVENTORY_CMD.md), [RRL_STOCK_REVISION_ENTRY](../programs/RRL_STOCK_REVISION_ENTRY.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_TRACE_SENDER_MANIFEST_GUARD](../programs/RRL_TRACE_SENDER_MANIFEST_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_REVIZION` в файле соответствующего типа.
