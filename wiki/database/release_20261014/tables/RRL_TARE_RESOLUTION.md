# RRL_TARE_RESOLUTION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RESOLUTION_KIND` | VARCHAR2(12 bytes) | N |  |
| `OWNER_WARE_ID` | NUMBER | N |  |
| `PALLET_TYPE_ID` | NUMBER | N |  |
| `CUSTODIAN_KIND` | VARCHAR2(12 bytes) | N |  |
| `CUSTODIAN_ID` | VARCHAR2(255 bytes) | N |  |
| `FROM_BALANCE_KEY` | RAW(32 bytes) | N |  |
| `TO_BALANCE_KEY` | RAW(32 bytes) | Y |  |
| `QUANTITY` | NUMBER(18,0) | N |  |
| `DELIVERY_ACCEPT_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `DAMAGE_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016819 | C | RESOLUTION_KIND |  | ENABLED |
| SYS_C0016820 | C | OWNER_WARE_ID |  | ENABLED |
| SYS_C0016821 | C | PALLET_TYPE_ID |  | ENABLED |
| SYS_C0016822 | C | CUSTODIAN_KIND |  | ENABLED |
| SYS_C0016823 | C | CUSTODIAN_ID |  | ENABLED |
| SYS_C0016824 | C | FROM_BALANCE_KEY |  | ENABLED |
| SYS_C0016825 | C | QUANTITY |  | ENABLED |
| SYS_C0016826 | C | REASON_TEXT |  | ENABLED |
| SYS_C0016827 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0016828 | C | ACTOR |  | ENABLED |
| SYS_C0016829 | C | CREATED_AT |  | ENABLED |
| SYS_C0016830 | C | RESOLUTION_KIND |  | ENABLED |
| SYS_C0016831 | C | CUSTODIAN_KIND |  | ENABLED |
| SYS_C0016832 | C | QUANTITY |  | ENABLED |
| SYS_C0016833 | C | RESOLUTION_KIND, TO_BALANCE_KEY, DAMAGE_OPERATION_ID |  | ENABLED |
| SYS_C0016834 | C | CUSTODIAN_KIND, DELIVERY_ACCEPT_OPERATION_ID |  | ENABLED |
| SYS_C0016835 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016836 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016837 | R | PALLET_TYPE_ID | RRL_PALLET_TYPE (PALLET_TYPE_ID) | ENABLED |
| SYS_C0016838 | R | FROM_BALANCE_KEY | RRL_TARE_BALANCE (BALANCE_KEY) | ENABLED |
| SYS_C0016839 | R | DELIVERY_ACCEPT_OPERATION_ID | RRL_TARE_ACCEPT (OPERATION_ID) | ENABLED |
| SYS_C0016840 | R | DAMAGE_OPERATION_ID | RRL_TARE_RESOLUTION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_TARE_RESOLVE](../programs/RRL_STOCK_TARE_RESOLVE.md), [RRL_TARE_RESOLUTION_GUARD](../programs/RRL_TARE_RESOLUTION_GUARD.md), [RRL_TARE_STORE_DEBT](../programs/RRL_TARE_STORE_DEBT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_RESOLUTION` в файле соответствующего типа.
