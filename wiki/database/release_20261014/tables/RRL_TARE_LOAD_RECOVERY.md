# RRL_TARE_LOAD_RECOVERY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ORIGINAL_BOOK_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RETURN_OFFER_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RETURN_ACCEPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `PALLET_TYPE_ID` | NUMBER | N |  |
| `CASE_PICK_TASK_ID` | NUMBER | Y |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `ROOT_UID` | VARCHAR2(150 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TARE_RECOVERY_PLACE_CK | C | CASE_PICK_TASK_ID, ROOT_UID |  | ENABLED |
| SYS_C0017780 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0017781 | C | ORIGINAL_BOOK_OPERATION_ID |  | ENABLED |
| SYS_C0017782 | C | RETURN_OFFER_OPERATION_ID |  | ENABLED |
| SYS_C0017783 | C | RETURN_ACCEPT_OPERATION_ID |  | ENABLED |
| SYS_C0017784 | C | WARE_ID |  | ENABLED |
| SYS_C0017785 | C | PALLET_TYPE_ID |  | ENABLED |
| SYS_C0017787 | C | CREATED_BY |  | ENABLED |
| SYS_C0017788 | C | CREATED_AT |  | ENABLED |
| SYS_C0017789 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017790 | U | ORIGINAL_BOOK_OPERATION_ID |  | ENABLED |
| SYS_C0017791 | U | RETURN_OFFER_OPERATION_ID |  | ENABLED |
| SYS_C0017792 | U | RETURN_ACCEPT_OPERATION_ID |  | ENABLED |
| SYS_C0017793 | R | OPERATION_ID | RRL_TARE_BOOK (OPERATION_ID) | ENABLED |
| SYS_C0017794 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| SYS_C0017795 | R | ORIGINAL_BOOK_OPERATION_ID | RRL_TARE_BOOK (OPERATION_ID) | ENABLED |
| SYS_C0017796 | R | RETURN_OFFER_OPERATION_ID | RRL_TARE_OFFER (OPERATION_ID) | ENABLED |
| SYS_C0017797 | R | RETURN_ACCEPT_OPERATION_ID | RRL_TARE_ACCEPT (OPERATION_ID) | ENABLED |
| SYS_C0017798 | R | PALLET_TYPE_ID | RRL_PALLET_TYPE (PALLET_TYPE_ID) | ENABLED |
| SYS_C0017799 | R | CASE_PICK_TASK_ID | RRL_CASE_PICK_TASK (CASE_PICK_TASK_ID) | ENABLED |
| SYS_C0017826 | R | ROOT_UID | RRL_PALLETS (UID_PALLET) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_TARE_LOAD_RECOVERY_API](../programs/RRL_TARE_LOAD_RECOVERY_API.md), [RRL_TARE_LOAD_RECOVERY_GUARD](../programs/RRL_TARE_LOAD_RECOVERY_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_LOAD_RECOVERY` в файле соответствующего типа.
