from pathlib import Path
import json
out={};base="db/migrations/2026-10-11_ni061_marked_partial/"
page="wiki/database/retailcase_ni061_marked_partial_20261011.md"
out[page]="""# Частичная приёмка точного маркированного состава
292 extends291 existing INTERWARE_RECEIVE/newreceiptUID/onefinalshortage/nativebalance/PUT, no newmarkregistry orstockwriter. RRL_STOCK_INTERWARE_PART.describe_selected_units takes exactunique unit_keys subset of frozenoriginalissuedmanifest, verifies BASEsum=currentreceivedqty, captures selected+fulloriginalsource separately. Sourcebinding/version stillvalidated by oldissued_manifest beforefirstreceipt andfreshdomainafterwait. SKUserializedwithoutconfiguredidentityprofile staysblocked; ordinaryunits0 unchanged.
 
RRL_INTERWARE_MARK_SCAN optional selected-unit filter retainsfulllegacy behavior whenabsent; exact currentSKUprofilematrix EACH selectedunit/system/profile mustbecovered. Missing/foreign/unselected/duplicatescans refuse; no EAN substitutionfor QR. Unitcore.receive_partial_issued reuses originalselected-return algorithm under distinct INTERWARE_RECEIVE/partial/capturedsource-target-unit-plan authorization. Movesonlyselectedunits/currentUID-cell/status AVAILABLE/version+1; birthUID/unitID/key/qty/UOM/everycode unchanged. Sourceunselectedunits remainISSUED. Same source/target/unitmutexes/freshplan andoneUOW. PUT snapshot readsselectedreceipt source_units fromactualAPPLIED canonicalplan, currentamount/versions stillchecked againsttargetstock. Custody/expecteddeparture remainblockedunresolvedshortage.
 
Typed optionalunit_keys leavesoldbodies unchanged(exclude_defaults). Originalunit-source reader addsdisplay_units/printedunitID viaonebounded PKjoin in sameRO, frozenmanifest/signature unmodified. Existingrawscreen renderschosenunitcheckboxes andcurrentQRprofiles; requiresselectedsubset andcodes atnativeboundary, durablecommand/retryunchanged.
 
Actualownmarkedsource3/EGAIS+CRPT sixcodes in tmp/context292.json/source292_progress.json, sourceP0. Selectedunit1/two scans: missingoneprofile denied20886; nativeouterrollbacknewP1+unit1AVAILABLE/newUID/version restoredtoall3ISSUED. ActualHTTP200/409 one winner qty1/short2, exactreplay/collision; samePUTcompletedP1H0 atoutbound, newUIDoneAVAILABLE qty1/originalUIDtwoISSUED qty2/all6codes retained. Incomingexpected3/received1/short2/false, nativepromisefalse, custody409/protected20-20. No hardware/GovACK/independentclaim. NEVER rerun birth; retainedcontext owns nextshortage resolution.
 
SQL292 selectedunit/receiptboundedqueries avg4.703ms4/34buffers,3.059ms2/22buf,4.129ms2/8buf, UIDlookup0.476ms9/22totalbuf. Decisioninventory: retain originalunit-key PK/profile codeindex and bounds10000units/20000profiles; no extraindex/cache. NativeallVALID/architecture627/JSsyntaxpass; existingcontracts manifestcurrentunitcore+partialhelper reflectnewmethods, additionaloverride sourcepaired. Next explicitloss/recovery/investigation closure andcustody/nextleg foracceptedfragment; nested/multi-finalreceipt notclaimed.
"""
for path,line in [
("wiki/index.md",f"- [Маркированная частичная приёмка]({page.removeprefix('wiki/')}):292 chosen1/2profiles from3/6codes, samecore+PUT, remaining2ISSUED/shortageopen."),
("wiki/index.md","- [Проект точного маркированного подмножества](database/retailcase_ni061_marked_partial_design_20261011.md):292 preservebirth/codes/currentversions andno falsecustodyrelease."),
("wiki/log.md","2026-10-11:292 extends291 markedexactsubset unit_keys/frozen-source/currentversions/baseqty +selectedprofilematrix scans, nativeunitcore distinctpartialcapturedauthorization/reusedreturnsubsetalgorithm; no newregistry/codebirth. PUT exactselectedreceiptsnapshot/currentquantity, optionalAPI/panelprintedunitIDs PKjoin preservesfrozenhash. Actualmarkedsource3/6codes chosen1/2profiles missingprofile20886/outerrollbackrestore3, HTTPone200/409/replay/collision/PUTP1/newUID1AVAILABLE/source2ISSUED/sixcodesretained/incomingnotready/nativepromisefalse/custody409/P20H20. SQLbounded4.7/3.05/4.13/.476ms keepPK/bounds. NativeVALID/architecture627/JSsyntaxpass. Rootserv292; shortage loss/recovery/nextleg/nested/independent remain."),
("wiki/runbooks/retailcase_active_work.md","LatestNative/app292 exactmarkedpartial singlepallet frozen3units/6codes ->accepted1/newUID+2profiles, original2ISSUED/codespreserved/short2 unresolved. tmp/context292.json+source292_progress.json actualsource/receipt/PUT done; NEVERrerun source292_marked_case/case292_marked_partial aftercommittedreceipt. Actualrollback/missingprofile/race/replay/collision/PUT/incoming-departblocked/custody409/P20H20. Oldmarked/fullunit behavior unchanged withoutselection; rawcheckboxunitIDdisplay usesseparatePKread/notfrozenhashmutation. NativeallVALID/architecture627/serv292. Next shortage resolution/recovery +acceptedfragmentcustody, externalcountry-base-govreplypending."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md","11.10.2026:292 Частичная приёмка маркированных единиц по точному исходному набору/QR каждого профиля доступна: source3/6codes→received1/2profiles, remaining2ISSUED и открытая недостача. Nativefalseprofile/rollback/race/replay/PUT/incomingnotready/custodyblocked/P20H20 passed. Код/партия/происхождение сохранены, ACK не подменён. Разрешение недостачи/поиск/следующее плечо/nested/independent остаются.")
]:out[path]=out.get(path,Path(path).read_text(encoding="utf-8"))+"\n"+line+"\n"
out["wiki/index.md"]=out["wiki/index.md"].replace("current native291/app291/","current native292/app292/")
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI06.1").setdefault("implementedSlices",[]).append("292 exactmarkedpartial frozenunit-key selection/currentprofile QR/subsetmove preservesbirth-codes/currentversions/samePUT, 1of3/2of6codes, remaining2issued/shortageopen")
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"))
j["components"]=[("../2026-10-11_ni061_marked_partial/001_unit_core.sql"if x=="../2026-10-11_ni062_marked_receiving/001_unit_core.sql"else "../2026-10-11_ni061_marked_partial/002_partial_helper.sql"if x=="../2026-10-11_ni061_partial_receiving/002_partial_helper.sql"else x)for x in j["components"]]
j["additional_scripts"].extend("../2026-10-11_ni061_marked_partial/"+x for x in ["001_unit_core.sql","002_partial_helper.sql","004_mark_scan.sql","003_receiving_body.sql","005_put_body.sql"])
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[(root/"NI06.1"/"292_marked_partial.md").as_posix()]="# Qwen292\nExactselectedunit_keys frozenmanifest/baseqty/version, currentSKUprofiles QRcoverage eachselectedunit; foreign/duplicate/missing/unselectedscansfail. SamepostCore subsetunitmove distinctcapturedINTERWARE_RECEIVE partial auth, originalbirthUID/code/key/qty/UOM remain; unselectedISSUED. Actual3units6codes→1unit2scans missingprofile/outerrollback/race/replay/PUTP1/source2issued/custody409/expecteddeparturefalse/P20H20 authorpassed. Selectedreceipt PUT proof, display_unitIDs separatePKquery do notrewritefrozenhash. Serializerwithoutidentityprofileblocked. No gov/hardware/independentacceptance, shortage recovery/loss/nextleg/nested stillopen. Do not recreate source292.\n"
out[base+"006_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-292-marked-partial-receipt'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Exact marked subset in original interwarehouse partial receipt',sysdate,user,'db/migrations/2026-10-11_ni061_marked_partial/001_unit_core.sql','db/migrations/2026-10-11_ni061_marked_partial/rollback.sql','APPLIED','Native selectedunit-quantity/profile matrix/capturedpartial unitmove; birth/codes retained. Actualsource3/6codes received1/2profiles/remaining2ISSUED, rollback/race/replay/PUTP1/currentnotready/custody409. No Gov/hardware/independentclaim.');
commit;
"""
out[base+"rollback.sql"]="""declare n number;begin
 select count(*)into n from RRL_INTERWARE_RECEIPT r join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=r.ROOT_UID where r.ORIGINAL_ROOT_UID is not null;
 if n>0 then raise_application_error(-20886,'INTERWARE_MARKED_PARTIAL_HISTORY_RETAINED');end if;
end;
/
@@../2026-10-11_ni061_partial_receiving/000_before_rrl_stock_unit_core_spec.sql
@@../2026-10-11_ni061_partial_receiving/000_before_rrl_stock_unit_core_body.sql
@@../2026-10-11_ni061_partial_receiving/002_partial_helper.sql
@@000_before_mark_scan.sql
@@../2026-10-11_ni061_partial_receiving/003_receiving_body.sql
@@../2026-10-11_ni061_partial_receiving/004_put_body.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
"""
print(json.dumps(out,ensure_ascii=True))
