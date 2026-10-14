# RRL_BILL_ORDERS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | Y |  |
| `NUM` | VARCHAR2(15 bytes) | Y |  |
| `COMPANY` | VARCHAR2(200 bytes) | Y |  |
| `DATEOFORDER` | DATE | Y |  |
| `DATEFROM` | DATE | Y |  |
| `DATETO` | DATE | Y |  |
| `CLOSED` | NUMBER | Y |  |
| `SUMM` | NUMBER | Y |  |
| `PAYED` | NUMBER | Y |  |
| `NUM_PLAT` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_ADD_TT_2_BILLINGORDER](../programs/RRL_ADD_TT_2_BILLINGORDER.md), [RRL_BILL_ADD_TTBILL](../programs/RRL_BILL_ADD_TTBILL.md), [RRL_CLOSE_BILLINGORDER](../programs/RRL_CLOSE_BILLINGORDER.md), [RRL_PAY_BILLINGORDER](../programs/RRL_PAY_BILLINGORDER.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_BILL_ORDERS` в файле соответствующего типа.
