# RRL_BOM_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_LINE |  |  | NUMBER | OUT | N |  |
| ADD_LINE | P_BOM_ID | 1 | NUMBER | IN | N |  |
| ADD_LINE | P_LINE_NO | 2 | NUMBER | IN | Y |  |
| ADD_LINE | P_COMPONENT_TYPE | 3 | VARCHAR2 | IN | Y |  |
| ADD_LINE | P_COMPONENT_ARTICUL | 4 | VARCHAR2 | IN | Y |  |
| ADD_LINE | P_COMPONENT_MOD_ID | 5 | NUMBER | IN | Y |  |
| ADD_LINE | P_COMPONENT_NAME | 6 | VARCHAR2 | IN | Y |  |
| ADD_LINE | P_QTY_PER_BASE | 7 | NUMBER | IN | Y |  |
| ADD_LINE | P_UNIT_CODE | 8 | VARCHAR2 | IN | Y |  |
| ADD_LINE | P_LOSS_PERCENT | 9 | NUMBER | IN | Y |  |
| ADD_LINE | P_MIN_TOLERANCE_PCT | 10 | NUMBER | IN | Y |  |
| ADD_LINE | P_MAX_TOLERANCE_PCT | 11 | NUMBER | IN | Y |  |
| ADD_LINE | P_IS_REQUIRED | 12 | NUMBER | IN | Y |  |
| ADD_LINE | P_SUBSTITUTION_GROUP | 13 | VARCHAR2 | IN | Y |  |
| ADD_LINE | P_REPLACEMENT_RATIO | 14 | NUMBER | IN | Y |  |
| ADD_LINE | P_COMMENT_TEXT | 15 | VARCHAR2 | IN | Y |  |
| ADD_LINE | P_CREATED_BY | 16 | VARCHAR2 | IN | Y |  |
| APPROVE_BOM | P_BOM_ID | 1 | NUMBER | IN | N |  |
| APPROVE_BOM | P_APPROVED_BY | 2 | VARCHAR2 | IN | Y |  |
| ARCHIVE_BOM | P_BOM_ID | 1 | NUMBER | IN | N |  |
| ARCHIVE_BOM | P_REASON | 2 | VARCHAR2 | IN | Y |  |
| ARCHIVE_BOM | P_UPDATED_BY | 3 | VARCHAR2 | IN | Y |  |
| BLOCK_BOM | P_BOM_ID | 1 | NUMBER | IN | N |  |
| BLOCK_BOM | P_REASON | 2 | VARCHAR2 | IN | Y |  |
| BLOCK_BOM | P_UPDATED_BY | 3 | VARCHAR2 | IN | Y |  |
| CLONE_BOM |  |  | NUMBER | OUT | N |  |
| CLONE_BOM | P_SOURCE_BOM_ID | 1 | NUMBER | IN | N |  |
| CLONE_BOM | P_BOM_CODE | 2 | VARCHAR2 | IN | N |  |
| CLONE_BOM | P_VALID_FROM | 3 | DATE | IN | N |  |
| CLONE_BOM | P_VALID_TO | 4 | DATE | IN | Y |  |
| CLONE_BOM | P_CREATED_BY | 5 | VARCHAR2 | IN | Y |  |
| CREATE_BOM |  |  | NUMBER | OUT | N |  |
| CREATE_BOM | P_BOM_CODE | 1 | VARCHAR2 | IN | N |  |
| CREATE_BOM | P_BOM_NAME | 2 | VARCHAR2 | IN | Y |  |
| CREATE_BOM | P_TARGET_ARTICUL | 3 | VARCHAR2 | IN | N |  |
| CREATE_BOM | P_TARGET_MOD_ID | 4 | NUMBER | IN | Y |  |
| CREATE_BOM | P_TARGET_GTIN | 5 | VARCHAR2 | IN | Y |  |
| CREATE_BOM | P_BOM_KIND | 6 | VARCHAR2 | IN | Y |  |
| CREATE_BOM | P_BASE_QTY | 7 | NUMBER | IN | N |  |
| CREATE_BOM | P_BASE_UNIT_CODE | 8 | VARCHAR2 | IN | Y |  |
| CREATE_BOM | P_IS_PRIMARY | 9 | NUMBER | IN | Y |  |
| CREATE_BOM | P_VALID_FROM | 10 | DATE | IN | N |  |
| CREATE_BOM | P_VALID_TO | 11 | DATE | IN | Y |  |
| CREATE_BOM | P_WARE_ID | 12 | NUMBER | IN | Y |  |
| CREATE_BOM | P_PRODUCTION_LINE | 13 | VARCHAR2 | IN | Y |  |
| CREATE_BOM | P_COMMENT_TEXT | 14 | VARCHAR2 | IN | Y |  |
| CREATE_BOM | P_CREATED_BY | 15 | VARCHAR2 | IN | Y |  |
| DELETE_LINE | P_BOM_LINE_ID | 1 | NUMBER | IN | N |  |
| DELETE_LINE | P_DELETED_BY | 2 | VARCHAR2 | IN | Y |  |
| FIND_PRIMARY_BOM |  |  | NUMBER | OUT | N |  |
| FIND_PRIMARY_BOM | P_TARGET_ARTICUL | 1 | VARCHAR2 | IN | N |  |
| FIND_PRIMARY_BOM | P_PLANNED_DATE | 2 | DATE | IN | Y |  |
| FIND_PRIMARY_BOM | P_TARGET_MOD_ID | 3 | NUMBER | IN | Y |  |
| FIND_PRIMARY_BOM | P_WARE_ID | 4 | NUMBER | IN | Y |  |
| FIND_PRIMARY_BOM | P_PRODUCTION_LINE | 5 | VARCHAR2 | IN | Y |  |
| MAKE_PRIMARY | P_BOM_ID | 1 | NUMBER | IN | N |  |
| MAKE_PRIMARY | P_UPDATED_BY | 2 | VARCHAR2 | IN | Y |  |
| UPDATE_BOM | P_BOM_ID | 1 | NUMBER | IN | N |  |
| UPDATE_BOM | P_BOM_CODE | 2 | VARCHAR2 | IN | Y |  |
| UPDATE_BOM | P_BOM_NAME | 3 | VARCHAR2 | IN | Y |  |
| UPDATE_BOM | P_TARGET_ARTICUL | 4 | VARCHAR2 | IN | Y |  |
| UPDATE_BOM | P_TARGET_MOD_ID | 5 | NUMBER | IN | Y |  |
| UPDATE_BOM | P_TARGET_GTIN | 6 | VARCHAR2 | IN | Y |  |
| UPDATE_BOM | P_BOM_KIND | 7 | VARCHAR2 | IN | Y |  |
| UPDATE_BOM | P_BASE_QTY | 8 | NUMBER | IN | Y |  |
| UPDATE_BOM | P_BASE_UNIT_CODE | 9 | VARCHAR2 | IN | Y |  |
| UPDATE_BOM | P_IS_PRIMARY | 10 | NUMBER | IN | Y |  |
| UPDATE_BOM | P_VALID_FROM | 11 | DATE | IN | Y |  |
| UPDATE_BOM | P_VALID_TO | 12 | DATE | IN | Y |  |
| UPDATE_BOM | P_WARE_ID | 13 | NUMBER | IN | Y |  |
| UPDATE_BOM | P_PRODUCTION_LINE | 14 | VARCHAR2 | IN | Y |  |
| UPDATE_BOM | P_COMMENT_TEXT | 15 | VARCHAR2 | IN | Y |  |
| UPDATE_BOM | P_UPDATED_BY | 16 | VARCHAR2 | IN | Y |  |
| UPDATE_LINE | P_BOM_LINE_ID | 1 | NUMBER | IN | N |  |
| UPDATE_LINE | P_LINE_NO | 2 | NUMBER | IN | Y |  |
| UPDATE_LINE | P_COMPONENT_TYPE | 3 | VARCHAR2 | IN | Y |  |
| UPDATE_LINE | P_COMPONENT_ARTICUL | 4 | VARCHAR2 | IN | Y |  |
| UPDATE_LINE | P_COMPONENT_MOD_ID | 5 | NUMBER | IN | Y |  |
| UPDATE_LINE | P_COMPONENT_NAME | 6 | VARCHAR2 | IN | Y |  |
| UPDATE_LINE | P_QTY_PER_BASE | 7 | NUMBER | IN | Y |  |
| UPDATE_LINE | P_UNIT_CODE | 8 | VARCHAR2 | IN | Y |  |
| UPDATE_LINE | P_LOSS_PERCENT | 9 | NUMBER | IN | Y |  |
| UPDATE_LINE | P_MIN_TOLERANCE_PCT | 10 | NUMBER | IN | Y |  |
| UPDATE_LINE | P_MAX_TOLERANCE_PCT | 11 | NUMBER | IN | Y |  |
| UPDATE_LINE | P_IS_REQUIRED | 12 | NUMBER | IN | Y |  |
| UPDATE_LINE | P_SUBSTITUTION_GROUP | 13 | VARCHAR2 | IN | Y |  |
| UPDATE_LINE | P_REPLACEMENT_RATIO | 14 | NUMBER | IN | Y |  |
| UPDATE_LINE | P_COMMENT_TEXT | 15 | VARCHAR2 | IN | Y |  |
| UPDATE_LINE | P_UPDATED_BY | 16 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

[RRL_BOM](../tables/RRL_BOM.md), [RRL_BOM_AUDIT](../tables/RRL_BOM_AUDIT.md), [RRL_BOM_LINE](../tables/RRL_BOM_LINE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_BOM](../tables/RRL_BOM.md), [RRL_BOM_API](../programs/RRL_BOM_API.md), [RRL_BOM_AUDIT](../tables/RRL_BOM_AUDIT.md), `RRL_BOM_AUDIT_SQ`, [RRL_BOM_LINE](../tables/RRL_BOM_LINE.md), `RRL_BOM_LINE_SQ`, `RRL_BOM_SQ`, [RRL_TRACEABILITY_API](../programs/RRL_TRACEABILITY_API.md)

## Кто использует

[RRL_BOM_API](../programs/RRL_BOM_API.md), [RRL_MES_PRODUCTION_API](../programs/RRL_MES_PRODUCTION_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_BOM_API` в файле соответствующего типа.
