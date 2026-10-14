# RRL_COMPL_RESERVE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(50 bytes) | Y |  |
| `PARTIONID` | VARCHAR2(250 bytes) | Y |  |
| `QTY` | NUMBER | Y |  |
| `ORDERID` | NUMBER | Y |  |
| `ORDERROWID` | NUMBER | Y |  |
| `CONDITION` | NUMBER | Y |  |
| `EXPDATE` | DATE | Y |  |
| `MOD_ID` | NUMBER | Y |  |
| `WARE_ID` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_COMPL_RESERVE_PK | P | ID |  | ENABLED |
| SYS_C0013813 | C | ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[COMPL](../programs/COMPL.md), [ORDERS](../programs/ORDERS.md), [RRL_COMPL_RESERVE_TGR](../programs/RRL_COMPL_RESERVE_TGR.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_COMPL_RESERVE` в файле соответствующего типа.
