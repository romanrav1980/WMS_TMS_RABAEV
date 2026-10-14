# RRL_PICK_WAVE_SETTING

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WAVE_SETTING_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | Y |  |
| `SETTING_CODE` | VARCHAR2(50 bytes) | N |  |
| `SETTING_NAME` | VARCHAR2(255 bytes) | Y |  |
| `MAX_CUSTOMERS` | NUMBER | N |  |
| `DEFAULT_ROUTE_ID` | NUMBER | Y |  |
| `DEFAULT_DOCK_ID` | NUMBER | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `COMMENT_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_WAVE_SETTING_CHK1 | C | ACTIVE |  | ENABLED |
| RRL_PICK_WAVE_SETTING_PK | P | WAVE_SETTING_ID |  | ENABLED |
| SYS_C0014527 | C | WAVE_SETTING_ID |  | ENABLED |
| SYS_C0014528 | C | SETTING_CODE |  | ENABLED |
| SYS_C0014529 | C | MAX_CUSTOMERS |  | ENABLED |
| SYS_C0014530 | C | ACTIVE |  | ENABLED |
| SYS_C0014531 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_WAVE_SETTING` в файле соответствующего типа.
