(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 let dossier=null,pending=null,busy=false,identity="",serial=0;
 const base=()=>auth().state.apiBase.replace(/\/$/,""),key=()=>"wms-store-return:"+base()+":"+auth().state.user?.username;
 const say=text=>{el("returnMessage").textContent=text;};
 function controls(){
  document.querySelectorAll("main input,main textarea,main select,main button").forEach(node=>{node.disabled=busy||!!pending;});
  el("returnRetry").hidden=!pending;el("returnRetry").disabled=busy;
  el("returnRestart").hidden=!pending?.confirmed;el("returnRestart").disabled=busy;
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
 function lines(target,rows,format){target.replaceChildren(...rows.map(row=>{const p=document.createElement("p");p.textContent=format(row);return p;}));}
 function render(data){
  dossier=data;el("returnSummary").textContent=data.source.operation_id+" · "+data.source.store_addr+" · "+data.source.receipt_state;
  lines(el("returnLines"),data.lines,row=>"Строка "+row.line_no+" · "+row.article+" · принято "+row.accepted_quantity+" "+row.base_uom+" · уже разрешено "+row.approved_quantity+" · доступно "+row.available_for_approval);
  lines(el("returnHistory"),data.approvals,row=>row.operation_id+" · "+row.quantity+" "+row.base_uom+" · "+row.disposition+" · "+row.approved_by+" · "+row.decision_reference+" · "+(row.return_document?"SAP: "+row.return_document+" · склад "+row.ware_id:"ожидает SAP-документ"));
  el("returnLine").replaceChildren(...data.lines.map(row=>{const option=document.createElement("option");option.value=String(row.line_no);option.textContent="Строка "+row.line_no+" · "+row.article+" · "+row.available_for_approval+" "+row.base_uom;return option;}));
 }
 async function load(){
  if(busy||pending)return;const source=el("returnSource").value,scope=key(),version=++serial;busy=true;controls();
  try{const data=await request("/api/delivery/store-returns/"+encodeURIComponent(source));if(scope===key()&&version===serial&&source===el("returnSource").value){render(data);say("");}}
  catch(error){if(scope===key()&&version===serial)say(error.message);}finally{busy=false;controls();}
 }
 async function send(scope){
  if(busy||!pending)return;const intent=pending;busy=true;controls();
  try{
   const result=await request(intent.path,intent.body);localStorage.removeItem(scope);
   if(scope===key()){pending=null;dossier=null;say("Возврат согласован: "+result.quantity+" "+result.base_uom+". Ожидает SAP и логистику. Обновите поставку.");}
  }catch(error){if(scope===key()){pending={...intent,confirmed:error.confirmed};try{localStorage.setItem(scope,JSON.stringify(pending));}catch(storageError){say("Исходное согласование сохранено в памяти. Не закрывайте страницу.");}
   say(error.message+(error.confirmed?" Отказ подтверждён.":" Повторите исходное согласование."));}}
  finally{busy=false;controls();}
 }
 async function approve(){
  if(busy||pending||!dossier||dossier.source.operation_id!==el("returnSource").value){say("Покажите актуальную исходную приёмку.");return;}
  const line=Number(el("returnLine").value);if(!Number.isSafeInteger(line)||line<1){say("Выберите строку исходной поставки.");return;}
  const body={operation_id:"STORE.RETURN:"+crypto.randomUUID(),line_no:line,quantity:el("returnQuantity").value,
   disposition:el("returnDisposition").value,reason:el("returnReason").value,decision_reference:el("returnReference").value,complete_good_box:el("returnGoodBox").checked};
  if(!/^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(body.quantity)||!body.reason.trim()||!body.decision_reference.trim()){say("Укажите точное количество, причину и ссылку на решение.");return;}
  pending={path:"/api/delivery/store-returns/"+encodeURIComponent(dossier.source.operation_id)+"/approve",body};
  const scope=key();try{localStorage.setItem(scope,JSON.stringify(pending));}catch(error){pending=null;controls();say("Согласование не направлено: не удалось сохранить исходную операцию.");return;}await send(scope);
 }
 function changedAuth(){
  const scope=key(),fingerprint=scope+":"+(auth().state.user?.permissions||[]).slice().sort().join(",");if(fingerprint===identity)return;identity=fingerprint;++serial;dossier=null;pending=null;
  for(const id of ["returnSummary","returnMessage"])el(id).textContent="";
  for(const id of ["returnLines","returnHistory","returnLine"])el(id).replaceChildren();
  for(const id of ["returnSource","returnQuantity","returnReason","returnReference"])el(id).value="";el("returnGoodBox").checked=false;
  try{pending=JSON.parse(localStorage.getItem(scope)||"null");}catch(error){say("Не удалось прочитать сохранённую операцию.");}controls();
 }
 el("returnLoad").addEventListener("click",load);el("returnApprove").addEventListener("click",approve);
 el("returnRetry").addEventListener("click",()=>send(key()));
 el("returnRestart").addEventListener("click",()=>{if(!busy&&pending?.confirmed){localStorage.removeItem(key());pending=null;dossier=null;controls();say("Обновите поставку и исправьте данные.");}});
 window.addEventListener("wms-admin-auth-ready",changedAuth);changedAuth();
})();
