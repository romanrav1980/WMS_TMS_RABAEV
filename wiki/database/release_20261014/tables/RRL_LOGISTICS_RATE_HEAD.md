# RRL_LOGISTICS_RATE_HEAD

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `RATE_KEY` | VARCHAR2(64 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `COST_CODE` | VARCHAR2(40 bytes) | N |  |
| `CURRENCY` | VARCHAR2(3 bytes) | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016992 | C | WARE_ID |  | ENABLED |
| SYS_C0016993 | C | COST_CODE |  | ENABLED |
| SYS_C0016994 | C | CURRENCY |  | ENABLED |
| SYS_C0016995 | C | VERSION_NO |  | ENABLED |
| SYS_C0016996 | C | COST_CODE |  | ENABLED |
| SYS_C0016997 | C | CURRENCY |  | ENABLED |
| SYS_C0016998 | C | VERSION_NO |  | ENABLED |
| SYS_C0016999 | P | RATE_KEY |  | ENABLED |
| SYS_C0017000 | U | WARE_ID, COST_CODE, CURRENCY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOG_COST_LINE_GUARD](../programs/RRL_LOG_COST_LINE_GUARD.md), [RRL_LOG_RATE_HEAD_GUARD](../programs/RRL_LOG_RATE_HEAD_GUARD.md), [RRL_LOG_RATE_HISTORY_GUARD](../programs/RRL_LOG_RATE_HISTORY_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_LOGISTICS_RATE_HEAD` в файле соответствующего типа.
