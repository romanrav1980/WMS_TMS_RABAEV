# RRL_TRP_MATRIX

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `REG_F` | VARCHAR2(250 bytes) | N |  |
| `RAI_F` | VARCHAR2(250 bytes) | N |  |
| `REG_2` | VARCHAR2(250 bytes) | N |  |
| `RAI_2` | VARCHAR2(250 bytes) | N |  |
| `DIST` | NUMBER | Y |  |
| `TIME1` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TRP_MATRIX_PK | P | REG_F, RAI_F, REG_2, RAI_2 |  | ENABLED |
| SYS_C0014029 | C | REG_F |  | ENABLED |
| SYS_C0014030 | C | RAI_F |  | ENABLED |
| SYS_C0014031 | C | REG_2 |  | ENABLED |
| SYS_C0014032 | C | RAI_2 |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[TRANSPORT_PLN](../programs/TRANSPORT_PLN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRP_MATRIX` в файле соответствующего типа.
