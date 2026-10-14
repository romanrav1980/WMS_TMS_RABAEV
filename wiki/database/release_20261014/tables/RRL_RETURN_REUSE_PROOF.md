# RRL_RETURN_REUSE_PROOF

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Возвраты.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `BOX_COUNT` | NUMBER(18,0) | N |  |
| `BOX_BASE_QTY` | NUMBER(27,9) | N |  |
| `UOM_POLICY_VERSION` | NUMBER(19,0) | N |  |
| `ARTICLE_BARCODE` | VARCHAR2(128 bytes) | N |  |
| `SOURCE_BATCH` | VARCHAR2(100 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016895 | C | BOX_COUNT |  | ENABLED |
| SYS_C0016896 | C | BOX_BASE_QTY |  | ENABLED |
| SYS_C0016897 | C | UOM_POLICY_VERSION |  | ENABLED |
| SYS_C0016898 | C | ARTICLE_BARCODE |  | ENABLED |
| SYS_C0016899 | C | SOURCE_BATCH |  | ENABLED |
| SYS_C0016900 | C | ACTOR |  | ENABLED |
| SYS_C0016901 | C | CREATED_AT |  | ENABLED |
| SYS_C0016902 | C | BOX_COUNT |  | ENABLED |
| SYS_C0016903 | C | BOX_BASE_QTY |  | ENABLED |
| SYS_C0016904 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016905 | R | OPERATION_ID | RRL_STORE_RETURN_RECEIPT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_RETURN_REUSE_PROOF_GUARD](../programs/RRL_RETURN_REUSE_PROOF_GUARD.md), [RRL_STOCK_RETURN_REUSE](../programs/RRL_STOCK_RETURN_REUSE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RETURN_REUSE_PROOF` в файле соответствующего типа.
