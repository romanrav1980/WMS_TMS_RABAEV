# RRL_QC_EXEMPT_FACT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Контроль качества.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `DOCUMENT_ID` | NUMBER | N |  |
| `PAYLOAD_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_QC_EXEMPT_FACT_PK | P | OPERATION_ID, DOCUMENT_ID |  | ENABLED |
| SYS_C0018924 | C | OPERATION_ID |  | ENABLED |
| SYS_C0018925 | C | DOCUMENT_ID |  | ENABLED |
| SYS_C0018926 | C | PAYLOAD_JSON |  | ENABLED |
| SYS_C0018927 | C | CREATED_AT |  | ENABLED |
| SYS_C0018928 | C | PAYLOAD_JSON |  | ENABLED |
| SYS_C0018930 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0018931 | R | DOCUMENT_ID | RRL_SBORKA_PALLETS (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_QC_EXEMPT_FACT_GUARD](../programs/RRL_QC_EXEMPT_FACT_GUARD.md), [RRL_QC_SCOPE_READ](../programs/RRL_QC_SCOPE_READ.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_QC_EXEMPT_FACT` в файле соответствующего типа.
