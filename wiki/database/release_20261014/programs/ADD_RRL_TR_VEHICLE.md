# ADD_RRL_TR_VEHICLE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Транспортные средства.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_RRL_TR_VEHICLE |  |  | NUMBER | OUT | N |  |
| ADD_RRL_TR_VEHICLE | ID1 | 1 | NUMBER | IN | N |  |
| ADD_RRL_TR_VEHICLE | NUM1 | 2 | VARCHAR2 | IN | N |  |
| ADD_RRL_TR_VEHICLE | TR_TYPE1 | 3 | VARCHAR2 | IN | N |  |
| ADD_RRL_TR_VEHICLE | MARKA1 | 4 | VARCHAR2 | IN | N |  |
| ADD_RRL_TR_VEHICLE | REF_REJIM1 | 5 | VARCHAR2 | IN | N |  |
| ADD_RRL_TR_VEHICLE | WORKOINGNOW | 6 | NUMBER | IN | N |  |
| ADD_RRL_TR_VEHICLE | PALLETS1 | 7 | NUMBER | IN | N |  |
| ADD_RRL_TR_VEHICLE | LOPATA | 8 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), `RRL_TR_VEHICLE_SQ`

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `ADD_RRL_TR_VEHICLE` в файле соответствующего типа.
