# RRL_OTHOD_NAKLAD_ROWS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | Y |  |
| `ID_NAKLAD` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(160 bytes) | N |  |
| `COUNT1` | NUMBER | N |  |
| `PRICE` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| BIN$UX1xZvT2S6/gYw8CAAo/Yg==$0 | C | ID_NAKLAD |  | ENABLED |
| BIN$UX1xZvT3S6/gYw8CAAo/Yg==$0 | C | ARTICUL |  | ENABLED |
| BIN$UX1xZvT4S6/gYw8CAAo/Yg==$0 | C | COUNT1 |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[ADD_RRL_OTHOD_NAKLAD_ROWS](../programs/ADD_RRL_OTHOD_NAKLAD_ROWS.md), [RRL_CLEAR_OTHOD_NAKLAD2](../programs/RRL_CLEAR_OTHOD_NAKLAD2.md), [RRL_CLOSE_OTHOD_NAKLAD_SP_OLD](../programs/RRL_CLOSE_OTHOD_NAKLAD_SP_OLD.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_OTHOD_NAKLAD_ROWS` в файле соответствующего типа.
