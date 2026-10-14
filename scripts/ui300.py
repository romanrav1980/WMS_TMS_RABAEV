from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8")
panel='<section class="panel" data-permission="interwarehouse_receive"><h2>Фактическая приёмка найденного остатка</h2><p>Загрузите сверку согласованного восстановления. Принимается весь найденный остаток на отдельную паллету в приёмочную ячейку.</p><label>Новый идентификатор паллеты<input id="iwFoundPallet" maxlength="50"></label><label>Скан исходной паллеты<input id="iwFoundSource" maxlength="200"></label><label>Скан новой паллеты<input id="iwFoundScan" maxlength="200"></label><label>Приёмочная ячейка<input id="iwFoundCell" maxlength="60"></label><label>ШК товара<input id="iwFoundArticle" maxlength="160"></label><label>Вес брутто, кг<input id="iwFoundGross"></label><label>Причина / наблюдение<input id="iwFoundReason" maxlength="1000"></label><label>Документ<input id="iwFoundEvidence" maxlength="255"></label><label>Система / профиль<select id="iwFoundProfile"></select></label><label>QR найденной единицы<input id="iwFoundCode" autocomplete="off"></label><button id="iwFoundAdd">Добавить QR</button><button id="iwFoundClear">Очистить QR</button><p id="iwFoundCount"></p><button id="iwFoundReceive">Подтвердить фактическую приёмку</button><p>Согласование не считается поступлением. Для маркированного товара необходим каждый обязательный профиль каждой найденной единицы.</p></section>'
s=s.replace('<button id="iwRetry"',panel+'<button id="iwRetry"',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('currentShortage=null,historyPlan=','currentShortage=null,foundScans=[],foundApproval="",historyPlan=',1)
s=s.replace('currentShortage=null;el("iwRecoveryStatus").textContent="";','currentShortage=null;foundScans=[];foundApproval="";el("iwFoundProfile").replaceChildren();el("iwFoundCount").textContent="";el("iwRecoveryStatus").textContent="";')
s=s.replace('currentShortage=r;el("iwRecoveryStatus")','currentShortage=r;if(foundApproval!==r.recovery_approval_operation_id){foundScans=[];foundApproval=r.recovery_approval_operation_id||"";}el("iwFoundProfile").replaceChildren(...(r.profiles||[]).map(p=>new Option(p.system_code+" / "+p.profile_code,JSON.stringify([p.system_code,p.profile_code]))));el("iwFoundCount").textContent="Сканов найденного товара: "+foundScans.length;el("iwRecoveryStatus")',1)
s=s.replace('" · "+(r.loss_confirmed?"подтверждённая недостача":"открытая недостача")','" · восстановлено "+r.recovered_quantity+" · ещё не восстановлено "+r.net_unrecovered_short_quantity+" · "+(r.loss_confirmed?"исторически подтверждённая недостача":"открытая недостача")',1)
s=s.replace('" · кодов "+u.registered_code_count','" · кодов "+u.registered_code_count+(u.recovered?" · фактически восстановлена":"")',1)
s=s.replace('say(intent.path==="/recovery-reports"?','say(intent.path==="/recovery-receipts"?"Найденный товар принят в приёмочную ячейку. Требуется размещение; приёмка магазина этим действием не подтверждается.":intent.path==="/recovery-reports"?',1)
handler=''' el("iwFoundAdd").addEventListener("click",()=>{if(busy||pending)return;try{
 const r=currentShortage;if(!r?.recovery_approval_operation_id||foundApproval!==r.recovery_approval_operation_id||!el("iwFoundProfile").value)throw Error("Загрузите согласованное восстановление и профиль.");
 const [system_code,profile_code]=JSON.parse(el("iwFoundProfile").value),code=el("iwFoundCode").value;
 if(!code||foundScans.length>=20000||foundScans.some(s=>s.system_code===system_code&&s.profile_code===profile_code&&s.code===code))throw Error("Пустой, повторный или избыточный QR.");
 foundScans.push({system_code,profile_code,code});el("iwFoundCode").value="";el("iwFoundCount").textContent="Сканов: "+foundScans.length;
 }catch(e){say(e.message);}});
 el("iwFoundCode").addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();el("iwFoundAdd").click();}});
 el("iwFoundClear").addEventListener("click",()=>{if(!busy&&!pending){foundScans=[];el("iwFoundCount").textContent="Сканов: 0";}});
 el("iwFoundReceive").addEventListener("click",async()=>{if(busy||pending)return;try{
 const r=currentShortage;if(!r||r.receipt_operation_id!==el("iwShortReceipt").value||!r.recovery_approval_operation_id||r.recovery_receipt_operation_id)throw Error("Загрузите выбранное согласованное восстановление без состоявшейся приёмки.");
 const body={operation_id:"INTERWARE.FOUND:"+crypto.randomUUID(),approval_operation_id:r.recovery_approval_operation_id,receipt_pallet_identifier:el("iwFoundPallet").value.trim(),scan_source_pallet:el("iwFoundSource").value.trim(),scan_pallet:el("iwFoundScan").value.trim(),scan_cell:el("iwFoundCell").value.trim(),scan_article:el("iwFoundArticle").value.trim(),gross_weight_kg:el("iwFoundGross").value.trim(),quantity:r.short_quantity,article:r.article,base_uom:r.base_uom,discrepancy_reason:el("iwFoundReason").value.trim(),discrepancy_reference:el("iwFoundEvidence").value.trim(),scans:foundScans.slice()};
 if(!body.receipt_pallet_identifier||body.scan_source_pallet!==r.original_pallet_identifier||body.scan_pallet!==body.receipt_pallet_identifier||!body.scan_cell||!body.scan_article||!body.gross_weight_kg||body.discrepancy_reason.length<8||!body.discrepancy_reference)throw Error("Проверьте сканы исходной/новой паллеты, ячейки, товара, вес и документ.");
 const intent={path:"/recovery-receipts",body};localStorage.setItem(key(),JSON.stringify(intent));pending=intent;await send(key());currentShortage=null;foundScans=[];foundApproval="";el("iwFoundCount").textContent="";
 }catch(e){say(e.message);}});
'''
s=s.replace(' el("iwLoad").addEventListener',handler+' el("iwLoad").addEventListener',1);out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
