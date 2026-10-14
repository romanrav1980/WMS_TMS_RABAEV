# RRL_RECEIPT_CELL_RULE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Приёмка.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `CELL` | VARCHAR2(60 bytes) | N |  |
| `TEMP_MIN` | NUMBER | Y |  |
| `TEMP_MAX` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_REC_CELLR_PK | P | WARE_ID, CELL |  | ENABLED |
| RRL_REC_CELLR_TEMP_CK | C | TEMP_MIN, TEMP_MAX |  | ENABLED |
| SYS_C0015990 | C | WARE_ID |  | ENABLED |
| SYS_C0015991 | C | CELL |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_INTERWARE_THERMAL](../programs/RRL_INTERWARE_THERMAL.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_RETURN_REUSE](../programs/RRL_STOCK_RETURN_REUSE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RECEIPT_CELL_RULE` в файле соответствующего типа.
