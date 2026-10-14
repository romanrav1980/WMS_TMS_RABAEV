# RRL_STOCK_BASELINE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `BASELINE_ID` | VARCHAR2(100 bytes) | N |  |
| `SNAPSHOT_SCN` | NUMBER | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | N |  |
| `STATE` | VARCHAR2(20 bytes) | N |  |
| `MANIFEST_HASH` | VARCHAR2(64 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STOCK_B0_STATE_CK | C | STATE |  | ENABLED |
| SYS_C0016139 | C | SNAPSHOT_SCN |  | ENABLED |
| SYS_C0016140 | C | CREATED_AT |  | ENABLED |
| SYS_C0016141 | C | CREATED_BY |  | ENABLED |
| SYS_C0016142 | C | STATE |  | ENABLED |
| SYS_C0016143 | C | MANIFEST_HASH |  | ENABLED |
| SYS_C0016145 | P | BASELINE_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_BASELINE` в файле соответствующего типа.
