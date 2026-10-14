# RRL_STORE_RECEIPT_WEIGHT_PHOTO

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PHOTO_ID` | VARCHAR2(64 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016516 | C | OPERATION_ID |  | ENABLED |
| SYS_C0016517 | C | PHOTO_ID |  | ENABLED |
| SYS_C0016518 | P | OPERATION_ID, PHOTO_ID |  | ENABLED |
| SYS_C0016519 | R | OPERATION_ID | RRL_STORE_RECEIPT_WEIGHT (OPERATION_ID) | ENABLED |
| SYS_C0016520 | R | PHOTO_ID | RRL_STORE_RECEIPT_PHOTO (PHOTO_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_WEIGHT_CORE](../programs/RRL_STOCK_STORE_WEIGHT_CORE.md), [RRL_STORE_WEIGHT_PHOTO_GUARD](../programs/RRL_STORE_WEIGHT_PHOTO_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RECEIPT_WEIGHT_PHOTO` в файле соответствующего типа.
