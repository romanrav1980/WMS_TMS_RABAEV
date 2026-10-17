/* Aware pre-departure delivery windows; stock stays with the existing loading owner. */
(() => {
 "use strict";
 const auth=()=>window.wmsAdminAuth,base=()=>auth().state.apiBase.replace(/\/$/,"");
 const panel=document.createElement("section");panel.id="deliveryWindow";panel.className="panel";
 panel.innerHTML=`<h2>Плановое окно магазина <a href="/help/delivery-timing.html" target="_blank" rel="noopener" title="Как фиксируется окно до выезда и считается прибытие вовремя" data-help-id="delivery.window.help">Справка</a></h2>
 <p>Выберите погруженное место. Окно сохраняется до выезда машины.</p>
 <label>Место и магазин<select data-place title="Выбрать магазин из фактического состава погрузки" data-help-id="delivery.window.place"></select></label>
 <button type="button" data-read title="Прочитать текущую версию окна и факт прибытия" data-help-id="delivery.window.read">Прочитать окно</button>
 <label>Время<select data-zone title="Явный часовой пояс вводимых границ окна" data-help-id="delivery.window.zone"><option value="+03:00">МСК · UTC+03:00</option><option value="+00:00">UTC</option></select></label>
 <label>Начало окна<input type="datetime-local" data-start title="Самый ранний плановый момент прибытия машины" data-help-id="delivery.window.start"></label>
 <label>Конец окна<input type="datetime-local" data-finish title="Самый поздний плановый момент прибытия машины" data-help-id="delivery.window.finish"></label>
 <label>Основание<input data-reason maxlength="500" title="Причина или документ согласования планового окна, минимум8символов" data-help-id="delivery.window.reason"></label>
 <button type="button" data-save title="Сохранить новую версию окна до выезда; товар и приёмка не меняются" data-help-id="delivery.window.save">Сохранить окно</button>
 <button type="button" data-retry title="Повторить тот же сохранённый запрос без изменения времени и номера операции" data-help-id="delivery.window.retry" hidden>Повторить сохранённое окно</button>
 <button type="button" data-restart title="После подтверждённого конфликта версии сохранить отказ в архиве и перечитать новое окно" data-help-id="delivery.window.restart" hidden>Перечитать после конфликта</button>
 <p data-status role="status"></p>`;
 document.getElementById("tripSummary").closest("section").after(panel);
 const el=key=>panel.querySelector("[data-"+key+"]"),message=text=>{el("status").textContent=text;};
 let rows=[],tripId=null,selected=null,pending=null,record=null,busy=false,damaged=false,version=0,identity="",generation=0;
 const key=()=>JSON.stringify(["delivery.window",base(),auth().state.user?.username||""]);
 const valid=value=>!!value&&Number.isSafeInteger(value.trip_id)&&value.trip_id>0&&value.body
  &&/^[A-Za-z0-9_.:-]{1,100}$/.test(value.body.operation_id||"")&&typeof value.body.load_operation_id==="string"
  &&typeof value.body.store_address==="string"&&Number.isSafeInteger(value.body.expected_version)&&value.body.expected_version>=0
  &&typeof value.body.reason==="string"&&value.body.reason.trim().length>=8&&value.body.reason.length<=500
  &&[value.body.window_start,value.body.window_finish].every(v=>typeof v==="string"&&/^\d{4}-\d{2}-\d{2}T.*Z$/.test(v)&&Number.isFinite(Date.parse(v)))
  &&Object.keys(value.body).sort().join(",")==="expected_version,load_operation_id,operation_id,reason,store_address,window_finish,window_start";
 const intent=window.wmsCommandIntent.create("",valid,{storageKey:key});
 function controls(){
  panel.querySelectorAll("input,select,button").forEach(n=>{n.disabled=busy||damaged||!!pending;});
  el("save").disabled=busy||damaged||!!pending||!selected||selected.load_status!=="LOADED"||!auth().hasPermission("transport_dispatch_edit");
  el("retry").hidden=!pending;el("retry").disabled=busy||damaged;
  el("restart").hidden=!pending?.confirmed_rejection;el("restart").disabled=busy||damaged;
 }
 function option(){return rows[Number(el("place").value)]||null;}
 async function request(path,body){
  const response=await fetch(base()+path,{method:body?"POST":"GET",headers:{...auth().headers(),...(body?{"Content-Type":"application/json"}:{})},...(body?{body:JSON.stringify(body)}:{})});
  const data=await response.json();if(!response.ok){const error=new Error(data.detail?.message||data.detail?.code||"Сервер не подтвердил действие ("+response.status+"). Повтор сохраняет исходный запрос.");error.versionConflict=!!body&&response.status===409&&data.detail?.operation_id===body.operation_id&&data.detail?.outcome_confirmed===true&&String(data.detail?.message).includes("DELIVERY_WINDOW_VERSION_CONFLICT");throw error;}return data;
 }
 function displayTime(stamp){if(!stamp)return"";const minutes=el("zone").value==="+03:00"?180:0;return new Date(Date.parse(stamp)+minutes*60000).toISOString().slice(0,16);}
 async function read(){
  if(busy||pending||damaged)return;const row=option(),scope=key(),ticket=++generation;selected=null;version=0;controls();if(!row)return;
  busy=true;controls();
  try{
   const value=await request("/api/delivery/timing/place?"+new URLSearchParams({load_operation_id:row.load_operation_id,store_address:row.destination_addr}));
   if(scope!==key()||ticket!==generation)return;
   if(value.load_operation_id!==row.load_operation_id||value.store_address!==row.destination_addr)throw new Error("Ответ относится к другому месту.");
   selected={...row,load_status:value.load_status};version=value.window?.version||0;el("start").value=displayTime(value.window?.window_start);el("finish").value=displayTime(value.window?.window_finish);
   message((version?"Версия окна "+version:"Окно не задано")+(value.arrival?" · прибытие "+new Date(value.arrival.arrived_at).toLocaleString("ru-RU"):"")+(value.load_status!=="LOADED"?". После выезда окно не изменяется.":""));
  }catch(error){if(scope===key()&&ticket===generation)message(error.message);}
  finally{if(scope===key()&&ticket===generation){busy=false;controls();}}
 }
 async function send(){
  if(busy||damaged||!pending||window.wmsPhysicalLoadState?.isBusy()||window.wmsPhysicalUnload?.isBusy())return;
  const scope=key(),saved=pending,savedRecord=record;busy=true;controls();
  try{
   const value=await request("/api/delivery/timing/window",saved.body);
   if(scope!==key())return;
   if(value.operation_id!==saved.body.operation_id||value.load_operation_id!==saved.body.load_operation_id||value.store_address!==saved.body.store_address
    ||value.version!==saved.body.expected_version+1||Date.parse(value.window_start)!==Date.parse(saved.body.window_start)||Date.parse(value.window_finish)!==Date.parse(saved.body.window_finish))throw new Error("Квитанция не подтверждает сохранённое окно.");
   localStorage.setItem(scope+":confirmed:"+value.operation_id,JSON.stringify({request:saved,result:value}));intent.settle(savedRecord);pending=null;record=null;version=value.version;
   message("Окно сохранено, версия "+value.version+". Обновите назначение рейса перед выездом.");
  }catch(error){if(scope===key()){
   if(error.versionConflict&&localStorage.getItem(scope)===savedRecord.raw){const rejected={...saved,confirmed_rejection:true},raw=JSON.stringify(rejected);localStorage.setItem(scope,raw);pending=rejected;record={storageKey:scope,raw,value:rejected};}
   message(error.message+" Исходный запрос сохранён; новое окно пока заблокировано.");}}
  finally{if(scope===key()){busy=false;controls();}}
 }
 function save(){
  if(busy||pending||damaged||!selected||selected.load_status!=="LOADED"||window.wmsPhysicalLoadState?.hasPending()||window.wmsPhysicalLoadState?.isBusy()||window.wmsPhysicalUnload?.hasPending())return;
  try{
   const start=new Date(el("start").value+el("zone").value),finish=new Date(el("finish").value+el("zone").value),reason=el("reason").value.trim();
   if(!el("start").value||!el("finish").value||!Number.isFinite(+start)||!Number.isFinite(+finish)||finish<start||finish-start>7*86400000||reason.length<8)throw new Error("Укажите обе границы (до7дней) и основание минимум8символов.");
   const value={trip_id:tripId,body:{operation_id:"DELIVERY.WINDOW:"+crypto.randomUUID(),load_operation_id:selected.load_operation_id,store_address:selected.destination_addr,expected_version:version,window_start:start.toISOString(),window_finish:finish.toISOString(),reason}};
   record=intent.save(value);pending=value;controls();void send();
  }catch(error){message(error.message);}
 }
 function restore(){
  const scope=key();if(scope===identity)return;identity=scope;++generation;busy=false;selected=null;rows=[];pending=null;record=null;damaged=false;el("place").replaceChildren();
  panel.hidden=!auth().state.user;
  try{if(auth().state.user){record=intent.read();damaged=!!record.damaged;pending=record.value;message(damaged?"Журнал окна повреждён. Не удаляйте его: передайте ответственному для разбора.":pending?"Есть неподтверждённое окно рейса "+pending.trip_id+". Повторите сохранённый запрос.":"Покажите назначение рейса.");}}
  catch(error){damaged=true;message(error.message);}controls();
 }
 window.addEventListener("wms-physical-load-cleared",()=>{
  ++generation;tripId=null;selected=null;rows=[];el("place").replaceChildren();
  el("start").value="";el("finish").value="";controls();
 });
 window.addEventListener("wms-physical-load-status",event=>{
  ++generation;busy=false;selected=null;tripId=event.detail.trip.id;rows=[];const seen=new Set();
  for(const row of event.detail.members||[]){const id=JSON.stringify([row.load_operation_id,row.destination_addr]);if(row.load_operation_id&&row.destination_addr&&!seen.has(id)){seen.add(id);rows.push(row);}}
  el("place").replaceChildren(...rows.map((row,index)=>{const o=document.createElement("option");o.value=String(index);o.textContent=row.destination_addr+" · "+row.root_uid;return o;}));controls();if(!pending&&!damaged)void read();
 });
 el("read").onclick=()=>void read();el("place").onchange=()=>void read();el("zone").onchange=()=>void read();el("save").onclick=save;el("retry").onclick=()=>void send();
 el("restart").onclick=()=>{if(busy||damaged||!pending?.confirmed_rejection)return;try{localStorage.setItem(key()+":rejected:"+pending.body.operation_id,JSON.stringify(pending));intent.settle(record);pending=null;record=null;selected=null;void read();}catch(error){message(error.message);}controls();};
 window.wmsDeliveryWindow={hasPending:()=>!!pending||damaged,isBusy:()=>busy};window.addEventListener("wms-admin-auth-ready",restore);restore();
})();
