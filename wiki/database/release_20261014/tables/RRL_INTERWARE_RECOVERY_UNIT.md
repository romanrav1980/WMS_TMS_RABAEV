# RRL_INTERWARE_RECOVERY_UNIT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PHYSICAL_UNIT_KEY` | VARCHAR2(64 bytes) | N |  |
| `RECOVERY_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LOSS_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `BASE_QTY` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `PREVIOUS_UNIT_VERSION` | NUMBER | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_IW_REC_EVENT_UNIT_PK | P | PHYSICAL_UNIT_KEY, RECOVERY_OPERATION_ID |  | ENABLED |
| SYS_C0018173 | C | RECOVERY_OPERATION_ID |  | ENABLED |
| SYS_C0018174 | C | LOSS_OPERATION_ID |  | ENABLED |
| SYS_C0018175 | C | BASE_QTY |  | ENABLED |
| SYS_C0018176 | C | BASE_UOM |  | ENABLED |
| SYS_C0018177 | C | PREVIOUS_UNIT_VERSION |  | ENABLED |
| SYS_C0018178 | C | BASE_QTY |  | ENABLED |
| SYS_C0018180 | R | RECOVERY_OPERATION_ID | RRL_INTERWARE_RECOVERY_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0018181 | R | LOSS_OPERATION_ID | RRL_INTERWARE_SHORTAGE_FACT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_RECOVERY_UNIT_G](../programs/RRL_IW_RECOVERY_UNIT_G.md), [RRL_STOCK_INTERWARE_SHORT_CMD](../programs/RRL_STOCK_INTERWARE_SHORT_CMD.md), [RRL_STOCK_IW_RECOVERY_PUT](../programs/RRL_STOCK_IW_RECOVERY_PUT.md), [RRL_STOCK_IW_RECOVERY_REC](../programs/RRL_STOCK_IW_RECOVERY_REC.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_STOCK_UNIT_GUARD](../programs/RRL_STOCK_UNIT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_RECOVERY_UNIT` в файле соответствующего типа.
