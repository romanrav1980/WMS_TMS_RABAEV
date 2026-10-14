# RRL_RESOURCE_EQUIPMENT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Персонал и техника.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `EQUIPMENT_ID` | NUMBER | N |  |
| `EQUIPMENT_CODE` | VARCHAR2(60 bytes) | N |  |
| `EQUIPMENT_TYPE` | VARCHAR2(40 bytes) | N |  |
| `EQUIPMENT_NAME` | VARCHAR2(160 bytes) | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `HOME_ZONE_CODE` | VARCHAR2(60 bytes) | Y |  |
| `CAPACITY_CLASS` | VARCHAR2(60 bytes) | Y |  |
| `SERVICE_STATUS` | VARCHAR2(20 bytes) | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_RESOURCE_EQUIP_CHK1 | C | SERVICE_STATUS |  | ENABLED |
| RRL_RESOURCE_EQUIP_CHK2 | C | ACTIVE |  | ENABLED |
| RRL_RESOURCE_EQUIP_FK1 | R | EQUIPMENT_TYPE | RRL_RESOURCE_TYPE (RESOURCE_TYPE) | ENABLED |
| RRL_RESOURCE_EQUIP_PK | P | EQUIPMENT_ID |  | ENABLED |
| RRL_RESOURCE_EQUIP_U1 | U | EQUIPMENT_CODE |  | ENABLED |
| SYS_C0014826 | C | EQUIPMENT_ID |  | ENABLED |
| SYS_C0014827 | C | EQUIPMENT_CODE |  | ENABLED |
| SYS_C0014828 | C | EQUIPMENT_TYPE |  | ENABLED |
| SYS_C0014829 | C | SERVICE_STATUS |  | ENABLED |
| SYS_C0014830 | C | ACTIVE |  | ENABLED |
| SYS_C0014831 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_RESOURCE_POLICY](../programs/RRL_CASE_RESOURCE_POLICY.md), [RRL_TASK_RESOURCE_POLICY](../programs/RRL_TASK_RESOURCE_POLICY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RESOURCE_EQUIPMENT` в файле соответствующего типа.
