from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
needle=' const say=t=>el("iwMessage").textContent=t;'
s=s.replace(needle,needle+'''
 const recoveryChoice=document.createElement("section");
 recoveryChoice.innerHTML='<label>Выбранная найденная часть <select id="iwRecoveryCase"></select></label><label>Количество нового сообщения о находке <input id="iwRecoveryQuantity" inputmode="decimal"></label><div id="iwRecoveryUnitChoices"></div><p>Для маркированного товара выберите точные единицы новой находки. Каждая часть согласуется и принимается отдельно; товар ещё не считается полученным магазином.</p>';
 el("iwRecoveryReport").parentElement.prepend(recoveryChoice);
''',1)
s=s.replace('const r=await request("/receipts/"+encodeURIComponent(receipt)+"/shortage");','const selected=el("iwRecoveryCase").value;const r=await request("/receipts/"+encodeURIComponent(receipt)+"/shortage"+(selected?"?selected_request="+encodeURIComponent(selected):""));',1)
needle=' currentShortage=r;if(foundApproval'
s=s.replace(needle,''' el("iwRecoveryCase").replaceChildren(...(r.recovery_cases||[]).map(c=>new Option(c.request_quantity+" "+r.base_uom+" · "+c.request_operation_id+" · "+(c.final_receipt_operation_id?"конечная приёмка":c.dispatch_operation_id?"отгружено":c.receipt_operation_id?"принято на склад":c.approval_operation_id?"согласовано":"ожидает согласования"),c.request_operation_id)));
 el("iwRecoveryCase").value=r.recovery_request_operation_id||"";el("iwRecoveryQuantity").value=r.unreported_recovery_quantity||"0";
 el("iwRecoveryUnitChoices").replaceChildren(...(r.missing_units||[]).filter(u=>!u.recovered&&!u.recovery_report_operation_id).map(u=>{const label=document.createElement("label"),input=document.createElement("input");input.type="checkbox";input.dataset.unitKey=u.key;label.append(input,document.createTextNode(" Найдена единица "+u.unit_id+" · "+u.declared_quantity+" "+u.base_uom));return label;}));
'''+needle,1)
s=s.replace('"Найденный товар фактически принят "+r.recovered_quantity','"Выбранная часть принята "+r.recovery_selection_quantity',1)
s=s.replace('if(r.recovery_receipt_operation_id||r.recovery_approval_operation_id)throw Error','if(approve&&(r.recovery_receipt_operation_id||r.recovery_approval_operation_id))throw Error',1)
s=s.replace(' if(!approve&&r.recovery_request_operation_id)throw Error("Сообщение уже записано: требуется согласование.");',' if(!approve&&r.unreported_recovery_quantity==="0")throw Error("Весь объём уже включён в сообщения о находке.");',1)
s=s.replace('operation_id:"INTERWARE.RECOVERY:"+crypto.randomUUID(),quantity:r.short_quantity','operation_id:"INTERWARE.RECOVERY:"+crypto.randomUUID(),quantity:approve?r.recovery_selection_quantity:el("iwRecoveryQuantity").value.trim()',1)
s=s.replace('if(approve)body.request_operation_id=r.recovery_request_operation_id;else body.loss_operation_id=r.shortage_confirmation_operation_id;','''if(approve)body.request_operation_id=r.recovery_request_operation_id;else {body.loss_operation_id=r.shortage_confirmation_operation_id;
 const selected=Array.from(el("iwRecoveryUnitChoices").querySelectorAll("input:checked")).map(input=>input.dataset.unitKey);if(selected.length)body.unit_keys=selected;}''',1)
s=s.replace('gross_weight_kg:el("iwFoundGross").value.trim(),quantity:r.short_quantity','gross_weight_kg:el("iwFoundGross").value.trim(),quantity:r.recovery_selection_quantity',1)
s=s.replace('currentShortage=null;foundScans=[];foundApproval="";','currentShortage=null;foundScans=[];foundApproval="";el("iwRecoveryCase").replaceChildren();el("iwRecoveryUnitChoices").replaceChildren();el("iwRecoveryQuantity").value="";')
needle=' el("iwRecoveryReport").addEventListener'
s=s.replace(needle,''' el("iwRecoveryCase").addEventListener("change",()=>{if(busy||pending)return;++serial;currentShortage=null;foundScans=[];foundApproval="";el("iwFoundCount").textContent="";el("iwShortLoad").click();});
'''+needle,1)
out[p.as_posix()]=s
print(json.dumps(out))
