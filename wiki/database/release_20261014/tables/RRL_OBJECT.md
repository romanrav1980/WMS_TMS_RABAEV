# RRL_OBJECT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OBJECT_NAME` | VARCHAR2(255 bytes) | N |  |
| `BUSINESS_FIELD` | VARCHAR2(255 bytes) | Y |  |
| `PARENT_OBJECT` | VARCHAR2(255 bytes) | Y |  |
| `COMMENT1` | VARCHAR2(1024 bytes) | Y |  |
| `TYPE1` | VARCHAR2(50 bytes) | Y |  |
| `ARTICLE1` | VARCHAR2(255 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_OBJECT_PK | P | OBJECT_NAME |  | ENABLED |
| SYS_C0013787 | C | OBJECT_NAME |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[HELP](../programs/HELP.md), [RRL_OBJECT_TRG](../programs/RRL_OBJECT_TRG.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_OBJECT` в файле соответствующего типа.
