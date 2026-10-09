(() => {
 "use strict";
 const key=()=>JSON.stringify(["nicora.caseCarrierReturn",cpTsdApiBase(),cpTsdUser()]);
 let busy=false;
 const originalRender=cpTsdRender;
 cpTsdRender=()=>{
  originalRender();
  const host=cpTsdEl("cpTsdReturnDestinations");host.replaceChildren();
  for(const lot of cpTsd.task?.physical_lots||[]){
   const label=document.createElement("label");
   const line=cpTsd.task.lines.find(l=>l.case_pick_line_id===lot.case_pick_line_id);
   label.append(document.createTextNode(lot.articul+" / "+lot.physical_qty+" — скан исходной ячейки "+(line?.cell_code||"")));
   const input=document.createElement("input");input.dataset.returnUid=lot.uid;input.autocomplete="off";
   label.append(input);host.append(label);
  }
  cpTsdEl("cpTsdRetryReturn").hidden=!localStorage.getItem(key());
 };
 async function submit(retry){
  if(busy||window.cpTsdStockBusy)return;
  busy=true;window.cpTsdStockBusy=true;let storageKey,priorUnknown=false,attempted=false;
  try{
   storageKey=key();
   for(const kind of ["nicora.casePickIntent","nicora.caseCarrierMove"]){
    if(localStorage.getItem(JSON.stringify([kind,cpTsdApiBase(),cpTsdUser()])))throw new Error("Сначала повторите незавершённую команду.");
   }
   let intent=JSON.parse(localStorage.getItem(storageKey)||"null");
   if(!retry&&intent)throw new Error("Сначала повторите сохранённый возврат.");
   if(!intent){
    if(retry||!cpTsd.task)throw new Error("Нет сохранённого возврата или выбранной паллеты.");
    const destinations={};
    for(const input of document.querySelectorAll("[data-return-uid]")){
     if(!input.value.trim())throw new Error("Отсканируйте исходные ячейки всех партий.");
     destinations[input.dataset.returnUid]=input.value.trim();
    }
    const scan=cpTsdEl("cpTsdScanContainer").value.trim();
    if(!scan||!Object.keys(destinations).length)throw new Error("Отсканируйте идентификатор паллеты.");
    intent={task:cpTsd.task.case_pick_task_id,body:{operation_id:"CASE.RETURN.UI:"+crypto.randomUUID(),
     scan_container:scan,expected_content_version:cpTsd.task.content_version,destinations}};
    localStorage.setItem(storageKey,JSON.stringify(intent));
   }
   priorUnknown=!!localStorage.getItem(storageKey+":delivery");
   localStorage.setItem(storageKey+":delivery","unknown");attempted=true;
   await cpTsdFetch("/api/case-pick/tasks/"+intent.task+"/return-carrier",
    {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(intent.body)});
   localStorage.removeItem(storageKey+":delivery");localStorage.removeItem(storageKey);
   cpTsd.task=await cpTsdFetch("/api/case-pick/tasks/"+intent.task);cpTsdRender();
   cpTsdSetState("Товар возвращён в исходные ячейки. Резерв снят, паллета отбора отменена.");
  }catch(error){
   if(attempted&&!priorUnknown&&error.detail?.outcome_confirmed===true){
    localStorage.removeItem(storageKey+":delivery");localStorage.removeItem(storageKey);
   }
   cpTsdSetState(error.message);
  }finally{
   busy=false;window.cpTsdStockBusy=false;
   cpTsdEl("cpTsdRetryReturn").hidden=!localStorage.getItem(key());
  }
 }
 window.addEventListener("DOMContentLoaded",()=>{
  cpTsdEl("cpTsdReturnCarrier").addEventListener("click",()=>submit(false));
  cpTsdEl("cpTsdRetryReturn").addEventListener("click",()=>submit(true));
 });
})();
