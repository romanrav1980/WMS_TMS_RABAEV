(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 let pending=null,busy=false,identity="",serial=0;
 const base=()=>auth().state.apiBase.replace(/\/$/,""),key=()=>"wms-return-transport:"+base()+":"+auth().state.user?.username;
 const say=text=>{el("transportMessage").textContent=text;};
 function controls(){
  document.querySelectorAll("main input,main select,main button").forEach(node=>{node.disabled=busy||!!pending;});
  el("transportRetry").hidden=!pending;el("transportRetry").disabled=busy;el("transportRestart").hidden=!pending?.confirmed;el("transportRestart").disabled=busy;
 }
 async function request(path,body){
  const response=await fetch(base()+"/api/delivery/store-return-transport"+path,{method:body?"POST":"GET",headers:auth().headers(body?{"Content-Type":"application/json"}:{}),...(body?{body:JSON.stringify(body)}:{})});
  const data=await response.json();
  if(!response.ok){const error=Error(typeof data.detail==="string"?data.detail:data.detail?.message||JSON.stringify(data.detail));error.confirmed=response.status<500&&data.detail?.outcome_confirmed===true&&!!body&&data.detail?.operation_id===body.operation_id;throw error;}return data;
 }
 async function eligible(){
  if(busy||pending)return;const scope=key(),version=++serial;busy=true;controls();
  try{const rows=await request("/eligible");if(scope!==key()||version!==serial)return;
   el("transportApproval").replaceChildren(...rows.map(row=>{const option=document.createElement("option");option.value=row.approval_id;option.textContent=row.store_addr+" · "+row.quantity+" "+row.base_uom+" · "+row.disposition+" · склад "+row.ware_id+" · "+row.return_document;return option;}));const linked=new URLSearchParams(location.search).get("approval_id");if(linked&&rows.some(r=>r.approval_id===linked))el("transportApproval").value=linked;say(linked&&!rows.some(r=>r.approval_id===linked)?"Выбранного согласования нет в текущей очереди. Проверьте, не назначен ли уже вывоз.":rows.length?"":"Нет возвратов с основанием SAP, ожидающих планирования.");
  }catch(error){if(scope===key()&&version===serial)say(error.message);}finally{busy=false;controls();}
 }
 async function show(){
  if(busy||pending)return;const trip=el("transportTrip").value,scope=key(),version=++serial;busy=true;controls();
  try{const rows=await request("/trips/"+encodeURIComponent(trip));if(scope!==key()||version!==serial||trip!==el("transportTrip").value)return;
   el("transportRows").replaceChildren(...rows.map(row=>{const p=document.createElement("p");p.textContent=row.approval_operation_id+" · "+row.store_addr+" → склад "+row.receiving_ware_id+" · "+row.gross_weight_kg+" кг · "+row.physical_places+" мест · "+row.vehicle_number;return p;}));say("");
  }catch(error){if(scope===key()&&version===serial)say(error.message);}finally{busy=false;controls();}
 }
 async function send(scope){
  if(busy||!pending)return;const intent=pending;busy=true;controls();
  try{const result=await request("/plan",intent.body);localStorage.removeItem(scope);if(scope===key()){pending=null;say("Вывоз включён в рейс "+result.task_id+". Фактический забор ещё не подтверждён.");}}
  catch(error){if(scope===key()){pending={...intent,confirmed:error.confirmed};try{localStorage.setItem(scope,JSON.stringify(pending));}catch(storageError){}say(error.message+(error.confirmed?" Отказ подтверждён.":" Повторите сохранённую операцию."));}}
  finally{busy=false;controls();}
 }
 async function plan(){
  if(busy||pending)return;const trip=Number(el("transportTrip").value),places=Number(el("transportPlaces").value),approval=el("transportApproval").value;
  if(!Number.isSafeInteger(trip)||trip<1||!Number.isSafeInteger(places)||places<1||places>200||!approval){say("Выберите согласованный возврат, рейс и целое число машиномест.");return;}
  if(!/^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(el("transportMass").value)){say("Введите массу брутто точным десятичным числом.");return;}
  pending={body:{operation_id:"RETURN.TRANSPORT:"+crypto.randomUUID(),approval_operation_id:approval,task_id:trip,gross_weight_kg:el("transportMass").value,physical_places:places}};
  const scope=key();try{localStorage.setItem(scope,JSON.stringify(pending));}catch(error){pending=null;controls();say("План не отправлен: не удалось сохранить исходную операцию.");return;}await send(scope);
 }
 function changedAuth(){
  const scope=key(),fingerprint=scope+":"+(auth().state.user?.permissions||[]).slice().sort().join(",");if(fingerprint===identity)return;identity=fingerprint;++serial;pending=null;
  el("transportRows").replaceChildren();el("transportApproval").replaceChildren();for(const id of ["transportTrip","transportMass","transportPlaces"])el(id).value="";say("");
  try{pending=JSON.parse(localStorage.getItem(scope)||"null");}catch(error){say("Не удалось прочитать сохранённый план.");}controls();
 }
 el("transportEligible").addEventListener("click",eligible);el("transportShow").addEventListener("click",show);el("transportPlan").addEventListener("click",plan);
 el("transportRetry").addEventListener("click",()=>send(key()));el("transportRestart").addEventListener("click",()=>{if(!busy&&pending?.confirmed){localStorage.removeItem(key());pending=null;controls();say("Обновите основания и исправьте план.");}});
 window.addEventListener("wms-admin-auth-ready",changedAuth);changedAuth();
 let openedLink=false;
 function openLink(){if(openedLink||!auth().state.user||busy||pending||!new URLSearchParams(location.search).get("approval_id"))return;openedLink=true;void eligible();}
 window.addEventListener("wms-admin-auth-ready",openLink);openLink();
})();
