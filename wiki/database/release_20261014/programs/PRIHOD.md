# PRIHOD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CLOSE_PRICE_CONTROL |  |  | NUMBER | OUT | N |  |
| CLOSE_PRICE_CONTROL | PRIH_ID | 1 | NUMBER | IN | N |  |
| GET_BRAK_REASON |  |  | VARCHAR2 | OUT | N |  |
| GET_BRAK_REASON | REASON_ID | 1 | NUMBER | IN | N |  |
| IS_PRIHOD_FRESH |  |  | VARCHAR2 | OUT | N |  |
| IS_PRIHOD_FRESH | PRIHOD_ID | 1 | NUMBER | IN | N |  |
| ORDER_ZAKAZ_NUMBER |  |  | VARCHAR2 | OUT | N |  |
| ORDER_ZAKAZ_NUMBER | PRIHOD_NAKLAD_ID | 1 | NUMBER | IN | N |  |
| PRIHOD_IS_CLOSED |  |  | NUMBER | OUT | N |  |
| PRIHOD_IS_CLOSED | ORD_ID | 1 | NUMBER | IN | N |  |
| PRIHOD_PALL_COUNT |  |  | NUMBER | OUT | N |  |
| PRIHOD_PALL_COUNT | PRIHOD_NAKLAD_ID | 1 | NUMBER | IN | N |  |
| SET_BRAK_PERC_NEW |  |  | NUMBER | OUT | N |  |
| SET_BRAK_PERC_NEW | PUID1 | 1 | VARCHAR2 | IN | N |  |
| SET_BRAK_PERC_NEW | NEW_PERC | 2 | NUMBER | IN | N |  |
| SET_BRAK_PERC_NEW | REASON_ID | 3 | NUMBER | IN | N |  |
| SET_DOCK |  |  | NUMBER | OUT | N |  |
| SET_DOCK | PRIH_ID | 1 | NUMBER | IN | N |  |
| SET_DOCK | H_DOCK | 2 | VARCHAR2 | IN | N |  |
| SET_PRIHOD_KPP |  |  | NUMBER | OUT | N |  |
| SET_PRIHOD_KPP | PRIHOD_ID | 1 | NUMBER | IN | N |  |
| SET_PRIHOD_KPP | KPP_N | 2 | VARCHAR2 | IN | N |  |
| SET_PRIORITY |  |  | NUMBER | OUT | N |  |
| SET_PRIORITY | PRIH_ID | 1 | NUMBER | IN | N |  |
| SET_PRIORITY | NEW_PRIORITY_ID | 2 | NUMBER | IN | N |  |
| SET_PRIORITY | NEW_USER_ID | 3 | VARCHAR2 | IN | N |  |
| SET_WARE_ID |  |  | NUMBER | OUT | N |  |
| SET_WARE_ID | PRIH_ID | 1 | NUMBER | IN | N |  |
| SET_WARE_ID | NEW_WARE_ID | 2 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PALLETS_HIST](../tables/RRL_PALLETS_HIST.md), [RRL_PRIHOD_NAKLAD](../tables/RRL_PRIHOD_NAKLAD.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[PRIHOD](../programs/PRIHOD.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PALLETS_HIST](../tables/RRL_PALLETS_HIST.md), `RRL_PALLETS_HIST_SQ`, [RRL_PALL_TRASH_REASON](../tables/RRL_PALL_TRASH_REASON.md), [RRL_PRIHOD_NAKLAD](../tables/RRL_PRIHOD_NAKLAD.md)

## Кто использует

[PRIHOD](../programs/PRIHOD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `PRIHOD` в файле соответствующего типа.
