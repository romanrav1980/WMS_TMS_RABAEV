# TRANSPORT_PLN

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| GET_DISTANCE |  |  | NUMBER | OUT | N |  |
| GET_DISTANCE | REG_F | 1 | VARCHAR2 | IN | N |  |
| GET_DISTANCE | RAI_F | 2 | VARCHAR2 | IN | N |  |
| GET_DISTANCE | REG_2 | 3 | VARCHAR2 | IN | N |  |
| GET_DISTANCE | RAI_2 | 4 | VARCHAR2 | IN | N |  |
| GET_DIST_M |  |  | NUMBER | OUT | N |  |
| GET_DIST_M | ADDRFROM | 1 | VARCHAR2 | IN | N |  |
| GET_DIST_M | ADDRTO | 2 | VARCHAR2 | IN | N |  |
| GET_TIME |  |  | NUMBER | OUT | N |  |
| GET_TIME | REG_F | 1 | VARCHAR2 | IN | N |  |
| GET_TIME | RAI_F | 2 | VARCHAR2 | IN | N |  |
| GET_TIME | REG_2 | 3 | VARCHAR2 | IN | N |  |
| GET_TIME | RAI_2 | 4 | VARCHAR2 | IN | N |  |
| GET_TIME_M |  |  | NUMBER | OUT | N |  |
| GET_TIME_M | ADDRFROM | 1 | VARCHAR2 | IN | N |  |
| GET_TIME_M | ADDRTO | 2 | VARCHAR2 | IN | N |  |
| IS_TT_JUST_OUT_GO |  |  | NUMBER | OUT | N |  |
| IS_TT_JUST_OUT_GO | TT_ID | 1 | NUMBER | IN | N |  |
| SET_DISTANCE |  |  | NUMBER | OUT | N |  |
| SET_DISTANCE | REG_F | 1 | VARCHAR2 | IN | N |  |
| SET_DISTANCE | RAI_F | 2 | VARCHAR2 | IN | N |  |
| SET_DISTANCE | REG_2 | 3 | VARCHAR2 | IN | N |  |
| SET_DISTANCE | RAI_2 | 4 | VARCHAR2 | IN | N |  |
| SET_DISTANCE | DIST | 5 | NUMBER | IN | N |  |
| SET_DISTANCE_M |  |  | NUMBER | OUT | N |  |
| SET_DISTANCE_M | ADDRFROM | 1 | VARCHAR2 | IN | N |  |
| SET_DISTANCE_M | ADDRTO | 2 | VARCHAR2 | IN | N |  |
| SET_DISTANCE_M | DIST1 | 3 | NUMBER | IN | N |  |
| SET_MAIL_SENDED |  |  | NUMBER | OUT | N |  |
| SET_MAIL_SENDED | TT_ID | 1 | NUMBER | IN | N |  |
| SET_TIME |  |  | NUMBER | OUT | N |  |
| SET_TIME | REG_F | 1 | VARCHAR2 | IN | N |  |
| SET_TIME | RAI_F | 2 | VARCHAR2 | IN | N |  |
| SET_TIME | REG_2 | 3 | VARCHAR2 | IN | N |  |
| SET_TIME | RAI_2 | 4 | VARCHAR2 | IN | N |  |
| SET_TIME | TIME1 | 5 | NUMBER | IN | N |  |
| SET_TIME_M |  |  | NUMBER | OUT | N |  |
| SET_TIME_M | ADDRFROM | 1 | VARCHAR2 | IN | N |  |
| SET_TIME_M | ADDRTO | 2 | VARCHAR2 | IN | N |  |
| SET_TIME_M | TIME1 | 3 | NUMBER | IN | N |  |
| SET_TT_CLOSED |  |  | NUMBER | OUT | N |  |
| SET_TT_CLOSED | TT_ID | 1 | NUMBER | IN | N |  |
| UPD_TT_PERDICTION |  |  | NUMBER | OUT | N |  |
| UPD_TT_PERDICTION | TT_ID | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TRP_ADDR_MATRIX](../tables/RRL_TRP_ADDR_MATRIX.md), [RRL_TRP_MATRIX](../tables/RRL_TRP_MATRIX.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TRP_ADDR_MATRIX](../tables/RRL_TRP_ADDR_MATRIX.md), [RRL_TRP_MATRIX](../tables/RRL_TRP_MATRIX.md), [TRANSPORT_PLN](../programs/TRANSPORT_PLN.md)

## Кто использует

[TRANSPORT_PLN](../programs/TRANSPORT_PLN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `TRANSPORT_PLN` в файле соответствующего типа.
