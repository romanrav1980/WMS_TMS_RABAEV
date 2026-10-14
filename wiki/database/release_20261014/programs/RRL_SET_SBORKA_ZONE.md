# RRL_SET_SBORKA_ZONE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_SET_SBORKA_ZONE |  |  | NUMBER | OUT | N |  |
| RRL_SET_SBORKA_ZONE | PALLET_UID1 | 1 | VARCHAR2 | IN | N |  |
| RRL_SET_SBORKA_ZONE | ZONE1 | 2 | VARCHAR2 | IN | N |  |
| RRL_SET_SBORKA_ZONE | USER_ID1 | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_BILLING](../tables/RRL_BILLING.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_BILLING](../tables/RRL_BILLING.md), [RRL_BILLING_NASTR_INTMOV](../tables/RRL_BILLING_NASTR_INTMOV.md), `RRL_BILLING_SEQ`, [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLETS_HISTORY](../tables/RRL_SBORKA_PALLETS_HISTORY.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SET_SBORKA_ZONE` в файле соответствующего типа.
