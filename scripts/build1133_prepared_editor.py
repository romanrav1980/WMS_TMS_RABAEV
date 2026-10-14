from pathlib import Path
import json
f={}
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
s=s.replace('<p>Задайте укладку по паллетам. Общее количество должно совпадать с исходным заказом.</p>','<div id="sapManualEditor"><p>Задайте укладку по паллетам. Общее количество должно совпадать с исходным заказом.</p>',1)
s=s.replace('<button id="sapPrepareSt" type="button">Подготовить СТ</button>','<button id="sapPrepareSt" type="button">Подготовить СТ</button></div>',1)
s=s.replace('customer-orders.js?v=20261013-1131','customer-orders.js?v=20261013-1133');f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.js");s=p.read_text(encoding="utf-8")
s=s.replace("  orderState.layoutOrderId=id;orderEl('sapLayoutRows').replaceChildren();","  orderEl('sapManualEditor').hidden=Boolean(detail.preparation_json);orderEl('sapPrepareSt').disabled=Boolean(detail.preparation_json);\n  orderState.layoutOrderId=id;orderEl('sapLayoutRows').replaceChildren();")
s=s.replace('`Подготовлена СТ '+chr(36)+'{result.st_number}.`;','`Подготовлена СТ '+chr(36)+'{result.st_number}, мест: '+chr(36)+'{result.pallet_identifiers.length}.`;')
s=s.replace('  orderEl("sapTripReviewMessage").textContent="";orderState.selectedId=orderId;', '  orderEl("sapManualEditor").hidden=false;orderEl("sapPrepareSt").disabled=true;orderEl("sapTripReviewMessage").textContent="";orderState.selectedId=orderId;')
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sap-automatic-preparation.css");f[str(p)]=p.read_text(encoding="utf-8")+"""
#sapAssignment{padding:16px;background:#f6f9fe;border:1px solid #e1e9f4;border-radius:10px;margin:14px}
#sapAssignment summary{font-weight:600;color:#25486d;cursor:pointer;margin-bottom:12px}
#sapAssignment input{padding:9px;border:1px solid #cdd6e2;border-radius:7px;max-width:200px}
#sapAssignment button{padding:9px 13px;border:1px solid #cdd6e2;border-radius:7px;background:white;cursor:pointer;margin:4px}
#sapAssignment #sapAssignSt{background:#2277ee;color:white;border-color:#2277ee}
#sapPreparationStatus,#sapTripReviewMessage:not(:empty){line-height:1.6;color:#274d75;padding:10px;background:#eef4ff;border-radius:7px}
"""
p=Path("wiki/runbooks/nicora_active_work.md");f[str(p)]="""# CHECKPOINT1133 — NI02.2 assignment bridge prepared/current read

Continueallowner no cutoff/noagents/noGithub. AfterNI02.1+QC alias deliveredreports30/31, addedactualUI auto savedresult→selectedorder2135#sapAssignment/currentGETreceipt→existing nativeassign endpoint, optional readonlyexistingpreflight button. No new writer/mapping/policy. Oldmanualeditor wronglydisplayed source18+18 asoneplace afteralreadyauto prepared;1133 hides editor/disablespreparation when savedreceipt exists, sameoldcurrent writer reused. Newmanualediting stillallowedforunpreparedsources throughexistingoldform; pending manualglobal safety gap remains priorlegacyinmemoryfunction (not newly claimed durable).

Read1132 current33571 vehicleQC241ede877f6d1 planned/unbilled/empty nativepreflight additionalSAP_2135: CHECKED_CURRENT_NATIVE_RULES/2places/24kg, own rows641507/641508 unassigned, operational_admissionfalse; no actualassignment performed. Userbutton optional/currentlockedrecheck remainswriter. Metadata targetedSKU/vehicle tables no temperaturecolumns; TEMP_REGION/TEMP_WEIGHT onTT are namesonly NOTproof actualtemperaturepolicy. Need inspectglobal existingcoldpolicy beforedesign. Browser43 showsselected source2135/FF2PLANNED0/P0 assignedsource, savedST butoldmanualeditor contradictory; preserved43pre-fix, new44needed. LatestUI customerjs1133 andsapauto1131 linked; scripts1122intentPASS afterbridge. API1127currentPython. Encoding77070PASS through1130, latest1131–1133pendingend. Newwikiindex/logfor1133+report32 stillneeded. Currentplan53NI02.2, nativeold001_rules archive inspectedonly notchanged.

""" +p.read_text(encoding="utf-8")
print(json.dumps(f,ensure_ascii=True))
