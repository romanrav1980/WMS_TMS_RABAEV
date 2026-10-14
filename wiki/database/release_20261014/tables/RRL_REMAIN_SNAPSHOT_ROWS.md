# RRL_REMAIN_SNAPSHOT_ROWS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(50 bytes) | Y |  |
| `PALLET_UID` | VARCHAR2(150 bytes) | Y |  |
| `CELL` | VARCHAR2(50 bytes) | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `SNAP_TIME` | DATE | Y |  |
| `REMAIN` | NUMBER | Y |  |
| `CONDITION` | NUMBER | Y |  |
| `SNAP_SHOT_ID` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_REMAIN_SNAPSHOT_ROWS_I1 | P | ID |  | ENABLED |
| SYS_C0013803 | C | ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[REMAINS](../programs/REMAINS.md), [REVIZION](../programs/REVIZION.md), [REVIZION_SP_OLD](../programs/REVIZION_SP_OLD.md), [RRL_REMAIN_SNAPSHOT_ROWS_TRG](../programs/RRL_REMAIN_SNAPSHOT_ROWS_TRG.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_REMAIN_SNAPSHOT_ROWS` в файле соответствующего типа.
