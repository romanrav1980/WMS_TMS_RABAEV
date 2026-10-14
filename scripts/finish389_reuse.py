from pathlib import Path
import json
out={};d=Path("db/migrations/2026-10-12_ni062_return_profile_matrix")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text());item="../"+d.name+"/001_core.sql"
if item not in m["additional_scripts"]:m["additional_scripts"].append(item)
out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
out[(d/"rollback.sql").as_posix()]="""declare n number;begin
 select count(*)into n from USER_SOURCE where NAME='RRL_STORE_MARK_CORE'and TYPE='PACKAGE BODY'and TEXT like '%STORE_MARK_UNIT_LOT_REQUIRED%';
 if n>0 then raise_application_error(-20899,'RETURN_MATRIX_BRIDGE_REQUIRES_MATCHING_SHARED_CONTRACT_FORWARD_RECOVERY');end if;
end;
/
@@000_before_core.sql
@@002_recompile.sql
"""
page="wiki/database/nicora_ni062_marked_reuse_20261012.md"
out[page]="""# Полная маркированная коробка возвращается в доступный отбор
388 APPLIED/VALID RABAEV/orcl. Stock remains written only by existing root receive/putaway owners. Reused originalapproval/SAPreturn/transport/physicalhandover/authdriverpickup/warehousebarcode/unitreceipt/task/eligibility.

Actual385: fresh SAPARTMAS10 BOX3/current distinctBOXEAN, supplierbatchPB385, native receipt3oldkeys6codes/fullpallet originalcustomer3. Actual386 originalcustomeraccepted3/sourceFF3once/P0.
Actual387: approveexact3keys/wholegoodBOX3; assumedERP return bound toapproval/source; originaltrip/ownvehiclecapacity; storehandover6QR/explicitbounddriverpickup6QR; warehouse blockedreceiving3/BOXbarcode/fullboxcount1/exact6QR; originaltask completion tocurrentSKU pickface ->P3H0/3oldAVAILABLEkeys/6birthcodes/ALLOCATEeligible. Repeatreturnsstable. Originaldriverbinding restored; own driver retired. Context387 retains all stages and available physical stock; originalfactory385 mustnotrerun.

Real mismatch discovered: approved_proof only allowed UNIT although card UNIT_OR_AGGREGATION authorizes unit scanning. Also shared StoreMark resolver now requires perunit profiles/lot identity and exact lot lines; returnowner still emitted oldflatshape. 388 bridges at original RRL_STORE_RETURN_UNIT_CORE: adds perunit lot_uid/article/currentprofiles and matching custody line, keeps sharedproof/globalprofiles for old readers, allows UNIT_OR_AGGREGATION through UNIT path. Saved CODE.PROFILES_JSON versions must match everycurrentSKUprofile for each approvedkey. Sourceqty/key/version/issuedstatus/WARE/stockOrigin/BOX/batch/date guards remain. BOX/PALLET-only modes are not silently accepted as unit scans. Rollback alone while sharednewmatrixcontract remains would break callers and is guarded for forward repair.

No new regulatedunit birth, legalGovACK, realERPconfirmation or productionhardware claim. Physical reuse is software-proved; source evidence remains syntheticdev.

CASErecipient383: old alreadyshippedCASE1112/7units ->accepted3/missing2/refused1/damaged1, tenQR ofthefive physicallypresentunits. Completelyabsentunits have zero scans and MISSING is derived from exact registeredsource, not inventedQR. Mixed dispositions ononeunit refused, native trial7unitfacts fullyrolledback, actualnonadminreceiptDISCREPANCY/orderaccepted3/unreceived0/sourceFF7once/threephotos/outbox1/noquantityevents/replay/actorsretired/P20H20. Context383 retained; source211/383 factories forbidden. Carrier responsibility for discrepancy staysopen; no premature custody release.

SQL382 afterCASE: unitINSERT6.766ms/7exec/571buf, exactCASEarchive1.526ms/26exec, carrierlot.981ms/26exec; CASEcalendar nativeaggregate37.915ms cold/12buf and companion4.438ms. Decision inventory/delivery: keep existing source/CASE indexes and200node/10000unit bounds; batch CASE/archive validation whenmanyleaves shareCASE, ownerdelivery backlog. Finance: retain load+CASE proof indexes, check warmed plan before changing it. No million-operation claim.

Remaining: truephysical recurrentlosscycle now startsfreshsource390 BOX1; groupedfirstlegmultiSKU receipt, aggregate-only returns/recipient, realproviderACK/hardware/independent acceptance.
"""
for file,text in [
 ("wiki/index.md","- [Маркированный REUSE и частичное CASE](database/nicora_ni062_marked_reuse_20261012.md):385–388 BOX3/original3keys6codes→return→P3H0/eligible;383CASE7 accepted3/missing2/refused1/damaged1/noP.\n"),
 ("wiki/log.md","\n- 12.10.2026 383–389: oldshippedCASE1112 actual DISCREPANCY3accepted/2missing/1refused/1damaged/10QR of5present/nativefulltrialrollback/replay/sourceFF7once/noP/3photos/outbox1. FreshSAPBOX3/source385directaccepted3 ->existingmarkedREUSE387 approved/SAP/physicalhandover/driverpickup/blockedreceipt/task/pickingP3H0/3oldkeys6codes/no rebirth/currenteligible. Fixed388 returnowner UNITOR mode/perunit-lot-profile bridge/sharedresolver andsavedcodeversion checks; nativeVALID. Driverbindingrestored/actorretired; rolling bridgeback alone guarded. SQLCASE1.526/.981ms/unitINSERT6.766ms; boundedPK/batchCASEprojectionbacklog.\n"),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni06_2.md","\n385–388 full positive markedREUSE now actual: originalSAPBOX3 verifiedbatch/3keys6QR/approvedfullbox/ERPreturn/originaltransport/physicalcustody/bounddriver/exactwarehousebarcode+QR/blocked3 ->existingPUT/pickP3H0/eligible; no newunits. Returnowner bridges currentperunit-lot-profile resolver andUNIT_OR_AGGREGATION unitpath/strictsavedversions. Aggregate-only/hardware/realgovernment/independent remain.\n"),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni05_3.md","\n383 CASE-specific partial actual: oldCASE7 ->accepted3/missing2/refused1/damaged1;10scans forfivepresentunits/twoabsent deriveMISSING. Oneunit inconsistentprofiles refused; nativewholetrialrollback/replay/discrepancyorder3/sourceFF7once/threephotos/outbox1/noP. This closes CASEpartial positive gap, not physicalhardware/aggregate-only acceptance.\n")]:
 p=Path(file);old=p.read_text(encoding="utf-8");out[file]=text+old if file=="wiki/index.md"else old+text
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
for x in m["increments"]:
 if x["id"]=="NI06.2":
  x["status"]="in_progress_marked_reuse_available"
  x.setdefault("implementedSlices",[]).append("385–388 positiveexistingmarkedREUSEBOX3/originalSAPbatch/3oldkeys6QR/blockedreceipt/nativePUT/P3H0eligible; currentreturnprofilematrix bridge/currentcodeversions/no rebirth")
 if x["id"]=="NI05.3":x.setdefault("implementedSlices",[]).append("383 CASE7 unitdispositions3accepted2missing1refused1damaged/10QR of5present/wholetrialrollback/actualorder3/sourceFF7once/noP")
 if x["id"]=="NI06.1":x["remainingScope"]=["atomic grouped multi-SKU first-leg nested receipt","aggregation invalidation/repacking lifecycle","true recurrent physical-loss cycle","independent acceptance/hardware/current real ERP and government ACK"]
