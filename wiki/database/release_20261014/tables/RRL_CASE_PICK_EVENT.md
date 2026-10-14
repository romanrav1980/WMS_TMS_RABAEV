# RRL_CASE_PICK_EVENT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CASE_PICK_EVENT_ID` | NUMBER | N |  |
| `CASE_PICK_TASK_ID` | NUMBER | Y |  |
| `CASE_PICK_LINE_ID` | NUMBER | Y |  |
| `EVENT_TYPE` | VARCHAR2(60 bytes) | N |  |
| `OFFLINE_EVENT_ID` | VARCHAR2(100 bytes) | Y |  |
| `RESOURCE_ID` | NUMBER | Y |  |
| `RESOURCE_SESSION_ID` | NUMBER | Y |  |
| `EQUIPMENT_ID` | NUMBER | Y |  |
| `MESSAGE_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `PAYLOAD_JSON` | CLOB | Y |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CASE_PICK_EVENT_PK | P | CASE_PICK_EVENT_ID |  | ENABLED |
| SYS_C0014999 | C | CASE_PICK_EVENT_ID |  | ENABLED |
| SYS_C0015000 | C | EVENT_TYPE |  | ENABLED |
| SYS_C0015001 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_CLOSE_JOURNAL_G](../programs/RRL_CASE_CLOSE_JOURNAL_G.md), [RRL_STOCK_CASE_MOVE_CMD](../programs/RRL_STOCK_CASE_MOVE_CMD.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md), [RRL_STOCK_CASE_SHORT_CMD](../programs/RRL_STOCK_CASE_SHORT_CMD.md), [RRL_STOCK_COMPOSITION_CORE](../programs/RRL_STOCK_COMPOSITION_CORE.md), [RRL_STOCK_HU_CMD](../programs/RRL_STOCK_HU_CMD.md), [RRL_STOCK_QC_CASE](../programs/RRL_STOCK_QC_CASE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CASE_PICK_EVENT` в файле соответствующего типа.
