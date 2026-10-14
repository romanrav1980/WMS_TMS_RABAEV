# RRL_TRANSPORT_PRICE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | Y |  |
| `PRICE_NAME` | VARCHAR2(1024 bytes) | N |  |
| `PRICE` | NUMBER(10,2) | N |  |
| `COMPANY` | VARCHAR2(255 bytes) | Y |  |
| `RANGE1` | NUMBER | Y |  |
| `PRICE_FOR_HOURS` | NUMBER | Y |  |
| `TYPE_TR` | VARCHAR2(15 bytes) | Y |  |
| `PRICE_FOLDER` | NUMBER | Y |  |
| `PRICE_FOR_ADDR` | NUMBER | Y |  |
| `NORM_HOURS` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| BIN$UX1xZvTbS6/gYw8CAAo/Yg==$0 | C | PRICE_NAME |  | ENABLED |
| BIN$UX1xZvTcS6/gYw8CAAo/Yg==$0 | C | PRICE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_GET_TT_PRICE](../programs/RRL_GET_TT_PRICE.md), [RRL_SET_TRANSPORT_PRICE](../programs/RRL_SET_TRANSPORT_PRICE.md), [RRL_TRANSPORT_NORM_API](../programs/RRL_TRANSPORT_NORM_API.md), [RRL_TT_BILL_RECALC_PRICE](../programs/RRL_TT_BILL_RECALC_PRICE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_PRICE` в файле соответствующего типа.
