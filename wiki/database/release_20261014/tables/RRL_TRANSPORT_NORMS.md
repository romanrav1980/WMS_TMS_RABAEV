# RRL_TRANSPORT_NORMS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER(10,0) | N |  |
| `OPERATION_CODE` | VARCHAR2(30 bytes) | N |  |
| `DURATION_MIN` | NUMBER(6,2) | N |  |
| `PER_UNIT` | NUMBER(1,0) | N |  |
| `COMMENT_TXT` | VARCHAR2(200 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| PK_RRL_TRANSPORT_NORMS | P | ID |  | ENABLED |
| SYS_C0015498 | C | ID |  | ENABLED |
| SYS_C0015499 | C | OPERATION_CODE |  | ENABLED |
| SYS_C0015500 | C | DURATION_MIN |  | ENABLED |
| SYS_C0015501 | C | PER_UNIT |  | ENABLED |
| UQ_RRL_TN_CODE | U | OPERATION_CODE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TT_OPERATION_PLAN_API](../programs/RRL_TT_OPERATION_PLAN_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_NORMS` в файле соответствующего типа.
