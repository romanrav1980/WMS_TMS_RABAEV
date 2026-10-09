(() => {
  "use strict";
  let busy=false;
  const key=()=>JSON.stringify(["nicora.caseCarrierMove",cpTsdApiBase(),cpTsdUser()]);
  const pending=()=>{cpTsdEl("cpTsdRetryCarrier").hidden=!localStorage.getItem(key());};
  async function move(retry) {
    if(busy||window.cpTsdStockBusy)return;busy=true;window.cpTsdStockBusy=true;cpTsdEl("cpTsdMoveCarrier").disabled=true;
    let storageKey;
    let attempted = false, priorUnknown = false;
    try {
      storageKey=key();
      if(localStorage.getItem(JSON.stringify(['nicora.caseCarrierReturn',cpTsdApiBase(),cpTsdUser()])))throw new Error('Сначала повторите сохранённый возврат.');
      if(localStorage.getItem(JSON.stringify(['nicora.casePickIntent',cpTsdApiBase(),cpTsdUser()])))throw new Error('Сначала повторите сохранённый отбор товара.');let intent=JSON.parse(localStorage.getItem(storageKey)||"null");
      if(retry&&!intent)throw new Error("Нет незавершённого перемещения.");
      if(!retry&&intent)throw new Error("Сначала повторите сохранённое перемещение.");
      if(!intent){
        if(!cpTsd.task)throw new Error("Выберите паллету отбора.");
        const barcode=cpTsdEl("cpTsdScanContainer").value.trim(),target=cpTsdEl("cpTsdCarrierDestination").value.trim();
        if(!barcode||!target)throw new Error("Отсканируйте паллету и место назначения.");
        intent={task:cpTsd.task.case_pick_task_id,body:{operation_id:"CASE.MOVE.UI:"+crypto.randomUUID(),
          scan_container:barcode,scanned_to_cell:target,expected_content_version:cpTsd.task.content_version}};
        localStorage.setItem(storageKey,JSON.stringify(intent));pending();
      }
      priorUnknown = !!localStorage.getItem(storageKey + ":delivery");
      localStorage.setItem(storageKey + ":delivery", "unknown"); attempted = true;
      await cpTsdFetch("/api/case-pick/tasks/"+intent.task+"/move-carrier",
        {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(intent.body)});
      localStorage.removeItem(storageKey + ":delivery");
      localStorage.removeItem(storageKey);pending();
      cpTsd.task=await cpTsdFetch("/api/case-pick/tasks/"+intent.task);cpTsdRender();
      cpTsdSetState("Перемещение всей паллеты подтверждено; партии и резерв сохранены.");
    }catch(error){
      if(attempted && !priorUnknown && error.detail?.outcome_confirmed===true) {
        localStorage.removeItem(storageKey + ":delivery");
        localStorage.removeItem(storageKey);
      }
      cpTsdSetState(error.message);
    }finally{busy=false;window.cpTsdStockBusy=false;cpTsdEl("cpTsdMoveCarrier").disabled=false;try{pending();}catch(error){cpTsdSetState(error.message);}}
  }
  window.addEventListener("DOMContentLoaded",()=>{
    cpTsdEl("cpTsdMoveCarrier").addEventListener("click",()=>move(false));
    cpTsdEl("cpTsdRetryCarrier").addEventListener("click",()=>move(true));pending();
  });
  window.addEventListener("wms-admin-auth-ready",()=>{try{pending();}catch(error){cpTsdSetState(error.message);}});
})();
