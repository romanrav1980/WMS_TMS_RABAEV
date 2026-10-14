# RRL_TRANSPORT_COST_CLAIM

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `DEPARTURE_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `SOURCE_PRICE_ID` | NUMBER | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018719 | C | OPERATION_ID |  | ENABLED |
| SYS_C0018720 | C | SOURCE_PRICE_ID |  | ENABLED |
| SYS_C0018721 | C | VERSION_NO |  | ENABLED |
| SYS_C0018722 | P | DEPARTURE_OPERATION_ID |  | ENABLED |
| SYS_C0018723 | U | OPERATION_ID |  | ENABLED |
| SYS_C0018724 | R | DEPARTURE_OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0018725 | R | OPERATION_ID | RRL_LOGISTICS_COST_RUN (OPERATION_ID) | ENABLED |
| SYS_C0018726 | R | SOURCE_PRICE_ID, VERSION_NO | RRL_TRANSPORT_NORM_HISTORY (SOURCE_PRICE_ID, VERSION_NO) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_NORM_COST_CORRECTION](../programs/RRL_NORM_COST_CORRECTION.md), [RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md), [RRL_TRAN_COST_CLAIM_GUARD](../programs/RRL_TRAN_COST_CLAIM_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_COST_CLAIM` в файле соответствующего типа.
