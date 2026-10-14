# RRL_BOM_AUDIT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `BOM_AUDIT_ID` | NUMBER | N |  |
| `BOM_ID` | NUMBER | Y |  |
| `ACTION_TYPE` | VARCHAR2(50 bytes) | N |  |
| `OLD_STATUS` | VARCHAR2(30 bytes) | Y |  |
| `NEW_STATUS` | VARCHAR2(30 bytes) | Y |  |
| `MESSAGE` | VARCHAR2(1000 bytes) | Y |  |
| `PAYLOAD_JSON` | CLOB | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_BOM_AUDIT_FK1 | R | BOM_ID | RRL_BOM (BOM_ID) | ENABLED |
| RRL_BOM_AUDIT_PK | P | BOM_AUDIT_ID |  | ENABLED |
| SYS_C0014217 | C | BOM_AUDIT_ID |  | ENABLED |
| SYS_C0014218 | C | ACTION_TYPE |  | ENABLED |
| SYS_C0014219 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_BOM_API](../programs/RRL_BOM_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_BOM_AUDIT` в файле соответствующего типа.
