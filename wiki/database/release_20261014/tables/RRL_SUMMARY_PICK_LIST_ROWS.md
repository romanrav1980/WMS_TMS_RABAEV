# RRL_SUMMARY_PICK_LIST_ROWS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: таблица строк суммарных сборочных листов

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(50 bytes) | N |  |
| `SPL_ID` | NUMBER | N | ИД ССЛ |
| `QUANTITY` | NUMBER | Y | Количество нужно |
| `QUANTITY_COMPLETE` | NUMBER | Y | Количество обеспечено |
| `CONDITION` | NUMBER | Y | Состояний 0 - спланировано 1-не полностью спланировано 2-полностью обеспечено и закрыто |
| `QUANTITY_PLANNED` | NUMBER | Y | Количество спланировано WT |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SUMMARY_PICK_LIST_ROWS_PK | P | ID |  | ENABLED |
| SYS_C0013522 | C | ID |  | ENABLED |
| SYS_C0013523 | C | ARTICUL |  | ENABLED |
| SYS_C0013524 | C | SPL_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[GOODS_TO_PICK](../programs/GOODS_TO_PICK.md), [RRL_SUMMARY_PICK_LIST_DELETE](../programs/RRL_SUMMARY_PICK_LIST_DELETE.md), [RRL_SUMMARY_PICK_LIST_ROWS_TRG](../programs/RRL_SUMMARY_PICK_LIST_ROWS_TRG.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SUMMARY_PICK_LIST_ROWS` в файле соответствующего типа.
