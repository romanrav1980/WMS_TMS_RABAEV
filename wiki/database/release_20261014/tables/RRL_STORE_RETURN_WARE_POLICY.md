# RRL_STORE_RETURN_WARE_POLICY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `SUPPLIER_RECEIVE_CELL` | VARCHAR2(60 bytes) | N |  |
| `DISPOSAL_RECEIVE_CELL` | VARCHAR2(60 bytes) | N |  |
| `POLICY_VERSION` | NUMBER(19,0) | N |  |
| `CHANGED_BY` | NVARCHAR2(100 bytes) | N |  |
| `CHANGED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `SUPPLIER_TARGET_CELL` | VARCHAR2(60 bytes) | Y |  |
| `DISPOSAL_TARGET_CELL` | VARCHAR2(60 bytes) | Y |  |
| `REUSE_RECEIVE_CELL` | VARCHAR2(60 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016669 | C | SUPPLIER_RECEIVE_CELL |  | ENABLED |
| SYS_C0016670 | C | DISPOSAL_RECEIVE_CELL |  | ENABLED |
| SYS_C0016671 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0016672 | C | CHANGED_BY |  | ENABLED |
| SYS_C0016673 | C | CHANGED_AT |  | ENABLED |
| SYS_C0016674 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0016675 | P | WARE_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_RETURN_REUSE_ZONE_GUARD](../programs/RRL_RETURN_REUSE_ZONE_GUARD.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STORE_RETURN_TARGET_GUARD](../programs/RRL_STORE_RETURN_TARGET_GUARD.md), [RRL_STORE_RETURN_WARE_GUARD](../programs/RRL_STORE_RETURN_WARE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RETURN_WARE_POLICY` в файле соответствующего типа.
