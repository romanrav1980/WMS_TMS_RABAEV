# RRL_STORE_ACCESS_RULES

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_MEMBERS | P_VEHICLE | 1 | NUMBER | IN | N |  |
| ASSERT_MEMBERS | P_MEMBERS | 2 | CLOB | IN | N |  |
| CHECK_STS | P_VEHICLE | 1 | NUMBER | IN | N |  |
| CHECK_STS | P_STS | 2 | CLOB | IN | N |  |
| CHECK_STS | P_COMPLETE | 3 | NUMBER | IN | N |  |
| CHECK_STS | P_RESULT | 4 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ADDR](../tables/RRL_ADDR.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STORE_ACCESS_RULES](../programs/RRL_STORE_ACCESS_RULES.md), [RRL_STORE_PROFILE](../tables/RRL_STORE_PROFILE.md), [RRL_VEHICLE_PROFILE_API](../programs/RRL_VEHICLE_PROFILE_API.md)

## Кто использует

[RRL_STOCK_HU_LOAD_CORE](../programs/RRL_STOCK_HU_LOAD_CORE.md), [RRL_STOCK_TRIP_DEPART_CMD](../programs/RRL_STOCK_TRIP_DEPART_CMD.md), [RRL_STORE_ACCESS_RULES](../programs/RRL_STORE_ACCESS_RULES.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_ACCESS_RULES` в файле соответствующего типа.
