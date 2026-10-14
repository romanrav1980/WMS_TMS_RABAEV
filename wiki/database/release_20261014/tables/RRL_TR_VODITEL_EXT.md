# RRL_TR_VODITEL_EXT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `VOD_ID` | NUMBER | N |  |
| `TABEL_NO` | VARCHAR2(50 bytes) | Y |  |
| `INN` | VARCHAR2(20 bytes) | Y |  |
| `LAST_UPD` | DATE | Y |  |
| `USER_ID` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| BIN$UX1xZvWBS6/gYw8CAAo/Yg==$0 | C | VOD_ID |  | ENABLED |
| BIN$UX1xZvWCS6/gYw8CAAo/Yg==$0 | P | VOD_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[TRANSPORT_TASK](../programs/TRANSPORT_TASK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TR_VODITEL_EXT` в файле соответствующего типа.
