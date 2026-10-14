(() => {
 const el=id=>document.getElementById(id);
 let pending=null,busy=false,composition=null,trip=null,generation=0,identity="";
 const base=()=>window.wmsAdminAuth.state.apiBase.replace(/\/$/,"");
 const scope=()=>"wms-physical-load:"+base()+":"+(window.wmsAdminAuth.state.user?.username||"");
 const modeInput=mode=>el(mode==="SINGLE"?"loadShipment":mode==="RECONCILE"?"loadOriginalOperation":"loadIdentifier").value;
 const status=text=>{el("loadStatus").textContent=text;};
 function controls(){document.querySelectorAll("main input,main select,main button").forEach(n=>{n.disabled=busy;});el("loadRetry").hidden=!pending;el("loadRestart").hidden=!pending?.confirmed_rejection;}
 async function request(path,body){
  const r=await fetch(base()+path,{method:body?"POST":"GET",headers:{...window.wmsAdminAuth.headers(),...(body?{"Content-Type":"application/json"}:{})},...(body?{body:JSON.stringify(body)}:{})});
  const data=await r.json();if(!r.ok){const error=new Error(JSON.stringify(data.detail||data));error.confirmed=r.status<500&&data.detail?.outcome_confirmed!==false;throw error;}return data;
 }
 function render(data){
  trip=data;
  el("tripSummary").textContent="Машина: "+(data.trip.transport||"не назначена")+"; ворота: "+(data.trip.dock||"не назначены")+"; физических мест: "+data.loaded_place_count+"; ожидают погрузки СТ: "+data.pending_st_ids.length+". Статус рейса: "+data.trip.condition;
  el("tripRows").replaceChildren(...data.members.map(item=>{
   const row=document.createElement("tr");
   [item.st_number,item.root_uid||"",item.load_status||"Ожидает",item.vehicle_number||"",item.dock||""].forEach(value=>{const td=document.createElement("td");td.textContent=String(value);row.append(td);});return row;
  }));
 }
 async function refresh(){
  if(busy)return;const id=Number(el("tripId").value),key=scope(),version=++generation;
  if(!Number.isSafeInteger(id)||id<1){status("Укажите номер рейса.");return;}
  try{const data=await request("/api/transport/loading/"+id+"/status");if(key===scope()&&version===generation&&id===Number(el("tripId").value))render(data);}
  catch(e){status(e.message);}
 }
 async function showComposition(){
  if(busy)return;const mode=el("loadMode").value,input=modeInput(mode),key=scope(),version=++generation;
  try{
   const preview=await request(mode==="RECONCILE"?"/api/transport/loading/reconciliation-preview?shipping_operation_id="+encodeURIComponent(input):mode==="SINGLE"?"/api/transport/loading/single-preview?shipment_identifier="+encodeURIComponent(input):"/api/warehouse-hus/composition?identifier="+encodeURIComponent(input));const data=mode==="HU"?preview:preview.snapshot;
   if(key!==scope()||version!==generation||mode!==el("loadMode").value||input!==modeInput(mode))return;
   if(preview.already_reconciled||(mode!=="RECONCILE"&&data.historical_composition)||(mode!=="SINGLE"&&data.nodes[0].kind!=="CONTAINER")||data.top_place_count!==1)throw new Error("Выберите актуальное верхнее грузовое место.");
   composition={...data,input,mode,shipment_identifier:preview.shipment_identifier,shipping_operation_id:preview.shipping_operation_id,composition_signature:preview.composition_signature};
   window.wmsPhysicalBoxes.render(composition);
   el("loadCompositionSummary").textContent="Версия "+data.nodes[0].version+"; товарных листьев "+data.leaf_count+"; ячейка "+data.cell+". Подтвердите новые измерения всего места.";
  }catch(e){composition=null;status(e.message);}
 }
 async function submit(action){
  if(busy||pending){status("Сначала повторите сохранённую операцию.");return;}
  const key=scope(),id=Number(el("tripId").value);
  try{
   if(!trip||trip.trip.id!==id)throw new Error("Сначала покажите назначение этого рейса.");
   let body={operation_id:"TT."+action+":"+crypto.randomUUID()},path;
   if(action==="LOAD"){
    if(!composition||composition.mode!==el("loadMode").value||composition.input!==modeInput(composition.mode))throw new Error("Сначала покажите текущий состав места.");
    body={...body,identifier:composition.root,expected_version:composition.nodes[0].version,scan_container:el("loadScan").value,scan_cell:el("loadCell").value,
     transport_task_id:id,scan_vehicle:el("loadVehicle").value,scan_dock:el("loadDock").value,measurements:{origin:"MANUAL_CONFIRMED",content_version:composition.nodes[0].version,
      gross_weight_kg:el("loadGross").value,width_m:el("loadWidth").value,depth_m:el("loadDepth").value,height_m:el("loadHeight").value}};
    const boxes=window.wmsPhysicalBoxes.collect();if(boxes)body.physical_boxes=boxes;
    if(composition.mode==="RECONCILE"){body.identifier=composition.shipping_operation_id;body.expected_composition_signature=composition.composition_signature;path="/api/transport/loading/confirm-reconciliation";}else if(composition.mode==="SINGLE"){body.identifier=composition.shipment_identifier;body.expected_composition_signature=composition.composition_signature;path="/api/transport/loading/confirm-single";}else path="/api/transport/loading/confirm";
   }else path="/api/transport/loading/"+id+"/depart";
   const saved={body,path,trip_id:id};localStorage.setItem(key,JSON.stringify(saved));pending=saved;await send(key);
  }catch(e){status(e.message);}
 }
 async function send(key){
  if(!pending||busy)return;busy=true;controls();const saved=pending;
  try{
   const result=await request(saved.path,saved.body);
   localStorage.removeItem(key);
   if(key!==scope())return;
   pending=null;composition=null;window.wmsPhysicalBoxes.render(null);el("loadCompositionSummary").textContent="";
   const data=await request("/api/transport/loading/"+saved.trip_id+"/status");
   if(key===scope()){el("tripId").value=String(saved.trip_id);render(data);status("Подтверждено. Операция "+result.operation_id);}
  }catch(e){if(key===scope()){if(e.confirmed){pending={...saved,confirmed_rejection:true};localStorage.setItem(key,JSON.stringify(pending));}status(e.message+(e.confirmed?" Отказ подтверждён: можно исправить данные и начать новую операцию.":" Повтор сохраняет исходный идентификатор и сканы."));}}
  finally{busy=false;controls();}
 }
 function auth(){
  const key=scope();if(key===identity)return;identity=key;++generation;trip=null;composition=null;pending=null;window.wmsPhysicalBoxes.render(null);el("tripRows").replaceChildren();el("tripSummary").textContent="";el("loadCompositionSummary").textContent="";
  try{pending=JSON.parse(localStorage.getItem(key)||"null");if(pending){el("tripId").value=String(pending.trip_id);status("Есть неподтверждённая операция. Повторите сохранённые данные.");}}catch(e){status("Не удалось восстановить операцию: "+e.message);}controls();
 }
 el("tripLoad").addEventListener("click",refresh);el("loadComposition").addEventListener("click",showComposition);
 el("loadConfirm").addEventListener("click",()=>submit("LOAD"));el("tripDepart").addEventListener("click",()=>submit("DEPART"));
 el("loadRetry").addEventListener("click",()=>send(scope()));el("loadRestart").addEventListener("click",()=>{if(!busy&&pending?.confirmed_rejection){localStorage.removeItem(scope());pending=null;controls();status("Исправьте данные. Следующее подтверждение создаст новую операцию.");}});window.addEventListener("wms-admin-auth-ready",auth);auth();
})();
