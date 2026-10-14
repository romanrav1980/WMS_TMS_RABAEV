# RRL_INVENTARIZ_LINES

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID_OF_INVENT` | NUMBER | N |  |
| `ID_LINE` | NUMBER | Y |  |
| `CELL` | VARCHAR2(200 bytes) | N |  |
| `PALLET_ID` | VARCHAR2(200 bytes) | N |  |
| `COUNT1` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| BIN$UX1xZvUJS6/gYw8CAAo/Yg==$0 | C | ID_OF_INVENT |  | ENABLED |
| BIN$UX1xZvUKS6/gYw8CAAo/Yg==$0 | C | CELL |  | ENABLED |
| BIN$UX1xZvULS6/gYw8CAAo/Yg==$0 | C | PALLET_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INVENTARIZ_LINES` в файле соответствующего типа.
