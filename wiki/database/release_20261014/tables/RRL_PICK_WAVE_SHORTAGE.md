# RRL_PICK_WAVE_SHORTAGE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_WAVE_SHORTAGE_ID` | NUMBER | N |  |
| `PICK_WAVE_ID` | NUMBER | N |  |
| `PICK_SHORTAGE_ID` | NUMBER | Y |  |
| `PICK_PLAN_ID` | NUMBER | Y |  |
| `CUSTOMER_ORDER_ID` | NUMBER | Y |  |
| `CUSTOMER_ID` | NUMBER | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `REQUESTED_QTY` | NUMBER | N |  |
| `PLANNED_QTY` | NUMBER | N |  |
| `SHORTAGE_QTY` | NUMBER | N |  |
| `REASON_CODE` | VARCHAR2(50 bytes) | Y |  |
| `REASON_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_WAVE_SHORTAGE_FK1 | R | PICK_WAVE_ID | RRL_PICK_WAVE (PICK_WAVE_ID) | ENABLED |
| RRL_PICK_WAVE_SHORTAGE_PK | P | PICK_WAVE_SHORTAGE_ID |  | ENABLED |
| SYS_C0014619 | C | PICK_WAVE_SHORTAGE_ID |  | ENABLED |
| SYS_C0014620 | C | PICK_WAVE_ID |  | ENABLED |
| SYS_C0014621 | C | ARTICUL |  | ENABLED |
| SYS_C0014622 | C | REQUESTED_QTY |  | ENABLED |
| SYS_C0014623 | C | PLANNED_QTY |  | ENABLED |
| SYS_C0014624 | C | SHORTAGE_QTY |  | ENABLED |
| SYS_C0014625 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_WAVE_SHORTAGE` в файле соответствующего типа.
