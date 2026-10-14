# RRL_ORDER_PALLET_ROWS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `ORDER_ID` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `SHORTNAME` | VARCHAR2(255 bytes) | Y |  |
| `EI` | VARCHAR2(40 bytes) | Y |  |
| `ORDER_WEIGHT` | NUMBER | Y |  |
| `QUANTITY` | NUMBER | N |  |
| `SORTFIELD` | NUMBER | Y |  |
| `WARE_ID` | NUMBER | N |  |
| `PACK_COUNT` | NUMBER | Y |  |
| `ORIGINAL_QUANTITY` | NUMBER | Y |  |
| `ORIGINAL_ORDER_WEIGHT` | NUMBER | Y |  |
| `CONDITION` | NUMBER | Y |  |
| `TARESIZE` | NUMBER | Y |  |
| `TAREWEIGHT` | NUMBER | Y |  |
| `VERSION_D` | NUMBER | Y |  |
| `PALL_NUMB` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_ORDER_PALLET_ROWS_I1 | P | ID |  | ENABLED |
| SYS_C0013463 | C | ID |  | ENABLED |
| SYS_C0013464 | C | ORDER_ID |  | ENABLED |
| SYS_C0013465 | C | ARTICUL |  | ENABLED |
| SYS_C0013466 | C | QUANTITY |  | ENABLED |
| SYS_C0013467 | C | WARE_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_ORDERS_DELETE](../programs/RRL_ORDERS_DELETE.md), [RRL_ORDER_PALLET_ROWS_TRG](../programs/RRL_ORDER_PALLET_ROWS_TRG.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ORDER_PALLET_ROWS` в файле соответствующего типа.
