# RRL_IW_SHORTAGE_GUARD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| REQUIRE_COMMAND | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| REQUIRE_COMMAND | P_KIND | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_IW_SHORTAGE_GUARD](../programs/RRL_IW_SHORTAGE_GUARD.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md)

## Кто использует

[RRL_IW_RECOVERY_APPROVAL_G](../programs/RRL_IW_RECOVERY_APPROVAL_G.md), [RRL_IW_RECOVERY_PLACE_GUARD](../programs/RRL_IW_RECOVERY_PLACE_GUARD.md), [RRL_IW_RECOVERY_PUT_GUARD](../programs/RRL_IW_RECOVERY_PUT_GUARD.md), [RRL_IW_RECOVERY_RECEIPT_G](../programs/RRL_IW_RECOVERY_RECEIPT_G.md), [RRL_IW_RECOVERY_REQUEST_G](../programs/RRL_IW_RECOVERY_REQUEST_G.md), [RRL_IW_RECOVERY_UNIT_G](../programs/RRL_IW_RECOVERY_UNIT_G.md), [RRL_IW_REC_CANCEL_G](../programs/RRL_IW_REC_CANCEL_G.md), [RRL_IW_REC_DISPATCH_GUARD](../programs/RRL_IW_REC_DISPATCH_GUARD.md), [RRL_IW_SHORTAGE_GUARD](../programs/RRL_IW_SHORTAGE_GUARD.md), [RRL_IW_SHORT_FACT_G](../programs/RRL_IW_SHORT_FACT_G.md), [RRL_IW_SHORT_REQUEST_G](../programs/RRL_IW_SHORT_REQUEST_G.md), [RRL_IW_SHORT_UNIT_G](../programs/RRL_IW_SHORT_UNIT_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_SHORTAGE_GUARD` в файле соответствующего типа.
