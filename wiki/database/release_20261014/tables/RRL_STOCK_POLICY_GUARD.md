# RRL_STOCK_POLICY_GUARD

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `POLICY_KEY` | RAW(1000 bytes) | N |  |
| `LOCK_ID` | NUMBER | N |  |
| `POLICY_VERSION` | NUMBER | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STOCK_POLICY_ID_CK | C | LOCK_ID |  | ENABLED |
| RRL_STOCK_POLICY_ID_UK | U | LOCK_ID |  | ENABLED |
| SYS_C0016116 | C | LOCK_ID |  | ENABLED |
| SYS_C0016117 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0016118 | C | CREATED_AT |  | ENABLED |
| SYS_C0016120 | P | POLICY_KEY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_UOM_CONFIG](../programs/RRL_STOCK_UOM_CONFIG.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_POLICY_GUARD` в файле соответствующего типа.
