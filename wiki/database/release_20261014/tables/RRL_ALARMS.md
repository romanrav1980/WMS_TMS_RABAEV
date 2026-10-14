# RRL_ALARMS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `TYPE1` | VARCHAR2(50 bytes) | Y |  |
| `ALARM_TIME` | DATE | Y |  |
| `USER_ID` | VARCHAR2(50 bytes) | Y |  |
| `COMMENT1` | VARCHAR2(1024 bytes) | Y |  |
| `SEND_BEGIN` | NUMBER | Y |  |
| `SEND_ENDED` | NUMBER | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `ARTICUL` | VARCHAR2(50 bytes) | Y |  |
| `CELL` | VARCHAR2(50 bytes) | Y |  |
| `PALLET_ID` | VARCHAR2(50 bytes) | Y |  |
| `TIME_SEND_ENDED` | DATE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_ALARMS_PK | P | ID |  | ENABLED |
| SYS_C0013422 | C | ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ALARMS` в файле соответствующего типа.
