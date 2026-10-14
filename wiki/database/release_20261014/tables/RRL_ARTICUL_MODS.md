# RRL_ARTICUL_MODS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | Y |  |
| `NAME` | VARCHAR2(50 bytes) | Y |  |
| `SHT_IN_KOR` | NUMBER | Y |  |
| `SHT_WEIGHT` | NUMBER | Y |  |
| `KARTON_WEIGHT` | NUMBER | Y |  |
| `DELETED` | NUMBER | Y |  |
| `SHK_SHT` | VARCHAR2(255 bytes) | Y |  |
| `SHK_KOR` | VARCHAR2(255 bytes) | Y |  |
| `DIMK_X` | NUMBER | Y |  |
| `DIMK_Y` | NUMBER | Y |  |
| `DIMK_Z` | NUMBER | Y |  |
| `BRT_WEIGHT_OF_KOR` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[ARTICULS](../programs/ARTICULS.md), [ARTICULS_SP_OLD](../programs/ARTICULS_SP_OLD.md), [CROSS_DOCKING](../programs/CROSS_DOCKING.md), [RRL_CARTON_WEIGHT2](../programs/RRL_CARTON_WEIGHT2.md), [RRL_COUNT_KOR2](../programs/RRL_COUNT_KOR2.md), [RRL_COUNT_KOR3](../programs/RRL_COUNT_KOR3.md), [RRL_COUNT_KOR4](../programs/RRL_COUNT_KOR4.md), [RRL_GET_MOD_INFO](../programs/RRL_GET_MOD_INFO.md), [RRL_PALLET_HAS_MODS](../programs/RRL_PALLET_HAS_MODS.md), [RRL_PRIHODPALLET_CALC_COUNT](../programs/RRL_PRIHODPALLET_CALC_COUNT.md), [RRL_PRIHODPALLET_CALC_WEIGHT](../programs/RRL_PRIHODPALLET_CALC_WEIGHT.md), [RRL_PRIHODPALLET_CHANGE](../programs/RRL_PRIHODPALLET_CHANGE.md), [RRL_PRIHODPALLET_CHANGE_WEIGHT](../programs/RRL_PRIHODPALLET_CHANGE_WEIGHT.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_INVENTORY_BIRTH](../programs/RRL_STOCK_INVENTORY_BIRTH.md), [RRL_STOCK_PALLET_UOM](../programs/RRL_STOCK_PALLET_UOM.md), [RRL_UPDATE_PALLET_ROW3_SP_CALC](../programs/RRL_UPDATE_PALLET_ROW3_SP_CALC.md), [RRL_UPDATE_PALLET_ROW3_SP_OLD](../programs/RRL_UPDATE_PALLET_ROW3_SP_OLD.md), [UPDATE_RRL_MOD](../programs/UPDATE_RRL_MOD.md), [UPDATE_RRL_MOD2](../programs/UPDATE_RRL_MOD2.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ARTICUL_MODS` в файле соответствующего типа.
