(() => {
 const el=id=>document.getElementById(id);
 let pending=null,busy=false,composition=null,trip=null,generation=0,identity="",record=null;
 const base=()=>window.wmsAdminAuth.state.apiBase.replace(/\/$/,"");
 const scope=()=>"wms-physical-load:"+base()+":"+(window.wmsAdminAuth.state.user?.username||"");
 const intent=window.wmsLoadingIntent.create(scope);
 const modeInput=mode=>el(mode==="SINGLE"?"loadShipment":mode==="RECONCILE"?"loadOriginalOperation":"loadIdentifier").value;
 const status=text=>{el("loadStatus").textContent=text;};
 function controls(){for(const [id,visible]of [["loadShipment",el("loadMode").value==="SINGLE"],["loadOriginalOperation",el("loadMode").value==="RECONCILE"],["loadIdentifier",["HU","BULK"].includes(el("loadMode").value)]])el(id).closest("label").hidden=!visible;el("loadConfirm").textContent=el("loadMode").value==="BULK"?"Погрузить короб":"Подтвердить фактическую погрузку";document.querySelectorAll("main input,main select,main button").forEach(n=>{if(!n.closest("#deliveryWindow"))n.disabled=busy;});el("loadRetry").hidden=!pending||!!record?.damaged;el("loadArchive").hidden=!record?.damaged;el("loadRestart").hidden=!pending?.confirmed_rejection;el("tripDepart").disabled=busy||!!pending||trip?.trip?.condition!=="Спланирован"||!trip?.all_members_physically_loaded;el("loadConfirm").disabled=busy||!!pending||trip?.trip?.condition!=="Спланирован";}
 async function request(path,body){
  const r=await fetch(base()+path,{method:body?"POST":"GET",headers:{...window.wmsAdminAuth.headers(),...(body?{"Content-Type":"application/json"}:{})},...(body?{body:JSON.stringify(body)}:{})});
  const data=await r.json();if(!r.ok){const error=new Error(JSON.stringify(data.detail||data));error.status=r.status;error.confirmed=(r.status===422||data.detail?.outcome_confirmed===true)&&![401,403].includes(r.status)&&!String(data.detail?.message||data.detail?.code||"").includes("CONFLICT");throw error;}return data;
 }
 function clearMeasurements(){
  for(const id of ["loadGross","loadWidth","loadDepth","loadHeight","loadTempObserved","loadTempReference","departTempObserved","departTempReference"]){const node=el(id);if(node)node.value="";}
  for(const id of ["loadTempConfirm","departTempConfirm","loadBoxWeightsEnabled"]){const node=el(id);if(node)node.checked=false;}
 }
 function clearTrip(){
  clearMeasurements();
  trip=null;composition=null;window.wmsPhysicalBoxes.render(null);window.wmsPalletFloorType.reset();
  el("tripRows").replaceChildren();el("tripSummary").textContent="Назначение рейса не прочитано.";el("loadCompositionSummary").textContent="";
  el("loadTempVersion").value="";el("loadTempProfile").textContent="";el("departTempProfile").textContent="";
  window.dispatchEvent(new CustomEvent("wms-physical-load-cleared"));controls();
 }
 function render(data){
  trip=data;
  const profile=data.temperature?.vehicle_profile,capability=profile?.profile?.temperature_capability;
  el("loadTempVersion").value=profile?.state==="READY"&&capability?String(profile.version):"";
  el("loadTempProfile").textContent=profile?.state==="READY"&&capability?
   "Текущая версия "+profile.version+": возможности машины "+capability.temp_min_c+" … "+capability.temp_max_c+" °C. Фактическое измерение подтвердите отдельно.":
   "Температурные возможности текущей машины не подтверждены. Для температурного товара настройте профиль автомобиля.";

  el("departTempProfile").textContent=el("loadTempProfile").textContent+(data.temperature?.departure_confirmation?" Сохранён факт температуры выезда "+data.temperature.departure_confirmation.observed_c+" °C.":"");
  const floor=data.floor_capacity?.departure_confirmation;
  if(floor?.status==="COMPATIBLE")el("departTempProfile").textContent+=" Норматив тары на выезде подтверждён: "+floor.matching_variants.join(", ")+"; верхних мест "+floor.loaded_top_places+".";
  window.dispatchEvent(new CustomEvent("wms-physical-load-status",{detail:data}));
  el("tripSummary").textContent="Машина: "+(data.trip.transport||"не назначена")+"; ворота: "+(data.trip.dock||"не назначены")+"; физических мест: "+data.loaded_place_count+"; ожидают погрузки СТ: "+data.pending_st_ids.length+". Статус рейса: "+data.trip.condition;
  el("tripRows").replaceChildren(...data.members.map(item=>{
   const row=document.createElement("tr");
   [item.st_number,item.root_uid||"",item.load_status||"Ожидает",item.vehicle_number||"",item.dock||"",data.floor_capacity?.load_confirmations?.[item.load_operation_id]?.current_type_name||"Тип верхнего места не подтверждён",data.temperature?.load_confirmations?.[item.load_operation_id]?.confirmation?.observed_c?data.temperature.load_confirmations[item.load_operation_id].confirmation.observed_c+" °C · вручную":"Не подтверждена"].forEach(value=>{const td=document.createElement("td");td.textContent=String(value);row.append(td);});return row;
  }));controls();
 }
 async function refresh(){
  if(busy)return;const id=Number(el("tripId").value),key=scope(),version=++generation;
  if(!Number.isSafeInteger(id)||id<1){clearTrip();status("Укажите номер рейса.");return;}
  if(trip?.trip?.id!==id)clearTrip();
  try{const data=await request("/api/transport/loading/"+id+"/status");if(key===scope()&&version===generation&&id===Number(el("tripId").value))render(data);}
  catch(e){if(key!==scope()||version!==generation||id!==Number(el("tripId").value))return;if([401,403,404].includes(e.status))clearTrip();status(e.message);}
 }
 async function showComposition(){
  if(busy)return;const mode=el("loadMode").value,input=modeInput(mode),key=scope(),version=++generation;window.wmsPalletFloorType.reset();
  clearMeasurements();composition=null;window.wmsPhysicalBoxes.render(null);el("loadCompositionSummary").textContent="";
  try{
   const preview=await request(mode==="RECONCILE"?"/api/transport/loading/reconciliation-preview?shipping_operation_id="+encodeURIComponent(input):mode==="SINGLE"?"/api/transport/loading/single-preview?shipment_identifier="+encodeURIComponent(input):mode==="BULK"?"/api/transport/loading/bulk-box-preview?identifier="+encodeURIComponent(input):"/api/warehouse-hus/composition?identifier="+encodeURIComponent(input));const data=mode==="HU"?preview:preview.snapshot;
   if(key!==scope()||version!==generation||mode!==el("loadMode").value||input!==modeInput(mode))return;
   if(preview.already_reconciled||(mode!=="RECONCILE"&&data.historical_composition)||(mode!=="SINGLE"&&!(mode==="BULK"&&preview.source_kind==="SINGLE")&&data.nodes[0].kind!=="CONTAINER")||data.top_place_count!==1)throw new Error("Выберите актуальное верхнее грузовое место.");
   if(mode==="BULK"&&((preview.source_kind!=="SINGLE"&&data.nodes[0].type!=="BOX")||data.ancestors?.length))throw new Error("Сканируйте самостоятельный короб. Если он вложен в паллету, сначала оформите вскрытие.");
   composition={...data,input,mode,bulk_source_kind:preview.source_kind,bulk_identifier:preview.identifier,shipment_identifier:preview.shipment_identifier,shipping_operation_id:preview.shipping_operation_id,composition_signature:preview.composition_signature};
   window.wmsPhysicalBoxes.render(composition);
   el("loadCompositionSummary").textContent="Версия "+data.nodes[0].version+"; товарных листьев "+data.leaf_count+"; ячейка "+data.cell+". Подтвердите новые измерения всего места.";
   await window.wmsPalletFloorType.read(composition,request,()=>key===scope()&&version===generation&&mode===el("loadMode").value&&input===modeInput(mode));
  }catch(e){if(key===scope()&&version===generation){composition=null;window.wmsPhysicalBoxes.render(null);el("loadCompositionSummary").textContent="";window.wmsPalletFloorType.reset();status(e.message);}}
 }
 async function submit(action){
  if(busy||pending||window.wmsPhysicalUnload?.hasPending()||window.wmsPhysicalUnload?.isBusy()||window.wmsDeliveryWindow?.hasPending()||window.wmsDeliveryWindow?.isBusy()){status("Сначала повторите сохранённую операцию.");return;}
  const key=scope(),id=Number(el("tripId").value);
  try{
   if(!trip||trip.trip.id!==id)throw new Error("Сначала покажите назначение этого рейса.");
   let body={operation_id:"TT."+action+":"+crypto.randomUUID()},path;
   if(action==="TYPE"){
    if(!composition||composition.mode!==el("loadMode").value||composition.input!==modeInput(composition.mode))throw new Error("Сначала покажите текущий состав места.");
    body={...body,...window.wmsPalletFloorType.collect(composition)};path="/api/inventory/pallet-floor-types";
   }else if(action==="LOAD"){
    if(!composition||composition.mode!==el("loadMode").value||composition.input!==modeInput(composition.mode))throw new Error("Сначала покажите текущий состав места.");
    body={...body,identifier:composition.root,expected_version:composition.nodes[0].version,scan_container:el("loadScan").value,scan_cell:el("loadCell").value,
     transport_task_id:id,scan_vehicle:el("loadVehicle").value,scan_dock:el("loadDock").value,measurements:{origin:"MANUAL_CONFIRMED",content_version:composition.nodes[0].version,
      gross_weight_kg:el("loadGross").value,width_m:el("loadWidth").value,depth_m:el("loadDepth").value,height_m:el("loadHeight").value}};
    const observed=el("loadTempObserved").value,reference=el("loadTempReference").value;
    if(observed||reference||el("loadTempConfirm").checked){
     const version=Number(el("loadTempVersion").value);
     if(!el("loadTempConfirm").checked||!Number.isSafeInteger(version)||version<1||!reference.trim()||!/^-?[0-9]{1,6}(\.[0-9]{1,3})?$/.test(observed))throw new Error("Подтвердите текущее измерение, основание и действующий температурный профиль машины.");
     body.temperature_confirmation={origin:"MANUAL_AT_LOADING",observed_c:observed,vehicle_profile_version:version,observation_reference:reference};
    }
    const boxes=window.wmsPhysicalBoxes.collect();if(boxes)body.physical_boxes=boxes;
    if(composition.mode==="RECONCILE"){body.identifier=composition.shipping_operation_id;body.expected_composition_signature=composition.composition_signature;path="/api/transport/loading/confirm-reconciliation";}else if(composition.mode==="SINGLE"){body.identifier=composition.shipment_identifier;body.expected_composition_signature=composition.composition_signature;path="/api/transport/loading/confirm-single";}else if(composition.mode==="BULK"){body.source_kind=composition.bulk_source_kind;body.identifier=composition.bulk_identifier;if(body.source_kind==="SINGLE")body.expected_composition_signature=composition.composition_signature;path="/api/transport/loading/confirm-bulk-box";}else path="/api/transport/loading/confirm";
   }else{
    const observed=el("departTempObserved").value,reference=el("departTempReference").value;
    if(observed||reference||el("departTempConfirm").checked){
     const version=Number(el("loadTempVersion").value);
     if(!el("departTempConfirm").checked||!Number.isSafeInteger(version)||version<1||!reference.trim()||!/^-?[0-9]{1,6}(\.[0-9]{1,3})?$/.test(observed))throw new Error("Подтвердите новое измерение перед выездом и действующий профиль машины.");
     body.temperature_confirmation={origin:"MANUAL_AT_DEPARTURE",observed_c:observed,vehicle_profile_version:version,observation_reference:reference};
    }
    path="/api/transport/loading/"+id+"/depart";
   }

   const saved={body,path,trip_id:id};record=intent.save(saved);pending=saved;await send(key);
  }catch(e){status(e.message);}
 }
 async function send(key){
  if(!pending||busy||record?.damaged)return;const saved=pending,raw=localStorage.getItem(key);
  if(key!==scope()||raw!==JSON.stringify(saved)){status('Сохранённая команда изменилась. Отправка остановлена.');return;}
  busy=true;controls();
  try{
   const result=await request(saved.path,saved.body);
   if(key!==scope()||localStorage.getItem(key)!==raw)return;
   if(!window.wmsLoadingIntent.confirms(saved,result))throw new Error("Ответ не подтверждает сохранённую операцию. Повторите исходный запрос.");
   intent.settle({storageKey:key,raw});record=null;
   if(key!==scope())return;
   pending=null;composition=null;window.wmsPalletFloorType.reset();el("loadTempObserved").value="";el("loadTempReference").value="";el("loadTempConfirm").checked=false;el("departTempObserved").value="";el("departTempReference").value="";el("departTempConfirm").checked=false;window.wmsPhysicalBoxes.render(null);el("loadCompositionSummary").textContent="";
   const data=await request("/api/transport/loading/"+saved.trip_id+"/status");
   if(key===scope()){el("tripId").value=String(saved.trip_id);render(data);status("Подтверждено. Операция "+result.operation_id);}
  }catch(e){if(key===scope()&&localStorage.getItem(key)===raw){if(e.confirmed){const rejected={...saved,confirmed_rejection:true},next=JSON.stringify(rejected);localStorage.setItem(key,next);if(localStorage.getItem(key)!==next)throw new Error("Не удалось сохранить подтверждённый отказ.");pending=rejected;record={storageKey:key,raw:next,value:rejected};}status(e.message+(e.confirmed?" Отказ подтверждён: можно исправить данные и начать новую операцию.":" Повтор сохраняет исходный идентификатор и сканы."));}}
  finally{busy=false;controls();}
 }
 function auth(){
  const key=scope();if(key===identity)return;identity=key;++generation;trip=null;composition=null;pending=null;clearMeasurements();window.wmsPalletFloorType.reset();window.wmsPhysicalBoxes.render(null);el("tripRows").replaceChildren();el("tripSummary").textContent="";el("loadCompositionSummary").textContent="";
  record=null;
  try{if(window.wmsAdminAuth.state.user?.username){record=intent.read();pending=record.damaged?{damaged:true}:record.value;
   if(record.damaged)status("Сохранённая команда повреждена. Новые операции заблокированы. Архивируйте исходный текст и перечитайте рейс.");
   else if(pending){el("tripId").value=String(pending.trip_id);status("Есть неподтверждённая операция. Повторите сохранённые данные.");}
  }}catch(e){pending={damaged:true};status("Не удалось прочитать сохранённую операцию: "+e.message);}controls();
  const initial=Number(new URLSearchParams(location.search).get("trip_id"));
  if((!pending||record?.damaged)&&window.wmsAdminAuth.state.user?.username&&Number.isSafeInteger(initial)&&initial>0){el("tripId").value=String(initial);if(!pending)refresh();}
 }
 window.wmsPhysicalLoadState={hasPending:()=>!!pending,isBusy:()=>busy,refresh};
 el("tripLoad").addEventListener("click",refresh);el("loadComposition").addEventListener("click",showComposition);
 el("palletFloorConfirm").addEventListener("click",()=>submit("TYPE"));
 el("loadConfirm").addEventListener("click",()=>submit("LOAD"));el("tripDepart").addEventListener("click",()=>submit("DEPART"));
 el("loadRetry").addEventListener("click",()=>send(scope()));
 el("loadRestart").addEventListener("click",()=>{try{if(!busy&&pending?.confirmed_rejection){intent.settle(record);record=null;pending=null;controls();status("Исправьте данные. Следующее подтверждение создаст новую операцию.");}}catch(e){status(e.message);}});
 el("loadArchive").addEventListener("click",async()=>{try{if(busy||!record?.damaged)return;intent.archiveDamaged(record);record=null;pending=null;controls();status("Исходный текст сохранён в архиве. Сверьте серверный статус перед новой операцией: архив не отменяет ранее выполненную погрузку.");await refresh();}catch(e){status(e.message);}});
 el("loadMode").addEventListener("change",()=>{generation++;composition=null;clearMeasurements();window.wmsPhysicalBoxes.render(null);window.wmsPalletFloorType.reset();el("loadCompositionSummary").textContent="";controls();});
 el("loadComposition").title="Перечитать состав места; введённые вес, размеры и температура сбросятся для нового измерения.";
 el("loadComposition").dataset.helpId="loading.composition.refresh";
 window.addEventListener("wms-admin-auth-ready",auth);auth();
})();
