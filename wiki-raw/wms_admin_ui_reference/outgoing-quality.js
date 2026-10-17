(() => {
 const panel=document.createElement("section");panel.className="panel qc-workspace";panel.id="outgoingQuality";
 panel.innerHTML='<header class="qc-header"><div><p>ПРОВЕРКА ГРУЗА</p><h2>Контроль перед отгрузкой</h2></div><span data-admission class="qc-admission">Состав не прочитан</span></header>'+
 '<div class="qc-toolbar"><label>Идентификатор паллеты / CASE / СТ <input data-id autocomplete="off"></label><button data-read>Прочитать состав</button><button data-load>Предъявить к контролю</button><button data-print-label>Этикетка допуска / красный тег</button></div>'+
 '<p data-summary class="qc-summary">Предъявите грузовое место. Допуск относится к подтверждённой версии состава.</p>'+
 '<div class="qc-columns"><section class="qc-stage"><h3>1 · Сверка состава</h3><div data-items class="qc-entry"><label>Штрихкод штуки или целой коробки <input data-item-code autocomplete="off"></label><button data-add-item>Добавить скан</button></div>'+
 '<div data-marks class="qc-marks"><label>Система / профиль <select data-profile></select></label><label>QR единицы товара <input data-code autocomplete="off"></label><button data-add-mark>Добавить QR</button></div>'+
 '<div class="qc-actions"><button data-last>Удалить последний скан</button><button data-clear>Очистить новые сканы</button></div><p data-count class="qc-count"></p><div data-scan-list class="qc-scan-list"></div><div class="qc-entry"><label>Ошибок сканирования <input data-errors type="number" min="0" step="1" value="0"></label><button data-scan class="qc-primary">Подтвердить сканирование</button></div></section>'+
 '<section class="qc-stage"><h3>2 · Контроль веса</h3><p>Используйте фактическое показание весов и вес тары в килограммах.</p><div class="qc-entry"><label>Вес брутто, кг <input data-gross inputmode="decimal"></label><label>Вес тары, кг <input data-tare inputmode="decimal" value="0"></label></div>'+
 '<label>Режим веса <select data-kind><option value="WEIGHT2">Контроль веса перед погрузкой</option><option value="WEIGHT">Контроль веса</option></select></label><button data-weight class="qc-primary">Подтвердить вес</button></section></div><button data-recover hidden>Архивировать повреждённый исходник и перечитать состав</button><p role="status" aria-live="polite"></p>';

 (document.querySelector("main")||document.body).prepend(panel);
 const finalPanel=document.createElement("div");
 finalPanel.innerHTML='<h3>Электронное показание коробки</h3><p>Брутто и измеренная тара берутся из архива весового поста.</p><select data-final-capture aria-label="Финальное показание весов"></select><button data-final-refresh>Обновить показания</button>';
 panel.insertBefore(finalPanel,panel.querySelector("[role=status]"));finalPanel.hidden=true;
 const weightSource=document.createElement("label");
 weightSource.innerHTML='Источник веса <select data-weight-source title="Ввести массу вручную или выбрать архивное показание электронных весов для коробки" data-help-id="qc.weight.source"><option value="MANUAL">Ввод пользователя</option><option value="SCALE">Электронные весы коробки</option></select> <a href="/help/manual-weight.html#warehouse-qc" target="_blank" rel="noopener" title="Как подтвердить вес при складском контроле; откроется в новой вкладке" data-help-id="qc.weight.help">Справка</a>';
 const weightStage=panel.querySelector('[data-gross]').closest('.qc-stage');
 weightStage.insertBefore(weightSource,weightStage.querySelector('.qc-entry'));
 weightStage.insertBefore(finalPanel,weightStage.querySelector('.qc-entry'));
 const el=k=>panel.querySelector("[data-"+k+"]"),message=panel.querySelector("[role=status]");
 const integrated=()=>el("weight-source").value==="SCALE";
 let snapshot=null,pending=null,draft=null,busy=false,generation=0,identity="",finalGeneration=0,pendingRecord=null,draftRaw=null;
 const base=()=>window.wmsAdminAuth.state.apiBase.replace(/\/$/,"");
 const key=()=> "wms-outgoing-quality:"+base()+":"+(window.wmsAdminAuth.state.user?.username||"");
 const draftKey=()=>key()+":scans";
 const intent=window.wmsQualityIntent;
 const path=id=>"/api/outgoing-quality/"+encodeURIComponent(id);
 const clone=value=>JSON.parse(JSON.stringify(value));
 function explain(reason){
  const messages={
   QUALITY_ITEM_COMPOSITION_COVERAGE_REQUIRED:"Не все товары отсканированы в нужном количестве.",
   QUALITY_ITEM_QUANTITY_EXCESS:"Отсканировано больше товара, чем подтверждено в составе СТ.",
   QUALITY_SI_WEIGHT_POLICY_REQUIRED:"В карточке товара отсутствуют весовые нормативы для контроля.",
   QUALITY_FOREIGN_ITEM_BARCODE:"Этот штрихкод не относится к товару данной СТ.",
   QUALITY_ITEM_SCAN_EVENT_CONTENT_CONFLICT:"Один сохранённый скан получил разное содержимое.",
   QUALITY_FOREIGN_UNIT_OR_PROFILE:"Уникальный код или профиль не принадлежит составу СТ.",
   QUALITY_UNIQUE_UNIT_PROFILE_COVERAGE_REQUIRED:"Не все уникальные коды проверены по всем требуемым профилям.",
   QUALITY_DUPLICATE_MARK_SCAN:"Уникальный код отсканирован повторно.",
   QUALITY_INDEPENDENT_CONTROLLER_REQUIRED_ACTUAL_PICK_FACTS:"Контроль должен выполнить другой сотрудник; нужны подтверждённые факты сборки.",
   SHIPMENT_FULL_COMPOSITION_SCAN_REQUIRED:"Требуется полная сверка текущего состава.",
   OUTGOING_CONTROL_PLAN_REQUIRED:"Сначала предъявите грузовое место к контролю."
  };
  for(const [code,text] of Object.entries(messages))if(String(reason||"").includes(code))return text;
  return String(reason||"");
 }
 async function call(url,options={}){
  const scope=key(),r=await fetch(base()+url,{...options,headers:{...window.wmsAdminAuth.headers(),...(options.headers||{})}}),data=await r.json();
  if(scope!==key()){const error=Error("Пользователь или API изменился.");error.obsolete=true;throw error;}
  if(!r.ok){const e=new Error(typeof data.detail==="string"?explain(data.detail):data.detail?.reason?explain(data.detail.reason):JSON.stringify(data.detail||data));e.detail=data.detail;throw e;}return data;
 }
 function count(){el("count").textContent="Сканов обычных штрихкодов: "+(draft?.entries.filter(x=>x.kind==="item").length||0)+", сканов QR: "+(draft?.entries.filter(x=>x.kind==="mark").length||0);}
 function saveDraft(){
  if(!intent.validDraft(draft))throw Error("Некорректный состав сканов.");
  if(localStorage.getItem(draftKey())!==draftRaw)throw Error("Сканы изменены другой вкладкой. Перечитайте состав.");
  const raw=JSON.stringify(draft);localStorage.setItem(draftKey(),raw);
  if(localStorage.getItem(draftKey())!==raw)throw Error("Сканы не сохранены.");draftRaw=raw;count();controls();
 }
 function damaged(){return intent.read().damaged||intent.readDraft(draftKey()).damaged;}
 function controls(){
  if(!window.wmsAdminAuth?.state?.user?.username){window.wmsQualityNext.render(panel,null,true);return;}
  window.wmsQualityNext.render(panel,snapshot,busy||!!pending||damaged());
  const broken=Boolean(damaged());
  el("weight-source").disabled=busy||broken||!!pending;
  for(const name of ["gross","tare","kind"])el(name).disabled=busy||broken||!!pending||integrated();
  el("weight-source").querySelector('[value="SCALE"]').disabled=!snapshot?.final_scale_required;
  for(const name of ["load","scan","weight","add-item","add-mark","last","clear","print-label","final-refresh"])el(name).disabled=busy||broken;
  for(const name of ["add-item","add-mark","last","clear"])el(name).disabled=busy||broken||!!pending;
  for(const name of ["scan","weight"])el(name).disabled=busy||broken||(!pending&&!snapshot?.composition_signature);
  for(const name of ["add-item","add-mark","last"])el(name).disabled=busy||broken||!!pending||!snapshot?.composition_signature;
  el("print-label").disabled=busy||broken||!snapshot?.shipment_identifier;
  el("id").disabled=busy||!!pending;el("read").disabled=busy;
  el("recover").hidden=!broken;el("recover").disabled=busy||!el("id").value.trim();
  el("load").textContent=pending?"Повторить сохранённую команду":"Предъявить к контролю";
  if(!pending&&snapshot?.required===false)for(const name of["load","scan","weight"])el(name).disabled=true;
  const editable=!busy&&!broken&&!pending&&snapshot?.composition_signature===draft?.signature&&snapshot?.shipment_identifier===draft?.identifier;
  window.wmsQualityScanView.render(el("scan-list"),draft?.entries||[],Boolean(editable),removeScan);

 }
 function adoptIdentifier(data,requested){
  if(data.shipment_identifier!==requested&&data.requested_identifier!==requested)throw Error("Ответ относится к другой СТ.");
  if(typeof data.shipment_identifier!=="string"||!data.shipment_identifier||data.shipment_identifier.length>150)throw Error("Источник контроля не подтверждён.");
  el("id").value=data.shipment_identifier;
 }
 async function readOnly(){
  if(busy)return;const id=el("id").value.trim(),current=++generation;if(!id||id.length>150)return;
  snapshot=null;busy=true;controls();
  try{const data=await call(path(id));if(current===generation&&el("id").value.trim()===id){
    adoptIdentifier(data,id);show(data);
    if(damaged())message.textContent+=" Сохранённый исходник повреждён. Новые команды заблокированы.";
   }}catch(e){if(!e.obsolete&&current===generation)message.textContent=e.message;}
  finally{busy=false;controls();}
 }
 async function recover(){
  if(busy)return;const saved=intent.read(),scans=intent.readDraft(draftKey()),scope=key(),id=el("id").value.trim(),current=++generation;
  if((!saved.damaged&&!scans.damaged)||!id||id.length>150)return;
  busy=true;controls();
  try{
   const data=await call(path(id));
   if(current!==generation||scope!==key()||el("id").value.trim()!==id)return;
   adoptIdentifier(data,id);
   if(saved.damaged)intent.archiveDamaged(saved);
   if(scans.damaged){
    if(scope!==key()||localStorage.getItem(scans.storageKey)!==scans.raw)throw Error("Исходник сканов изменился.");
    const archive=scans.storageKey+":damaged:"+crypto.randomUUID();localStorage.setItem(archive,scans.raw);
    if(localStorage.getItem(archive)!==scans.raw)throw Error("Архив сканов не сохранён.");
    localStorage.removeItem(scans.storageKey);
   }
   pendingRecord=intent.read();pending=pendingRecord.value;
   const latest=intent.readDraft(draftKey());draft=latest.value;draftRaw=latest.raw;show(data);
   message.textContent+=" Повреждённый исходник сохранён в архив. Физическое проведение прежней команды этим не подтверждается.";
  }catch(e){if(!e.obsolete&&current===generation)message.textContent=e.message+" Новые команды остаются заблокированными.";}
  finally{busy=false;controls();}
 }
 async function finalReadings(){
  const id=snapshot?.shipment_identifier,signature=snapshot?.composition_signature,gen=++finalGeneration;
  finalPanel.hidden=!snapshot?.final_scale_required||!integrated();
  for(const name of ["gross","tare","kind"])el(name).disabled=busy||!!pending||integrated();
  el("final-capture").replaceChildren(new Option("Выберите актуальное показание",""));
  if(finalPanel.hidden||!id)return;
  try{
   const data=await call(path(id)+"/final-captures");
   if(gen!==finalGeneration||snapshot?.shipment_identifier!==id||snapshot?.composition_signature!==signature)return;
   for(const item of data.items||[]){
    if(item.case_content_version!==snapshot.case_content_version||item.composition_signature!==signature||data.use_by_capture?.[item.capture_key])continue;
    el("final-capture").append(new Option(item.measured_at+" / брутто "+item.weight_kg+" / тара "+item.tare_weight_kg+" / нетто "+item.net_weight_kg+" кг / "+(item.device_mode==="TEST"?"TEST: техническое показание":"HARDWARE"),item.capture_key));
   }
  }catch(error){if(gen===finalGeneration&&!error.obsolete)message.textContent=error.message;}
 }
 function show(data){
  el("admission").textContent=data.required===false?"Контроль не требуется":data.ready?"Допуск подтверждён":"Ожидает контроля";el("admission").className="qc-admission"+(data.ready?" ready":" pending");
  el("summary").textContent=["СТ "+data.shipment_identifier,data.case_content_version!==undefined?"Состав v"+data.case_content_version:null,
   "Режим "+(data.control_mode||"по настройке"),data.independent_controller_required?"Независимый контролёр":null,
   data.unique_mark_control_required?"Уникальные коды обязательны":"Обычные штрихкоды"].filter(Boolean).join(" · ");
  snapshot=data;finalReadings();el("marks").hidden=!data.unique_mark_control_required;el("profile").replaceChildren();
  for(const p of data.mark_profiles||[]){const option=document.createElement("option");option.value=JSON.stringify(p);option.textContent=p.system_code+" / "+p.profile_code;el("profile").append(option);}
  if(!draft||(draftRaw===null&&!draft.entries.length))draft={identifier:data.shipment_identifier,signature:data.composition_signature,entries:[]};
  count();
  if(draft.identifier!==data.shipment_identifier||draft.signature!==data.composition_signature){message.textContent="Состав изменился или предъявлена другая СТ. Очистите новые сканы и повторите сверку текущего состава.";return;}
  message.textContent=(data.required===false?"По текущим настройкам контроль не требуется. ":data.ready?"Допуск подтверждён. ":"Допуск пока не подтверждён. ")+explain(data.reason)+
   (data.sample_selected?" Выборочная полная проверка назначена и сохранена.":"")+
   (data.rescan_required?" После отклонения требуется полная сверка состава.":"")+
   (data.independent_controller_required?" Контролёр должен отличаться от фактического сборщика.":"")+
   (data.expected_weight_kg?" Ожидаемый вес "+data.expected_weight_kg+" кг, допуск ±"+data.tolerance_kg+" кг.":data.required===false||data.weight_exemption?.eligible?"":" "+explain(data.weight_policy_reason));controls();
 }
 el("print-label").onclick=async()=>{
  const id=snapshot?.shipment_identifier,signature=snapshot?.composition_signature,scope=key(),stamp=generation;
  if(busy||pending||!id||el("id").value.trim()!==id){message.textContent="Перечитайте текущий результат контроля.";return;}
  const popup=window.open("about:blank","_blank");if(!popup){message.textContent="Разрешите открытие окна печати.";return;}
  try{
   const response=await fetch(base()+path(id)+"/control-label"+(signature?"?expected_signature="+encodeURIComponent(signature):""),{headers:window.wmsAdminAuth.headers(),cache:"no-store"});
   if(!response.ok){const data=await response.json();throw Error(typeof data.detail==="string"?data.detail:"Этикетка не сформирована");}
   const html=await response.text();
   if(scope!==key()||stamp!==generation||snapshot?.shipment_identifier!==id||snapshot?.composition_signature!==signature||el("id").value.trim()!==id){popup.close();return;}
   if(!popup.closed){popup.document.open();popup.document.write(html);popup.document.close();}
  }catch(error){popup.close();if(scope===key()&&stamp===generation)message.textContent=error.message;}
 };
 function freeze(identifier,kind,body){
  const value={identifier,kind,body:clone(body)};pendingRecord=intent.save(value);pending=pendingRecord.value;controls();
 }
 async function transmit(){
  if(busy||!pending)return;
  if(damaged()||!pendingRecord||pendingRecord.storageKey!==key()||localStorage.getItem(pendingRecord.storageKey)!==pendingRecord.raw){message.textContent="Исходная команда изменилась или повреждена. Перечитайте состояние.";controls();return;}
  busy=true;panel.querySelectorAll("input,select,button").forEach(x=>x.disabled=true);
  const sent=pending,savedKey=key(),savedRaw=localStorage.getItem(savedKey);
  try{
   const result=await call(path(sent.identifier)+"/"+sent.kind,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(sent.body)});
   if(result.operation_id!==sent.body.operation_id||(sent.kind==="plan"&&
     (result.control_status?.shipment_identifier!==sent.identifier||result.control_status?.composition_signature!==sent.body.expected_composition_signature)))
    throw Error("Ответ не соответствует исходной операции. Повторите сохранённую команду.");
   if(localStorage.getItem(savedKey)!==savedRaw)throw Error("Исходная команда изменилась в другой вкладке.");
   intent.settle(pendingRecord);pendingRecord=null;pending=null;
   if(sent.kind==="plan"){
    snapshot=null;const current=++generation,data=await call(path(sent.identifier));
    if(current!==generation||el("id").value.trim()!==sent.identifier)return;
    if(data.shipment_identifier!==sent.identifier)throw Error("Актуальное чтение относится к другой СТ.");show(data);
   }
   else{if(sent.kind==="scan"||!result.verified||result.shipped){if(localStorage.getItem(draftKey())===draftRaw){localStorage.removeItem(draftKey());draftRaw=null;}draft=null;}snapshot=null;count();message.textContent=(result.verified?"Контроль пройден.":"Контроль выявил отклонение.")+(result.failure_reason?" "+explain(result.failure_reason):"")+(result.shipped?" Сохранённая историческая отгрузка уже проведена.":" Предъявите СТ для просмотра допуска; погрузка подтверждается отдельно.");}
  }catch(e){
   if(e.obsolete)return;
   if(e.detail?.outcome_confirmed===true&&e.detail.operation_id===sent.body.operation_id&&localStorage.getItem(savedKey)===savedRaw){intent.settle(pendingRecord);pendingRecord=null;pending=null;snapshot=null;}
   message.textContent=e.message+(pending?" Результат сохранён: повторите без изменений.":" Предъявите актуальный состав перед новой проверкой.");
  }finally{busy=false;panel.querySelectorAll("input,select,button").forEach(x=>x.disabled=false);el("gross").disabled=Boolean(snapshot?.final_scale_required);el("tare").disabled=Boolean(snapshot?.final_scale_required);el("kind").disabled=Boolean(snapshot?.final_scale_required);controls();}
 }
 async function load(){
  if(busy)return;if(damaged()){message.textContent="Сначала восстановите повреждённый исходник.";controls();return;}if(pending){await transmit();return;}
  const id=el("id").value.trim(),current=++generation;if(!id)return;
  snapshot=null;
  try{
   const data=await call(path(id));if(current!==generation||el("id").value.trim()!==id)return;
   if(!data.composition_signature){show(data);return;}
   freeze(id,"plan",{operation_id:"QC.PLAN:"+crypto.randomUUID(),expected_composition_signature:data.composition_signature,note:null});
   await transmit();
  }catch(e){if(!e.obsolete)message.textContent=e.message;}
 }
 function currentDraft(){
  if(busy||pending||damaged()||!snapshot?.composition_signature||draft?.identifier!==snapshot.shipment_identifier||draft.signature!==snapshot.composition_signature){message.textContent="Сначала предъявите текущий состав либо повторите сохранённую операцию.";return false;}return true;
 }
 function removeScan(index){
  if(!currentDraft()||!Number.isSafeInteger(index)||index<0||index>=draft.entries.length)return;
  const removed=draft.entries.splice(index,1)[0];
  try{saveDraft();}catch(error){draft.entries.splice(index,0,removed);message.textContent=error.message;controls();}
 }
 function append(entry){
  if(!currentDraft())return false;
  if(draft.entries.length>=40000){message.textContent="Достигнут предел сканов проверки.";return false;}
  draft.entries.push(entry);try{saveDraft();return true;}catch(e){draft.entries.pop();message.textContent="Скан не сохранён: "+e.message;return false;}
 }
 el("add-item").onclick=()=>{
  const barcode=el("item-code").value.trim();if(!barcode||barcode.length>128)return;
  if(append({kind:"item",value:{scan_id:"QCI:"+crypto.randomUUID(),barcode,quantity:"1"}})){el("item-code").value="";el("item-code").focus();}
 };
 el("add-mark").onclick=()=>{
  if(!currentDraft()||!snapshot.unique_mark_control_required||!el("profile").value)return;
  const code=el("code").value;if(!code||code.length>4000)return;const profile=JSON.parse(el("profile").value);
  if(draft.entries.some(x=>x.kind==="mark"&&x.value.system_code===profile.system_code&&x.value.profile_code===profile.profile_code&&x.value.code===code)){message.textContent="Этот код уже отсканирован.";return;}
  if(append({kind:"mark",value:{...profile,code}})){el("code").value="";el("code").focus();}
 };
 for(const [field,button] of [["item-code","add-item"],["code","add-mark"]])el(field).addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();el(button).click();}});
 el("last").onclick=()=>{if(!currentDraft()||!draft.entries.length)return;const old=draft.entries.pop();try{saveDraft();}catch(e){draft.entries.push(old);message.textContent=e.message;}};
 el("clear").onclick=()=>{
  if(busy||pending||damaged()){message.textContent="Сначала повторите или восстановите сохранённый результат.";return;}
  if(localStorage.getItem(draftKey())!==draftRaw){message.textContent="Сканы изменены другой вкладкой.";return;}
  localStorage.removeItem(draftKey());draftRaw=null;draft=snapshot?{identifier:snapshot.shipment_identifier,signature:snapshot.composition_signature,entries:[]}:null;count();controls();
 };
 async function check(kind){
  if(busy)return;if(damaged()){controls();return;}if(pending){await transmit();return;}
  if(!currentDraft()||el("id").value.trim()!==snapshot.shipment_identifier)return;
  const body={operation_id:"QC:"+crypto.randomUUID(),expected_composition_signature:snapshot.composition_signature,note:null};
  if(kind==="scan"){
   const errors=Number(el("errors").value);if(!Number.isSafeInteger(errors)||errors<0){message.textContent="Укажите целое неотрицательное число ошибок.";return;}
   body.error_count=errors;body.scans=draft.entries.filter(x=>x.kind==="mark").map(x=>x.value);body.item_scans=draft.entries.filter(x=>x.kind==="item").map(x=>x.value);
  }else if(integrated()){
   if(!snapshot.final_scale_required){message.textContent="Для этого места электронное показание коробки недоступно.";return;}
   if(!el("final-capture").value){message.textContent="Выберите актуальное архивное показание весового поста.";return;}
   kind="final-weight";body.capture_key=el("final-capture").value;
  }else{
   const gross=el("gross").value.trim(),tare=el("tare").value.trim(),decimal=/^(0|[1-9][0-9]*)(\.[0-9]{1,9})?$/;
   if(!decimal.test(gross)||Number(gross)<=0||!decimal.test(tare)){message.textContent="Введите точный вес через точку.";return;}
   body.gross_weight=gross;body.wood_weight=tare;body.quality_kind=el("kind").value;body.measurement_origin="MANUAL_CONFIRMED";
  }
  try{freeze(snapshot.shipment_identifier,kind,body);await transmit();}catch(e){message.textContent="Результат не сохранён: "+e.message;}
 }
 function rights(){
  panel.hidden=!window.wmsAdminAuth?.hasPermission("outgoing_pallet_check");if(panel.hidden)return;
  if(identity!==key()){identity=key();snapshot=null;pending=null;draft=null;
   try{pendingRecord=intent.read();pending=pendingRecord.value;const saved=intent.readDraft(draftKey());draft=saved.value;draftRaw=saved.raw;count();
    if(pending){el("id").value=pending.identifier;message.textContent="Сохранённая операция ожидает точного повтора.";}else if(draft){el("id").value=draft.identifier;message.textContent="Сканы сохранены. Предъявите текущий состав.";}
    else {
     const requested=new URLSearchParams(window.location.search).get("qc_shipment");
     if(requested && requested.length<=150){
      el("id").value=requested;const current=++generation;
      message.textContent="Читается текущий состав выбранной СТ.";
      call(path(requested)).then(data=>{if(current===generation&&el("id").value.trim()===requested){adoptIdentifier(data,requested);show(data);}})
        .catch(error=>{if(current===generation&&!error.obsolete)message.textContent=error.message;});
     }
    }
    if(damaged())message.textContent="Сохранённая команда или сканы повреждены. Укажите СТ, прочитайте актуальный состав и восстановите исходник.";controls();
   }catch(e){message.textContent=e.message;}
  }
 }
 el("final-refresh").onclick=finalReadings;
 el("weight-source").onchange=()=>{if(busy||pending)return;el("gross").value="";el("tare").value="";finalReadings();controls();};
 el("read").onclick=readOnly;el("recover").onclick=recover;
 el("id").addEventListener("input",()=>{generation++;finalGeneration++;snapshot=null;finalPanel.hidden=true;controls();});el("load").onclick=load;el("scan").onclick=()=>check("scan");el("weight").onclick=()=>check("weight");
 window.addEventListener("storage",event=>{if(event.key===key()||event.key===draftKey())controls();});
 window.addEventListener("wms-admin-auth-ready",rights);rights();
})();
