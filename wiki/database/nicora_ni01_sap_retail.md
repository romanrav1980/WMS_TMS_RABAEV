# NI01 — RABAEV: SAP Retail и паллетная приёмка

7 октября 2026 года. Установлены миграции **001–007 в существующей ORCL/orcl, схеме RABAEV**. Другой инстанс/схема не создавались. Успешные применения завершились Errors=0; первая попытка 005 остановилась на PL/SQL синтаксисе до DDL, затем исправлена. Metadata новых объектов/колонок прочитана в live Oracle. Это установка, не функциональная приёмка.

[SQL и откаты](../../db/migrations/2026-10-07_ni01_sap_retail/) · source checkpoints/installation logs: runtime/ni01. Git/GitHub не менялись.

## Добавочные структуры

| Объект | Назначение |
|---|---|
| RRL_SKU_RECEIPT_POLICY / PROFILE / POLICY_LOG | WMS authority: применимость, все версии профилей, разрешённый режим сканирования; immutable history |
| RRL_SAP_IDOC_INBOX | raw XML/parsed JSON, sender+DOCNUM unique, hash, RECEIVED/APPLIED/ERROR; 002 добавляет RESULT_JSON/LAST_ERROR |
| RRL_SAP_ARTICLE_META | ARTICUL PK, SAP sender, базовая единица, JSON коэффициентов, timestamp/DOCNUM источника; не второй справочник товара |
| RRL_SAP_SUPPLY_ORDER | ORDER_ID PK, sender+OrderNumber unique, NAKLAD_ID unique; версия, WMS warehouse/cell, hash |
| RRL_SAP_SUPPLY_LINE | order+line PK; уникальная legacy ROW_ID и order+articul; план в base UoM, исходные qty/UoM |
| RRL_SAP_SUPPLY_MESSAGE | sender+MessageId PK, raw XML/result/hash/actor; durable ответ повторного импорта |
| RRL_SAP_PALLET_RECEIPT | operation PK, UID_PALLET unique, order/line FK; supplier batch/hash/result/actor/time |
| RRL_SAP_TRACE_AGG | Состав коробки/паллеты из сообщения шлюза: order/line/profile/code hash, raw code и JSON физических единиц |
| RRL_WMS_RECEIPT_UNIT | pallet+physical unit PK, policy version, BASE_QTY>0; одна физическая единица при нескольких профилях, поддержка кг/л |
| RRL_WMS_RECEIPT_CODE | system+canonical hash PK, CANONICAL_CODE NOT NULL, raw code и все profile/version/raw JSON; index(pallet,unit) |
| RRL_WMS_RECEIPT_AGG | system+raw hash PK, первичный профиль/уровень/паллета принятой агрегации; полный список отсканированных профилей/версий/хэшей хранится в immutable RESULT_JSON receipt fact |
| RRL_SAP_RECEIPT_OUTBOX | EventId PK; payload/type, PENDING/EXPORTED/ERROR/ACKNOWLEDGED/REJECTED, FILE_HASH, внешний номер/время ACK; index(status,date) |
| RRL_SAP_RECEIPT_ACK | sender+MessageId PK, event FK, неизменный raw XML/hash/result и серверный автор |
| RRL_RECEIPT_WARE_SETTINGS | GS1 prefix/extension, координатный масштаб, скорости, TIME/DISTANCE |
| RRL_RECEIPT_SKU_RULE / CELL_RULE / TRAVEL_TIME | отбор/температура/остаточный срок; режим ячейки; время пары хранение–отбор и основание |
| RRL_RECEIPT_SLOT_CLAIM | unique task/pallet/slot, RESERVED/OCCUPIED; освобождение при отмене/новом назначении |
| RRL_RECEIPT_LABEL / SSCC_SQ | unique операция/SSCC, неизменная этикетка, ISSUED/CONFIRMED/USED и серия |
| RRL_SAP_RECEIPT_API | REGISTER_PALLET без commit; узкий writer существующей RRL_PALLETS |
| RRL_SAP_PALLET_WRITE_GUARD | Запрещает старую автоматическую вставку/замену/удаление SAP-паллет вне writer; обычные legacy паллеты не затрагивает |

