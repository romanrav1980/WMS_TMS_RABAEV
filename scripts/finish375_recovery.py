from pathlib import Path
import json
out={};d=Path("db/migrations/2026-10-12_ni061_recovery_consolidation")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text())
for key,files in [("startup_scripts",["001_key.sql"]),("additional_scripts",["002_next.sql","003_ship.sql","004_dispatch_guard.sql"])]:
 for file in files:
  value="../"+d.name+"/"+file
  if value not in m[key]:m[key].append(value)
out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
out[(d/"000_before_dispatch_guard.sql").as_posix()]=Path("db/migrations/2026-10-11_ni061_recovery_redelivery/004_dispatch_guard.sql").read_text().split("create or replace trigger RRL_IW_REC_ST_IMMUTABLE")[0]
p=d/"rollback.sql";out[p.as_posix()]=p.read_text().replace("@@000_before_ship.sql","@@000_before_ship.sql\n@@000_before_dispatch_guard.sql")
page="wiki/database/nicora_ni061_recovery_consolidation_20261012.md"
out[page]="""# Найденный товар в общем физическом месте
Миграция2026-10-12-367-recovery-consolidated-dispatch APPLIED RABAEV/orcl, all currentVALID. Переиспользованы recovery approval/receipt/placement, ST constructor/assignment, QC, HU_SHIP, departure и STORE receipt. Не добавлен второй shipment/fulfillment writer.

RRL_IW_RECOVERY_DISPATCH PK теперь OPERATION_ID+ST_ID; BIND_OPERATION_ID/RECOVERY_OPERATION_ID unique сохранены. Outbox EVENT_ID hash(operation+ST), поэтому несколько correctiveST одного HUcommand не теряют сообщения. Dispatch rowanchor по operation сохраняется: immutable writes только в одной native captured operation, никакого последующего update/delete. Source validators повторно проверяют eachwholeplacedreceipt/currentactor/WARE/trip/unitfingerprint и exact captured HU shipment binding.

HU compiler допускает recovery вместе с originalonward в bounded200 STOCK/CONTAINER tree, same existing whole leaf consumption/current perSKU UNIT matrices. Recovery guard принимает только captured LOAD_SHIPMENT/HU_SHIP в actual nativeTX; HUbranch сверяет resolved recovery ID+binding+ST отдельно, затем immutable bind/recovery/placement/source qty/UOM. Старое REQUIRE_COMMAND LOAD_SHIPMENT-only давало отказ на пробном HU load; исправлено explicit nativebranch, без снятия guards.

Actual source368:3old marked units/6codes shipped firstleg; accepted1, independentlyconfirmedloss2, found1+found1 by exact oldkeys/codes, three originaltasks placed1each. Existing custody/ST/assignment/QC -> oneTOP IH372:c7f60695a8/threeST. Trial373 twoexact recoverydispatch+oneoriginal/P0 then wholetransactionrollback restoredP1each/dispatch0. Actual373 thenDEPART374+STORE374: buyeraccepted3/unreceived0, originalFF3 once, history2-found2-net0, old6codes retained, protected P20/H20 unchanged. Context372 fully delivered; source368/found/initial373 factories forbidden. Replay complete originalcachedreceipts only.

Transport capacity still plans three logicalSTplaces; fixture ownvehicle PALLETS3, physicalloadoneTOP. Do not claim automatic planning capacity saving. No real governmentACK/hardwareproof.

SQL374 dispatch INSERT5.995ms/271buf fourexec; sourcebindlookup.198ms/83exec; constructorproof11.729ms/104buf; legacyFFread10.175ms; currentbound selection13.394ms. Inventory decision: retain STunique/bind/receipt indexes/200nodebound; batch source binding projection if grouped receiving grows, ownerinventory backlog. No million-op claim.

Remaining: firstleg groupedmultiSKU receiving preservingtop/group contract; repeatedphysical shortagecycle; aggregation-only recipient modes; real regulationACK/independent Qwen. Recoveryconsolidation is now covered, wholeNI06.1 not complete.
"""
for file,text in [
 ("wiki/index.md","- [Консолидация найденного товара](database/nicora_ni061_recovery_consolidation_20261012.md):367–374 original1+found1+1/3ST/oneTOP/6oldcodes/actualSTOREbuyer3/FF3once/rollback-replay.\n"),
 ("wiki/log.md","\n- 12.10.2026 367–375 APPLIED/VALID: recoverydispatch compositeOP+ST/outboxperST/exactnativecapturedlineage; original/recovery wholeST consolidated inoneHU. Actual368 firstleg3 accepted1/lost2/found1+1; existingtasks/ST/QC/HUSHIP/DEPART/STORE buyer3/sourceFF3once/history2-found2-net0/protected20/20/old6codes. Trialfullrollback/replay; nativeLOAD/HUSHIP guards preserved. SQLdispatch5.995ms/source.198ms/bounded200/inventorybatch backlog. Finance read373 now frozenperioddate/mode/version in originalinvoice UI; adminTS final pending.\n"),
 ("wiki/runbooks/nicora_active_work.md","\nCurrent375: native367VALID; context372 fullydelivered oneTOP/original1+twofound1/3ST/source3683oldkeys6codes/order accepted3/FF3once/P0. Factories368/372/initial373 mustnotrepeat. Finance APIserv366 updatedpolicy andassembly source; read373 periodmetadata nextrestart; finalbundle/encoding/TS next. Remaining groupedfirstlegmultiSKU, recurrentphysical losscycle, NI08 operational admission and external evidence.\n"),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni06_1.md","\n367–374 actualoriginal1+found1+1 ->threecorrective/originalST inoneTOP/existingHUload/depart/STOREbuyer3/FF3once/old6QR/history2-found2-net0; composite recoverydispatch+perSToutbox+exactnative resolvedlineage; late rollback/replay. Recoveryconsolidation no longer gap. FirstleggroupedmultiSKU, recurrentphysical losscycle andexternalregulatoryacceptance remain.\n")]:
 p=Path(file);old=p.read_text(encoding="utf-8");out[file]=text+old if file=="wiki/index.md"else old+text
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
for x in m["increments"]:
 if x["id"]=="NI06.1":
  x["status"]="in_progress_recovery_consolidation_delivered"
  x.setdefault("implementedSlices",[]).append("367–374 recovered1+1 andoriginal1 consolidated3ST/oneTOP/old6QR/existingload-depart-STOREbuyer3/sourceFFonce/native exactlineage/rollback-replay")
 if x["id"]=="NI07.1":x.setdefault("implementedSlices",[]).append("361–366 awareCASE start/sourcepreview/explicitWAREfinancialperiod/native date-rate proof/concurrent decisions/missingtime nocharge; oldsmallCASEloadedUTCcost2.50/immutableperiodinbilling")
out[p.as_posix()]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI06.1/375_recovery_consolidation.md").as_posix()]="# Qwen367–374\nUse retained fully deliveredcontext372/source368. Actualoriginal1+found1+1 oldkeys6codes ->threeST/oneTOP, two recoverydispatch keyedOP+ST andoneordinary; full native late rollback/replay; finalbuyer3/sourceFF3once/history2-found2-net0. Each recoveredbinding/receipt/placement/nativecapturedHUlineage/WARE/currentactor/trip mustmatch; foreign or duplicate recovery denied. OutboxperST distinct. No initial factories. NativeguardsVALID; realgovernmentACK/hardware/independentreview stillpending.\n"
print(json.dumps(out))
