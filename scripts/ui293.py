from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8")
panel='<section class="panel" data-permission="transport_dispatch_edit"><h2>Закрыть расследование после полной приёмки</h2><p>Загрузите историю решений и выберите сообщение. Частичная приёмка не закрывает недостачу или ответственность перевозчика.</p><label>Сообщение<select id="iwCloseIncident"></select></label><label>Причина закрытия<input id="iwCloseReason" maxlength="500"></label><label>Подтверждающий документ<input id="iwCloseEvidence" maxlength="255"></label><button id="iwCloseSave">Записать закрытие расследования</button></section>'
assert 'id="iwRetry"'in s;s=s.replace('<button id="iwRetry"',panel+'<button id="iwRetry"',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('decisionPlans=[],historyPlan=', 'decisionPlans=[],incidentCandidates=[],historyPlan=',1)
s=s.replace('if(!more)el("iwDecisionHistoryRows").replaceChildren();','if(!more){el("iwDecisionHistoryRows").replaceChildren();incidentCandidates=[];}\n incidentCandidates.push(...result.decisions.filter(r=>r.incident_kind&&r.followup_receipt_operation_id&&!r.incident_close_operation_id));el("iwCloseIncident").replaceChildren(...incidentCandidates.map(r=>new Option("Редакция "+r.revision_no+" · "+r.incident_detail,r.operation_id)));',1)
s=s.replace('el("iwDecisionHistoryRows").append(p);','if(row.incident_close_operation_id)p.textContent+=" · закрыто "+row.incident_closed_at+" · "+row.incident_close_reason+" / "+row.incident_close_evidence;el("iwDecisionHistoryRows").append(p);',1)
s=s.replace('historyPlan="";historyNext=null;','incidentCandidates=[];el("iwCloseIncident").replaceChildren();historyPlan="";historyNext=null;')
s=s.replace('say(intent.path==="/temperature-decisions"?','say(intent.path==="/incident-closures"?"Расследование закрыто по полной приёмке. История и остаток сохранены. Обновите историю.":intent.path==="/temperature-decisions"?',1)
needle=' el("iwLoad").addEventListener'
handler=''' el("iwCloseSave").addEventListener("click",async()=>{if(busy||pending)return;try{
 const selected=incidentCandidates.find(r=>r.operation_id===el("iwCloseIncident").value);
 if(!selected)throw Error("Загрузите историю и выберите незакрытое сообщение с последующей приёмкой.");
 const body={operation_id:"INTERWARE.CLOSE:"+crypto.randomUUID(),incident_operation_id:selected.operation_id,incident_revision:selected.revision_no,followup_receipt_operation_id:selected.followup_receipt_operation_id,reason:el("iwCloseReason").value.trim(),evidence_reference:el("iwCloseEvidence").value.trim()};
 if(body.reason.length<8||!body.evidence_reference)throw Error("Укажите причину закрытия и подтверждающий документ.");
 const intent={path:"/incident-closures",body};localStorage.setItem(key(),JSON.stringify(intent));pending=intent;await send(key());
 incidentCandidates=[];el("iwCloseIncident").replaceChildren();
 }catch(e){say(e.message);}});
'''
assert needle in s;s=s.replace(needle,handler+needle,1);out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
