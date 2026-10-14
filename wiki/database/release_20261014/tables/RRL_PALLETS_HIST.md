# RRL_PALLETS_HIST

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `PUID` | VARCHAR2(50 bytes) | Y |  |
| `TYPE` | VARCHAR2(50 bytes) | Y |  |
| `DEF_PERC_BEFORE` | NUMBER | Y |  |
| `DEF_PERC_AFTRER` | NUMBER | Y |  |
| `DEF_PERC_REASON` | VARCHAR2(255 bytes) | Y |  |
| `EVENT_TIME` | DATE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PALLETS_HIST_PK | P | ID |  | ENABLED |
| SYS_C0014025 | C | ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[PRIHOD](../programs/PRIHOD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PALLETS_HIST` в файле соответствующего типа.
