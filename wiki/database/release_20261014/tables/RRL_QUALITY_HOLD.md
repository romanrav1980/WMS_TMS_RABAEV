# RRL_QUALITY_HOLD

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Контроль качества.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `QUALITY_HOLD_ID` | NUMBER | N |  |
| `ENTITY_TYPE` | VARCHAR2(50 bytes) | N |  |
| `ENTITY_ID` | VARCHAR2(100 bytes) | N |  |
| `HOLD_STATUS` | VARCHAR2(30 bytes) | N |  |
| `REASON_CODE` | VARCHAR2(50 bytes) | Y |  |
| `REASON_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `RELEASED_AT` | DATE | Y |  |
| `RELEASED_BY` | VARCHAR2(50 bytes) | Y |  |
| `RELEASE_REASON` | VARCHAR2(1000 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_QUALITY_HOLD_CHK1 | C | HOLD_STATUS |  | ENABLED |
| RRL_QUALITY_HOLD_PK | P | QUALITY_HOLD_ID |  | ENABLED |
| SYS_C0014173 | C | QUALITY_HOLD_ID |  | ENABLED |
| SYS_C0014174 | C | ENTITY_TYPE |  | ENABLED |
| SYS_C0014175 | C | ENTITY_ID |  | ENABLED |
| SYS_C0014176 | C | HOLD_STATUS |  | ENABLED |
| SYS_C0014177 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TRACEABILITY_API](../programs/RRL_TRACEABILITY_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_QUALITY_HOLD` в файле соответствующего типа.
