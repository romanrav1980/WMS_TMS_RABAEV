# RRL_SAP_RECEIPT_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Интеграция SAP.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| PALLET_WRITE_ALLOWED |  |  | PL/SQL BOOLEAN | OUT | N |  |
| REGISTER_PALLET | P_SSCC | 1 | VARCHAR2 | IN | N |  |
| REGISTER_PALLET | P_ARTICUL | 2 | VARCHAR2 | IN | N |  |
| REGISTER_PALLET | P_EXPIRY | 3 | DATE | IN | N |  |
| REGISTER_PALLET | P_PRODUCED | 4 | DATE | IN | N |  |
| REGISTER_PALLET | P_QTY | 5 | NUMBER | IN | N |  |
| REGISTER_PALLET | P_NAKLAD | 6 | NUMBER | IN | N |  |
| REGISTER_PALLET | P_ACTOR | 7 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_PALLETS](../tables/RRL_PALLETS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_SAP_RECEIPT_API](../programs/RRL_SAP_RECEIPT_API.md), [RRL_SAP_SUPPLY_ORDER](../tables/RRL_SAP_SUPPLY_ORDER.md)

## Кто использует

[RRL_SAP_PALLET_WRITE_GUARD](../programs/RRL_SAP_PALLET_WRITE_GUARD.md), [RRL_SAP_RECEIPT_API](../programs/RRL_SAP_RECEIPT_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_RECEIPT_API` в файле соответствующего типа.
