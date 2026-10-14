# RRL_WT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `TYPE1` | VARCHAR2(5 bytes) | Y |  |
| `PUID` | VARCHAR2(50 bytes) | Y |  |
| `FROM1` | VARCHAR2(50 bytes) | Y |  |
| `TO1` | VARCHAR2(50 bytes) | Y |  |
| `COUNT1` | NUMBER | Y |  |
| `PLAN_START_TIME` | DATE | Y |  |
| `PLAN_END_TIME` | DATE | Y |  |
| `FACT_START_TIME` | DATE | Y |  |
| `FACT_END_TIME` | DATE | Y |  |
| `WORKER` | VARCHAR2(50 bytes) | Y |  |
| `CONDTION` | NUMBER | Y |  |
| `PARENT_ID` | NUMBER | Y |  |
| `ORDER1` | NUMBER | Y |  |
| `ARTICUL` | VARCHAR2(50 bytes) | Y |  |
| `FLAG_LAST_PAL` | NUMBER | Y |  |
| `FLAG_PARTIAL` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WT_PK | P | ID |  | ENABLED |
| SYS_C0013553 | C | ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[GOODS_TO_PICK](../programs/GOODS_TO_PICK.md), [RRL_SUMMARY_PICK_LIST_DELETE](../programs/RRL_SUMMARY_PICK_LIST_DELETE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WT` в файле соответствующего типа.
