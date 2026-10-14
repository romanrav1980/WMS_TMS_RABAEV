(() => {
  "use strict";
  let busy = false, policyGeneration = 0, currentPolicy = null;
  const key = () => JSON.stringify(["retailcase.casePickIntent", cpTsdApiBase(), cpTsdUser()]);
  const saved = () => {
    const value=JSON.parse(localStorage.getItem(key()) || "null");
    if(value&&(!Number.isSafeInteger(value.task)||value.task<1||!Number.isSafeInteger(value.line)||value.line<1||
      !["confirm","weighted-box","weigh-line","short"].includes(value.route||"confirm")||!value.payload||
      typeof window.cpCaseShortIntent.identity(value)!=="string"||!/^[A-Za-z0-9_.:-]{1,100}$/.test(window.cpCaseShortIntent.identity(value))))
      throw Error("Сохранённая команда повреждена. Отправка заблокирована.");
    return value;
  };
  function pending() {
    let intent;const button=cpTsdEl("cpTsdRetryPosting"),archive=cpTsdEl("cpTsdArchivePosting");
    try{intent=saved();archive.hidden=true;}catch(error){archive.hidden=false;button.hidden=true;cpTsdEl("cpTsdConfirm").disabled=true;cpTsdSetState(error.message);return;}
    button.hidden = !intent;
    button.textContent = intent ? "Повторить: паллета " + intent.task + ", строка " + intent.line : "";
  }
  const originalRender = cpTsdRender;
  cpTsdRender = function () {
    window.cpCaseDraft.begin();
    originalRender();
    cpTsdEl("cpTsdScanCell").value = "";
    cpTsdEl("cpTsdScanProduct").value = "";
    cpTsdEl("cpTsdScanContainer").value = "";

    const line = cpTsdCurrentLine(), task = cpTsd.task, generation = ++policyGeneration;
    const policyScope=key();
    currentPolicy = null;
    window.cpCaseMarking.show(null);cpTsdEl("cpTsdMethod").textContent="Читаю настройки способа отбора…";
    window.cpWeightedBox.show({serialized_weight_boxes:false,profiles:[]});cpTsdEl("cpTsdFactQty").disabled=true;
    if (!line || !task) return;
    cpTsdFetch("/api/case-pick/tasks/" + task.case_pick_task_id + "/lines/" + line.case_pick_line_id + "/marking-policy")
      .then(policy => {
        if(generation !== policyGeneration||policyScope!==key()||task.case_pick_task_id!==cpTsd.task?.case_pick_task_id||line.case_pick_line_id!==cpTsdCurrentLine()?.case_pick_line_id)return;
        currentPolicy = policy; window.cpWeightedBox.show(policy);
        window.cpCaseMarking.show(policy);
        window.cpCaseDraft.mount(task,line,policy);
        cpTsdEl("cpTsdMethod").textContent=policy.serialized_weight_boxes?"Весовая коробка: этикетка → коды применимых профилей → подтверждение массы системой.":
          policy.loose_weight_kg?"Товар на развес: ячейка → паллета отбора → архивное нетто-показание. Ручной факт недоступен.":
          policy.marking_required?"Маркированный товар: ячейка → паллета отбора → уникальные коды всех профилей → накопленный факт.":
          "Коробочный / поштучный отбор: ячейка → паллета отбора → штрихкод товара или коробки → накопленный факт.";

      }).catch(error => { if(generation === policyGeneration)cpTsdSetState(error.message); });
  };
  async function post(retry,kind="pick") {
    if (busy || window.cpTsdStockBusy || window.cpCaseClose?.hasPending() || window.wmsCaseType?.hasPending()) return;
    busy = true;window.cpTsdStockBusy = true;cpTsdEl("cpTsdConfirm").disabled = cpTsdEl("cpTsdRetryPosting").disabled = true;
    let storageKey,draftNotice="";
    let attempted = false, priorUnknown = false, capturedRaw=null;
    try {
      storageKey = key();
      if(localStorage.getItem(JSON.stringify(['retailcase.caseCarrierReturn',cpTsdApiBase(),cpTsdUser()])))throw new Error('Сначала повторите сохранённый возврат.');
      if(localStorage.getItem(JSON.stringify(['retailcase.caseCarrierMove',cpTsdApiBase(),cpTsdUser()])))throw new Error('Сначала повторите сохранённое перемещение паллеты.');
      let intent = saved();
      if(retry && !intent)throw new Error("Нет незавершённой команды.");
      if(!retry && intent)throw new Error("Сначала повторите сохранённую команду.");
      if(!intent) {
        const task=cpTsd.task,line=cpTsdCurrentLine();
        if(!task || !line)throw new Error("Выберите строку.");
        if(kind==="short")intent=window.cpCaseShortIntent.create(task,line);
        else {
        if(!currentPolicy)throw new Error("Дождитесь загрузки настроек товара.");
        const weighted = Boolean(currentPolicy.serialized_weight_boxes);
        const weighed = Boolean(currentPolicy.loose_weight_kg);
        const quantity=cpTsdEl("cpTsdFactQty").value.trim();
        if(!weighted && !weighed && !/^[0-9]{1,18}([.][0-9]{1,9})?$/.test(quantity))throw new Error("Введите накопленный факт в базовой единице.");
        let payload={operation_id:"CASE.PICK.UI:"+crypto.randomUUID(),fact_qty:quantity,
          scan_cell:cpTsdEl("cpTsdScanCell").value.trim(),scan_product:cpTsdEl("cpTsdScanProduct").value.trim()||null,
          scan_box:cpTsdEl("cpTsdScanBox").value.trim()||null,scan_container:cpTsdEl("cpTsdScanContainer").value.trim(),
          unit_scans:weighted||weighed?[]:window.cpCaseMarking.collect(),offline_event_id:crypto.randomUUID(),
          resource_id:cpTsd.session?.resource_id||null,resource_session_id:cpTsd.session?.session_id||null,
          equipment_id:cpTsd.session?.equipment_id||null,actor:cpTsdPicker()};
        if(!payload.scan_cell || !payload.scan_container)throw new Error("Отсканируйте ячейку и идентификатор паллеты отбора.");
        if(weighted)payload=window.cpWeightedBox.payload(payload.operation_id,payload.scan_cell,payload.scan_container);
        if(weighed)payload=window.cpWeightedBox.netPayload(payload.operation_id,payload.scan_cell,payload.scan_container);
        intent={task:task.case_pick_task_id,line:line.case_pick_line_id,route:weighted?"weighted-box":weighed?"weigh-line":"confirm",payload,draft:window.cpCaseDraft.capture(task.case_pick_task_id,line.case_pick_line_id)};
        }
        const wire=JSON.stringify(intent);localStorage.setItem(storageKey,wire);
        if(localStorage.getItem(storageKey)!==wire)throw Error("Запрос не сохранён. Отправка не выполнена.");pending();
      }
      capturedRaw=localStorage.getItem(storageKey);
      cpTsdSetState(retry?"Повтор сохранённой команды...":"Проведение отбора...");
      priorUnknown = !!localStorage.getItem(storageKey + ":delivery");
      localStorage.setItem(storageKey + ":delivery", "unknown");
      if(localStorage.getItem(storageKey + ":delivery")!=="unknown")throw Error("Не удалось сохранить состояние отправки."); attempted = true;
      const result=await cpTsdFetch("/api/case-pick/tasks/"+intent.task+"/lines/"+intent.line+"/"+(intent.route||"confirm"),
        {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(intent.payload)});
      if(storageKey!==key()||localStorage.getItem(storageKey)!==capturedRaw)return;
      if(!window.cpCaseShortIntent.confirms(intent,result)||Number(result.case_pick_task_id)!==intent.task||Number(result.case_pick_line_id)!==intent.line)
        throw Error("Ответ не подтверждает исходную команду. Повторите сохранённый запрос.");
      localStorage.removeItem(storageKey + ":delivery");
      localStorage.removeItem(storageKey);
      if(localStorage.getItem(storageKey)!==null)throw Error("Ответ подтверждён, но запрос не очищен; повторите тот же запрос.");pending();
      try{window.cpCaseDraft.settle(intent.draft);}catch(error){draftNotice=" "+error.message;}
      const task=await cpTsdFetch("/api/case-pick/tasks/"+intent.task);
      if(storageKey!==key())return;cpTsd.task=task;
      cpTsdRender();cpTsdSetState((intent.route==="short"?"Недостача #"+result.case_pick_short_id+" зарегистрирована. Решение и восстановление — в рабочем месте управления сборкой.":"Отбор проведён. Товар и резерв находятся в составе паллеты отбора.")+draftNotice);
    } catch(error) {
      if(storageKey!==key())return;
      if(attempted && !priorUnknown && localStorage.getItem(storageKey)===capturedRaw && error.detail?.outcome_confirmed===true && !error.detail?.retry_same_operation_id && !error.detail?.operation_id_conflict && error.detail?.code!=="OPERATION_CONTENT_CONFLICT") {
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
  cpTsdShortLine = () => post(false,"short");
  window.addEventListener("DOMContentLoaded",()=>{
    cpTsdEl("cpTsdRetryPosting").addEventListener("click",()=>post(true));
    cpTsdEl("cpTsdArchivePosting").addEventListener("click",()=>{
      if(busy)return;try{saved();return;}catch(_){}
      const storageKey=key(),raw=localStorage.getItem(storageKey);if(raw===null)return;
      localStorage.setItem(storageKey+":damaged:"+new Date().toISOString(),raw);
      if(localStorage.getItem(storageKey)===raw)localStorage.removeItem(storageKey);
      cpTsdEl("cpTsdConfirm").disabled=false;pending();cpTsdSetState("Повреждённый запрос сохранён в локальном архиве. Проверьте факт задания перед новым подтверждением.");
    });pending();
  });
  window.addEventListener("wms-admin-auth-ready",()=>{++policyGeneration;currentPolicy=null;window.cpCaseMarking.show(null);try{pending();if(window.wmsAdminAuth?.state.user)cpTsdSafe(cpTsdLoad);}catch(error){cpTsdSetState(error.message);}});
})();
