# RRL_SBORKA_PALLETS_HISTORY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | Y |  |
| `PALLET_UID` | VARCHAR2(50 bytes) | Y |  |
| `USER_ID` | VARCHAR2(50 bytes) | Y |  |
| `ZONE` | VARCHAR2(50 bytes) | Y |  |
| `EVENT` | VARCHAR2(50 bytes) | Y |  |
| `TIME1` | DATE | Y |  |
| `WEIGHT` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[BIN$UX1xZvVQS6/gYw8CAAo/Yg==$0](../programs/BIN_UX1xZvVQS6_gYw8CAAo_Yg___0.md), [RRL_GET_PALLET_CHECK_TIMES](../programs/RRL_GET_PALLET_CHECK_TIMES.md), [RRL_GET_SBORKA_PALLET_TIME](../programs/RRL_GET_SBORKA_PALLET_TIME.md), [RRL_GET_ST_CHECK_TIMES](../programs/RRL_GET_ST_CHECK_TIMES.md), [RRL_GIVE_TERMINAL_TASK2](../programs/RRL_GIVE_TERMINAL_TASK2.md), [RRL_IS_PALLET_LIKE_FAKE](../programs/RRL_IS_PALLET_LIKE_FAKE.md), [RRL_IS_PALLET_STRICTLY_FAKE](../programs/RRL_IS_PALLET_STRICTLY_FAKE.md), [RRL_SET_SBORKA_ZONE](../programs/RRL_SET_SBORKA_ZONE.md), [RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_TRIAL_BY_WEIGHT2_SP_OLD](../programs/RRL_TRIAL_BY_WEIGHT2_SP_OLD.md), [RRL_TRIAL_BY_WEIGHT_SP_OLD](../programs/RRL_TRIAL_BY_WEIGHT_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SBORKA_PALLETS_HISTORY` в файле соответствующего типа.
