from pathlib import Path
import json
out={}
out["wiki/components/nicora_ni011_receipt_layout_20261011.md"]="""# NI01.1: список SAP и изменяемая укладка
260 integrations supply_reads extracts original supplylist/detail/document read into one READ ONLY cursor. Current active RUSERS+sap_supply_view; GLOBAL_ADMIN allwares, ordinaryuser onlycurrentWARE; explicitforeignfilter/detail/document403. Filterbefore200worklist cap; detail<=1000lines failoverflow, original accepted-pallet/Decimal/norm suggestion preserved. Header/lines/acceptedqty/policyversions one snapshot. Actual actor passedtypedport/APIs, no caller-supplied actor. This changes readbehavior, no import/receipt writer duplicated.
Case260 existing originalsupplies in twoWAREs, ownrole seesownlist/defaultWARE/detail/document/HTTP200/currentresponse consistent_snapshot, foreign403/changeduserWARE/revokedright denied. Onlyone ownSR260 user reusedandretired; initialHTTP worker was oldsource, hiddenrootserv260 restart and reusedsameactor provedcurrentwire. Protected20/20/no goods. SQL12.334ms5 detail/10.842ms1 currentlist: keepexisting supplyOrder/line/sourcepallet indexes and1000bound; ownerintegrations bulkaccepted-quantity query if1000lineprofile expensive.
261 inventory/domain receipt_layout exports through inventory/public to SAPowner. Existing norma_ukladki default proposal expandedwithcount1..200 or explicitquantitylist/optionalquantum. ExistingPIECE_UNITS helper retainswholepiece step1; exactFraction ticks +Decimal atmost6fractiondigits, largest-remainder count distribution retains exactsum. Defaultnorm groupsfull+last; manualsubset allowed but unplannedqtyexplicit; empty/zero/nonfinite/finerpiece/overcurrent/refusal; aboveNorm informativeonly, no fakecell/weight capacity certification.
API pallet-plan current scoped source snapshot/source_signature expectedoptional; response not stock/label/task/reservation. Separate rawreceiving-layout component triggeredcurrentorder/line showscount/quantities/units/aboveNorm/unplanned; no auto physicalcommand or label alteration. Operators stillscan batch/expiry/codes per actual pallet.
Case261 normal10/4→4,4,2; more4→3,3,2,2; fewer2→5,5aboveNorm; explicit4+3 leaves3; weighted1.000001 split3 exact; impossiblepiece/over/0/0.5refused; actualexisting remaining source currentREADONLY/strict signature conflict/HTTP200/protected20/20. Architecture587files0cycles76debt/rawJSsyntaxPASS. CurrentAPIserv261; noOracleDDL or newquantitywriter. Author evidence not realERP/physicalscanner/independentfull acceptance.
Historical wiki/database/nicora_ni01_sap_retail.md 7Oct reference to enabled legacytrigger is historical, superseded by8Oct fullstock cutover. Current onlyRRL_STOCK_POSTING_API ACTIVE/compatibilityOFF. No return to trigger stock writer.
"""
for path,line in [
("wiki/index.md","- [Приёмка SAP: доступ и укладка](components/nicora_ni011_receipt_layout_20261011.md):260 scoped same snapshot originalsource/261 count/manualexactlayout/no newstockwriter."),
("wiki/log.md","2026-10-11:260 currentSAP worklist/detail/document nativeRUSERSWare/right singleREADONLY/port actor/sourceextraction/foreign403/changeWare/revoke/oneSR260retired/protected20-20.261 inventory-owned originalnorm count/manualsplit/PIECE_UNITS step1/exactDecimalFraction/max200/unplannedexplicit/typedAPI/signature/currentrawUI; actualremainingHTTP200/no stock-label-reserve or task.5870cycles76/rawJS; SQL12.334ms5/10.842ms1 existingboundedkeysretainownerintegrations. OldNI01trigger description historicalsuperseded currentACTIVE singleRoot."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni01_1.md","11.10.2026:260 currentWARE SAP list/detail/document sameSnapshot actualactor;261 originalnorm expandedexact count/manual quantities/sourceSignature/partialunplanned/PIECE_UNITS/receiving separateUI. Existing actualreceive Root labels andputtasks reused. FullERP externalcontract/ACK/physical acceptance remain."),
("wiki/database/nicora_ni01_sap_retail.md","11.10.2026 correction: the 7Oct enabledlegacytrigger description above is historical source state; full8Oct stockcutover supersedes it. Current RRL_STOCK_POSTING_API ACTIVE/compatibilityOFF is sole quantity writer. 260/261 scoped same-snapshot originalSAP reads and inventory-owned exact layout proposal, see [[../components/nicora_ni011_receipt_layout_20261011]].")
]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));inc=next(x for x in j["increments"]if x["id"]=="NI01.1")
inc["status"]="in_progress_bounded_receipt_layout";inc.setdefault("implementedSlices",[]).extend(["260 currentWare/readright sameSnapshot originalSAP source/detail/document","261 originalnorm/count/manual exactlayout/sourceSignature/partialunplanned/rawUI"])
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[str(root/"NI01.1"/"260_261_receipt_layout.md")]="# Qwen:260–261 — SAP и укладка\nCurrentactor Ware/right beforeworklist cap; scopedall reads current snapshot/headeracceptedqty/policy/norm, foreigndetail/document/filter403 andremovedreadright denied. Existing service signatures nowactorrequired, nooptionaladmin fallback. Originalreceipt Root andlabels unchanged. Count/manuallayout exact quantum/PIECE_UNITS1/no float, leftoverexplicit/overlimitrefused/signature changedSource denied. Layout is proposal noStock/HU/place admission/reservation and no physicalscanner proof. 260oneSR260actor retired, don'tcreate newfixture;261 tmp/context261 existsreadonlysource. SQL1000line bulkprofile futuredecision ownerintegrations.\n"
out["wiki/runbooks/nicora_active_work.md"]="""# NICORA: текущая работа
Приоритет — 18 функциональных инкрементов NICORA. Исходные 17 спринтов TMS2 выполнены; не создавать повторно готовые ВМС/ТМС функции. Продолжать до завершения всех инкрементов или 12.10.2026 06:00 МСК (03:00 UTC). GitHub требует нового прямого поручения; субагенты в этой сессии запрещены. Минимум80% — функционал, проверки только изменённого поведения.

## Действующее окружение
RABAEV@127.0.0.1:1521/orcl — выделенный dev. Единственный quantitywriter RRL_STOCK_POSTING_API, ACTIVE/compatibilityOFF. Карантин — недоступные ячейки. Без копии БД, новой схемы или инстанса.
Native manifest259: time materialV2/approval256, original route estimate259, regulatorywarehouseindex252, plannedDEFAULT253, awarefutureTaskFinish254. Bundle генерируется, не применяется целиком на ACTIVE.
App261/APIserv261, rootserv.bat/front.bat/terminal.bat. После native recompilation restart rootserver и дождаться нового Application startup complete; иначеORA04068 pool/sameID retry. Не выводить settings/passwords/serverstdout.

## Последняя функциональность
[[../database/nicora_ni081_route_input_20261011]]: existing33564 future14Oct/route45+50/12sameOPS IDs/native appendjournal1/currentTimeV2/Tbilisi/95min; manualestimate не realrouting или law.
[[../components/nicora_ni081_driver_rest_20261011]] и [[../components/nicora_ni081_driver_day_20261011]]: explicitREST, plannedcontinuity and driverday sameSnapshot/ownzones/exactmidnight/unknowns, без юридического допуска.
[[../components/nicora_ni011_receipt_layout_20261011]]: currentWARE SAP list/detail/document snapshot и exact count/manual palletproposal. Noqty/labels/tasks createdbyproposal. NativeRoot receipt unchanged.

## Сохранённые сценарии — не рождать заново
tmp/context254.json tag4ecffb36dd: sourceWARE5265051→55265051/task979/sourceTT33569→33570, receipt/PUT980/ST641394/load/depart done; original3units6codesISSUED10/P0. Не запускать source254/continue255/resume255/loadedreview256.
tmp/context259.json: existingempty33564routejournal1 +TimeV2 alreadydone; case259 start assumesjournal0, не повторять. Source clock rollback restored, customDOCK_ASSIGN restored.
tmp/context261.json existingERP remaining proposal read only; SR260 actor retired.
ProtectedWARE6667491/SKUQNATIVED9A5C53B54 P20/H20/wave395/cases1031+1032 unchanged.
Original219/221/224TT33541 pendingST/tarehandoffHELD1 — не подделывать закрытие/освобождение. Original230partialStore custody retained; requiresexplicitmissing disposition.

## Далее
CurrentNI08.1/NI01.1 bounded increments; planrev13 18increments/68NS/363scenarios preserved. Other earlierimplemented baseline deltas mayhave stale planned labels: wiki evidence first.
Remaining full driver duty/legal/realrouting-storewindows/sharedadmission and realERP/government/hardware/independent acceptance not complete. Never markwhole allaccepted because boundeddevcases pass.
Next functional work: durable receipt UI recovery before editable-layout-to-command integration; remaining missing-delivery ownership, originalsplit source and calendar exceptions. Read relevant smallest wiki before rawsources.
Architecture last587files0cycles76debt; maintain modules/public boundaries/no legacy filegrowth. All nativeVALID last259. SQL scoped source bounds/currentPK retained, ownerdecisions in linkedwiki. Encoding aftermaintained edits.
"""
p=Path("wiki/index.md");s=out["wiki/index.md"];s=s.replace("onramp11Oct/current manifest250/app251/planrev13/next remaining functional scope.","onramp11Oct/current native259/app261/planrev13/remaining functional scope.")
out["wiki/index.md"]=s
print(json.dumps(out,ensure_ascii=True))
