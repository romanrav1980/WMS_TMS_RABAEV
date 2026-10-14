# RRL_STORE_AGG_SCAN

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| NORMALIZE | P_PROOF | 1 | CLOB | IN | N |  |
| NORMALIZE | P_METADATA | 2 | CLOB | IN | N |  |
| NORMALIZE | P_SCANS | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md), [RRL_STORE_AGG_SCAN](../programs/RRL_STORE_AGG_SCAN.md), [RRL_WMS_RECEIPT_CODE](../tables/RRL_WMS_RECEIPT_CODE.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STORE_AGG_SCAN](../programs/RRL_STORE_AGG_SCAN.md), [RRL_STORE_MARK_CORE](../programs/RRL_STORE_MARK_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_AGG_SCAN` в файле соответствующего типа.
