(() => {
 "use strict";
 let panel, message, issue, retry, print, confirm, scan, busy=false, generation=0, current=null,tareNote,tareRefresh;
 const storageKey=()=>JSON.stringify(["nicora.caseSscc",cpTsdApiBase(),cpTsdUser()]);
 const path=task=>"/api/case-pick/tasks/"+task+"/sscc-label";
 function node(tag,text){const e=document.createElement(tag);if(text)e.textContent=text;return e;}
 function mount(){
  if(panel)return;
  panel=node("section");panel.className="tsd-panel";
  panel.append(node("h3","Этикетка пустой коробки SSCC"),node("p","До отбора выдайте этикетку, прикрепите её и подтвердите сканированием. Повторная печать сохраняет идентификатор."));
  issue=node("button","Выдать SSCC");retry=node("button","Повторить сохранённую выдачу");print=node("button","Печать");confirm=node("button","Подтвердить этикетку");scan=node("input");scan.autocomplete="off";scan.setAttribute("aria-label","Скан прикреплённого SSCC");message=node("p");
  tareNote=node("p");tareRefresh=node("button","Обновить показание пустой тары");tareRefresh.onclick=refresh;panel.append(issue,retry,print,scan,confirm,message,tareNote,tareRefresh);
  document.getElementById("cpTsdWeightedBox").after(panel);
  issue.onclick=()=>submit(false);retry.onclick=()=>submit(true);
  print.onclick=async()=>{
   if(!current?.issued||!cpTsd.task)return;
   const id=cpTsd.task.case_pick_task_id;
   const popup=window.open("about:blank","_blank");
   try{
    const response=await fetch(cpTsdApiBase()+path(id)+"/document",{headers:cpTsdHeaders()});
    if(!response.ok)throw new Error("Этикетка не загружена: HTTP "+response.status);
    const blob=await response.blob(),url=URL.createObjectURL(blob);
    if(popup){popup.opener=null;popup.location.href=url;setTimeout(()=>URL.revokeObjectURL(url),60000);}
    else {URL.revokeObjectURL(url);throw new Error("Разрешите открытие окна печати.");}
   }catch(error){popup?.close();message.textContent=error.message;}
  };
  confirm.onclick=async()=>{
   if(busy||window.cpTsdStockBusy||!cpTsd.task||!scan.value.trim())return;
   busy=true;window.cpTsdStockBusy=true;
   try{await cpTsdFetch(path(cpTsd.task.case_pick_task_id)+"/confirm",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({scan:scan.value.trim()})});await refresh();}
   catch(error){message.textContent=error.message;}
   finally{busy=false;window.cpTsdStockBusy=false;}
  };
 }
 async function refresh(){
  mount();const id=cpTsd.task?.case_pick_task_id,gen=++generation;
  current=null;issue.disabled=true;print.disabled=true;confirm.disabled=true;retry.hidden=!localStorage.getItem(storageKey());
  panel.hidden=!id;if(!id)return;
  try{
   const data=await cpTsdFetch(path(id));if(gen!==generation||id!==cpTsd.task?.case_pick_task_id)return;
   current=data;print.disabled=!data.issued;confirm.disabled=!data.issued||data.confirmed;
   issue.disabled=data.issued||!["NEW","ASSIGNED"].includes(cpTsd.task.status)||!!localStorage.getItem(storageKey());
   tareNote.hidden=!data.final_scale_required;tareRefresh.hidden=!data.final_scale_required;
   const readings=data.final_scale_required?await cpTsdFetch("/api/inventory/warehouse-scales/final-captures?task="+id):{items:[]};
   if(gen!==generation||id!==cpTsd.task?.case_pick_task_id)return;
   const tare=(readings.items||[]).find(item=>item.purpose==="EMPTY_TARE"&&item.scan_container===cpTsd.task.sscc);
   tareNote.textContent=tare?"Пустая тара измерена: "+tare.weight_kg+" кг / "+tare.device_mode+" / "+tare.measured_at:"До наполнения малой коробки измерьте её пустую тару на весовом посту и обновите показание.";
   message.textContent=data.issued?data.sscc+" — "+(data.confirmed?"этикетка подтверждена":"требуется скан прикреплённой этикетки"):"SSCC ещё не выдан. Сканируйте текущий идентификатор пустого места.";
  }catch(error){if(gen===generation)message.textContent=error.message;}
 }
 async function submit(replay){
  if(busy||window.cpTsdStockBusy)return;
  busy=true;window.cpTsdStockBusy=true;let attempted=false,priorUnknown=false,key;
  try{
   key=storageKey();let intent=JSON.parse(localStorage.getItem(key)||"null");
   if(!replay&&intent)throw new Error("Повторите сохранённую команду.");
   if(!intent){
    if(replay||!cpTsd.task)throw new Error("Нет сохранённой команды.");
    const carrier=cpTsdEl("cpTsdScanContainer").value.trim();
    if(!carrier)throw new Error("Сканируйте текущий идентификатор пустого места.");
    intent={task:cpTsd.task.case_pick_task_id,body:{operation_id:"CASE.SSCC.UI:"+crypto.randomUUID(),scan_container:carrier,expected_content_version:cpTsd.task.content_version}};
    localStorage.setItem(key,JSON.stringify(intent));
   }
   priorUnknown=!!localStorage.getItem(key+":delivery");localStorage.setItem(key+":delivery","unknown");attempted=true;
   await cpTsdFetch(path(intent.task),{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(intent.body)});
   localStorage.removeItem(key);localStorage.removeItem(key+":delivery");
   cpTsd.task=await cpTsdFetch("/api/case-pick/tasks/"+intent.task);cpTsdRender();
  }catch(error){
   if(attempted&&!priorUnknown&&error.detail?.outcome_confirmed===true){localStorage.removeItem(key);localStorage.removeItem(key+":delivery");}
   message.textContent=error.message;
  }finally{busy=false;window.cpTsdStockBusy=false;retry.hidden=!localStorage.getItem(storageKey());}
 }
 const original=cpTsdRender;
 cpTsdRender=()=>{original();refresh();};
 window.addEventListener("DOMContentLoaded",refresh);
})();
