# PLACE_AUDIT_ERROR_LINES

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PALLETID` | VARCHAR2(100 bytes) | N |  |
| `CONDITION` | VARCHAR2(60 bytes) | Y |  |
| `UNIT_COUNT` | NUMBER | N |  |
| `UID1` | VARCHAR2(48 bytes) | Y |  |
| `EAN` | VARCHAR2(100 bytes) | Y |  |
| `RUSER` | NVARCHAR2(100 bytes) | Y |  |
| `DATE1` | DATE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| BIN$UX1xZvUdS6/gYw8CAAo/Yg==$0 | C | PALLETID |  | ENABLED |
| BIN$UX1xZvUeS6/gYw8CAAo/Yg==$0 | C | UNIT_COUNT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `PLACE_AUDIT_ERROR_LINES` в файле соответствующего типа.
