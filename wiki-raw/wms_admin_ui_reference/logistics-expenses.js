// Дополнительные расходы (NI07.1, рабочий экран C-0008). Команды — существующие POST сервера;
// сохранённая операция повторяется тем же operation_id/body, успех показывается после сверки идентичности ответа.
(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth,base=()=>auth().state.apiBase.replace(/\/$/,""),key=()=>"logistics-expenses:"+base()+":"+auth().state.user?.username;
 const M=window.LxModel,V=window.LxView,PATHS=["/articles","/report","/decide","/allocate"];
 let pending=null,busy=false,identity="",serial=0,articles=null,expenses=[],normativeCosts=[],loadedWare=null;
 const filter={stage:"all",kind:"all",object:"",query:""};
 const say=(t,tone)=>{const n=el("exMessage");n.textContent=t;if(tone)n.dataset.tone=tone;else delete n.dataset.tone;};
 const positive=id=>{const n=Number(el(id).value);if(!Number.isSafeInteger(n)||n<1)throw Error("Укажите склад и ID объекта.");return n;};
 const store={get:k=>{try{return localStorage.getItem(k);}catch{return null;}},set:(k,v)=>{try{localStorage.setItem(k,v);}catch{}},del:k=>{try{localStorage.removeItem(k);}catch{}}};
 const ctx=()=>({has:p=>auth().hasPermission(p),user:auth().state.user?.username||""});

 function controls(){
  const locked=busy||!!pending;
  document.querySelectorAll("main input,main select,main button").forEach(n=>{if(n.hasAttribute("data-lx-free"))return;n.disabled=locked||n.dataset.lxBlocked==="1";});
  document.querySelectorAll("#lxStage button").forEach(n=>n.disabled=false);
  el("exRetry").hidden=!pending||!!pending.damaged;el("exRetry").disabled=busy;
  el("exRestart").hidden=!(pending?.confirmed||pending?.damaged);el("exRestart").disabled=busy;
  el("exRestart").textContent=pending?.damaged?"Удалить повреждённую запись":"Исправить подтверждённый отказ";
  pendingBanner();
 }
 function describe(intent){
  const b=intent.body||{};
  if(intent.path==="/articles")return"сохранение статьи "+b.code;
  if(intent.path==="/report")return"регистрация расхода "+b.operation_id+" (документ "+b.document_reference+", "+b.amount+" "+b.currency+")";
  if(intent.path==="/decide")return"решение "+(b.phase==="LOGIST"?"логиста":"финконтроля")+" "+b.operation_id+" по расходу "+b.expense_operation_id;
  return"распределение "+b.operation_id+" расхода "+b.expense_operation_id;
 }
 function pendingBanner(){
  const n=el("lxPending");n.hidden=!pending;if(!pending)return;
  n.dataset.tone=pending.damaged||pending.confirmed?"error":"warn";
  n.textContent=pending.damaged?"Сохранённая на этом устройстве операция повреждена и не может быть повторена. Новые команды заблокированы: проверьте в реестре, сохранилась ли она, затем удалите запись.":
   pending.confirmed?"Сервер подтвердил отказ: "+describe(pending)+". Исправьте данные и создайте новую операцию.":
   "Результат не подтверждён: "+describe(pending)+". Повторите ту же операцию — сервер вернёт сохранённый результат, дубль не создастся.";
 }
 async function request(path,body){
  let r,d;
  try{r=await fetch(base()+(path==="/allocate"?"/api/finance/expense-allocation":"/api/finance/logistics-expenses"+path),{method:body?"POST":"GET",headers:auth().headers(body?{"Content-Type":"application/json"}:{}),...(body?{body:JSON.stringify(body)}:{})});}
  catch{throw Error(body?"Сервер не ответил; результат операции неизвестен.":"Сервер не ответил.");}
  try{d=await r.json();}catch{d=null;}
  if(!r.ok||d==null){
   const e=Error(r.status===403?"Нет прав на это действие или склад.":typeof d?.detail==="string"?d.detail:d?.detail?.message||(body?"Ответ операции не подтверждён.":"Ответ сервера не прочитан."));
   e.confirmed=r.status<500&&d?.detail?.outcome_confirmed===true&&(d?.detail?.operation_id??null)===(body?.operation_id??null);throw e;}
  return d;
 }
 function articleOptions(){
  if(!articles)return;const kind=el("exKind").value,prev=el("exArticleSelect").value;
  el("exArticleSelect").replaceChildren(...articles.filter(r=>r.active_flag===1&&r.included_in_rate===0&&(r.object_scope===kind||r.object_scope==="BOTH")).map(r=>new Option(r.name+" · "+r.code+" · версия "+r.version_no,r.code)));
  if([...el("exArticleSelect").options].some(o=>o.value===prev))el("exArticleSelect").value=prev;
 }
 function fillSelects(rows,norms){
  el("exNormativeCorrection").replaceChildren(new Option("Не корректировать норматив",""),...norms.map(r=>new Option(r.operation_id+" · рейс "+r.trip_id+" · исходно "+r.original_total+" · итог "+r.confirmed_total+" "+r.currency,r.operation_id)));
  el("exCorrection").replaceChildren(new Option("Новый расход",""),...rows.filter(r=>!M.isCorrection(r)&&r.finance_outcome==="APPROVE").map(r=>new Option(r.operation_id+" · "+r.article_name+" · итог "+r.confirmed_total+" "+r.currency,r.operation_id)));
  el("exConfirmed").value="";
  el("exAllocation").replaceChildren(...rows.filter(r=>r.object_kind==="TRIP"&&r.finance_outcome==="APPROVE"&&!r.allocation_operation_id).map(r=>new Option(r.article_name+" · "+r.amount+" "+r.currency+" · рейс "+r.object_id+" · "+r.distribution_basis,r.operation_id)));
  articleOptions();
  el("exExpense").replaceChildren(...rows.filter(r=>!r.finance_operation_id&&r.logist_outcome!=="REJECT").map(r=>new Option(r.article_name+" · "+r.amount+" "+r.currency+" · "+r.object_kind+" "+r.object_id+" · база "+(r.distribution_basis||"не выбрана")+" · логист "+(r.logist_actor||"не согласован"),r.operation_id)));
 }
 async function load(prefix){
  if(busy||pending)return false;const scope=key(),seq=++serial;busy=true;controls();
  try{
   const ware=positive("exWare"),search=el("exNormativeSearch").value.trim();
   const[rows,catalog,norms]=await Promise.all([request("/warehouses/"+ware),request("/articles"),request("/warehouses/"+ware+"/normative-costs"+(search?"?cost_operation_id="+encodeURIComponent(search):""))]);
   if(scope!==key()||seq!==serial)return false;
   articles=catalog;expenses=rows;normativeCosts=norms;loadedWare=ware;fillSelects(rows,norms);
   say((prefix?prefix+" ":"")+"Реестр склада "+ware+" и версии статей обновлены.",prefix?"ok":null);return true;
  }catch(e){
   if(scope===key()&&seq===serial)say(prefix?prefix+" Реестр не прочитан: "+e.message+" Повторно выполнять операцию не нужно — обновите реестр.":e.message,prefix?"warn":"error");return false;
  }finally{busy=false;render();}
 }
 function render(){
  const shown=expenses.filter(r=>M.matches(r,filter));
  V.counters(el("lxStage"),expenses,filter.stage,s=>{filter.stage=s;render();});
  V.render(el("exRows"),shown,{...ctx(),emptyText:loadedWare==null?"Укажите склад и обновите реестр.":expenses.length?"По фильтру в загруженном окне ничего нет.":"У склада нет дополнительных расходов."});
  V.totals(el("lxTotals"),shown);
  const w=el("lxWindow");w.hidden=loadedWare==null;
  if(loadedWare!=null){
   const full=expenses.length>=100;if(full)w.dataset.tone="warn";else delete w.dataset.tone;
   w.textContent="Загружено "+expenses.length+" расходов склада "+loadedWare+". Сервер отдаёт не более 100 записей склада — первые по времени регистрации; фильтры и поиск работают только по загруженному окну, это не поиск по всей базе."+(full?" Окно заполнено: более поздние расходы сюда не попали.":"");
  }
  el("lxShown").textContent=loadedWare==null?"":"Показано "+shown.length+" из "+expenses.length+".";
  controls();
 }
 function verified(intent,r){
  const b=intent.body;
  if(intent.path==="/articles")return r?.code===b.code;
  return r?.operation_id===b.operation_id&&(!b.expense_operation_id||r.expense_operation_id===b.expense_operation_id);
 }
 function successText(intent,r){
  const op=intent.body.operation_id;
  if(intent.path==="/articles")return"Статья "+r.code+" сохранена, версия "+r.version+".";
  if(r.status==="ALLOCATED")return"Распределение "+op+": точно "+r.amount+" "+r.currency+" по фактическому товару.";
  if(r.status==="REPORTED")return"Расход "+op+" зарегистрирован: "+r.amount+" "+r.currency+".";
  if(r.status==="LOGIST_APPROVED")return"Решение логиста "+op+" сохранено; дальше — финансовый контроль другим сотрудником.";
  if(r.status==="APPROVED_PENDING_ALLOCATION")return"Расход рейса подтверждён ("+op+"); требуется распределение.";
  if(r.status==="APPROVED_VEHICLE_ONLY")return"Расход подтверждён только на автомобиль ("+op+").";
  if(r.status==="REJECTED")return"Расход отклонён ("+op+").";
  return"Операция "+op+" сохранена.";
 }
 async function send(scope){
  if(busy||!pending||pending.damaged)return;
  const intent=pending;busy=true;controls();let ok=false,r=null;
  try{
   r=await request(intent.path,intent.body);
   if(!verified(intent,r))throw Object.assign(Error("Ответ сервера не совпадает с отправленной операцией; результат не подтверждён. Повторите ту же операцию."),{confirmed:false});
   ok=true;store.del(scope);
  }catch(e){
   if(scope===key()&&pending===intent){pending.confirmed=e.confirmed===true;store.set(scope,JSON.stringify(pending));say(e.message,"error");}
  }finally{busy=false;controls();}
  if(ok&&scope===key()&&pending===intent){pending=null;controls();await load(successText(intent,r));}
 }
 function expenseBody(){
  if(!articles)throw Error("Сначала обновите реестр.");
  const source=expenses.find(r=>r.operation_id===el("exCorrection").value),norm=normativeCosts.find(r=>r.operation_id===el("exNormativeCorrection").value);
  if(source&&norm)throw Error("Выберите один исходник коррекции.");
  const body={warehouse_id:positive("exWare"),article_code:source?source.article_code:el("exArticleSelect").value,object_kind:source?source.object_kind:norm?"TRIP":el("exKind").value,
   object_id:source?source.object_id:norm?norm.trip_id:positive("exObject"),amount:el("exAmount").value.trim(),currency:source?source.currency:norm?norm.currency:el("exCurrency").value.trim().toUpperCase(),
   expense_date:el("exDay").value,document_reference:el("exReference").value.trim(),reason:el("exReason").value.trim()};
  if(body.warehouse_id!==loadedWare)throw Error("Склад изменён после чтения реестра — обновите реестр.");
  if(source){body.correction_of_operation_id=source.operation_id;body.expected_confirmed_total=source.confirmed_total;}
  if(norm){body.cost_correction_of_operation_id=norm.operation_id;body.expected_confirmed_total=norm.confirmed_total;}
  return body;
 }
 async function prepare(path,make){
  if(busy||pending)return;
  try{
   const body=make();if(path!=="/articles")body.operation_id="EXPENSE:"+crypto.randomUUID();
   if(Object.values(body).some(v=>v===""||v==null))throw Error("Заполните поля документа.");
   const intent={path,body};store.set(key(),JSON.stringify(intent));pending=intent;await send(key());
  }catch(e){say(e.message,"error");}
 }
 // Сохранённая операция принимается только целой; повреждённую запись нельзя обойти новой командой.
 function restore(scope){
  const raw=store.get(scope);if(!raw)return null;
  try{const p=JSON.parse(raw);if(p&&PATHS.includes(p.path)&&p.body&&typeof p.body==="object"&&(p.path==="/articles"||typeof p.body.operation_id==="string"))return p;}catch{}
  return{damaged:true};
 }
 function clearData(){
  ++serial;articles=null;expenses=[];normativeCosts=[];loadedWare=null;
  for(const id of ["exArticleSelect","exExpense","exAllocation","exCorrection","exNormativeCorrection"])el(id).replaceChildren();
  for(const id of ["lxReportPreview","lxDecisionHint","lxAllocHint"])el(id).textContent="";
  el("exConfirmed").value="";render();
 }
 function changed(){
  const scope=key(),fp=scope+":"+(auth().state.user?.permissions||[]).slice().sort().join(",");if(identity===fp)return;identity=fp;pending=null;
  for(const id of ["exWare","exNormativeSearch","exCode","exName","exObject","exAmount","exDay","exReference","exReason","exDecisionRef","exDecisionReason","exConfirmed","lxObject","lxQuery"])el(id).value="";
  Object.assign(filter,{stage:"all",kind:"all",object:"",query:""});el("lxKind").value="all";
  clearData();pending=restore(scope);controls();
  if(pending?.damaged)say("Сохранённая операция повреждена — новые команды заблокированы до проверки.","error");
 }
 function discard(){
  if(busy||!pending)return;
  if(pending.damaged&&!window.confirm("Удалить повреждённую запись операции? Сначала проверьте в реестре, сохранилась ли операция на сервере."))return;
  if(!pending.damaged&&!pending.confirmed)return;
  store.del(key());pending=null;articles=null;controls();say("Обновите реестр перед новой операцией.");
 }
 window.LxPage={el,expenses:()=>expenses,ctx,say,positive,articleOptions,prepare,expenseBody,load,send,key,discard,filter,render,clearData,
  normativeCosts:()=>normativeCosts,articles:()=>articles,isLocked:()=>busy||!!pending};
 window.addEventListener("wms-admin-auth-ready",changed);changed();
})();
