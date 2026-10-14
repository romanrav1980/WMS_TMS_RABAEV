# RRL_RESOURCE_TASK_QUAL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Персонал и техника.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `RESOURCE_ID` | NUMBER | N |  |
| `TASK_TYPE` | VARCHAR2(40 bytes) | N |  |
| `VALID_FROM` | TIMESTAMP(6) | N |  |
| `VALID_UNTIL` | TIMESTAMP(6) | Y |  |
| `ACTIVE` | NUMBER | N |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `UPDATED_AT` | TIMESTAMP(6) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_RESOURCE_TASK_QUAL_CK | C | VALID_UNTIL, VALID_FROM, ACTIVE |  | ENABLED |
| RRL_RESOURCE_TASK_QUAL_FK | R | RESOURCE_ID | RRL_RESOURCE (RESOURCE_ID) | ENABLED |
| RRL_RESOURCE_TASK_QUAL_PK | P | RESOURCE_ID, TASK_TYPE |  | ENABLED |
| SYS_C0016206 | C | RESOURCE_ID |  | ENABLED |
| SYS_C0016207 | C | TASK_TYPE |  | ENABLED |
| SYS_C0016208 | C | VALID_FROM |  | ENABLED |
| SYS_C0016209 | C | ACTIVE |  | ENABLED |
| SYS_C0016210 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_RESOURCE_POLICY](../programs/RRL_CASE_RESOURCE_POLICY.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_TASK_RESOURCE_POLICY](../programs/RRL_TASK_RESOURCE_POLICY.md), [RRL_WORKLOAD_CONFIG_API](../programs/RRL_WORKLOAD_CONFIG_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RESOURCE_TASK_QUAL` в файле соответствующего типа.
