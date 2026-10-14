# RRL_VEHICLE_PROFILE_HEAD

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортные средства.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `VEHICLE_ID` | NUMBER | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018681 | C | VERSION_NO |  | ENABLED |
| SYS_C0018682 | C | VERSION_NO |  | ENABLED |
| SYS_C0018683 | P | VEHICLE_ID |  | ENABLED |
| SYS_C0018684 | R | VEHICLE_ID | RRL_TR_VEHICLE (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_VEHICLE_PROFILE_API](../programs/RRL_VEHICLE_PROFILE_API.md), [RRL_VEH_PROFILE_HEAD_GUARD](../programs/RRL_VEH_PROFILE_HEAD_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_VEHICLE_PROFILE_HEAD` в файле соответствующего типа.
