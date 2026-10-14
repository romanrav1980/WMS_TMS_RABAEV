# RRL_STORE_EVIDENCE_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| PHOTOS_JSON |  |  | CLOB | OUT | N |  |
| PHOTOS_JSON | P_LOAD | 1 | VARCHAR2 | IN | N |  |
| PHOTOS_JSON | P_STORE | 2 | VARCHAR2 | IN | N |  |
| PHOTOS_JSON | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| REGISTER_PHOTO | P_LOAD | 1 | VARCHAR2 | IN | N |  |
| REGISTER_PHOTO | P_STORE | 2 | VARCHAR2 | IN | N |  |
| REGISTER_PHOTO | P_VIEW | 3 | VARCHAR2 | IN | N |  |
| REGISTER_PHOTO | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| REGISTER_PHOTO | P_MIME | 5 | VARCHAR2 | IN | N |  |
| REGISTER_PHOTO | P_WIDTH | 6 | NUMBER | IN | N |  |
| REGISTER_PHOTO | P_HEIGHT | 7 | NUMBER | IN | N |  |
| REGISTER_PHOTO | P_BYTES | 8 | BLOB | IN | N |  |
| REGISTER_PHOTO | P_RESULT | 9 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_STORE_MEDIA_ASSET](../tables/RRL_STORE_MEDIA_ASSET.md), [RRL_STORE_RECEIPT_PHOTO](../tables/RRL_STORE_RECEIPT_PHOTO.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_STORE_RECEIPT_READ](../programs/RRL_STOCK_STORE_RECEIPT_READ.md), [RRL_STORE_EVIDENCE_API](../programs/RRL_STORE_EVIDENCE_API.md), [RRL_STORE_MEDIA_ASSET](../tables/RRL_STORE_MEDIA_ASSET.md), [RRL_STORE_RECEIPT_PHOTO](../tables/RRL_STORE_RECEIPT_PHOTO.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md)

## Кто использует

[RRL_STORE_EVIDENCE_API](../programs/RRL_STORE_EVIDENCE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_EVIDENCE_API` в файле соответствующего типа.
