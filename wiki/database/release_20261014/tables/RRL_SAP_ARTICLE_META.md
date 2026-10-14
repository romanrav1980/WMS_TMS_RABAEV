# RRL_SAP_ARTICLE_META

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Интеграция SAP.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `SENDER` | VARCHAR2(100 bytes) | N |  |
| `SOURCE_STAMP` | VARCHAR2(14 bytes) | N |  |
| `SOURCE_DOCNUM` | VARCHAR2(16 bytes) | N |  |
| `UNITS_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_ART_META_JSON | C | UNITS_JSON |  | ENABLED |
| RRL_SAP_ART_META_PK | P | ARTICUL |  | ENABLED |
| SYS_C0015869 | C | ARTICUL |  | ENABLED |
| SYS_C0015870 | C | BASE_UOM |  | ENABLED |
| SYS_C0015871 | C | SENDER |  | ENABLED |
| SYS_C0015872 | C | SOURCE_STAMP |  | ENABLED |
| SYS_C0015873 | C | SOURCE_DOCNUM |  | ENABLED |
| SYS_C0015874 | C | UNITS_JSON |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_ARTICLE_META` в файле соответствующего типа.
