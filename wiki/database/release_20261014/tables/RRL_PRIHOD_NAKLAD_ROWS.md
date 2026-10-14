# RRL_PRIHOD_NAKLAD_ROWS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ORDID` | NUMBER | Y |  |
| `ARTICUL` | VARCHAR2(160 bytes) | Y |  |
| `EXPIRY_DATE` | DATE | Y |  |
| `ID` | NUMBER | Y |  |
| `COUNT1` | NUMBER | Y |  |
| `PRICE` | NUMBER | Y |  |
| `INVENT_CELL` | VARCHAR2(15 bytes) | Y |  |
| `KOLPAL` | NUMBER | Y |  |
| `SROK_GODNOSTI` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[ADD_RRL_PRIH_NAKLAD_ROW](../programs/ADD_RRL_PRIH_NAKLAD_ROW.md), [ADD_RRL_PRIH_NAKLAD_ROW2](../programs/ADD_RRL_PRIH_NAKLAD_ROW2.md), [DELETE_RRL_PRIH_NAKLAD_ROW](../programs/DELETE_RRL_PRIH_NAKLAD_ROW.md), [RRL_ACCEPT_ORDER](../programs/RRL_ACCEPT_ORDER.md), [RRL_ACCEPT_ORDER2_2_SP_OLD](../programs/RRL_ACCEPT_ORDER2_2_SP_OLD.md), [RRL_ACCEPT_ORDER2_3_SP_OLD](../programs/RRL_ACCEPT_ORDER2_3_SP_OLD.md), [RRL_ACCEPT_ORDER2_SP_OLD](../programs/RRL_ACCEPT_ORDER2_SP_OLD.md), [RRL_CLEAR_PRIH_NAKLAD_ROWS](../programs/RRL_CLEAR_PRIH_NAKLAD_ROWS.md), [RRL_INV_CREATE_LINE](../programs/RRL_INV_CREATE_LINE.md), [RRL_PRIHODPALLET_CHANGE_COUNT](../programs/RRL_PRIHODPALLET_CHANGE_COUNT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PRIHOD_NAKLAD_ROWS` в файле соответствующего типа.
