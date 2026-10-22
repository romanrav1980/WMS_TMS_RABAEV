(() => {
 "use strict";
 const key=()=>JSON.stringify(["retailcase.caseCarrierReturn",cpTsdApiBase(),cpTsdUser()]);
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
  cpTsdEl("cpTsdCancelEmpty").disabled=!cpTsd.task||!!(cpTsd.task.physical_lots||[]).length||
    !/^0(?:\.0+)?$/.test(String(cpTsd.task.picked_qty??"0"))||["CANCELLED","SHIPPED","FAILED"].includes(cpTsd.task.status);
 };
 async function submit(retry,empty=false){
  if(busy||window.cpTsdStockBusy||window.wmsCaseType?.hasPending()||window.wmsCaseManualTare?.hasPending())return;
  busy=true;window.cpTsdStockBusy=true;let storageKey,raw,priorUnknown=false,attempted=false;
  const sameIdentity=()=>Boolean(window.wmsAdminAuth?.state.user?.username)&&storageKey===key();
  const current=()=>sameIdentity()&&raw!==undefined&&localStorage.getItem(storageKey)===raw;
  try{
   storageKey=key();
   for(const kind of ["retailcase.casePickIntent","retailcase.caseCarrierMove"]){
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
    if(!scan||(!empty&&!Object.keys(destinations).length))throw new Error("Отсканируйте идентификатор паллеты.");
    const reason=cpTsdEl("cpTsdEmptyCancelReason").value.trim();
    if(empty&&(Object.keys(destinations).length||!reason))throw new Error("Требуются пустое место и причина отмены.");
    intent={task:cpTsd.task.case_pick_task_id,body:{operation_id:"CASE.RETURN.UI:"+crypto.randomUUID(),
     scan_container:scan,expected_content_version:cpTsd.task.content_version,destinations,...(empty?{allow_empty:true,reason}:{})}};
    localStorage.setItem(storageKey,JSON.stringify(intent));
   }
   raw=localStorage.getItem(storageKey);if(!current())throw Error("Сохранённый запрос или пользователь изменился.");
   priorUnknown=!!localStorage.getItem(storageKey+":delivery");
   localStorage.setItem(storageKey+":delivery","unknown");attempted=true;
   const result=await cpTsdFetch("/api/case-pick/tasks/"+intent.task+"/return-carrier",
    {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(intent.body)});
   if(!current())return;
   if(result.operation_id!==intent.body.operation_id||result.task!==intent.task||!["CANCELLED_EMPTY","RETURNED"].includes(result.status))throw Error("Ответ не подтвердил исходный возврат. Повторите сохранённый запрос.");
   localStorage.removeItem(storageKey+":delivery");localStorage.removeItem(storageKey);
   cpTsd.task=null;cpTsdRender();
   const nextTask=await cpTsdFetch("/api/case-pick/tasks/"+intent.task);if(!sameIdentity())return;
   cpTsd.task=nextTask;cpTsdRender();
   cpTsdSetState(result.status==="CANCELLED_EMPTY"?
    "Пустое место отменено, резерв снят. Если закреплена тара, освободите её бронь; затем примите решение по волне. Потребность заказа сохраняется.":
    "Товар возвращён в исходные ячейки. Резерв снят, паллета отбора отменена.");
  }catch(error){
   if(!sameIdentity())return;
   if([401,403].includes(error.status)){cpTsd.task=null;cpTsdRender();}
   if(attempted&&!priorUnknown&&current()&&error.detail?.outcome_confirmed===true){
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
  cpTsdEl("cpTsdCancelEmpty").addEventListener("click",()=>submit(false,true));
 });
})();
