from pathlib import Path
import json
files={};d=Path("wiki-raw/wms_admin_ui_reference")
p=d/"case-pick-tsd.html";s=p.read_text(encoding="utf-8")
s=s.replace('<link rel="stylesheet" href="case-pallet-type.css','<link rel="stylesheet" href="case-pick-guide.css?v=20261014-1292" /><link rel="stylesheet" href="case-pallet-type.css')
start=s.index('        <section id="cpTsdMarking"');end=s.index('</section>',start)+len('</section>')
s=s[:start]+'        <section id="cpTsdMarking" hidden></section>'+s[end:]
s=s.replace('<section class="tsd-scans"','<p id="cpTsdMethod" role="status">Выберите строку для определения способа отбора.</p><section class="tsd-scans"')
s=s.replace('<label>Факт<input id="cpTsdFactQty"','<label>Накопленный факт в базовой единице<input id="cpTsdFactQty"')
s=s.replace('placeholder="план" /></label>','placeholder="план" /><small id="cpTsdFactHelp">Общее отобранное количество по строке, включая предыдущие подтверждения.</small></label>')
s=s.replace('<button id="cpTsdShort"','<button id="cpTsdArchivePosting" type="button" hidden title="Сохранить повреждённую команду в локальном архиве. Это не отменяет операцию на сервере.">Архивировать повреждённую команду</button><button id="cpTsdShort"')
s=s.replace('<script src="case-pick-posting.js?v=20261011-weighted"></script>','<script src="case-marking-input.js?v=20261014-1292"></script><script src="case-pick-posting.js?v=20261014-1292"></script>')
files[str(p)]=s
p=d/"case-weighted-box.js";s=p.read_text(encoding="utf-8").replace('Boolean(policy.serialized_weight_boxes);','Boolean(policy.serialized_weight_boxes || policy.loose_weight_kg);').replace('Boolean(policy.serialized_weight_boxes || select.value)','Boolean(policy.serialized_weight_boxes || policy.loose_weight_kg || select.value)')
s=s.replace('new Option("Без показания весового поста", "")','new Option(policy.loose_weight_kg ? "Выберите обязательное нетто-показание" : "Без показания весового поста", "")')
files[str(p)]=s
p=d/"case-pick-posting.js";s=p.read_text(encoding="utf-8")
s=s.replace('const saved = () => JSON.parse(localStorage.getItem(key()) || "null");','''const saved = () => {
    const value=JSON.parse(localStorage.getItem(key()) || "null");
    if(value&&(!Number.isSafeInteger(value.task)||value.task<1||!Number.isSafeInteger(value.line)||value.line<1||
      !["confirm","weighted-box","weigh-line"].includes(value.route||"confirm")||!value.payload||
      typeof value.payload.operation_id!=="string"||!/^[A-Za-z0-9_.:-]{1,100}$/.test(value.payload.operation_id)))
      throw Error("Сохранённая команда повреждена. Отправка заблокирована.");
    return value;
  };''')
s=s.replace('    const intent = saved(), button = cpTsdEl("cpTsdRetryPosting");','''    let intent;const button=cpTsdEl("cpTsdRetryPosting"),archive=cpTsdEl("cpTsdArchivePosting");
    try{intent=saved();archive.hidden=true;}catch(error){archive.hidden=false;button.hidden=true;cpTsdEl("cpTsdConfirm").disabled=true;cpTsdSetState(error.message);return;}''')
