(() => {
  "use strict";
  let busy = false, policyGeneration = 0;
  const key = () => JSON.stringify(["nicora.casePickIntent", cpTsdApiBase(), cpTsdUser()]);
  const saved = () => JSON.parse(localStorage.getItem(key()) || "null");
  function pending() {
    const intent = saved(), button = cpTsdEl("cpTsdRetryPosting");
    button.hidden = !intent;
    button.textContent = intent ? "Повторить: паллета " + intent.task + ", строка " + intent.line : "";
  }
  const originalRender = cpTsdRender;
  cpTsdRender = function () {
    originalRender();
    cpTsdEl("cpTsdScanCell").value = "";
    cpTsdEl("cpTsdScanProduct").value = "";
    cpTsdEl("cpTsdScanContainer").value = "";
    cpTsdEl("cpTsdUnitCodes").value = "";
    const line = cpTsdCurrentLine(), task = cpTsd.task, generation = ++policyGeneration;
    const profile = cpTsdEl("cpTsdMarkProfile");
    profile.replaceChildren();cpTsdEl("cpTsdMarking").hidden = true;
    if (!line || !task) return;
    cpTsdFetch("/api/case-pick/tasks/" + task.case_pick_task_id + "/lines/" + line.case_pick_line_id + "/marking-policy")
      .then(policy => {
        if(generation !== policyGeneration)return;
        cpTsdEl("cpTsdMarking").hidden = !policy.marking_required;
        for(const item of policy.profiles) {
          const option = document.createElement("option");
          option.value = JSON.stringify(item);option.textContent = item.system_code + " / " + item.profile_code;profile.appendChild(option);
        }
        if(policy.marking_required && !policy.profiles.length)cpTsdSetState("У товара нет настроенного профиля маркировки.");
      }).catch(error => { if(generation === policyGeneration)cpTsdSetState(error.message); });
  };
  async function post(retry) {
    if (busy || window.cpTsdStockBusy) return;
    busy = true;window.cpTsdStockBusy = true;cpTsdEl("cpTsdConfirm").disabled = cpTsdEl("cpTsdRetryPosting").disabled = true;
    let storageKey;
    let attempted = false, priorUnknown = false;
    try {
      storageKey = key();
      if(localStorage.getItem(JSON.stringify(['nicora.caseCarrierReturn',cpTsdApiBase(),cpTsdUser()])))throw new Error('Сначала повторите сохранённый возврат.');
      if(localStorage.getItem(JSON.stringify(['nicora.caseCarrierMove',cpTsdApiBase(),cpTsdUser()])))throw new Error('Сначала повторите сохранённое перемещение паллеты.');
      let intent = saved();
      if(retry && !intent)throw new Error("Нет незавершённой команды.");
      if(!retry && intent)throw new Error("Сначала повторите сохранённую команду.");
      if(!intent) {
        const task=cpTsd.task,line=cpTsdCurrentLine();
        if(!task || !line)throw new Error("Выберите строку.");
        const quantity=cpTsdEl("cpTsdFactQty").value.trim();
        if(!/^[0-9]{1,18}([.][0-9]{1,9})?$/.test(quantity))throw new Error("Введите накопленный факт в базовой единице.");
        const codes=cpTsdEl("cpTsdUnitCodes").value.split(/\r?\n/).filter(value=>value.length>0);
        if(codes.length && !cpTsdEl("cpTsdMarkProfile").value)throw new Error("Выберите профиль маркировки.");
        const profile=codes.length ? JSON.parse(cpTsdEl("cpTsdMarkProfile").value) : null;
        const payload={operation_id:"CASE.PICK.UI:"+crypto.randomUUID(),fact_qty:quantity,
          scan_cell:cpTsdEl("cpTsdScanCell").value.trim(),scan_product:cpTsdEl("cpTsdScanProduct").value.trim()||null,
          scan_box:cpTsdEl("cpTsdScanBox").value.trim()||null,scan_container:cpTsdEl("cpTsdScanContainer").value.trim(),
          unit_scans:codes.map(code=>({...profile,code})),offline_event_id:crypto.randomUUID(),
          resource_id:cpTsd.session?.resource_id||null,resource_session_id:cpTsd.session?.session_id||null,
          equipment_id:cpTsd.session?.equipment_id||null,actor:cpTsdPicker()};
        if(!payload.scan_cell || !payload.scan_container)throw new Error("Отсканируйте ячейку и идентификатор паллеты отбора.");
        intent={task:task.case_pick_task_id,line:line.case_pick_line_id,payload};
        localStorage.setItem(storageKey,JSON.stringify(intent));pending();
      }
      cpTsdSetState(retry?"Повтор сохранённой команды...":"Проведение отбора...");
      priorUnknown = !!localStorage.getItem(storageKey + ":delivery");
      localStorage.setItem(storageKey + ":delivery", "unknown"); attempted = true;
      await cpTsdFetch("/api/case-pick/tasks/"+intent.task+"/lines/"+intent.line+"/confirm",
        {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(intent.payload)});
      localStorage.removeItem(storageKey + ":delivery");
      localStorage.removeItem(storageKey);pending();
      cpTsd.task=await cpTsdFetch("/api/case-pick/tasks/"+intent.task);
      cpTsdRender();cpTsdSetState("Отбор проведён. Товар и резерв находятся в составе паллеты отбора.");
    } catch(error) {
      if(attempted && !priorUnknown && error.detail?.outcome_confirmed===true) {
        localStorage.removeItem(storageKey + ":delivery");
        localStorage.removeItem(storageKey);
      }
      let unresolved = false;
      try { unresolved = !!(storageKey && localStorage.getItem(storageKey)); } catch (_) {}
      cpTsdSetState(error.message + (unresolved ? " Исход не подтверждён: повторите сохранённую команду." : ""));
    } finally {
      busy=false;window.cpTsdStockBusy=false;cpTsdEl("cpTsdConfirm").disabled=cpTsdEl("cpTsdRetryPosting").disabled=false;
      try{pending();}catch(error){cpTsdSetState(error.message);}
    }
  }
  cpTsdConfirmLine = () => post(false);
  window.addEventListener("DOMContentLoaded",()=>{
    cpTsdEl("cpTsdRetryPosting").addEventListener("click",()=>post(true));pending();
  });
  window.addEventListener("wms-admin-auth-ready",()=>{try{pending();}catch(error){cpTsdSetState(error.message);}});
})();