out[p.as_posix()]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI06.2/389_marked_reuse.md").as_posix()]="# Qwen385–388\nContext387 actual available3/H0/same3birthkeys6codes/originalSAPbatch/fullBOX3/explicitboxbarcode/approvedboundERP/source/trip/storehandover/driverpickup/exactwarehouse6QR/nativePUT/currentpickfaceeligible. Verify returnedstock stillavailable; do notzero orrerunfactory385. Originaldriverbinding restored/QAactorretired. SharedReturnproof perunit lot/profiles/version matrix andcurrent CODE.PROFILES versions; UNITOR acceptsunit path whileBOX/PAL-only denied. RealGovACK/ERP/hardware notpassed. Source390 recurrentcycle separate.\n"
out[(root/"NI05.3/383_case_dispositions.md").as_posix()]="# Qwen383\nRetainedcontext383 actualoldCASE7 ->accepted3/absent2/refused1/damaged1;10QR for5present andallprofiles perunit. Absentunits deriveMISSING without fakeQR. Conflictoneunit denied/nativefulltrialrollback/actualDISCREPANCY/oneoutbox/3photos/noP/replay/retiredactor/protected20. Do notreruninitial383 orsource211; opencarrierresponsibility is preserved.\n"
p=Path("scripts/case383_partial_marked_case.py");t=p.read_text(encoding="utf-8").replace('result["status"]=="PARTIALLY_ACCEPTED"','result["status"]=="DISCREPANCY"');out[p.as_posix()]=t
print(json.dumps(out))
