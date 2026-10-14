# RRL_TR_VEHICLE_ADD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Транспортные средства.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TR_VEHICLE_ADD |  |  | NUMBER | OUT | N |  |
| RRL_TR_VEHICLE_ADD | P_NUM_PLAT | 1 | VARCHAR2 | IN | N |  |
| RRL_TR_VEHICLE_ADD | P_TRANSTYPE_ID | 2 | VARCHAR2 | IN | Y |  |
| RRL_TR_VEHICLE_ADD | P_MAX_WEIGHT_KG | 3 | NUMBER | IN | Y |  |
| RRL_TR_VEHICLE_ADD | P_MAX_PALLETS | 4 | NUMBER | IN | Y |  |
| RRL_TR_VEHICLE_ADD | P_SOBSTVENNYY | 5 | NUMBER | IN | Y |  |
| RRL_TR_VEHICLE_ADD | P_DOVERENNOST_OT | 6 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), `SEQ_TR_VEHICLE`

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TR_VEHICLE_ADD` в файле соответствующего типа.
