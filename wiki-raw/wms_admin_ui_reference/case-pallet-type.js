(() => {
 "use strict";
 const el=id=>document.getElementById(id);
 const valid=v=>Boolean(v&&Object.keys(v).length===2&&Number.isSafeInteger(v.task_id)&&v.task_id>0&&v.body&&
  Object.keys(v.body).length===5&&typeof v.body.operation_id==="string"&&/^[A-Za-z0-9_.:-]{1,100}$/.test(v.body.operation_id)&&
  Number.isSafeInteger(v.body.pallet_type_id)&&v.body.pallet_type_id>0&&Number.isSafeInteger(v.body.expected_version)&&v.body.expected_version>=0&&
  typeof v.body.scan_container==="string"&&v.body.scan_container.length>0&&v.body.scan_container.length<=200&&
  typeof v.body.reason==="string"&&v.body.reason.trim().length>0&&v.body.reason.length<=500);
 const store=window.wmsCommandIntent.create("wms-case-type:",valid);
 let current=null,busy=false,epoch=0,rejected=null;
 const labels={CASE_TYPE_USE_PHYSICAL_REPACK:"Сборка начата или содержит товар. Используйте физическую перепаковку.",
  CASE_TYPE_BOUND_PLACE_REPACK_REQUIRED:"Место уже связано с отгрузкой, ячейкой или HU. Используйте физическую перепаковку.",
  CASE_TYPE_RELEASE_EMPTY_TARE_FIRST:"Сначала освободите закреплённую пустую тару."};
 function status(text){el("cpTypeStatus").textContent=text;}
 function record(){try{return store.read();}catch{return {raw:null};}}
 function controls(){
  const saved=record(),blocked=busy||saved.raw!==null;
  el("cpTypeSave").disabled=blocked||!current?.can_change_empty_type;
  el("cpTypeRetry").hidden=!saved.value;el("cpTypeRetry").disabled=busy;
  el("cpTypeRestart").hidden=!(saved.damaged||(saved.raw!==null&&rejected===saved.raw));el("cpTypeRestart").disabled=busy;
  el("cpTypeSelect").disabled=el("cpTypeReason").disabled=blocked;
 }
 async function refresh(task){
  const token=++epoch,key=window.wmsAdminAuth.state.user?.username,api=cpTsdApiBase();
  current=null;el("cpTypePanel").hidden=!task;controls();if(!task)return;
  try{
   const [data,types]=await Promise.all([cpTsdFetch("/api/case-pick/tasks/"+task.case_pick_task_id+"/pallet-type"),cpTsdFetch("/api/case-pick/pallet-types?active_only=1")]);
   if(token!==epoch||key!==window.wmsAdminAuth.state.user?.username||api!==cpTsdApiBase()||task.case_pick_task_id!==cpTsd.task?.case_pick_task_id)return;
   current=data;
   el("cpTypePlanned").textContent=data.planned_type_name||"Тип адресата не настроен";
   el("cpTypeActual").textContent=data.actual_type_name+" · версия "+data.version;
   el("cpTypeSelect").replaceChildren(...types.map(t=>new Option(t.pallet_type_name,String(t.pallet_type_id))));
   el("cpTypeSelect").value=String(data.actual_pallet_type_id);
   el("cpTypeTare").href="tare-assembly.html?place_kind=CASE&place_id="+data.case_task_id+"&ware_id="+data.warehouse_id;
   const saved=record();
   status(saved.damaged?"Сохранённый запрос повреждён. Новая команда заблокирована.":saved.value?"Есть сохранённое переопределение CASE "+saved.value.task_id+". Повторите его.":labels[data.change_blocker]||"Проверьте фактический тип перед началом сборки.");
   controls();
  }catch(e){if(token===epoch){status(e.message);controls();}}
 }
 function otherPending(){
  return ["nicora.casePickIntent","nicora.caseCarrierMove","nicora.caseCarrierReturn","nicora.partialShipmentLayout"].some(kind=>
   localStorage.getItem(JSON.stringify([kind,cpTsdApiBase(),cpTsdUser()])));
 }
 async function send(saved){
  if(busy||window.cpTsdStockBusy)return;
  if(saved.storageKey!==store.scope()||localStorage.getItem(saved.storageKey)!==saved.raw)throw Error("Сохранённая команда изменилась.");
  busy=true;window.cpTsdStockBusy=true;controls();
  try{
   const data=await cpTsdFetch("/api/case-pick/tasks/"+saved.value.task_id+"/pallet-type",
    {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(saved.value.body)});
   if(saved.storageKey!==store.scope()||localStorage.getItem(saved.storageKey)!==saved.raw)return;
   if(data.operation_id!==saved.value.body.operation_id||data.case_task_id!==saved.value.task_id||data.status!=="APPLIED"||data.pallet_type_id!==saved.value.body.pallet_type_id)throw Error("Результат не подтверждает сохранённую команду. Повторите её.");
   store.settle(saved);rejected=null;
   if(cpTsd.task?.case_pick_task_id===saved.value.task_id){cpTsd.task=await cpTsdFetch("/api/case-pick/tasks/"+saved.value.task_id);cpTsdRender();}
   status("Фактический тип сохранён. Товарное количество не изменилось.");
  }catch(e){
   if(saved.storageKey===store.scope()&&localStorage.getItem(saved.storageKey)===saved.raw){
    if(e.status<500&&e.detail?.outcome_confirmed!==false)rejected=saved.raw;
    status(e.message+(rejected===saved.raw?" Отказ подтверждён. Обновите данные перед новой командой.":" Запрос сохранён для точного повтора."));
   }
  }finally{busy=false;window.cpTsdStockBusy=false;controls();}
 }
 async function save(){
  if(busy||window.cpTsdStockBusy)return;
  if(record().raw!==null||otherPending())throw Error("Сначала завершите сохранённую складскую команду.");
  if(!current?.can_change_empty_type||current.case_task_id!==cpTsd.task?.case_pick_task_id)throw Error("Покажите актуальное пустое место сборки.");
  const type=Number(el("cpTypeSelect").value);
  if(type===current.actual_pallet_type_id)throw Error("Выбранный тип уже установлен.");
  const saved=store.save({task_id:current.case_task_id,body:{operation_id:"CASE.TYPE.UI:"+crypto.randomUUID(),
   expected_version:current.version,pallet_type_id:type,scan_container:cpTsdEl("cpTsdScanContainer").value.trim(),reason:el("cpTypeReason").value.trim()}});
  await send(saved);
 }
 async function restart(){
  const saved=record();if(busy||!(saved.damaged||(saved.raw!==null&&rejected===saved.raw)))return;
  if(!cpTsd.task)throw Error("Сначала выберите задание и перечитайте его состояние.");
  await cpTsdFetch("/api/case-pick/tasks/"+cpTsd.task.case_pick_task_id+"/pallet-type");
  if(saved.damaged)store.archiveDamaged(saved);else store.settle(saved);
  rejected=null;await refresh(cpTsd.task);
 }
 window.wmsCaseType={hasPending:()=>record().raw!==null};
 window.addEventListener("wms-case-render",e=>refresh(e.detail.task));
 window.addEventListener("wms-admin-auth-ready",()=>{++epoch;rejected=null;refresh(cpTsd.task);});
 window.addEventListener("storage",()=>{rejected=null;controls();});
 el("cpTypeSave").addEventListener("click",()=>cpTsdSafe(save));
 el("cpTypeRetry").addEventListener("click",()=>cpTsdSafe(()=>send(record())));
 el("cpTypeRestart").addEventListener("click",()=>cpTsdSafe(restart));
})();
