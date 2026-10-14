# RRL_CASE_ROUTE_ADMISSION

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Сборка CASE.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_NEXT | P_CASE | 1 | NUMBER | IN | N |  |
| ASSERT_NEXT | P_LINE | 2 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_LINE](../tables/RRL_CASE_PICK_LINE.md), [RRL_CASE_ROUTE_ADMISSION](../programs/RRL_CASE_ROUTE_ADMISSION.md)

## Кто использует

[RRL_CASE_ROUTE_ADMISSION](../programs/RRL_CASE_ROUTE_ADMISSION.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CASE_ROUTE_ADMISSION` в файле соответствующего типа.
