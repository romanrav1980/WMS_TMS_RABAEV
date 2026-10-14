# RRL_STOCK_SETTING_AUDIT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SETTING_KEY` | VARCHAR2(100 bytes) | N |  |
| `SETTING_VERSION` | NUMBER | N |  |
| `OLD_VALUE` | VARCHAR2(100 bytes) | Y |  |
| `NEW_VALUE` | VARCHAR2(100 bytes) | N |  |
| `REASON` | VARCHAR2(1000 bytes) | N |  |
| `CHANGED_BY` | VARCHAR2(50 bytes) | N |  |
| `CHANGED_AT` | TIMESTAMP(6) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STOCK_SETTING_AUDIT_PK | P | SETTING_KEY, SETTING_VERSION |  | ENABLED |
| SYS_C0016172 | C | SETTING_KEY |  | ENABLED |
| SYS_C0016173 | C | SETTING_VERSION |  | ENABLED |
| SYS_C0016174 | C | NEW_VALUE |  | ENABLED |
| SYS_C0016175 | C | REASON |  | ENABLED |
| SYS_C0016176 | C | CHANGED_BY |  | ENABLED |
| SYS_C0016177 | C | CHANGED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_SETTING_API](../programs/RRL_STOCK_SETTING_API.md), [RRL_STOCK_SETTING_AUDIT_GUARD](../programs/RRL_STOCK_SETTING_AUDIT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_SETTING_AUDIT` в файле соответствующего типа.
