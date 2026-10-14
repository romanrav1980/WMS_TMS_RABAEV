# TMP_PALLET_ROWS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `VERS` | NUMBER | Y |  |
| `ORDER_ID` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `EI` | VARCHAR2(3 bytes) | Y |  |
| `ORDER_WEIGHT` | NUMBER | Y |  |
| `QUANTITY` | NUMBER | N |  |
| `SORTFIELD` | NUMBER | Y |  |
| `PACK_COUNT` | NUMBER | Y |  |
| `TARESIZE` | NUMBER | Y |  |
| `TAREWEIGHT` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0013562 | C | ORDER_ID |  | ENABLED |
| SYS_C0013563 | C | ARTICUL |  | ENABLED |
| SYS_C0013564 | C | QUANTITY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `TMP_PALLET_ROWS` в файле соответствующего типа.
