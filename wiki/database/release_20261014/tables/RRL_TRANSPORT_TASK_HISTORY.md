# RRL_TRANSPORT_TASK_HISTORY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `TTASK_ID` | NUMBER | Y |  |
| `USER_ID` | VARCHAR2(50 bytes) | Y |  |
| `TRANSTYPE` | VARCHAR2(20 bytes) | Y |  |
| `TRANSPORT` | VARCHAR2(50 bytes) | Y |  |
| `ROUTETYPE` | VARCHAR2(100 bytes) | Y |  |
| `SHIPMENT_TIME` | DATE | Y |  |
| `VODITEL_ID` | NUMBER | Y |  |
| `PRIMECHANIE` | VARCHAR2(1024 bytes) | Y |  |
| `DOCK` | VARCHAR2(50 bytes) | Y |  |
| `SHIPMENT_DATE` | DATE | Y |  |
| `OPERATION` | VARCHAR2(20 bytes) | Y |  |
| `EVENT_TIME` | TIMESTAMP(0) | Y |  |
| `ST_NUMBER` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| BIN$UX1xZvV7S6/gYw8CAAo/Yg==$0 | C | ID |  | ENABLED |
| BIN$UX1xZvV8S6/gYw8CAAo/Yg==$0 | P | ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TRANPORT_TASK_HISTORY_ADD](../programs/RRL_TRANPORT_TASK_HISTORY_ADD.md), [RRL_TT_DROP2](../programs/RRL_TT_DROP2.md), [TRANSPORT_TASK](../programs/TRANSPORT_TASK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_TASK_HISTORY` в файле соответствующего типа.
