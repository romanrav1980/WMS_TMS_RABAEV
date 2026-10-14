from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8")
panel='<section class="panel"><h2>Акт транспортной недостачи</h2><p>Сначала загрузите сверку приёмки. Акт не списывает запас повторно. Подтвердить его должен другой согласующий.</p><label>Основание<input id="iwLossReason" maxlength="500"></label><label>Документ<input id="iwLossEvidence" maxlength="255"></label><span data-permission="transport_dispatch_edit"><button id="iwLossReport">Записать акт недостачи</button></span><span data-permission="store_return_approve"><button id="iwLossConfirm">Подтвердить чужой акт</button></span><p id="iwLossStatus"></p></section>'
s=s.replace('<button id="iwRetry"',panel+'<button id="iwRetry"',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('incidentCandidates=[],historyPlan=','incidentCandidates=[],currentShortage=null,historyPlan=',1)
s=s.replace('el("iwShortReceipt").replaceChildren();el("iwShortSummary")','currentShortage=null;el("iwLossStatus").textContent="";el("iwShortReceipt").replaceChildren();el("iwShortSummary")')
s=s.replace('el("iwShortSummary").textContent="Заявлено','currentShortage=r;el("iwLossStatus").textContent=r.loss_confirmed?"Недостача подтверждена "+r.shortage_confirmation_operation_id+" · "+r.shortage_approver+" · "+r.shortage_confirmation_reason+" / "+r.shortage_confirmation_evidence:r.shortage_request_operation_id?"Акт ожидает другого согласующего · автор "+r.shortage_reporter:"Акт ещё не записан";\n el("iwShortSummary").textContent="Заявлено',1)
s=s.replace('say(intent.path==="/incident-closures"?','say(intent.path==="/shortage-reports"?"Акт записан. Требуется подтверждение другим согласующим. Обновите сверку.":intent.path==="/shortage-confirmations"?"Недостача подтверждена. Запас не списан повторно. Ответственность рейса завершите отдельным действием.":intent.path==="/incident-closures"?',1)
handler=''' async function loss(confirm){if(busy||pending)return;try{
 const r=currentShortage;if(!r||r.receipt_operation_id!==el("iwShortReceipt").value)throw Error("Загрузите текущую сверку выбранной приёмки.");
 if(r.loss_confirmed||r.short_quantity==="0")throw Error("Нет открытой недостачи для этого действия.");
 if(confirm&&!r.shortage_request_operation_id)throw Error("Сначала должен быть записан акт другим диспетчером.");
 if(!confirm&&r.shortage_request_operation_id)throw Error("Акт уже существует: требуется независимое подтверждение.");
 const body={operation_id:"INTERWARE.SHORTAGE:"+crypto.randomUUID(),quantity:r.short_quantity,reason:el("iwLossReason").value.trim(),evidence_reference:el("iwLossEvidence").value.trim()};
 if(body.reason.length<8||!body.evidence_reference)throw Error("Укажите основание и подтверждающий документ.");
 if(confirm)body.request_operation_id=r.shortage_request_operation_id;else body.receipt_operation_id=r.receipt_operation_id;
 const intent={path:confirm?"/shortage-confirmations":"/shortage-reports",body};localStorage.setItem(key(),JSON.stringify(intent));pending=intent;await send(key());currentShortage=null;
 }catch(e){say(e.message);}}
 el("iwLossReport").addEventListener("click",()=>loss(false));el("iwLossConfirm").addEventListener("click",()=>loss(true));
 el("iwShortReceipt").addEventListener("change",()=>{++serial;currentShortage=null;el("iwLossStatus").textContent="";el("iwShortSummary").textContent="";el("iwShortUnits").replaceChildren();});
'''
s=s.replace(' el("iwLoad").addEventListener',handler+' el("iwLoad").addEventListener',1)
out[p.as_posix()]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));base="../2026-10-11_ni061_shortage_disposition/"
roots=[n for n in j["components"]if "create or replace package RRL_STOCK_POSTING_API"in (p.parent/n).read_text(encoding="utf-8")]
assert len(roots)==1,roots
d=Path("db/migrations/2026-10-11_ni061_shortage_disposition")
out[(d/"006_root_current.sql").as_posix()]=(d/"000_before_rrl_stock_posting_api_package.sql").read_text(encoding="utf-8")+"\n"+(d/"004_root_body.sql").read_text(encoding="utf-8")
index=j["components"].index(roots[0]);j["components"][index:index+1]=[base+"002_command.sql",base+"003_guards.sql",base+"006_root_current.sql"]
j["components"]=[base+"005_unit_core.sql"if n=="../2026-10-11_ni061_marked_partial/001_unit_core.sql"else n for n in j["components"]]
j["packages"]+=["RRL_STOCK_INTERWARE_SHORT_CMD","RRL_IW_SHORTAGE_GUARD"];j["startup_scripts"].append(base+"001_schema.sql")
j["additional_scripts"]+=[base+"002_command.sql",base+"003_guards.sql",base+"004_root_body.sql",base+"005_unit_core.sql"]
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
