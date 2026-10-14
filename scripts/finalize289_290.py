from pathlib import Path
import json
out={};base="db/migrations/2026-10-11_ni062_reuse_approval/"
p=Path(base+"004_preview.sql");s=p.read_text(encoding="utf-8")
s=s.replace("qty:=RRL_STOCK_MATH.quantity(p_quantity);","qty:=RRL_STOCK_MATH.quantity(p_quantity);if qty<=0 then raise_application_error(-20886,'RETURN_REUSE_POSITIVE_QUANTITY_REQUIRED');end if;")
out[p.as_posix()]=s
p=Path(base+"rollback.sql");s=p.read_text(encoding="utf-8");out[p.as_posix()]="drop package RRL_RETURN_REUSE_API;\n"+s+"alter package RRL_STOCK_STORE_RETURN_REC_CMD compile body;\nalter package RRL_STOCK_STORE_RETURN_PUT compile body;\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"))
for name in ["RRL_STOCK_RETURN_REUSE","RRL_RETURN_REUSE_API"]:
 if name not in j["packages"]:j["packages"].append(name)
j["components"].append("../2026-10-11_ni062_reuse_approval/004_preview.sql")
j["additional_scripts"].extend(["../2026-10-11_ni062_reuse_approval/001_reuse_helper.sql","../2026-10-11_ni062_reuse_approval/002_command.sql","../2026-10-11_ni062_reuse_approval/003_recompile.sql"])
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
page="wiki/database/retailcase_ni062_reuse_approval_20261011.md"
out[page]="""# Ранний допуск источника годного возврата
289–290 NI06.2. Existing marked REUSE path already composes exact approvedunit custody with originalREC/PUT/fullBOX/SAPbatch/picktarget. It wasincorrectto callthewholemarkedREUSE engineabsent; physicalpositivefullmarkedchain remainsunaccepted. Do not recreate engine.
 
Confirmedgap: oldapproval REUSE onlyrequired complete_good_box=true, thenwarehouseREC deterministically rejectedunverifiedoriginalSAPbatch/fractionalBOX AFTER SAPreturn+driverpickup. Existing RRL_STOCK_RETURN_REUSE.describe_source now reusedby native STORE_RETURN_APPROVE duringcompile AND aftercanonicalwait. Checksoriginallotarticle/unexpiredexpiry/uniqueoriginalSAPreceiptbatch/currentBOX exactconversion/fullBOXcount/currentbaseUOM. Capturesorigin/batch/expiry/UOMversion/BOXamount incompileddomain, freshdomainmustmatchbeforeappend. No physicalcompletebox/QR assertion. Actualtargetminlife/temperature/mixing/receipt scan remainatREC/PUT. Supplier/disposal existing behavior unchanged, oldsavedapprovals/history retained. Onlypostcore executeswrite.
 
RRL_RETURN_REUSE_API.preview is read-only, currentactive supplychainrightfirst. Quantitypositive, currentoriginalsource proof andacceptedremainingcalculatedindependently: sourcecanbeeligible butquantityalreadyfullyapproved. No spoofedSAP/source/stockregistry. Accessor addedto sameexistinghelperaccessibleby list, otherclients cannotcallwriteinternals. GET existingdelivery/store-returns/{receipt}/reuse-preview?line_no&quantity, originalreaderrole used. Existingrawstore-returns paneladdscheckbutton, humanreasons, APIactor/serialracefence; authchangesclearbusy/report; no autocreatingapproval. Positivewarehousephysicalbox andmarkedunit selection stillrequired.
 
Author actualoriginal229 remainingaccepted1/legacybatch denied atnativeprepare BEFORE pickup, noapproval/P20H20. CurrentoriginalSAPsourceSTORE.RECEIPT:cdbf4c0962 BOX24 returns sourceeligibletrue/proof1x24/currentlyapprovablefalse/available0; BOX12 refusesfractional; legacybatchfalse; gateway403; actualHTTPreadonly200. Thisverifieshelperpositiveread, notnewfreshapprovalfullchain. Existing107fullBOXpositivehistory retained, independentlynotrerun.
 
SQL289 originalSAPlookupcold4.343ms/138buf; afteractualreads290 average1.159ms4exec/143totalbuf (next3total5buf): retainoriginalUID receiptkey/boundedoneselectedline, no newindex/cache. NativeallVALID afterexplicitdependentrecompile, architecture6270cycles76, JSsyntax+encodingpassed. Rootserv290 freshworker; no stock/history cleanup/newfixture/GovACK. Canonicalmanifest helper/preview overrides+pairedrollback current. Owner inventory/delivery; freshunapprovedverifiedBOX+markedREUSEphysical/independentcase remain.
"""
for path,line in [
("wiki/index.md",f"- [Ранний допуск годного возврата]({page.removeprefix('wiki/')}):289–290 existingnativehelper beforepickup/current source preview/BOX24 positive-source vsremaining0; no freshphysicalclaim."),
("wiki/index.md","- [Проект раннего допуска REUSE](database/retailcase_ni062_reuse_approval_design_20261011.md):289 deterministic batch/BOX blockers movedbeforepickup."),
("wiki/log.md","2026-10-11:289–290 nativeexistingREUSEhelper sourcecheck reusedatapproval compile+afterwait; deterministicoriginalSAPbatch/fullBOX/currentUOM/expiry early beforepickup, frozenproof/version; receiptphysicalQR/BOX/picktarget remain. Currentright readonlypreview distinguishes sourceeligible fromremaining0; rawexistingbutton/racefence. Actual229legacybatch Nativepreparedenied/noapproval, actualexistingSAPBOX24 positive sourceproof1x24/remaining0 vsBOX12fractional refusal/gateway403/currentHTTP. No fakefreshapproval/fullmarkedphysicalacceptance. SQLcold4.343ms138buf ->avg1.159ms4/143buf keepUIDkey/oneselectedline. NativeallVALID/dependentsrecompiled/architecture627/JSsyntaxPASS/serv290fresh. Manifest/rollback/ledger maintained."),
("wiki/runbooks/retailcase_active_work.md","LatestNative289/app290 existingRETURN_REUSE sourcepreflight beforeapproval+afterwait and readonlyRRL_RETURN_REUSE_API preview/currentSupplyChainrole. Original229remaining1 legacybatchdenied early/noP; existingcdbfSAPBOX24 positiveproof butremaining0/currentlyapprovablefalse, BOX12fractional/gateway403/currentHTTP authorpassed. No freshfullmarkedREUSEflowclaim. Rootserv290freshworker, NativeallVALID/architecture627. Commoncoordination288/timeSourceV5 stillcurrent; own33564original12IDs regenerated/oldtimeapprovalstale/noautoreview. Next remainingphysicalownership/recommendations andrealexternalcontract gaps; ownerhub-country-govconfig pending."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_2.md","11.10.2026:289–290 Неподтверждённая исходная партия/неполная коробка теперь отклоняют REUSE уже при согласовании до забора. Тот же nativehelper даёт чтение пригодности источника и остатка согласования, кнопка в прежнем экране. Native229negative/currentSAPBOX24 positivesource+remaining0/HTTP passed; новая полная markedREUSEприёмка/independent ещё не объявлена.")
]:out[path]=out.get(path,Path(path).read_text(encoding="utf-8"))+"\n"+line+"\n"
out["wiki/index.md"]=out["wiki/index.md"].replace("current native287/app288/","current native289/app290/")
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI06.2").setdefault("implementedSlices",[]).append("289-290 existingnativeREUSE sourcebatch/fullBOX approvalpreflight beforepickup/currentreadpreview sourceeligibility vsavailableamount/existingpanel; nofreshfullmarkedacceptance")
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[(root/"NI06.2"/"289_290_reuse_approval.md").as_posix()]="# Qwen289–290\nExistingmarkedREUSE REC/PUT/fullBOX/SAPbatch exists; fullphysicalpositive notpassed. Earlyapproval checksoriginalsource batch/currentBOX exact amount/UOMversion/expiry incompile+freshdomainafterwait. Savedoldapproval retained/currentright. Nativewrite onlycore; physicalBOX/QR/target guards remain. ReadpreviewcurrentSupplyChainright/sourceeligible independentremaining; actualSAPBOX24 positiveproof1x24 available0 currentlyapprovablefalse, BOX12fractionalrefused/legacybatch/gateway403/HTTP authorpassed. NewfreshunapprovedverifiedBOX/markedphysicalbrowser/independentpending. No quantitybirth/GovACK/sourceforge.\n"
out[base+"005_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-289-reuse-approval-source'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Early existing return reuse source and readonly preview',sysdate,user,'db/migrations/2026-10-11_ni062_reuse_approval/001_reuse_helper.sql','db/migrations/2026-10-11_ni062_reuse_approval/rollback.sql','APPLIED','Nativecompile/fresh checkedSAPbatch/fullBOX/UOMexpiry; currentreadonlypreview. Actuallegacybatchnegative/BOX24positive-source available0/BOX12fractional/gateway403/HTTP noqty. FreshphysicalmarkedREUSE independent notclaimed.');
commit;
"""
print(json.dumps(out,ensure_ascii=True))
