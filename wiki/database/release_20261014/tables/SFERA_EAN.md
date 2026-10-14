# SFERA_EAN

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TMC_UID` | VARCHAR2(200 bytes) | N |  |
| `EAN_SHT` | VARCHAR2(80 bytes) | Y |  |
| `EAN_BL` | VARCHAR2(80 bytes) | Y |  |
| `EAN_KOR` | VARCHAR2(80 bytes) | Y |  |
| `MANUALENTER` | CHAR(4 bytes) | Y |  |
| `SHT_IN_BL` | NUMBER | N |  |
| `BL_IN_KOR` | NUMBER | N |  |
| `\uFFFD\uFFFD\uFFFD` | NUMBER | Y | Исходный комментарий Oracle повреждён; требуется уточнение. |
| `NAME` | VARCHAR2(1020 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| BIN$UX1xZvTqS6/gYw8CAAo/Yg==$0 | C | TMC_UID |  | ENABLED |
| BIN$UX1xZvTrS6/gYw8CAAo/Yg==$0 | C | SHT_IN_BL |  | ENABLED |
| BIN$UX1xZvTsS6/gYw8CAAo/Yg==$0 | C | BL_IN_KOR |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[BIN$UX1xZvTtS6/gYw8CAAo/Yg==$0](../programs/BIN_UX1xZvTtS6_gYw8CAAo_Yg___0.md), [RRL_SFERA_EAN_EAN_BL](../programs/RRL_SFERA_EAN_EAN_BL.md), [RRL_SFERA_EAN_EAN_KOR](../programs/RRL_SFERA_EAN_EAN_KOR.md), [RRL_SFERA_EAN_EAN_SHT](../programs/RRL_SFERA_EAN_EAN_SHT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `SFERA_EAN` в файле соответствующего типа.

У одного legacy-поля имя в Oracle состоит из трёх символов U+FFFD; в таблице выше оно показано escape-последовательностью. SQL-снимок сохраняет фактическое имя, без переименования.
