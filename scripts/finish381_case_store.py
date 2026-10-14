from pathlib import Path
import json
out={};d=Path("db/migrations/2026-10-12_ni053_marked_case_receipt")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text())
for file in ["001_units.sql","002_store.sql"]:
 value="../"+d.name+"/"+file
 if value not in m["additional_scripts"]:m["additional_scripts"].append(value)
out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
page="wiki/database/retailcase_ni053_marked_case_20261012.md"
out[page]="""# Покупатель принимает маркированное CASE
379 APPLIED dev RABAEV/orcl; all nativeVALID. Existing STORE_RECEIPT/markedunitdispositions/weight-photo/custody/orderdelivery preserved. Stock is not received a second time at the customer.

RRL_INTERWARE_UNIT_SOURCE.issued_manifest accepts APPLIED frozen HU_SHIP/LOAD_SHIPMENT CASE+CONTAINER+STOCK archive. New private assert_case_archive proves each archived CASE against current exact SHIPPED operation/WARE/SSCC/version+1, each CASE-tagged STOCK against actual CASE_CARRIER_LOT plus archivedCASE. It still proves exact stockleafquantity/UOM/issuedunitset/original physical_before fingerprint. StoreMark accepts CASE nodes and declares CASE rowlocks in addition to existing stock closures. Current perSKU profile/version/quantity coverage retained; no product barcode or skipped profile can substitute for unit QR.

Actual376 newly assembledCASE1122/7EA/14oldCRPT+EGAIS codes/.450-.100=.350KG plusouter1=1.45, independentwarehouse TESTQC/native shipment/departure; actual TSTZstart retained. Source remaining5 cleaned only through original nativeinventorycommands, no factory211 recreation.

Actual380 bound nonadmin shop/gateway, originalthree photo views, addressed synthetic store scale: measured1.224999999 refused at tolerance.225;1.225 inclusive accepted. Missing one required profile refused STORE_MARK_ALL_UNIT_PROFILES_REQUIRED. Full14QR ->existing receipt7accepted/same7physicalkeys, orderaccepted7, oneoutbox/noquantityevents, replay before retirement, whole original source quantities untouched. QA actors retired after case. Context380 stores request/result/order without passwords. No initial source376 or receipt380 factory rerun. Printed old copied208 label says6/.4; actual assertions/context prove7/.45/.35.

Financial377 same newCASE: explicit synthetic Pacific/Kiritimati fixture region gives12Oct whileloadedUTC11Oct. PolicyCASE chooses day12 rate3 (v2), not day11 rate2(v1), actual1BOX3.00 once/nativeproof/replay/frozenbillperiod. This timezone is a synthetic test input, not a statement about RETAILCASE geography. RuntimeJSON_TABLE alias UID collided with Oracle builtin in CASE branch; final UID_VALUE/KIND_VALUE/PERIOD_KIND_VALUE compiled and actual377 passed. OldCASE naive starts still not fabricated.

CASEpartial missing/refused/damaged uses existing unitdisposition mechanism but needs an actual CASE-specific positive scenario; aggregate-only store acceptance and physicalscale/government/independent verification remain. Firstlegwarehouse CASE receiving is not declared supported by this recipient-only increment.
"""
for file,text in [
 ("wiki/index.md","- [Приёмка маркированного CASE покупателем](database/retailcase_ni053_marked_case_20261012.md):379–380 exact archivedCASE/7EA14codes/.225weightboundary/3photos/nonadmin/actualaccepted7/oneoutbox/no stock;377actualassembly-date cost3.00.\n"),
 ("wiki/log.md","\n- 12.10.2026 376–381: originalnewmarkedCASE1122/7EA14codes/awarestart/TESTwarehouseQC/HUload/depart. Actualfin377 nativeCASE calendar12Oct choosesrate3 versusloadedUTC11Oct rate2,1BOX3.00/frozenbillperiod/replay. Native379 recipientCASE-source/stockcarrier proof andCASErowlocks/currentprofiles/fingerprints VALID. Actual380 nonadmin3photos/storeTEST1.225/.225inclusive/epsilonrefusal/incompleteprofiledenied/full14QR accepted7/order7/oneoutbox/noquantityjournal/replay/actorsretired/P20H20. No source211 recreation or governmentACK. CASEpartial/aggregation/hardware independent remain.\n"),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni05_3.md","\n379–380 marked measured CASE accepted by existing shop receipt: exact archivedSHIPPEDCASE/carrierlots/originalunitfingerprints/currentprofiles/CASErowlocks; actual7EA14QR/nonadmin3photos/.225inclusive/epsilonrefusal/missingprofile409/orderaccepted7/replay/outbox1/no secondP. CASEpartial statuses/aggregate-only recipient/hardware/independent remaining.\n"),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","\n376–380 newly assembled measured markedCASE7/14QR/actualTSTZstart/fulloriginalwarehouse flow ->customeraccepted7/.225 tolerance/3views/native exactcarrierproof; this covers full markedsmall recipient software path. Physicalequipment andindependent acceptance still pending.\n"),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni07_1.md","\n377 positive newly assembledCASE actualcalendar date12Oct versusloadedUTC11Oct: exactCASEperiod policy choosesrate3(v2) ratherthan2(v1), oneBOX3.00/nativeproof/replay/frozenoriginalbilldate. RegionPacific/Kiritimati is explicit syntheticfixture only. PositiveCASEassembly-charge gap closed forsingleCASE/singleperiod; ordinaryBOX assembly linkage/multiple days/othernorms/realfinancialSAP remain.\n")]:
 p=Path(file);old=p.read_text(encoding="utf-8");out[file]=text+old if file=="wiki/index.md"else old+text
