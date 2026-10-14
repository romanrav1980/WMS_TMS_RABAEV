# RRL_OTHOD_NAKLAD

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | Y |  |
| `NAKLADNAME` | VARCHAR2(200 bytes) | N |  |
| `MAG_NO` | VARCHAR2(200 bytes) | N |  |
| `NAKLADDATE` | DATE | N |  |
| `CREATIONDATE` | DATE | N |  |
| `PLANNEDDELIVERYDATE` | DATE | Y |  |
| `CONDITION` | NUMBER | Y |  |
| `SUMM` | NUMBER | Y |  |
| `WARE_ID` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| BIN$UX1xZvT+S6/gYw8CAAo/Yg==$0 | C | MAG_NO |  | ENABLED |
| BIN$UX1xZvT/S6/gYw8CAAo/Yg==$0 | C | NAKLADDATE |  | ENABLED |
| BIN$UX1xZvT9S6/gYw8CAAo/Yg==$0 | C | NAKLADNAME |  | ENABLED |
| BIN$UX1xZvUAS6/gYw8CAAo/Yg==$0 | C | CREATIONDATE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[ADD_RRL_OTHOD_NAKLAD](../programs/ADD_RRL_OTHOD_NAKLAD.md), [ADD_RRL_OTHOD_NAKLAD_ROWS](../programs/ADD_RRL_OTHOD_NAKLAD_ROWS.md), [RRL_CLEAR_OTHOD_NAKLAD2](../programs/RRL_CLEAR_OTHOD_NAKLAD2.md), [RRL_CLOSE_OTHOD_NAKLAD_SP_OLD](../programs/RRL_CLOSE_OTHOD_NAKLAD_SP_OLD.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_OTHOD_NAKLAD` в файле соответствующего типа.
