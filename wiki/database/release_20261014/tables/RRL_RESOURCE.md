# RRL_RESOURCE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Персонал и техника.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `RESOURCE_ID` | NUMBER | N |  |
| `RESOURCE_CODE` | VARCHAR2(60 bytes) | N |  |
| `RESOURCE_NAME` | VARCHAR2(160 bytes) | N |  |
| `RESOURCE_CLASS` | VARCHAR2(40 bytes) | N |  |
| `RESOURCE_TYPE` | VARCHAR2(40 bytes) | N |  |
| `EQUIPMENT_ID` | NUMBER | Y |  |
| `USER_ID` | VARCHAR2(100 bytes) | Y |  |
| `TEAM_CODE` | VARCHAR2(60 bytes) | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `ZONE_CODE` | VARCHAR2(60 bytes) | Y |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_RESOURCE_CHK1 | C | RESOURCE_CLASS |  | ENABLED |
| RRL_RESOURCE_CHK2 | C | STATUS |  | ENABLED |
| RRL_RESOURCE_CHK3 | C | ACTIVE |  | ENABLED |
| RRL_RESOURCE_FK1 | R | RESOURCE_TYPE | RRL_RESOURCE_TYPE (RESOURCE_TYPE) | ENABLED |
| RRL_RESOURCE_FK2 | R | EQUIPMENT_ID | RRL_RESOURCE_EQUIPMENT (EQUIPMENT_ID) | ENABLED |
| RRL_RESOURCE_PK | P | RESOURCE_ID |  | ENABLED |
| RRL_RESOURCE_U1 | U | RESOURCE_CODE |  | ENABLED |
| SYS_C0014837 | C | RESOURCE_ID |  | ENABLED |
| SYS_C0014838 | C | RESOURCE_CODE |  | ENABLED |
| SYS_C0014839 | C | RESOURCE_NAME |  | ENABLED |
| SYS_C0014840 | C | RESOURCE_CLASS |  | ENABLED |
| SYS_C0014841 | C | RESOURCE_TYPE |  | ENABLED |
| SYS_C0014842 | C | STATUS |  | ENABLED |
| SYS_C0014843 | C | ACTIVE |  | ENABLED |
| SYS_C0014844 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_RESOURCE_POLICY](../programs/RRL_CASE_RESOURCE_POLICY.md), [RRL_TASK_RESOURCE_POLICY](../programs/RRL_TASK_RESOURCE_POLICY.md), [RRL_WORKLOAD_CONFIG_API](../programs/RRL_WORKLOAD_CONFIG_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RESOURCE` в файле соответствующего типа.