Unit/aggregation FK к receipt fact отложены до commit: вся запись состава и факта в одной транзакции. Коды здесь — физический состав WMS; external regulatory state остаётся во владении RRL_PRODUCTION_API / RRL_REGULATORY_API, новые таблицы не подменяют подтверждение CRPT/ЕГАИС.

## Переиспользуемые объекты

RRL_ARTICULS и RRL_FINISHED_GOODS_SKU остаются master. Неполные/неоднозначные legacy ключи отклоняются; SAP importer сериализует создание identity через metadata table lock, не добавляет фиктивный FK к nullable ACTICUL. Маркировка не перезаписывается SAP.

RRL_PRIHOD_NAKLAD / ROWS — существующий приход по SAP-заказу. RRL_PALLETS — физическая паллета с UNIT_COUNT/SSCC/EXPIRY_DATE; supplier batch хранится в receipt fact, не превращается в вымышленный PROD_BATCH_ID. RRL_EVENTS type=1/2 — приход/перемещение. Прочитан **включённый legacy event trigger**, который сам изменяет RRL_REMAINS; второй прямой inventory write отсутствует. RRL_EVENT_ID_SQ и RRL_WAREHOUSE_TASK_SQ переиспользованы.

RRL_WAREHOUSE_TASK_CHK1/CHK2 расширены значениями PUTAWAY/SAP_RECEIPT с сохранением прежних вариантов. Новая complete-ветка сохраняет stock move/task DONE/outbox вместе, не пользуется прежним post-commit domain sync. Запись pallet write guard касается identifier/count/incoming document; обычные regulatory metadata updates не запрещаются.

Количество в критических receipt/complete чтениях приходит через TO_CHAR(TM9) с явным NLS и Decimal. В штучной единице каждая физическая штука имеет BASE_QTY=1; для кг/л количество задаётся или берётся из однозначной упаковочной нормы SAP. Сумма BASE_QTY равна факту паллеты; обязательны все профили. Raw QR/GS сохраняются отдельно от канонической идентичности.

## Миграции и ограничения

- 001: inbox и SKU policy — **2026-10-07-001-ni01-sap-retail**.
- 002: article apply и supply plan — **2026-10-07-002-ni01-sap-supply**.
- 003: receipt/tasks/guard/outbox — **2026-10-07-003-ni01-physical-receipt**.
- 004: марки и source aggregation manifests — **2026-10-07-004-ni01-receipt-marking**.
- 005: labels/config/slot claims/reconciliation/ACK — **2026-10-07-005-ni01-completion**.
- 006: canonical NOT NULL, index состава, RRL_REG_OPERATION_JOURNAL.SYSTEM_CODE расширен 20→40, RRL_REGULATORY_API body перекомпилирован — **2026-10-07-006-ni01-registry-contract**.
- 007: BASE_QTY/check>0 для физических единиц — **2026-10-07-007-ni01-unit-quantity**.

Откаты не выполнялись. Порядок при явном поручении — 007 → 006 → 005 → 004 → 003 → 002 → 001; guards препятствуют потере накопленных данных. DDL имеет implicit commit.

SUPPLY_ORDER дополнен CLOSED_AT/RECONCILIATION_JSON. Изменения плана сохраняют факты/строки; закрытие с недостачей и запрос повторного открытия — отдельные исторические outbox события. Source aggregation — дополнение шлюза, не стандартное поле SAP. CRPT запись выполняется существующим RRL_PRODUCTION_API, регуляторный журнал — RRL_REGULATORY_API; прямого изменения внешних подтверждённых статусов нет. [Запуск и границы](../runbooks/nicora_ni01_sap_retail.md), [XML](../../exchange/contracts/ni01/README.md).