s=s.replace('    cpTsdEl("cpTsdUnitCodes").value = "";','')
s=s.replace('    const profile = cpTsdEl("cpTsdMarkProfile");','    const policyScope=key();')
s=s.replace('    profile.replaceChildren();cpTsdEl("cpTsdMarking").hidden = true;','    window.cpCaseMarking.show(null);cpTsdEl("cpTsdMethod").textContent="Читаю настройки способа отбора…";')
s=s.replace('if(generation !== policyGeneration)return;','if(generation !== policyGeneration||policyScope!==key()||task.case_pick_task_id!==cpTsd.task?.case_pick_task_id||line.case_pick_line_id!==cpTsdCurrentLine()?.case_pick_line_id)return;')
start=s.index('        cpTsdEl("cpTsdMarking").hidden =');end=s.index('\n      }).catch',start)
s=s[:start]+'''        window.cpCaseMarking.show(policy);
        cpTsdEl("cpTsdMethod").textContent=policy.serialized_weight_boxes?"Весовая коробка: этикетка → коды применимых профилей → подтверждение массы системой.":
          policy.loose_weight_kg?"Товар на развес: ячейка → паллета отбора → архивное нетто-показание. Ручной факт недоступен.":
          policy.marking_required?"Маркированный товар: ячейка → паллета отбора → уникальные коды всех профилей → накопленный факт.":
          "Коробочный / поштучный отбор: ячейка → паллета отбора → штрихкод товара или коробки → накопленный факт.";
''' +s[end:]
s=s.replace('Boolean(currentPolicy.loose_weight_kg && window.cpWeightedBox.selectedScale())','Boolean(currentPolicy.loose_weight_kg)')
start=s.index('        const codes=');end=s.index('        let payload=',start);s=s[:start]+s[end:]
s=s.replace('unit_scans:codes.map(code=>({...profile,code}))','unit_scans:weighted||weighed?[]:window.cpCaseMarking.collect()')
s=s.replace('    let attempted = false, priorUnknown = false;','    let attempted = false, priorUnknown = false, capturedRaw=null;')
s=s.replace('      cpTsdSetState(retry?', '      capturedRaw=localStorage.getItem(storageKey);\n      cpTsdSetState(retry?')
s=s.replace('      await cpTsdFetch("/api/case-pick/tasks/"+intent.task', '      const result=await cpTsdFetch("/api/case-pick/tasks/"+intent.task')
needle='''      localStorage.removeItem(storageKey + ":delivery");
      localStorage.removeItem(storageKey);pending();'''
s=s.replace(needle,'''      if(storageKey!==key()||localStorage.getItem(storageKey)!==capturedRaw)return;
      if(result.operation_id!==intent.payload.operation_id||Number(result.case_pick_task_id)!==intent.task||Number(result.case_pick_line_id)!==intent.line)
        throw Error("Ответ не подтверждает исходную команду. Повторите сохранённый запрос.");
      localStorage.removeItem(storageKey + ":delivery");
      localStorage.removeItem(storageKey);pending();''',1)
s=s.replace('      cpTsd.task=await cpTsdFetch("/api/case-pick/tasks/"+intent.task);','      const task=await cpTsdFetch("/api/case-pick/tasks/"+intent.task);\n      if(storageKey!==key())return;cpTsd.task=task;')
s=s.replace('      if(attempted && !priorUnknown && error.detail?.outcome_confirmed===true)', '      if(storageKey!==key())return;\n      if(attempted && !priorUnknown && localStorage.getItem(storageKey)===capturedRaw && error.detail?.outcome_confirmed===true && !error.detail?.retry_same_operation_id && !error.detail?.operation_id_conflict && error.detail?.code!=="OPERATION_CONTENT_CONFLICT")')
s=s.replace('    cpTsdEl("cpTsdRetryPosting").addEventListener("click",()=>post(true));pending();','''    cpTsdEl("cpTsdRetryPosting").addEventListener("click",()=>post(true));
    cpTsdEl("cpTsdArchivePosting").addEventListener("click",()=>{
      if(busy)return;try{saved();return;}catch(_){}
      const storageKey=key(),raw=localStorage.getItem(storageKey);if(raw===null)return;
      localStorage.setItem(storageKey+":damaged:"+new Date().toISOString(),raw);
      if(localStorage.getItem(storageKey)===raw)localStorage.removeItem(storageKey);
      cpTsdEl("cpTsdConfirm").disabled=false;pending();cpTsdSetState("Повреждённый запрос сохранён в локальном архиве. Проверьте факт задания перед новым подтверждением.");
    });pending();''')
s=s.replace('window.addEventListener("wms-admin-auth-ready",()=>{try{pending();}', 'window.addEventListener("wms-admin-auth-ready",()=>{++policyGeneration;currentPolicy=null;window.cpCaseMarking.show(null);try{pending();if(window.wmsAdminAuth?.state.user)cpTsdSafe(cpTsdLoad);}')
files[str(p)]=s
print(json.dumps(files,ensure_ascii=True))
