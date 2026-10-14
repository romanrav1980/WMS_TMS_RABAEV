import json
from pathlib import Path
out={}
out["wiki/database/retailcase_ni071_revision_summary_20261012.md"]='''# NI07.1: редакция периода и сводка начислений
12.10.2026. [497/503 SQL](../../db/migrations/2026-10-12_ni071_rate_revision/apply.sql). Owner finance. Количества товара не изменяются.

Прежний API и UNIQUE(RATE_KEY,EFFECTIVE_FROM) запрещали вторую редакцию одной даты. Теперь новая редакция того же последнего периода допускается с ожидаемой текущей версией, причиной и документом. PK(RATE_KEY,VERSION_NO) сохраняет историю. Date uniqueness удаляется только после проверки отсутствия зависимых FK; добавлен индекс(RATE_KEY,EFFECTIVE_FROM DESC,VERSION_NO DESC). Python calculation и Oracle cost-line guard выбирают последнюю применимую дату и на ней максимальную VERSION_NO. Более ранний период после позднего уже опубликованного периода не переписывается этим API: требуются отдельные финансовые коррекции. Повтор исходной редакции остаётся идемпотентным; конфликт текущей версии отказан.

Существующие начисления immutable. Изменение ставок не пересчитывает сохранённый cost run. Source load не оплачивается повторно; финансовый outbox признаёт начисление один раз. При наличии committed same-period revisions rollback к date uniqueness запрещён; forward repair, исходный guard сохранён. Глобального изменения запаса/stock-trigger не вводилось.

GET /api/finance/logistics-costs/billing-orders/{invoice}/summary возвращает существующие строки, группировку по WARE/business date/period policy/rate version/currency/basis и раздельные currency totals. Decimal80 без binary float; сумма — исходные recognized costs по доступным текущему пользователю складам. Она не включает corrections/extra expenses и не является суммой счёта перевозчика. Duplicate sources/nonfinite/subcent amounts отказаны; отсутствующая историческая дата не выдумывается. Те же warehouse filters/500-row bound сохраняются. В существующем BillingWarehouseCosts добавлены группы, итоги и раскрываемые источники; суммы вычисляются сервером. Oracle to_char decimal separator фиксирован.

Авторские доказательства:
-498 pure projection: разные даты/ставки/склады/валюты раздельно, сумма large cents точна; invalid/duplicates отказаны. Это модельный тест группировки, не доказательство multiple-day charge внутри одного HU.
-499 свежий действительный measured CASE1123/WARE39819118/TT33620:7 физических единиц/14 codes, одна коробка. Начало имеет aware instant; source first attempt interrupted API restart before goods/warehouse creation, resumed exact progress500 без повторного рождения. Retained tmp/context499.json; не повторять source factory.
-502: месяц2026-10 rates v1=2+.5=2.5, v2=2+1=3 same effective date; фактическое BOX1 начисление3.00/v2. После v3=4 и futurev4=9 exact old operation возвращает3.00/v2; другое operation ID не начисляет место повторно. Trip rows/root summary3GEL/HTTPexisting invoice summary contract; P0/H0 unchanged.
-505: native forged stale same-date rate denied LOGISTICS_COST_ACTUAL_SOURCE_RATE_REQUIRED; outer rollback removes transient foreign run; original line3/v2 remains once.
-Architecture648/0cycles/76debt PASS, admin TypeScript PASS, encoding PASS before final docs. Native live errors/invalid empty.

Границы: ordinary BOX assembly clock, несколько дат CASE внутри одного load (пока отказ), остальные нормативные основания/real financial ERP agreement/independent acceptance остаются открытыми. UI не объявляет полную сумму скрытых складов или carrier bill. Hardware/government ACK не относятся к этому финансовому доказательству.
'''
for filename,entry in [
("wiki/index.md","- [Редакции периода и сводка затрат](database/retailcase_ni071_revision_summary_20261012.md):495–505 same-month revisions/deterministic date+version/native stale refusal/actualBOX1 charge3 frozenv2/scoped exact invoice groups.\n"),
("wiki/log.md","\n-12.10.2026 495–505: NI07.1 exact scoped invoice warehouse/date/rate/currency grouping and existingUI; new same-last-period revision replaces previous date uniqueness, preserves versionPK/immutable charges; dated-version index/native+Python stable selector. Fresh499 measuredCASE1123/TT33620/7units14codes,502norm2.5→3 actualcost3(v2),later4/future9 keepold3/no duplicate;505 native stale rate denied/rollback. API504/adminTS/architecture648 passed; multidaywithinload/ordinaryBOX source/realERP/independent remain.\n"),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni07_1.md","\n495–505: same latest-period/month norm revisions + max VERSION tie selector in Python/Oracle, immutable original charges/source uniqueness; fresh measuredCASE BOX1 cost3(v2),later4/future9 preserve replay3, native oldrate refused. Exact scoped invoice summary byWARE/date/rate/currency/typed existing UI. Source not actual multi-day oneHU charge; that and ordinaryBOX assembly source remain. See [[database/retailcase_ni071_revision_summary_20261012]].\n")]:
 p=Path(filename);s=p.read_text(encoding="utf-8");out[filename]=entry+s if filename=="wiki/index.md"else s+entry
# Decisions from prior cases, append without rewriting immutable evidence.
for filename,entry in [
("wiki/database/retailcase_ni043_aggregation_lifecycle_20261012.md","\nSQL466/468/469: old ancestor query22.575ms/225buffers; changed to one exact manifest graph per query, new cold39.16ms/170buffers (not a throughput improvement claim). UID-use/block-op indices added. Decision inventory: preserve 1000/10000 bounds; large-graph edge materialisation/batch only when measured fanout requires it. API470/then504 current.\n"),
("wiki/database/retailcase_ni062_exception_returns_20261012.md","\nSQL493: cumulative per-source/basis0.34ms/2buffers, approvalINSERT4.906ms, modern eligible read25.888ms/180buffers, XMLfield proof25.894ms. Decision: retain receipt/line indices and same-line serialization; modern units read batched; bounded10000/16KBXML. Owner finance/inventory to revisit cumulative materialised quota only above1000 approvals per line or measured50ms; no redundant counter now. Physical supplier/disposal complete489–491; API504 current.\n")]:
 p=Path(filename);out[filename]=p.read_text(encoding="utf-8")+entry
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"));m["date"]="2026-10-12";m["planRevision"]=17;m["currentSprint"]="NI07.1"
for x in m["increments"]:
 if x["id"]=="NI07.1":
  x["status"]="in_progress_period_revision_summary_delivered"
  x.setdefault("implementedSlices",[]).append("495–505 same last-period monthly revisions/date-version native guard/actualBOX1 cost3 immutablev2/scoped exact invoice summary/UI")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
q=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[str(q/"NI07.1"/"507_revision_summary.md")]='''# Qwen: monthly revision and invoice summary
Read wiki/database/retailcase_ni071_revision_summary_20261012.md. Context502 already committed: exact replays only, never source499 initial. Verify expected version+same latest effective date, stale/new/future rates, independent revisions collision, native direct stale date/version refusal and whole transaction rollback. Old cost/outbox/source P/H unchanged, no duplicate load charge. Oracle date uniqueness removed only with no FK dependency; version PK/history/index retained; forward repair after committed revisions. Decimal groups preserve dates/WARE/rate versions/currencies, no float/subcent/duplicate source. Existing current user warehouse filters, partial visible totals labeled; old unknown date not fabricated; summary excludes corrections/expenses/carrier bill. Test UI switching invoice and faults. Multi-day charging inside one load is still refused, do not mark it accepted from summary test. Real ERP/independent/hardware evidence separately.
'''
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));name="../2026-10-12_ni071_rate_revision/apply.sql"
if name not in m["additional_scripts"]:m["additional_scripts"].append(name)
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki/runbooks/retailcase_active_work.md");out[str(p)]="12Oct507: latest finance495–505/planrev17/API504/currentNativeVALID. ctx502 costBOX1=3/v2 frozen after4/future9, sameperiod version history preserved. ctx499 shippedCASE7/14codes P0 source, no buyerreceipt yet. ctx483 REF1 supplier491/DAM1 disposal490 completed P0/buyer3+missing2 preserved. No initial fixtures rerun. Next NI07.1 ordinaryBOX assembly/multiday charging; remaining external/independent cannot be assumed.\n\n"+p.read_text(encoding="utf-8")
print(json.dumps(out))
