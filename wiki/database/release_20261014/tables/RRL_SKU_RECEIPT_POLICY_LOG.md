# RRL_SKU_RECEIPT_POLICY_LOG

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Приёмка.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `POLICY_VERSION` | NUMBER | N |  |
| `POLICY_JSON` | CLOB | N |  |
| `CHANGED_AT` | TIMESTAMP(6) | N |  |
| `CHANGED_BY` | VARCHAR2(100 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SKU_RPLOG_JSON_CK | C | POLICY_JSON |  | ENABLED |
| RRL_SKU_RPLOG_PK | P | ARTICUL, POLICY_VERSION |  | ENABLED |
| SYS_C0015847 | C | ARTICUL |  | ENABLED |
| SYS_C0015848 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0015849 | C | POLICY_JSON |  | ENABLED |
| SYS_C0015850 | C | CHANGED_AT |  | ENABLED |
| SYS_C0015851 | C | CHANGED_BY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SKU_RECEIPT_POLICY_LOG` в файле соответствующего типа.
