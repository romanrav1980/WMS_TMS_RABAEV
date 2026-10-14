# RRL_STOCK_WRITE_GUARD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ENFORCEMENT_REQUIRED |  |  | PL/SQL BOOLEAN | OUT | N |  |
| REQUIRE_EFFECT | P_KIND | 1 | VARCHAR2 | IN | N |  |
| REQUIRE_EFFECT | P_UID | 2 | VARCHAR2 | IN | Y |  |
| REQUIRE_EFFECT | P_CELL | 3 | VARCHAR2 | IN | Y |  |
| REQUIRE_EFFECT | P_ROW_ID | 4 | NUMBER | IN | Y |  |
| REQUIRE_UNIT | P_KEY | 1 | VARCHAR2 | IN | N |  |
| REQUIRE_UNIT | P_UID | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md), [RRL_STOCK_WRITE_GUARD](../programs/RRL_STOCK_WRITE_GUARD.md)

## Кто использует

[RRL_COMPOSITION_VERSION_GUARD](../programs/RRL_COMPOSITION_VERSION_GUARD.md), [RRL_PHYSICAL_VERSION_GUARD](../programs/RRL_PHYSICAL_VERSION_GUARD.md), [RRL_STOCK_JOURNAL_GUARD](../programs/RRL_STOCK_JOURNAL_GUARD.md), [RRL_STOCK_REMAINS_GUARD](../programs/RRL_STOCK_REMAINS_GUARD.md), [RRL_STOCK_RESERVATION_GUARD](../programs/RRL_STOCK_RESERVATION_GUARD.md), [RRL_STOCK_UNIT_GUARD](../programs/RRL_STOCK_UNIT_GUARD.md), [RRL_STOCK_WRITE_GUARD](../programs/RRL_STOCK_WRITE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_WRITE_GUARD` в файле соответствующего типа.
