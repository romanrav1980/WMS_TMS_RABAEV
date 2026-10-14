# RRL_SBORKA_PALL_ROWS_PARTS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `PALLET_UID` | VARCHAR2(50 bytes) | Y |  |
| `COUNT` | NUMBER | Y |  |
| `ARTICUL` | VARCHAR2(50 bytes) | Y |  |
| `EXPIRY_DATE` | DATE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SBORKA_PALL_ROWS_PARTSPK | P | ID |  | ENABLED |
| SYS_C0013517 | C | ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_OTHOD_PALLET_PODBOR_PARTII](../programs/RRL_OTHOD_PALLET_PODBOR_PARTII.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SBORKA_PALL_ROWS_PARTS` в файле соответствующего типа.
