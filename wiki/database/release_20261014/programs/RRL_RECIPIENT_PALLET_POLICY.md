# RRL_RECIPIENT_PALLET_POLICY

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RULE_ID |  |  | NUMBER | OUT | N |  |
| RULE_ID | P_CUSTOMER | 1 | NUMBER | IN | N |  |
| RULE_ID | P_STORE | 2 | NUMBER | IN | N |  |
| TYPE_ID |  |  | NUMBER | OUT | N |  |
| TYPE_ID | P_CUSTOMER | 1 | NUMBER | IN | N |  |
| TYPE_ID | P_STORE | 2 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER_PALLET_TYPE_RULE](../tables/RRL_CUSTOMER_PALLET_TYPE_RULE.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_RECIPIENT_PALLET_POLICY](../programs/RRL_RECIPIENT_PALLET_POLICY.md)

## Кто использует

[RRL_CASE_PALLET_TYPE_READ](../programs/RRL_CASE_PALLET_TYPE_READ.md), [RRL_RECIPIENT_PALLET_POLICY](../programs/RRL_RECIPIENT_PALLET_POLICY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RECIPIENT_PALLET_POLICY` в файле соответствующего типа.
