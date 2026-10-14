# RRL_INTERWARE_SHORTAGE_UNIT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PHYSICAL_UNIT_KEY` | VARCHAR2(64 bytes) | N |  |
| `FACT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ORIGINAL_UID` | VARCHAR2(200 bytes) | N |  |
| `UNIT_VERSION` | NUMBER | N |  |
| `BASE_QTY` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_IW_LOSS_EVENT_UNIT_PK | P | PHYSICAL_UNIT_KEY, FACT_OPERATION_ID |  | ENABLED |
| SYS_C0018119 | C | FACT_OPERATION_ID |  | ENABLED |
| SYS_C0018120 | C | ORIGINAL_UID |  | ENABLED |
| SYS_C0018121 | C | UNIT_VERSION |  | ENABLED |
| SYS_C0018122 | C | BASE_QTY |  | ENABLED |
| SYS_C0018123 | C | BASE_UOM |  | ENABLED |
| SYS_C0018124 | C | BASE_QTY |  | ENABLED |
| SYS_C0018126 | R | FACT_OPERATION_ID | RRL_INTERWARE_SHORTAGE_FACT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_SHORT_UNIT_G](../programs/RRL_IW_SHORT_UNIT_G.md), [RRL_STOCK_INTERWARE_SHORT_CMD](../programs/RRL_STOCK_INTERWARE_SHORT_CMD.md), [RRL_STOCK_IW_RECOVERY_PLAN](../programs/RRL_STOCK_IW_RECOVERY_PLAN.md), [RRL_STOCK_IW_RECOVERY_REC](../programs/RRL_STOCK_IW_RECOVERY_REC.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_STOCK_UNIT_GUARD](../programs/RRL_STOCK_UNIT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_SHORTAGE_UNIT` в файле соответствующего типа.
