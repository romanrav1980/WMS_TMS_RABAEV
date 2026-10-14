(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 let dossier=null,pending=null,busy=false,identity="",serial=0;
 const base=()=>auth().state.apiBase.replace(/\/$/,""),key=()=>"wms-case-work:"+base()+":"+auth().state.user?.username;
 const say=text=>{el("caseMessage").textContent=text;};
 function controls(){
  document.querySelectorAll("main input,main textarea,main select,main button").forEach(node=>{node.disabled=busy||!!pending;});
  el("caseRetry").hidden=!pending;el("caseRetry").disabled=busy;
  el("caseRestart").hidden=!pending?.confirmed;el("caseRestart").disabled=busy;
 }
 async function request(path,body){
  const response=await fetch(base()+path,{method:body?"POST":"GET",headers:auth().headers(body?{"Content-Type":"application/json"}:{}),...(body?{body:JSON.stringify(body)}:{})});
  const data=await response.json();
  if(!response.ok){
   const error=Error(typeof data.detail==="string"?data.detail:data.detail?.message||JSON.stringify(data.detail));
   error.confirmed=response.status<500&&data.detail?.outcome_confirmed===true&&!!body&&data.detail?.operation_id===body.operation_id;throw error;
  }
  return data;
 }
 function list(target,rows,format){
  target.replaceChildren(...rows.map(row=>{const p=document.createElement("p");p.textContent=format(row);return p;}));
 }
 function render(data){
  dossier=data;el("caseSummary").textContent=data.case_id+" · версия "+data.case_version+" · "+data.status+" · "+data.reason_text+" · срок "+(data.search_deadline||"не назначен");
  list(el("caseObligations"),data.obligations,row=>"Строка "+row.line_no+": "+row.kind+" · "+row.base_qty+" "+row.base_uom+" · "+row.status);
  list(el("caseFindings"),data.findings||[],row=>row.role_code+" · "+row.reported_by+" · "+row.report_text);
  list(el("caseLosses"),data.losses||[],row=>"Подтверждённая потеря: "+row.base_qty+" "+row.base_uom+" · "+row.confirmed_by+" · "+row.reason_text);
  list(el("caseClosure"),data.closure?[data.closure]:[],row=>row.decision_reference+" · "+row.actor+" · "+row.reason_text);
  list(el("caseReturns"),data.return_approvals||[],row=>row.disposition+" · "+row.base_qty+" "+row.base_uom+" · согласовал "+row.approved_by+" · "+(row.warehouse_receipt_operation_id?"История складского приёма: "+row.warehouse_receipt_operation_id:"Складской приём ожидается"));
  el("caseLossLine").replaceChildren(...data.obligations.filter(row=>row.kind==="MISSING_INVESTIGATION"&&["OPEN","SEARCHING"].includes(row.status)).map(row=>{
   const option=document.createElement("option");option.value=String(row.line_no);option.textContent="Строка "+row.line_no+" · "+row.base_qty+" "+row.base_uom;return option;
  }));
  el("caseExp").value=data.expedition_user||"";el("caseSec").value=data.security_user||"";
 }
 async function load(){
  if(busy||pending)return;const caseId=el("caseId").value,scope=key(),version=++serial;busy=true;controls();
  const suffix=auth().hasPermission("store_case_manage")?"management":auth().hasPermission("store_loss_confirm")?"loss-review":"investigation";
  try {const data=await request("/api/delivery/case-work/"+encodeURIComponent(caseId)+"/"+suffix);
   if(scope===key()&&version===serial&&caseId===el("caseId").value){render(data);say("");}
  }catch(error){if(scope===key()&&version===serial)say(error.message);}finally{busy=false;controls();}
 }
 async function mine(){
  if(busy||pending)return;const scope=key(),version=++serial;busy=true;controls();
  try{
   const rows=await request("/api/delivery/case-work/mine");
   if(scope!==key()||version!==serial)return;
   el("caseQueue").replaceChildren(...rows.map(row=>{const button=document.createElement("button");button.textContent=row.case_id+" · "+row.search_deadline;button.addEventListener("click",()=>{el("caseId").value=row.case_id;void load();});return button;}));
  }catch(error){if(scope===key()&&version===serial)say(error.message);}finally{busy=false;controls();}
 }
 async function send(scope){
  if(busy||!pending)return;const intent=pending;busy=true;controls();
  try{
   const result=await request(intent.path,intent.body);localStorage.removeItem(scope);
   if(scope===key()){pending=null;dossier=null;el("caseSummary").textContent="";say("Подтверждено: "+result.action+" · версия "+result.case_version+". Обновите досье.");}
  }catch(error){if(scope===key()){pending={...intent,confirmed:error.confirmed};localStorage.setItem(scope,JSON.stringify(pending));say(error.message+(error.confirmed?" Отказ подтверждён.":" Повторите исходную сохранённую операцию."));}}
  finally{busy=false;controls();}
 }
 async function command(action){
  if(busy||pending||!dossier||dossier.case_id!==el("caseId").value){say("Покажите актуальное досье и завершите сохранённую операцию.");return;}
  try{
   const body={operation_id:"CASE."+action+":"+crypto.randomUUID(),expected_version:dossier.case_version};
   if(action==="assign"){
    const date=new Date(el("caseDeadline").value);if(!Number.isFinite(date.getTime()))throw Error("Укажите срок поиска.");
    Object.assign(body,{expedition_user:el("caseExp").value,security_user:el("caseSec").value,search_deadline:date.toISOString().replace("Z","000+00:00")});
   }else if(action==="finding")Object.assign(body,{role:el("caseRole").value,report:el("caseReport").value});
   else if(action==="close")Object.assign(body,{reason:el("caseCloseReason").value.trim(),decision_reference:el("caseCloseReference").value.trim()});
   else {const line=Number(el("caseLossLine").value);if(!Number.isSafeInteger(line)||line<1)throw Error("Нет открытой исходной недостачи.");Object.assign(body,{line_no:line,reason:el("caseLossReason").value});}
   pending={body,path:"/api/delivery/case-work/"+encodeURIComponent(dossier.case_id)+"/"+action};
   const scope=key();try{localStorage.setItem(scope,JSON.stringify(pending));}catch(error){pending=null;controls();throw Error("Не удалось сохранить операцию. Действие не направлено на сервер.");}await send(scope);
  }catch(error){say(error.message);}
 }
 function changedAuth(){
  const scope=key(),fingerprint=scope+":"+(auth().state.user?.permissions||[]).slice().sort().join(",");if(fingerprint===identity)return;identity=fingerprint;++serial;dossier=null;pending=null;el("caseSummary").textContent="";el("caseQueue").replaceChildren();
  for(const id of ["caseObligations","caseFindings","caseLosses","caseClosure","caseReturns"])el(id).replaceChildren();
  for(const id of ["caseId","caseExp","caseSec","caseDeadline","caseReport","caseLossReason","caseCloseReason","caseCloseReference"])el(id).value="";el("caseLossLine").replaceChildren();
  try{pending=JSON.parse(localStorage.getItem(scope)||"null");}catch(error){say("Не удалось прочитать сохранённую операцию.");}controls();
 }
 el("caseLoad").addEventListener("click",load);el("caseMine").addEventListener("click",mine);
 for(const action of ["assign","finding","loss","close"])el("case"+action[0].toUpperCase()+action.slice(1)).addEventListener("click",()=>command(action));
 el("caseRetry").addEventListener("click",()=>send(key()));el("caseRestart").addEventListener("click",()=>{if(!busy&&pending?.confirmed){localStorage.removeItem(key());pending=null;dossier=null;controls();say("Обновите досье и исправьте данные.");}});
 window.addEventListener("wms-admin-auth-ready",changedAuth);changedAuth();
})();
