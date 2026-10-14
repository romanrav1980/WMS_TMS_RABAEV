# NI06.2: возврат отказанного и повреждённого товара
12.10.2026. [Migration472–492](../../db/migrations/2026-10-12_ni062_return_basis/apply.sql). Existing command STORE_RETURN_APPROVE, затем прежние SAP bind / transport / custody / warehouse receipt / PUT / supplier dispatch или disposal. Второго процесса количества нет: RRL_STOCK_POSTING_API остаётся единственным writer.

RRL_STORE_RETURN_APPROVAL.RETURN_BASIS: ACCEPTED(default для старых записей), REFUSED, DAMAGED. Для каждой исходной receipt line — отдельный cumulative cap по соответствующему факту приёмки. Все основания блокируют исходную строку в прежнем глобальном порядке; точные единицы дополнительно блокируются UNIT anchors. Уникальный физический ключ нельзя согласовать дважды. MISSING/EXTRA не являются разрешённым основанием возврата. Выбор единиц должен совпадать с UNIT_DISPOSITION и BASE Qty/UOM/version исходного APPLIED STORE_RECEIPT; все исходные коды сохраняются. Legacy full accepted proof сохраняется для ACCEPTED; отказ/повреждение маркированного legacy без точного unit evidence не выдумываются. Current marked policy требует capture уже при approval492.

REUSE для REFUSED/DAMAGED в этом инкременте запрещён: требуется отдельный процесс инспекции и допуска качества. SUPPLIER или DISPOSAL разрешены соответствующим решением. Возврат исключения не увеличивает/не меняет accepted quantity магазина, не меняет original fulfillment и не создаёт финансовую квитанцию ERP. Зоны приёмки/хранения возвратов недоступны обычному резервированию по прежним cell rules.

Предполагаемый gateway WarehouseStoreReturn:
- Version1 прежний exact contract — только ACCEPTED.
- Version2 добавляет обязательный OriginalReceiptDisposition=ACCEPTED/REFUSED/DAMAGED.
- Native проверяет исходный XML/hash/версию/поля и совпадение disposition с неизменяемым approval; v1 не может легализовать REFUSED/DAMAGED.
Это локальный согласуемый XML контракт, не стандартный SAP IDoc. Подтверждения SAP и государственных операторов не заявлены. В последующих native transport/custody/receiving domain добавлен return_basis для non-accepted; он идёт в frozen outbox. Старые APPLIED результаты не переписываются.

Существующий dossier/UI показывает три остатка согласования и точные eligible unit keys по основанию; тип явно выбирается оператором. Современные unit facts читаются одной bounded выборкой, вместо N+1 по каждой строке; legacy accepted fallback сохраняется. reuse-preview считает только ACCEPTED approvals. Basis видна в transport/store/warehouse read models. Старые HTTP payload/hash не меняются: default ACCEPTED поле не добавляется в canonical metadata.

Доказательства автора:
-477: исходная383 accepted3/missing2/refused1/damaged1 даёт5 eligible observed keys. Native approval1 REFUSED и1 DAMAGED, полные rollback; wrong keys/type, MISSING, excess и REUSE исключения отказаны.
-483/484/486: конкурентное согласование REFUSED1 (200/409, один winner), DAMAGED1, SAPv1 отказ/SAPv2 импорт, существующий originalTT33534, store handover, временная привязка настоящего driver1 к тестовому пользователю, QR2 каждой единицы, две warehouse receipts1/P1H0 в карантине. Привязка водителя восстановлена, временный пользователь retired. Retained fixture article QPB2118258E0AB имел общий тестовый GTIN: добавлен уникальный прежний BARCODE_KOR QBOX483c09bc5c0, resolver не ослаблялся. Партия и срок взяты из оригинала, не заменены произвольными.
-489: по1 в две отдельные returns target cells через существующие задания; точные ключи сохранены, обычная allocation отказана.
-490: DAMAGED1 проведён через прежнее disposal: отдельный reporter/SC decision, SAME physical key, P0, CRPT/EGAIS notifications PENDING/no ACK, replay.
-491: REFUSED1 прошёл прежний PALL_SPLITTER→supplier ST→назначение→QC2→native physical LOAD/DEPART. P0/H0, тот же ключ/коды; late rollback/load replay. Два сообщения CRPT/EGAIS pending, не квитанции. Supplier trip новый существующего типа; нового allocator/quantity writer нет.
-Оригинал383 остаётся accepted3/missing2/refused1/damaged1; available accepted-return cap3 не уменьшен исключениями. Недостача2 не закрыта фиктивным возвратом. tmp/context483.json хранит завершённые операции; исходные factories/check477/initial483 не повторять.
- Native live USER_ERRORS/INVALID empty. Independent Qwen/сканер/real SAP/Gov/production throughput не проверены.

Границы: aggregate-only возвращаемой маркированной упаковки, отдельная инспекция отказанного товара для REUSE, multi-place return custody, юридическая обработка внешних подтверждений и независимая приёмка остаются открытыми. Возврат товара не доказывает возврат тары: tare registry отдельный.

SQL493: cumulative per-source/basis0.34ms/2buffers, approvalINSERT4.906ms, modern eligible read25.888ms/180buffers, XMLfield proof25.894ms. Decision: retain receipt/line indices and same-line serialization; modern units read batched; bounded10000/16KBXML. Owner finance/inventory to revisit cumulative materialised quota only above1000 approvals per line or measured50ms; no redundant counter now. Physical supplier/disposal complete489–491; API504 current.
