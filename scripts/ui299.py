from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8")
panel='<section class="panel"><h2>Найденный товар после подтверждения недостачи</h2><p>Загрузите сверку приёмки. Здесь оформляются сообщение о находке и независимое согласование. Остаток появится только при фактической корректирующей приёмке.</p><label>Основание<input id="iwRecoveryReason" maxlength="500"></label><label>Документ<input id="iwRecoveryEvidence" maxlength="255"></label><span data-permission="transport_dispatch_edit"><button id="iwRecoveryReport">Сообщить о найденном остатке</button></span><span data-permission="store_return_approve"><button id="iwRecoveryApprove">Согласовать чужое сообщение</button></span><p id="iwRecoveryStatus"></p></section>'
s=s.replace('<button id="iwRetry"',panel+'<button id="iwRetry"',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('currentShortage=null;el("iwLossStatus").textContent="";','currentShortage=null;el("iwRecoveryStatus").textContent="";el("iwLossStatus").textContent="";')
s=s.replace('currentShortage=r;el("iwLossStatus")','currentShortage=r;el("iwRecoveryStatus").textContent=r.recovery_receipt_operation_id?"Найденный товар фактически принят "+r.recovered_quantity+" · "+r.recovered_pallet_identifier:r.recovery_approval_operation_id?"Согласовано, требуется физическая корректирующая приёмка":r.recovery_request_operation_id?"Сообщение о находке ожидает другого согласующего · "+r.recovery_reporter:"Сообщения о найденном товаре нет";el("iwLossStatus")',1)
s=s.replace('say(intent.path==="/shortage-reports"?','say(intent.path==="/recovery-reports"?"Сообщение о находке сохранено. Требуется другой согласующий. Обновите сверку.":intent.path==="/recovery-approvals"?"Восстановление согласовано. Запас пока не создан: требуется фактическая приёмка.":intent.path==="/shortage-reports"?',1)
handler=''' async function recovery(approve){if(busy||pending)return;try{
 const r=currentShortage;if(!r||r.receipt_operation_id!==el("iwShortReceipt").value||!r.loss_confirmed)throw Error("Загрузите текущую сверку подтверждённой недостачи.");
 if(r.recovery_receipt_operation_id||r.recovery_approval_operation_id)throw Error("Восстановление уже согласовано или выполнено.");
 if(approve&&!r.recovery_request_operation_id)throw Error("Сначала другое лицо должно сообщить о находке.");
 if(!approve&&r.recovery_request_operation_id)throw Error("Сообщение уже записано: требуется согласование.");
 const body={operation_id:"INTERWARE.RECOVERY:"+crypto.randomUUID(),quantity:r.short_quantity,reason:el("iwRecoveryReason").value.trim(),evidence_reference:el("iwRecoveryEvidence").value.trim()};
 if(body.reason.length<8||!body.evidence_reference)throw Error("Укажите основание и документ.");
 if(approve)body.request_operation_id=r.recovery_request_operation_id;else body.loss_operation_id=r.shortage_confirmation_operation_id;
 const intent={path:approve?"/recovery-approvals":"/recovery-reports",body};localStorage.setItem(key(),JSON.stringify(intent));pending=intent;await send(key());currentShortage=null;
 }catch(e){say(e.message);}}
 el("iwRecoveryReport").addEventListener("click",()=>recovery(false));el("iwRecoveryApprove").addEventListener("click",()=>recovery(true));
'''
s=s.replace(' el("iwLoad").addEventListener',handler+' el("iwLoad").addEventListener',1);out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
