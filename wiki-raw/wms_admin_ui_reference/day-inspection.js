(() => {
 "use strict";
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 const scope=()=>JSON.stringify([auth().state.apiBase,auth().state.user?.username]),key=()=>"wms-day-inspection:"+scope();
 let pending=null,corrupt=false,context=null,busy=false,epoch=0;
 const message=value=>el("diMessage").textContent=value;
 function controls(){
  for(const id of ["diReview","diRole","diObserved","diNote","diRead","diSave"])el(id).disabled=busy||!!pending||corrupt;
  el("diReview").disabled=busy||!!pending;el("diRecover").disabled=busy||!corrupt||!el("diReview").value.trim();
  el("diSave").disabled=busy||!!pending||corrupt||!context||!auth().hasPermission(el("diRole").value==="WAREHOUSE_CHIEF"?"warehouse_day_inspect":"transport_dispatch_edit");
  el("diRetry").disabled=busy||!pending;el("diResolve").disabled=busy||!pending;
  el("diPending").textContent=pending?"Сохранена подпись "+pending.operation_id+" к сверке "+pending.review_operation_id+". Тело повторяется без изменения.":corrupt?"Повреждённая сохранённая подпись блокирует новую команду. Не удаляйте её до сверки.":"";
 }
 async function api(path,body){
  const identity=scope(),response=await fetch(auth().state.apiBase.replace(/\/$/,"")+"/api/finance/day-reconciliation"+path,{method:body?"POST":"GET",headers:auth().headers(body?{"Content-Type":"application/json"}:{}),...(body?{body:JSON.stringify(body)}:{})});
  const data=await response.json();if(identity!==scope())throw Error("Контекст пользователя изменился.");
  if(!response.ok)throw Error(data.detail?.message||data.detail||"Исход подписи не подтверждён.");return data;
 }
 function show(value){
  context=value;el("diRows").replaceChildren(...value.rows.map(row=>{
   const paragraph=document.createElement("p");paragraph.textContent=(row.inspection_role==="WAREHOUSE_CHIEF"?"Начальник склада":"Диспетчер")+": "+row.actor+" · "+(row.observed_empty?"заявлена пустая зона":"заявлена занятая зона")+" · "+row.note;return paragraph;
  }));
  message(value.shipping_zone_confirmed_for_frozen_review?"Обе независимые подписи и пустота по снятому снимку подтверждены. День и внешние обязательства не закрыты.":value.paired_independent_declarations?"Обе подписи сохранены. Пустота по снятому снимку не подтверждена; день не закрыт.":"Нужны подписи двух разных пользователей. День не закрыт.");controls();
 }
 async function read(){
  if(busy||pending||corrupt)return;const token=++epoch,identity=scope(),review=el("diReview").value.trim();context=null;busy=true;controls();
  try{if(!review)throw Error("Выберите сохранённую сверку.");const value=await api("/reviews/"+encodeURIComponent(review)+"/shipping-inspections");if(token===epoch&&identity===scope()&&review===el("diReview").value.trim())show(value);}
  catch(error){if(token===epoch&&identity===scope())message(error.message);}
  finally{busy=false;controls();}
 }
 async function recover(){
  if(busy||!corrupt)return;const identity=scope(),storageKey=key(),review=el("diReview").value.trim(),token=++epoch;
  if(!review)return;busy=true;controls();
  try{
   const raw=localStorage.getItem(storageKey);localStorage.setItem(storageKey+":archive:"+crypto.randomUUID(),raw||"");
   const value=await api("/reviews/"+encodeURIComponent(review)+"/shipping-inspections");
   if(identity!==scope()||token!==epoch)return;
   if(localStorage.getItem(storageKey)!==raw)throw Error("Исходник изменён другой вкладкой. Повторите восстановление.");
   localStorage.removeItem(storageKey);corrupt=false;pending=null;show(value);
   message("Исходник сохранён в архив. Подписи выбранной сверки перечитаны; перед новым осмотром проверьте её актуальность.");
  }catch(error){if(identity===scope()&&token===epoch)message(error.message+" Отправка остаётся заблокированной.");}
  finally{busy=false;controls();}
 }
 async function send(resolve=false){
  if(busy||corrupt)return;const identity=scope();let command=pending;
  try{
   if(!command){
    if(resolve||!context||context.review_operation_id!==el("diReview").value.trim())throw Error("Прочитайте подписи выбранной сверки.");
    const observed=el("diObserved").value,note=el("diNote").value.trim();if(!["EMPTY","NON_EMPTY"].includes(observed)||note.length<8)throw Error("Укажите результат осмотра и основание.");
    command={operation_id:"DAYINSPECT:"+crypto.randomUUID(),review_operation_id:context.review_operation_id,source_hash:context.source_hash,inspection_role:el("diRole").value,observed_empty:observed==="EMPTY",note};
    localStorage.setItem(key(),JSON.stringify(command));pending=command;
   }
   if(localStorage.getItem(key())!==JSON.stringify(command))throw Error("Сохранённая команда изменена другой вкладкой. Перезагрузите форму и проверьте исход.");
   busy=true;controls();const result=await api("/shipping-inspections"+(resolve?"/resolve":""),command);if(identity!==scope())return;
   if(localStorage.getItem(key())!==JSON.stringify(command))throw Error("Сохранённая команда изменена во время запроса. Исход подтверждён сервером; перечитайте форму.");
   localStorage.removeItem(key());pending=null;context=null;
   message(result.state==="NOT_RECORDED"?"На момент проверки подпись не найдена. Перечитайте текущую сверку; старое тело не изменяйте.":"Подпись сохранена. Прочитайте обе подписи; запись не закрывает день.");
  }catch(error){if(identity===scope())message(error.message+" Сохранённую команду можно повторить или проверить её исход.");}
  finally{busy=false;controls();}
 }
 el("diRecover").onclick=recover;el("diRead").onclick=read;el("diSave").onclick=()=>send();el("diRetry").onclick=()=>send();el("diResolve").onclick=()=>send(true);
 el("diRole").onchange=controls;el("diReview").oninput=()=>{epoch++;context=null;el("diRows").replaceChildren();controls();};
 window.addEventListener("wms-day-review-selected",event=>{if(!busy&&!pending){el("diReview").value=event.detail.operation_id;if(corrupt)controls();else read();}});
 function changed(){
  epoch++;pending=null;context=null;corrupt=false;
  try{const raw=localStorage.getItem(key());if(raw!==null){const value=JSON.parse(raw);if(!value||Object.keys(value).length!==6||typeof value.operation_id!=="string"||value.operation_id.length>100||!/^[A-Za-z0-9_.:-]+$/.test(value.operation_id)||typeof value.review_operation_id!=="string"||!value.review_operation_id||value.review_operation_id.length>100||!["WAREHOUSE_CHIEF","DISPATCHER"].includes(value.inspection_role)||typeof value.observed_empty!=="boolean"||typeof value.note!=="string"||value.note.trim().length<8||value.note.length>500||!/^[a-f0-9]{64}$/.test(value.source_hash))throw Error("Invalid saved inspection");pending=value;}}
  catch{corrupt=true;}
  el("diReview").value="";el("diNote").value="";el("diRows").replaceChildren();message("");controls();
 }
 window.addEventListener("storage",event=>{if(event.key===key()){changed();message("Сохранённая команда изменена другой вкладкой. Проверьте её исход.");}});
 window.addEventListener("wms-admin-auth-ready",changed);changed();
})();
