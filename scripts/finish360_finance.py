from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
startup="../2026-10-12_ni071_monthly_rate/001_columns.sql"
if startup not in m["startup_scripts"]:m["startup_scripts"].append(startup)
for item in["../2026-10-12_ni071_monthly_rate/002_history_guard.sql","../2026-10-12_ni071_case_allocation/001_guard.sql"]:
 if item not in m["additional_scripts"]:m["additional_scripts"].append(item)
m["required_columns"].setdefault("RRL_LOGISTICS_RATE_HISTORY",[]).append("COMPONENTS_JSON")
out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
page="wiki/database/retailcase_ni071_monthly_case_20261012.md"
out[page]="""# Месячные общие работы и фактическая малая тара в прежнем биллинге
353/359 APPLIED в dev RABAEV/orcl, guards VALID. Структура прежних счетов, ставки BOX, cost run/lines и двухфазные расходы/распределение сохранены. Миграция353 добавляет nullable COMPONENTS_JSON к неизменяемой RATE_HISTORY; manual legacy versions имеют NULL и прежний replay.

POST /api/finance/logistics-costs/rates/monthly принимает месяц, базовую ставку, общую сумму месяца и объявленную расчётную базу коробок, ожидаемую версию, причину и документ. Decimal50 precision, ROUND_HALF_UP9 для доли, точные денежные суммы до копеек. Итог base+common/basis входит в существующий WAREHOUSE_PICKING BOX RATE_KEY. Native history guard проверяет seven-field provenance/first-of-month/date/count/integer/rounding/total и текущего финансового пользователя склада. Отдельный common-work expense или charge не создаётся. Расчётная база — DECLARED_MONTHLY_BOX_BASE, не выдаётся за автоматически подтверждённый фактический объём.

Actual354:800/1600=.5 plusbase2=2.5, immutableversion1; другая база400/800 с тем же итогом и старым version0 отказана409. Будущий manualv2=9 не изменил version1; originalrequest replay возвращает v1. Invalidmonth/zero422. История355: bounded keyset100/currentwarehouse/same readonly snapshot, страницы2→1 с точным компонентным provenance. UI logistics-costs использует прежний durableintent и позволяет сохранять месячную ставку/смотреть более ранние страницы. Состояния склада/валюты/пользователя отделены.

356–357: domain physical_boxes считает прежние CONTAINER BOX и измеренную малую CASE только при точном immutable proof по UID/CASE/version/finalscale/QC/signature/coverage/gross-tare-net. Новый сквозной источник не придуман. Actual SMALL211.LOAD:8258e0ab/trip33534/WARE38542432/CASE1112:1 physicalbox, measured .45/.1/.35KG, goods7EA/14oldcodes. Existing cost начислен2.50 один раз, monthly common.5 included; repeat стабильный/otherOP secondcharge denied. Trip and existing invoice detail показывают COMPONENTS именно замороженной RATE_HISTORY version1, не текущей head. Proof device_mode TEST — не аппаратная приёмка и не реальный платёж.

358–359: прежний expense actual_goods допускает frozen CASE STOCK leaves. Quantity7EA остаётся quantity, для single-leaf измеренной малой CASE Weight=.35KG из exactfull archivedproof. Нельзя распределить весь net на несколько неподтверждённых товарных листьев. WEIGHT_SOURCE=MEASURED_CASE_NET; native allocation guard проверяет APPLIED load/exactStockUID/article/qty/UOM плюс actualCASEBox/finalQC/versions/singlecarrierleaf/link/net/basis. Actual independent fixture LOGIST/FINANCE→2.01GEL allocated to original7EA/.35KG/one cents-preservingline/replay; QA logist retired. P20/H20 preserved, goods/invoice PRICE не перепроводятся.

Сохранённые источники: tmp/context354/355/357/358/359.json; script case357 и case359 повторяют существующие операции, не создавать source211 повторно. Native353 guard reserved-word SHARE исправлен на v_share; live invalid/errors пусты.

SQL360 runtime: allocINSERT46.089ms/194buf; CASEexact-net20.853ms/73buf; proof-by-load10.444ms/39buf; componentinvoice13.598ms/134buf; ratehistoryINSERT7.963ms/265buf. Решение finance: сохранить currentPK/load+box и bounded200/100 windows; при росте CASE allocation собрать единый batch frozen-source projection, ownerfinance backlog. DDL313/182ms не считаются оперативной нагрузкой. Миллионная производительность не заявлена.

Открыто: выбор нормативного периода по aware actual assembly-start/warehouse operating day вместо прежнего loaded UTC date, multi-warehouse expense resolver, полный состав других нормативных работ, реальные финансовые SAP contracts/independent/hardware. NS56/NS57 полностью не закрыты.
"""
p=Path("wiki/index.md");out[p.as_posix()]="- [Месячная ставка и измеренная CASE в биллинге](database/retailcase_ni071_monthly_case_20261012.md):353–359 shared.5 inside existing2.5BOX norm/history; actualsmallCASE cost1×2.5 and independent expense2.01 on7EA/.35KG.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 12.10.2026 353–360 nativeVALID: nullable immutable ratecomponents/monthly .5+2=2.5/current finance/native rounding guard/replayafterfuturev2/differentdeclaredbase409/historykeyset/UI. Actual oldSMALL211 archivedCASE1112 cost1BOX2.50 once; independent approvedexpense2.01 on7EA/.35KG via exactnative archivedCASEguard; no stock/payment/carrierinvoicechange/protected20/20. SQLruntime46/20/13/10ms boundedPK; financebatch backlog/loadedUTCperiod gap retained.\n"
p=Path("wiki/runbooks/retailcase_active_work.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\nCurrent360: native353/359VALID; APIserv355 routes monthly/history (new356358 runtime restart next). Finance contexts354rate61123418 v1monthly2.5/v2future9;357CASE1112/trip33534/WARE38542432 cost2.50/version1 monthly .5+2;359additional2.01 allocated7EA/.35KG, QAactorQF35933534 retired. ExistingSMALL211 factory forbidden. AdminTypeScript final afterfinanceUI pending; architecture6390cycles76. Next actual awareassemblystart/period or remainingNI08 shared admission; no fake timezone interpretation of legacy naiveCASEtimes.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni07_1.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n353–360: existing monthly common work norm2+.5=2.5 with immutable components/nativeguard/currentfinance/replay/history100pages/UI; actual archived measuredsmall CASE1BOXcost2.50 once and quantity7/net.35 basis for existing approvedexpense2.01 allocation. Futuremanualnorm preservesoldcharge/version. Period byware-aware assemblystart/multiwarehouse/fullnormbasis/realfinancialERP/independent remain; monthly declaredboxbase is not automatically actual volume. See retailcase_ni071_monthly_case_20261012.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
for x in m["increments"]:
 if x["id"]=="NI07.1":
  x["status"]="in_progress_monthly_components_case_sources"
  x.setdefault("implementedSlices",[]).append("353–360 monthly common-work included originalBOXrate/immutable components/currentfinance/history; measuredsmallCASE actual cost2.50 once and approvedextra2.01 on7EA/.35KG byexactnative archive source")
out[p.as_posix()]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI07.1/360_monthly_case.md").as_posix()]="# Qwen353–360\nMonthly declaredwork800/basis1600=.5 plusbase2=2.5; zero/invalidmonth/currentforeignWARE/version conflicts; same-total400/800 differentintent409; oldreplayafterfuture9 unchanged. Nativehistorycomponents exactfirstmonth/rate/rounding. Boundedkeyset history2→1 and user/ware/currency UI state. MeasuredCASE1112 archivedproof .45/.1/.35/source7EA14codes ->oneBOXcost2.50 once. Existing independentphase expense2.01 allocated7/.35 bynative exactfrozenCASE/stock/version/QC/net/link proof. Nodoublegoods/commonwork/financecharge; DeviceTEST notphysicalpilot. Source211 factory forbidden, contexts saved. Actual assembly-start period/multiwarehouse unresolved.\n"
print(json.dumps(out))
