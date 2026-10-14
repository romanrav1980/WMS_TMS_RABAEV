# RRL_RECEIPT_TRAVEL_TIME

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Приёмка.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `CELL` | VARCHAR2(60 bytes) | N |  |
| `PICK_CELL` | VARCHAR2(60 bytes) | N |  |
| `TRAVEL_SEC` | NUMBER | N |  |
| `BASIS` | VARCHAR2(30 bytes) | N |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_REC_TRAVEL_BASIS_CK | C | BASIS |  | ENABLED |
| RRL_REC_TRAVEL_PK | P | WARE_ID, CELL, PICK_CELL |  | ENABLED |
| RRL_REC_TRAVEL_SEC_CK | C | TRAVEL_SEC |  | ENABLED |
| SYS_C0015994 | C | WARE_ID |  | ENABLED |
| SYS_C0015995 | C | CELL |  | ENABLED |
| SYS_C0015996 | C | PICK_CELL |  | ENABLED |
| SYS_C0015997 | C | TRAVEL_SEC |  | ENABLED |
| SYS_C0015998 | C | BASIS |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RECEIPT_TRAVEL_TIME` в файле соответствующего типа.
