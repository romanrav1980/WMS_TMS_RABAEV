# RRL_RESOURCE_TYPE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Персонал и техника.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `RESOURCE_TYPE` | VARCHAR2(40 bytes) | N |  |
| `RESOURCE_CLASS` | VARCHAR2(40 bytes) | N |  |
| `RESOURCE_NAME` | VARCHAR2(120 bytes) | N |  |
| `DEFAULT_TASK_TYPES` | VARCHAR2(500 bytes) | Y |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_RESOURCE_TYPE_CHK1 | C | RESOURCE_CLASS |  | ENABLED |
| RRL_RESOURCE_TYPE_CHK2 | C | ACTIVE |  | ENABLED |
| RRL_RESOURCE_TYPE_PK | P | RESOURCE_TYPE |  | ENABLED |
| SYS_C0014818 | C | RESOURCE_TYPE |  | ENABLED |
| SYS_C0014819 | C | RESOURCE_CLASS |  | ENABLED |
| SYS_C0014820 | C | RESOURCE_NAME |  | ENABLED |
| SYS_C0014821 | C | ACTIVE |  | ENABLED |
| SYS_C0014822 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_RESOURCE_POLICY](../programs/RRL_CASE_RESOURCE_POLICY.md), [RRL_TASK_RESOURCE_POLICY](../programs/RRL_TASK_RESOURCE_POLICY.md), [RRL_WORKLOAD_CONFIG_API](../programs/RRL_WORKLOAD_CONFIG_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RESOURCE_TYPE` в файле соответствующего типа.
