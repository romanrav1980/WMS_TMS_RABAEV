import json
from pathlib import Path
out={}
page="wiki/database/retailcase_ni062_exception_returns_20261012.md"
out[page]='''# NI06.2: возврат отказанного и повреждённого товара
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
'''
entries=[("wiki/index.md","- [Возврат отказа и повреждений](database/retailcase_ni062_exception_returns_20261012.md):472–492 existing return owners/three caps/SAPv2/real custody/quarantine/tasks/supplier departure+disposal; buyer3/missing2 preserved.\n"),
("wiki/log.md","\n-12.10.2026 472–492: NI06.2 unified existing return owner with separate ACCEPTED/REFUSED/DAMAGED cap and exact observed unit state; v1 accepted/v2explicit SAP XML/native raw verify; modern unit read bounded/no N+1. Native477 rollback/denials; actual483 REF1+DAM1 approval/SAP/oldTT/handover/driverpickup/receipt,489 isolatedPUT,490independentdisposal/491existing supplierST/QC/LOAD/DEPART. Same two physical keys/QR2each, finalP0, originalbuyer3/missing2 untouched; original driver1 binding restored/tempusers retired. Current policy capture gate492. Immutable oldrecords retained; legalGovACK/aggregate-only/multiplace/qualityinspection open.\n"),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_2.md","\n472–492: implemented separate ACCEPTED/REFUSED/DAMAGED approvals + exact units/caps/SAPv2; actual refused1→existing supplier departure and damaged1→independent disposal via originalreturn transport/custody/warehouse/PUT. Original buyer3 and missing2 unchanged. See [[database/retailcase_ni062_exception_returns_20261012]]. Aggregate-only/multiplace/quality inspection/externalACK/independent remain.\n")]
for filename,entry in entries:
 p=Path(filename);s=p.read_text(encoding="utf-8");out[filename]=entry+s if filename=="wiki/index.md"else s+entry
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"));m["planRevision"]=16;m["date"]="2026-10-12";m["currentSprint"]="NI07.1"
for x in m["increments"]:
 if x["id"]=="NI06.2":
  x["status"]="in_progress_exception_return_disposition_delivered"
  x.setdefault("implementedSlices",[]).append("472–492 existing accepted/refused/damaged caps and exact unit states/SAPv2/actual custody-receipt-PUT/refused supplierdeparture+damageddisposal/buyer3-missing2 unchanged")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
q=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[str(q/"NI06.2"/"494_exception_returns.md")]='''# Qwen: separate delivery exception returns
Read wiki/database/retailcase_ni062_exception_returns_20261012.md. Retained context483 already disposed/delivered supplier: exact saved replays/read only, never initial477/483/489. Verify three independent cumulative caps; concurrent same basis, same physical key reuse, cross-basis/wrong key, missing/excess, current-marked/no capture, legacy/no partial evidence. V1 XML cannot bind nonaccepted approval; V2 exact original disposition/hash/fields, old accepted payload unchanged. Native outbox source basis/current permissions/ERP credit false; source receipt/FF unchanged, loss2 not closed. Modern dossier bounded one-unit query vs legacy fallback; UI basis filter/op uncertainresponse.
On fresh isolated fixture verify full physical custody/warehouse/task/supplier ordisposal, rollback each stock+unit+document+queue. Separate reporters/SC approvals. Hardware/governmentACK require real evidence; never infer from PENDING. Slow SQL decisions and limits. Report independent outcome without editing protected fixtures.
'''
p=Path("wiki/runbooks/retailcase_active_work.md");out[str(p)]="12Oct494: latest NI06.2 exceptions472–492/liveVALID/API489/planrev16. ctx483 complete REF1 supplier491/DAM1 disposal490/P0/buyer3+missing2 unchanged. Keep driver1 binding restored; tempusers retired. NI04.3 ctx462 original BOX1/PAL canceled, freshSAP464 received3/6. Next NI07.1.\n\n"+p.read_text(encoding="utf-8")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for name in ["../2026-10-12_ni043_aggregation_lifecycle/004_indexes.sql","../2026-10-12_ni062_return_basis/apply.sql"]:
 if name not in m["additional_scripts"]:m["additional_scripts"].append(name)
out[str(p)]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out))
