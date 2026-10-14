# RRL_SUMMARY_PICK_LIST

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `CREATEDATE` | DATE | Y |  |
| `CONDITION` | NUMBER | Y |  |
| `WARE_ID` | NUMBER | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SUMMARY_PICK_LIST_PK | P | ID |  | ENABLED |
| SYS_C0013519 | C | ID |  | ENABLED |
| SYS_C0013520 | C | WARE_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[GOODS_TO_PICK](../programs/GOODS_TO_PICK.md), [RRL_SUMMARY_PICK_LIST_DELETE](../programs/RRL_SUMMARY_PICK_LIST_DELETE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SUMMARY_PICK_LIST` в файле соответствующего типа.