p=Path("wiki/runbooks/retailcase_active_work.md");t=p.read_text(encoding="utf-8");a=t.index("Current native");b=t.index("## Последняя функциональность",a)
t=t[:a]+"""Current native379/app373, APIserv366 (latest invoice-period read373 pending restart). Current compiled objects VALID. Architecture641/0cycles/76debt, adminTS373 passed, encoding366 passed; current wiki edits need final encoding. Native bundle includes current migrations; never full-apply over ACTIVE.

Latest:367–374 recovery1+1/original1 inoneTOP/threeST deliveredbuyer3/sourceFF3once. 361/376 actualCASE start TSTZ (legacy assignedshift timezone unknown);363 financialperiodpolicy/version/nativeexactdate,377 actualnewCASE date-boundary charge3.00 once. 379–380 markedsmallCASE7/14QR fullcustomerreceipt/nonadmin/3photos/.225weightboundary, no secondquantitywriter.

Retained fullydelivered contexts372(recovery),380(CASE),319/326(nested),330/336/342/348(consolidation). Context377 is immutable financecharge. Never rerun initial factories or originalP assertions. Source307 remains separate: accepted1+found1 inquarantine+oneunitmissing; no false fullrecovery.

Next: CASE-specific partialdispositions or groupedmultiSKU firstleg receiving; ordinaryBOX assembly linkage/multiday financial dimensions; NI08 configured/legal/external duty admission. RealproviderACK/hardware/independent verification remain open; no legal readiness invented.

"""+t[b:];out[p.as_posix()]=t
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
for x in m["increments"]:
 if x["id"]=="NI05.3":x.setdefault("implementedSlices",[]).append("379–380 exact frozen markedCASE7/14QR recipient/nonadminweightphoto/currentprofiles/carrierfingerprints/orderaccepted7/replay/no secondstock")
 if x["id"]=="NI07.1":x.setdefault("implementedSlices",[]).append("377 positiveactualCASEassemblycalendar differsloadedUTC selects3 ratherthan2/oneBOX3.00/frozenbillperiod/nativeproof/replay")
out[p.as_posix()]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI05.3/381_marked_case.md").as_posix()]="# Qwen379–380\nRetainedcontext380 actual accepted7/14QR CASE1122/threephotos/nonadmin/.225inclusive/epsilonrefusal/profilecoverage409/outbox1/noquantityevents/replay before retiredactor. Exact frozenCASE SHIPPEDop/WARE/SSCC/version+1/carrierstocklot/fingerprint/currentprofile required. Originalsource376 andreceipt380 factories forbidden. CASEspecific partial/aggregate-only/physicaldevice/GovACK stillpending. Do not reinterpret naiveCASE time.\n"
out[(root/"NI07.1/377_actual_case_period.md").as_posix()]="# Qwen377\nRetainedcontext377 actualnewCASE awarestart ->syntheticexplicitPacific/Kiritimati12Oct versusloadedUTC11Oct. CurrentwarehousepolicyCASE ->rate3(v2) ratherthan2(v1), original1BOX3.00 once/frozenbilldate/replay/noP. Native JSON_TABLE UID alias fixed to UID_VALUE; legacytime stillblocked. Do not claim real RETAILCASEtimezone or rerun376 factory. OrdinaryBOX linkage/multidaydimensions remain.\n"
p=Path("scripts/case380_marked_small_receipt.py");t=p.read_text(encoding="utf-8").replace("PASS380 existing departed measuredCASE6/.400 + outer1=1.4, nonadmin store actual synthetic1.2 inclusive .2 tolerance, epsilon refused, 3 original views, accepted6/replay/outbox1/no quantity journal/no second stock/no government ACK","PASS380 markedCASE7/.450-.100=.350 +outer1=1.45/14oldQR/nonadmin3views/synthetic1.225/.225inclusive/epsilon-and-profile refusals/accepted7/replay/outbox1/no stock/no GovACK");out[p.as_posix()]=t
print(json.dumps(out))
