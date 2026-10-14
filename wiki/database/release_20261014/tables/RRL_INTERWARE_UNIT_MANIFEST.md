# RRL_INTERWARE_UNIT_MANIFEST

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PLAN_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `UNIT_SIGNATURE` | VARCHAR2(64 bytes) | N |  |
| `MANIFEST_JSON` | CLOB | N |  |
| `CREATED_BY` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017828 | C | UNIT_SIGNATURE |  | ENABLED |
| SYS_C0017829 | C | MANIFEST_JSON |  | ENABLED |
| SYS_C0017830 | C | CREATED_BY |  | ENABLED |
| SYS_C0017831 | C | CREATED_AT |  | ENABLED |
| SYS_C0017832 | C | MANIFEST_JSON |  | ENABLED |
| SYS_C0017833 | P | PLAN_OPERATION_ID |  | ENABLED |
| SYS_C0017834 | R | PLAN_OPERATION_ID | RRL_INTERWARE_PLAN (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_INTERWARE_UNIT_MANIFEST_G](../programs/RRL_INTERWARE_UNIT_MANIFEST_G.md), [RRL_INTERWARE_UNIT_SOURCE](../programs/RRL_INTERWARE_UNIT_SOURCE.md), [RRL_STOCK_INTERWARE_NEXT](../programs/RRL_STOCK_INTERWARE_NEXT.md), [RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_UNIT_MANIFEST` в файле соответствующего типа.
