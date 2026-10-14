# RRL_REVISION_ROW

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `REVISION_ID` | NUMBER | N |  |
| `CELL` | VARCHAR2(50 bytes) | N |  |
| `REMARK1` | VARCHAR2(1024 bytes) | Y |  |
| `COUNT1` | NUMBER | Y |  |
| `REV_DATE` | DATE | Y |  |
| `COUNT_KOR` | NUMBER | Y |  |
| `ARTICUL1` | VARCHAR2(50 bytes) | Y |  |
| `NUM_OF_PALL` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_REVISION_ROW_PK | P | ID |  | ENABLED |
| SYS_C0013502 | C | ID |  | ENABLED |
| SYS_C0013503 | C | REVISION_ID |  | ENABLED |
| SYS_C0013504 | C | CELL |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[REVIZION](../programs/REVIZION.md), [REVIZION_SP_OLD](../programs/REVIZION_SP_OLD.md), [RRL_REVISION_ROW_TRG](../programs/RRL_REVISION_ROW_TRG.md), [RRL_STOCK_INVENTORY_CMD](../programs/RRL_STOCK_INVENTORY_CMD.md), [RRL_STOCK_REVISION_ENTRY](../programs/RRL_STOCK_REVISION_ENTRY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_REVISION_ROW` в файле соответствующего типа.
