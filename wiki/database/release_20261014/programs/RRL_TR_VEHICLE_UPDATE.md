# RRL_TR_VEHICLE_UPDATE

Тип: **PROCEDURE**. Схема: `RABAEV`.

Подсистема по имени: Транспортные средства.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TR_VEHICLE_UPDATE | P_ID | 1 | NUMBER | IN | N |  |
| RRL_TR_VEHICLE_UPDATE | P_NUM_PLAT | 2 | VARCHAR2 | IN | N |  |
| RRL_TR_VEHICLE_UPDATE | P_TRANSTYPE_ID | 3 | VARCHAR2 | IN | N |  |
| RRL_TR_VEHICLE_UPDATE | P_MAX_WEIGHT_KG | 4 | NUMBER | IN | N |  |
| RRL_TR_VEHICLE_UPDATE | P_MAX_PALLETS | 5 | NUMBER | IN | N |  |
| RRL_TR_VEHICLE_UPDATE | P_SOBSTVENNYY | 6 | NUMBER | IN | N |  |
| RRL_TR_VEHICLE_UPDATE | P_DOVERENNOST_OT | 7 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TR_VEHICLE_UPDATE` в файле соответствующего типа.
