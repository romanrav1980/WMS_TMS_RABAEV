# ORDER_MOV_HIST

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `ORDER_UID` | NUMBER | N |  |
| `ZONE` | NVARCHAR2(30 bytes) | Y |  |
| `RUSER` | NVARCHAR2(30 bytes) | N |  |
| `TIME_STAMP` | DATE | Y |  |
| `LAST_FLAG` | NUMBER | Y |  |
| `USSCC` | VARCHAR2(200 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| BIN$UX1xZvUiS6/gYw8CAAo/Yg==$0 | C | ID |  | ENABLED |
| BIN$UX1xZvUjS6/gYw8CAAo/Yg==$0 | C | ORDER_UID |  | ENABLED |
| BIN$UX1xZvUkS6/gYw8CAAo/Yg==$0 | C | RUSER |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[BIN$UX1xZvUmS6/gYw8CAAo/Yg==$0](../programs/BIN_UX1xZvUmS6_gYw8CAAo_Yg___0.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `ORDER_MOV_HIST` в файле соответствующего типа.
