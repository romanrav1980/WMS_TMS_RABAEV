(() => {
 "use strict";
 const valid=v=>Boolean(v&&Object.keys(v).length===2&&Number.isSafeInteger(v.task_id)&&v.task_id>0&&v.body&&Object.keys(v.body).length===5&&
  typeof v.body.operation_id==="string"&&/^[A-Za-z0-9_.:-]{1,100}$/.test(v.body.operation_id)&&
  Number.isSafeInteger(v.body.expected_content_version)&&v.body.expected_content_version>=0&&
  typeof v.body.scan_container==="string"&&v.body.scan_container.length>0&&v.body.scan_container.length<=150&&
  typeof v.body.tare_weight_kg==="string"&&/^[0-9]{1,9}(\.[0-9]{1,9})?$/.test(v.body.tare_weight_kg)&&Number(v.body.tare_weight_kg)>0&&
  typeof v.body.measurement_ref==="string"&&v.body.measurement_ref.trim().length>0&&v.body.measurement_ref.length<=100);
 const store=window.wmsCommandIntent.create("wms-case-manual-tare:",valid);
 let panel,weight,reference,scan,save,retry,archive,message,current=null,busy=false,epoch=0,context="";
 const record=()=>{try{return store.read();}catch{return{raw:null,value:null};}};
 const isCurrent=r=>{try{return r.storageKey===store.scope()&&localStorage.getItem(r.storageKey)===r.raw;}catch{return false;}};
 function node(tag,text){const e=document.createElement(tag);if(text)e.textContent=text;return e;}
 function controls(){
  const r=record(),blocked=busy||r.raw!==null;
  for(const field of [weight,reference,scan])field.disabled=blocked;
  save.disabled=blocked||!current?.confirmed||!current?.final_scale_required||Number(cpTsd.task?.picked_qty)>0||!["NEW","ASSIGNED","IN_PROGRESS"].includes(cpTsd.task?.status);
  retry.hidden=!r.value;retry.disabled=busy;archive.hidden=!r.damaged;archive.disabled=busy;
 }
 function mount(){
  if(panel)return;panel=node("section");panel.className="tsd-panel";panel.id="cpManualTare";
  panel.append(node("h3","Вес пустого короба"),node("p","Взвесьте пустой короб до первого отбора. Введите фактическую массу тары; электронный замер не создаётся."));
  for(const [id,title]of [["scan","Скан этикетки короба"],["weight","Пустая тара, кг"],["reference","Номер измерения / записи"]]){
   const label=node("label",title),input=node("input");input.autocomplete="off";input.dataset.field=id;input.setAttribute("aria-label",title);input.maxLength=id==="scan"?150:id==="weight"?19:100;
   if(id==="weight")input.inputMode="decimal";label.append(input);panel.append(label);
  }
  [scan,weight,reference]=["scan","weight","reference"].map(id=>panel.querySelector('[data-field="'+id+'"]'));
  save=node("button","Сохранить вес тары");retry=node("button","Повторить сохранённый вес");archive=node("button","Архивировать повреждённый запрос");message=node("p");message.setAttribute("role","status");
  for(const [button,title,id]of [[save,"Записать измеренный вес пустого короба перед первым отбором.","case.tare.save"],[retry,"Повторить исходный запрос с прежним весом и идентификатором операции.","case.tare.retry"],[archive,"Сохранить повреждённый текст в архив; ранее записанное измерение не отменяется.","case.tare.archive"]]){button.type="button";button.title=title;button.dataset.helpId=id;}
  const help=node("a","Как взвесить пустую тару");help.href="/help/manual-weight.html#empty-tare";help.title="Открыть порядок измерения тары и восстановления запроса.";
  panel.append(save,retry,archive,message,help);document.getElementById("cpTsdWeightedBox").after(panel);
  save.onclick=()=>send(false);retry.onclick=()=>send(true);
  archive.onclick=async()=>{try{const r=record();if(busy||!r.damaged||!cpTsd.task)return;await cpTsdFetch('/api/case-pick/tasks/'+cpTsd.task.case_pick_task_id+'/sscc-label');store.archiveDamaged(r);localStorage.removeItem(r.storageKey+':delivery');await refresh();}catch(e){message.textContent=e.message;}};
 }
 async function refresh(){
  mount();const token=++epoch,task=cpTsd.task?.case_pick_task_id,key=cpTsdApiBase()+":"+cpTsdUser(),next=key+":"+task;
  if(next!==context){context=next;weight.value=reference.value=scan.value="";message.textContent="";}
  current=null;const r=record();panel.hidden=!task&&r.raw===null;controls();if(!task)return;
  try{
   const data=await cpTsdFetch('/api/case-pick/tasks/'+task+'/sscc-label');if(token!==epoch||key!==cpTsdApiBase()+":"+cpTsdUser()||task!==cpTsd.task?.case_pick_task_id)return;
   current=data;panel.hidden=!data.final_scale_required&&r.raw===null;
   message.textContent=r.damaged?"Запрос повреждён: новые измерения заблокированы.":r.value?"Повторите сохранённое измерение задания "+r.value.task_id+".":data.manual_empty_tare?"Пустая тара: "+data.manual_empty_tare.tare_weight_kg+" кг, введено вручную; "+data.manual_empty_tare.measurement_ref:"Подтвердите этикетку и введите фактический вес пустой тары.";
   controls();
  }catch(e){if(token===epoch){current=null;weight.value=reference.value=scan.value="";message.textContent=e.message;controls();}}
 }
 async function send(replay){
  if(busy||window.cpTsdStockBusy)return;let r,priorUnknown=false,attempted=false;
  try{
   r=record();if(r.damaged)throw Error("Сохранённый запрос повреждён.");
   if(!r.value&&(window.wmsCaseType?.hasPending()||window.cpCaseClose?.hasPending()||["retailcase.casePickIntent","retailcase.caseCarrierMove","retailcase.caseCarrierReturn","retailcase.partialShipmentLayout"].some(kind=>localStorage.getItem(JSON.stringify([kind,cpTsdApiBase(),cpTsdUser()])))))throw Error("Сначала повторите сохранённую складскую команду.");
   if(!r.value){if(replay||!current?.confirmed||!cpTsd.task)throw Error("Покажите подтверждённую этикетку пустого короба.");
    r=store.save({task_id:cpTsd.task.case_pick_task_id,body:{operation_id:"CASE.TARE.UI:"+crypto.randomUUID(),expected_content_version:current.current_content_version,scan_container:scan.value.trim(),tare_weight_kg:weight.value.trim(),measurement_ref:reference.value.trim()}});
   }else if(!replay)throw Error("Повторите сохранённое измерение.");
   if(!isCurrent(r))throw Error("Сохранённый запрос изменился.");
   busy=true;window.cpTsdStockBusy=true;controls();priorUnknown=Boolean(localStorage.getItem(r.storageKey+':delivery'));localStorage.setItem(r.storageKey+':delivery','unknown');attempted=true;
   const data=await cpTsdFetch('/api/inventory/warehouse-scales/tasks/'+r.value.task_id+'/manual-empty-tare',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(r.value.body)});
   if(!isCurrent(r))return;
   if(data.operation_id!==r.value.body.operation_id||data.case_pick_task_id!==r.value.task_id||data.sscc!==r.value.body.scan_container||data.origin!=="MANUAL_CONFIRMED"||data.stock_changed!==false)throw Error("Ответ не подтвердил исходное измерение. Повторите запрос.");
   store.settle(r);localStorage.removeItem(r.storageKey+':delivery');weight.value=reference.value=scan.value="";await refresh();
  }catch(e){
   if(r?.storageKey&&!isCurrent(r))return;
   if(attempted&&!priorUnknown&&e.detail?.outcome_confirmed===true&&isCurrent(r)){store.settle(r);localStorage.removeItem(r.storageKey+':delivery');}
   message.textContent=e.message+(record().value?" Повтор сохранит исходное измерение.":"");
  }finally{busy=false;window.cpTsdStockBusy=false;controls();}
 }
 window.wmsCaseManualTare={hasPending:()=>record().raw!==null};
 window.addEventListener("wms-case-render",refresh);window.addEventListener("wms-admin-auth-ready",refresh);window.addEventListener("DOMContentLoaded",refresh);window.addEventListener("storage",refresh);
})();
