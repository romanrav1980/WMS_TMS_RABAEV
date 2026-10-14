# RRL_CROSS_DOCKING_ZONES

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `CELL` | VARCHAR2(50 bytes) | Y |  |
| `ARTICUL` | VARCHAR2(50 bytes) | Y |  |
| `CONDITION_FROM_COUNT` | NUMBER | Y |  |
| `CONDITION_TO_COUNT` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CROSS_DOCKING_ZONES_PK | P | ID |  | ENABLED |
| SYS_C0013445 | C | ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CROSS_DOCKING_ZONES_TRG](../programs/RRL_CROSS_DOCKING_ZONES_TRG.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CROSS_DOCKING_ZONES` в файле соответствующего типа.
