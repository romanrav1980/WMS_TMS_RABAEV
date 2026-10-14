# RRL_PICK_WAVE_AUDIT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_WAVE_AUDIT_ID` | NUMBER | N |  |
| `PICK_WAVE_ID` | NUMBER | N |  |
| `EVENT_TYPE` | VARCHAR2(50 bytes) | N |  |
| `MESSAGE_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `PAYLOAD_JSON` | CLOB | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_WAVE_AUDIT_FK1 | R | PICK_WAVE_ID | RRL_PICK_WAVE (PICK_WAVE_ID) | ENABLED |
| RRL_PICK_WAVE_AUDIT_PK | P | PICK_WAVE_AUDIT_ID |  | ENABLED |
| SYS_C0014628 | C | PICK_WAVE_AUDIT_ID |  | ENABLED |
| SYS_C0014629 | C | PICK_WAVE_ID |  | ENABLED |
| SYS_C0014630 | C | EVENT_TYPE |  | ENABLED |
| SYS_C0014631 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_WAVE_AUDIT` в файле соответствующего типа.
