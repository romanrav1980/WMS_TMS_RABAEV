from pathlib import Path
import json
out={};base="db/migrations/2026-10-11_ni061_partial_receiving/"
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('r.pallet_identifier+" · "+r.quantity+" "+r.base_uom+" → "+r.outbound_dock','(r.received_pallet_identifier||r.pallet_identifier)+" · "+(r.received_quantity||r.quantity)+" "+r.base_uom+" → "+r.outbound_dock')
needle='if(r.arrival_timing&&r.gate_timing)'
assert needle in s;s=s.replace(needle,'if(r.receipt_operation_id)p.textContent+=" · принято "+r.received_quantity+" "+r.base_uom+" на паллете "+r.received_pallet_identifier+(r.short_quantity&&r.short_quantity!=="0"?" · недостача "+r.short_quantity+" · "+r.discrepancy_reason+" / "+r.discrepancy_reference:"");'+needle,1)
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/coordination_preflight.py");s=p.read_text(encoding="utf-8")
needle='        placed+=int(ready)'
assert needle in s
s=s.replace(needle,'''        plan["accepted_part_placement_completed"]=ready
        if plan.get("receipt_complete",1)!=1:
            ready=False
            blockers.append({"code":"COORDINATION_INCOMING_RECEIPT_INCOMPLETE","plan_operation_id":plan["operation_id"],
                "received_quantity":plan.get("received_quantity"),"short_quantity":plan.get("short_quantity")})
'''+needle,1)
out[p.as_posix()]=s
p=Path("admin/wms_admin_frontend/src/components/TransportCoordination.tsx");s=p.read_text(encoding="utf-8").replace(' COORDINATION_TIME_NOT_CURRENT_APPROVED:',' COORDINATION_INCOMING_RECEIPT_INCOMPLETE:"Межскладская поставка принята не полностью; недостача остаётся открытой",\n COORDINATION_TIME_NOT_CURRENT_APPROVED:');out[p.as_posix()]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"))
j["packages"].append("RRL_STOCK_INTERWARE_PART");j["components"].append("../2026-10-11_ni061_partial_receiving/002_partial_helper.sql");j["startup_scripts"].append("../2026-10-11_ni061_partial_receiving/001_schema.sql")
j["additional_scripts"].extend("../2026-10-11_ni061_partial_receiving/"+name for name in ["003_receiving_body.sql","004_put_body.sql","005_custody_body.sql","006_depart_gate.sql","007_sap_clone_guard.sql","008_recompile.sql"])
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
page="wiki/database/retailcase_ni061_partial_receiving_20261011.md"
out[page]="""# Частичная приёмка обычной межскладской паллеты
291 NI06.1 bounded firstslice. Existing INTERWARE_RECEIVE /stockbalance/event/outbox/PUT remainsoleowners. RRL_INTERWARE_RECEIPT additive ORIGINAL_ROOT_UID/EXPECTED_BASE_QTY/DISCREPANCY_REASON/REFERENCE; originalPLAN/UNLOAD/SOURCE_LOAD uniqueness retained, no implicit repeatedpartialreceipts. Onefinal receiptstrictlybelowdeclaredamount onfreshphysicalpalletUID, mandatoryreason/reference/manualgross. Originalshipment/composition/fulfillment/history remainunchanged. ExistingSKU identity BASE_SCALE/exactarithmetic, currentreceiverTargetWARE, oldpallet/barcode/location checks, plan+new/sourceStock closure andfreshdomaincompare. Newcopy preservesexpiry/production/price/origin/SAPlineage; SAPpalletcloneguard permits only capturednativepartialplan/held source+targetstock. Trigger doesnot SELECTmutatingPALLETS table.
 
Serializer/markedphysicalunits explicitlyrefuse firstslice. No missinggoodsornewcodes created. Generic rootcommand records+actualqty only; declareddifference is unresolvedcarrierobligation. Custodyrelease refusespartial; nativeexpectedcargo departure excludesincomplete receipt, incomingstatus distinguishescomplete vsacceptedfragment, commonsnapshot shows shortageblocker. ExistingPUT basesactualqty/newUID/actualmanualgross andoldtargetrules; sourceFull20cases unaffectedsourcefields absent. APIoptionalfields defaultNone/exclude_defaults preserveoldreplaypayload. Existingrawpanel addsnewUID/gross/reason/reference/durableintent, queue showsaccepted+short+UID. No SSCC-only restriction.
 
Actualownsource tag retained tmp/context291.json. Sameold inventory/fullpick/singleload/departure created3 ordinaryunits(no physicalunitregistry), sourceP0/declared3, realfrozenplan. Firstsourceattempt incorrectlycalledmarked-only context; resumedsame alreadycreatedmetadata/source ratherthanrecreating. Planordinaryoutput lacksmarkedfields, contextfinalizedfromactualrows. Partialnativeouterrollback yieldednewPAL/P1H0/receipt/event/outbox thenrollback removedallnewfacts. ActualHTTP concurrenttwofreshUIDs qty1 gave200/409, onewinnerreceipt1/expected3/short2; exactreplay200/collision409. Nativecustodyrelease409. ExistingPUT taskcompletedactual+1 atoutboundcell, originalloadcustodyretained, incomingexpected3/received1/short2/notready/departpromisefalse; protected20/20.
 
SQLcurrent scopedincoming18.853ms47buf, originalunitUIDcount avg1.001ms4/12totalbuf, source/receiptqueries5.893ms18buf and8.01ms6buf. Decisioninventory/transport: keeporiginalplan/sourceunique keys/newUID stockmutex and boundedqueue100/incoming200; no broadindex/cache. NativeallVALID/architecture627/JSsyntaxpassed. Independentfullphysical/markedsubset/recovery-loss/continuedmultiple receipts notaccepted. 291preservesuniques deliberately: nextslices mustdefine resolution/custody, notdrop constraintsblindly.
"""
for path,line in [
("wiki/index.md",f"- [Частичная межскладская приёмка]({page.removeprefix('wiki/')}):291 ordinarysinglepallet expected3→accepted1/short2, freshUID/native+PUT/concurrent200-409; carrier remainsopen."),
("wiki/index.md","- [Проект частичной приёмки](database/retailcase_ni061_partial_receiving_design_20261011.md):291 onefinalshortreceipt/uniquesretained/markedsubset+resolution separate."),
("wiki/log.md","2026-10-11:291 additiveoriginalreceiptfields/uniquesretained, existingINTERWARE_RECEIVE partialordinary freshUID/actualqty/gross/source-lineage +compilerclosure/freshplan; samebalance/event/outbox/PUT. No serializer/marked bypass/missingPbirth. Source3 ordinary frozenfixture resumedsamecontext aftermarked-only-context misuse; sourceP0. Nativeouterrollbackallfactsremoved; actualHTTP200/409 onereceipt1 expected3 short2/replay/collision; custody409, PUTcompletedP1H0/outbound, incomingnotready/nativepromisefalse/protected20-20. SQL18.85ms47buf/1msUIDlookup keepbounds/keys. NativeVALID/architecture627/JSsyntaxpass. Markedsubset/recovery-loss/continuation fullacceptance open."),
("wiki/runbooks/retailcase_active_work.md","LatestNative/app291 ordinarypartialinterware onefinalreceipt/freshUID qty1 expected3 short2 +actualPUT done. tmp/context291.json/source291_progress.json preserveactualnewfixture; NEVERrerun source291_ordinary_case/resume291_source birth. Originalsource3 fullydeparted/zeroP, newacceptedP1 atoutbound/sourcecarrier2 unresolved. Actualraceonewinner/replay/collision/rollback/custodyblocked/incomingnotready/promisefalse/P20H20. Oldreceiptuniquesretained. Next exactmarkedsubset andshortage resolution/recovery usingsamecore, no blindmulti-receiptconstraintdrop. AllNativeVALID; rootserv291b fresh thenstatreload commonsnapshot. Externalhub-country-govreplypending."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md","11.10.2026:291 ordinarysinglepallet partialactualreceipt onnewUID andsamePUT available. Actualsource3→received1/short2 opencarrier, outerrollback/concurrentwinner/replay/custodyrefused/currentexpecteddeparturefalse/P20H20. Existingreceiptuniquesretained, no repeatedpartial/missingPbirth. Markedexactsubset/shortage recovery-resolution/nested and independent/fullacceptance remain.")
]:out[path]=out.get(path,Path(path).read_text(encoding="utf-8"))+"\n"+line+"\n"
out["wiki/index.md"]=out["wiki/index.md"].replace("current native289/app290/","current native291/app291/")
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI06.1").setdefault("implementedSlices",[]).append("291 ordinarysinglepallet onefinalpartialreceipt/freshUID/samecore-PUT expected3 received1 shortage2 opencarrier, no missingstockbirth/uniquesretained")
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[(root/"NI06.1"/"291_partial_receiving.md").as_posix()]="# Qwen291\nExistingINTERWARE_RECEIVE onefinalordinarypartial receipt/freshPALID/positiveactualqty<original/manualgross/reason/reference, originaluniquesretained. CurrentTargetWARE/planmutex/source-targetstockclosure/freshdomain, oldreplayunchanged. Originalmetadata/SAPlineage copy guardprivateplan, no mutatingtable read. Source3 departedP0→newP1 expected3 short2, no missingP/codesbirth; marked/serializedexplicitrefuse. Actualrollback/concurrencyone200/409/replay/collision, originalPUTP1/outbound, sourcecustodyopen/incomingnotready/nativepromisefalse/P20H20 authorpassed. Markedsubset/recovery-loss/incrementalreceipts/nested/independent stillopen. Preservecontext291; never recreate source.\n"
out[base+"009_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-291-interware-partial-receipt'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing ordinary partial interwarehouse receipt and same PUT',sysdate,user,'db/migrations/2026-10-11_ni061_partial_receiving/001_schema.sql','db/migrations/2026-10-11_ni061_partial_receiving/rollback.sql','APPLIED','Uniqueplan/load/unload retained; source3 received1 freshUID short2/custodypending. Native rollback/concurrent200-409/replay/PUTP1/protected20-20. Markedsubset/resolution/recovery/fullindependent notclaimed.');
commit;
"""
out[base+"rollback.sql"]="""declare n number;begin select count(*)into n from RRL_INTERWARE_RECEIPT where ORIGINAL_ROOT_UID is not null;if n>0 then raise_application_error(-20886,'INTERWARE_PARTIAL_HISTORY_RETAINED');end if;end;
/
@@000_before_rrl_stock_interware_rec_body.sql
@@000_before_rrl_stock_interware_put_body.sql
@@000_before_rrl_stock_interware_custody_body.sql
@@000_before_rrl_interware_depart_gate_body.sql
"""
print(json.dumps(out,ensure_ascii=True))
