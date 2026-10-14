# RRL_TT_UNLOAD_FACT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `TT_ID` | NUMBER | N |  |
| `CASE_PICK_TASK_ID` | NUMBER | Y |  |
| `WARE_ID` | NUMBER | N |  |
| `CELL_CODE` | VARCHAR2(60 bytes) | N |  |
| `COMPOSITION_JSON` | CLOB | N |  |
| `REASON` | VARCHAR2(1000 bytes) | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `ROOT_UID` | VARCHAR2(150 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TT_UNLOAD_ROOT_CK | C | ROOT_UID, CASE_PICK_TASK_ID |  | ENABLED |
| SYS_C0017762 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0017763 | C | TT_ID |  | ENABLED |
| SYS_C0017765 | C | WARE_ID |  | ENABLED |
| SYS_C0017766 | C | CELL_CODE |  | ENABLED |
| SYS_C0017767 | C | COMPOSITION_JSON |  | ENABLED |
| SYS_C0017768 | C | REASON |  | ENABLED |
| SYS_C0017769 | C | CREATED_BY |  | ENABLED |
| SYS_C0017770 | C | CREATED_AT |  | ENABLED |
| SYS_C0017771 | C | COMPOSITION_JSON |  | ENABLED |
| SYS_C0017772 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017773 | U | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0017774 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0017775 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| SYS_C0017776 | R | TT_ID | RRL_TRANSPORT_TASK (ID) | ENABLED |
| SYS_C0017777 | R | CASE_PICK_TASK_ID | RRL_CASE_PICK_TASK (CASE_PICK_TASK_ID) | ENABLED |
| SYS_C0017778 | R | ROOT_UID | RRL_PALLETS (UID_PALLET) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_TT_HU_LOAD_FACT_GUARD](../programs/RRL_TT_HU_LOAD_FACT_GUARD.md), [RRL_TT_HU_LOAD_ST_GUARD](../programs/RRL_TT_HU_LOAD_ST_GUARD.md), [RRL_TT_UNLOAD_FACT_GUARD](../programs/RRL_TT_UNLOAD_FACT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_UNLOAD_FACT` в файле соответствующего типа.
