# RRL_QC_SCOPE_RULE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Контроль качества.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `STORE_ADDR` | VARCHAR2(255 bytes) | N |  |
| `PLACE_CATEGORY` | VARCHAR2(10 bytes) | N |  |
| `RULE_VERSION` | NUMBER | N |  |
| `ACTIVE_FLAG` | NUMBER(1,0) | N |  |
| `CONTROL_MODE` | VARCHAR2(10 bytes) | N |  |
| `INDEPENDENT_FLAG` | NUMBER(1,0) | N |  |
| `SAMPLE_PERCENT` | NUMBER(5,2) | N |  |
| `EXEMPT_WHOLE` | NUMBER(1,0) | N |  |
| `EXEMPT_STORAGE` | NUMBER(1,0) | N |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | N |  |
| `UPDATED_AT` | TIMESTAMP(6) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_QC_SCOPE_RULE_PK | P | WARE_ID, STORE_ADDR, PLACE_CATEGORY |  | ENABLED |
| SYS_C0018895 | C | WARE_ID |  | ENABLED |
| SYS_C0018896 | C | STORE_ADDR |  | ENABLED |
| SYS_C0018897 | C | PLACE_CATEGORY |  | ENABLED |
| SYS_C0018898 | C | RULE_VERSION |  | ENABLED |
| SYS_C0018899 | C | ACTIVE_FLAG |  | ENABLED |
| SYS_C0018900 | C | CONTROL_MODE |  | ENABLED |
| SYS_C0018901 | C | INDEPENDENT_FLAG |  | ENABLED |
| SYS_C0018902 | C | SAMPLE_PERCENT |  | ENABLED |
| SYS_C0018903 | C | EXEMPT_WHOLE |  | ENABLED |
| SYS_C0018904 | C | EXEMPT_STORAGE |  | ENABLED |
| SYS_C0018905 | C | UPDATED_BY |  | ENABLED |
| SYS_C0018906 | C | UPDATED_AT |  | ENABLED |
| SYS_C0018907 | C | PLACE_CATEGORY |  | ENABLED |
| SYS_C0018908 | C | RULE_VERSION |  | ENABLED |
| SYS_C0018909 | C | ACTIVE_FLAG |  | ENABLED |
| SYS_C0018910 | C | CONTROL_MODE |  | ENABLED |
| SYS_C0018911 | C | INDEPENDENT_FLAG |  | ENABLED |
| SYS_C0018912 | C | SAMPLE_PERCENT |  | ENABLED |
| SYS_C0018913 | C | EXEMPT_WHOLE |  | ENABLED |
| SYS_C0018914 | C | EXEMPT_STORAGE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_QC_SCOPE_READ](../programs/RRL_QC_SCOPE_READ.md), [RRL_QC_SCOPE_RULE_GUARD](../programs/RRL_QC_SCOPE_RULE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_QC_SCOPE_RULE` в файле соответствующего типа.
