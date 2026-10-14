// Недостача складской тары: заявление и независимое решение существующими командами /loss-report и /loss-decide.
// C-0020: переход ?warehouse_id=&claim_id= к конкретному случаю, карточки случаев, проверка автора в UI,
// запись намерения с проверкой чтением (иначе 0 POST), сверка ответа с operation_id, перечитывание после успеха.
(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth,base=()=>auth().state.apiBase.replace(/\/$/,""),key=()=>"tare-loss:"+base()+":"+auth().state.user?.username;
 let balances=[],claims=[],cases=[],pending=null,busy=false,identity="",serial=0,focusClaim="",deepDone=false;
 const say=text=>{el("tlMessage").textContent=text;};
 const me=()=>auth().state.user?.username||"";
 function controls(){
  document.querySelectorAll("main input,main select,main button").forEach(n=>{if(!n.hasAttribute("data-tl-free"))n.disabled=busy||!!pending||n.dataset.tlBlocked==="1";});
  el("tlRetry").hidden=!pending||!!pending.damaged;el("tlRetry").disabled=busy;
  el("tlRestart").hidden=!(pending?.confirmed||pending?.damaged);el("tlRestart").disabled=busy;
  el("tlRestart").textContent=pending?.damaged?"Удалить повреждённую запись после сверки по реестру":"Исправить подтверждённый отказ";
  decisionHint();
 }
 async function request(path,body){
  let r,d=null;
  try{r=await fetch(base()+"/api/inventory/tare"+path,{method:body?"POST":"GET",headers:auth().headers(body?{"Content-Type":"application/json"}:{}),...(body?{body:JSON.stringify(body)}:{})});}
  catch{throw Error(body?"Сервер не ответил; результат операции неизвестен.":"Сервер не ответил.");}
  try{d=await r.json();}catch{}
  if(!r.ok||d==null){const e=Error(typeof d?.detail==="string"?d.detail:d?.detail?.message||"Операция не подтверждена.");e.confirmed=r.status<500&&d?.detail?.outcome_confirmed===true&&d?.detail?.operation_id===body?.operation_id;throw e;}
  return d;
 }
 const ware=()=>{const id=Number(el("tlWare").value);if(!Number.isSafeInteger(id)||id<1)throw Error("Выберите склад.");return id;};
 function clear(){++serial;balances=[];claims=[];cases=[];el("tlBalance").replaceChildren();el("tlClaim").replaceChildren();el("tlRows").replaceChildren();el("tlCases").replaceChildren();decisionHint();}
 async function read(fn){if(busy)return false;const scope=key(),seq=++serial;busy=true;controls();try{return await fn(()=>scope===key()&&seq===serial);}catch(e){if(scope===key())say(e.message);return false;}finally{busy=false;controls();}}
 async function catalog(){return read(async current=>{const d=await request("/assembly/catalog");if(!current())return false;clear();el("tlWare").replaceChildren(...d.warehouses.map(w=>new Option(w.name,w.id)));return true;});}
 function renderCases(){
  const canDecide=auth().hasPermission("tare_writeoff");
  const found=window.TareLossCases.render(el("tlCases"),cases,me(),canDecide,pick,focusClaim);
  if(focusClaim&&!found)say("Заявление "+focusClaim+" не найдено среди 200 последних заявлений склада.");
 }
 async function load(prefix){return read(async current=>{
  const id=ware(),[rows,history,available]=await Promise.all([request("/warehouses/"+id+"/balances"),request("/warehouses/"+id+"/loss-cases"),request("/warehouses/"+id+"/availability")]);
  if(!current())return false;
  balances=rows.filter(r=>r.custodian_kind==="WAREHOUSE"&&r.custodian_id===String(id));cases=history;claims=history.filter(r=>!r.decision_operation_id);
  el("tlBalance").replaceChildren(...balances.map((r,i)=>new Option(r.pallet_type_name+" · "+r.condition_code+" · баланс "+r.quantity,i)));
  el("tlClaim").replaceChildren(new Option("Выберите заявление",""),...claims.map(r=>new Option(r.pallet_type_name+" · "+r.custodian_kind+" "+r.custodian_id+" · "+r.condition_code+" · "+r.quantity+" · "+r.actor+" · "+r.decision_reference,r.operation_id)));
  el("tlRows").replaceChildren(...available.map(r=>{const p=document.createElement("p");p.textContent=r.pallet_type_name+" · свободно "+(r.available_quantity??"пересчёт не выполнен")+" · заявлена недостача "+(r.loss_pending_quantity??"0");return p;}));
  renderCases();if(focusClaim&&claims.some(c=>c.operation_id===focusClaim))el("tlClaim").value=focusClaim;decisionHint();
  say((prefix?prefix+" ":"")+"Баланс и заявления обновлены.");return true;
 });}
 // Кнопка карточки только выбирает заявление и раскрывает форму решения.
 function pick(c){el("tlClaim").value=c.operation_id;focusClaim=c.operation_id;decisionHint();const f=el("tlDecideForm");f.scrollIntoView({behavior:"smooth",block:"start"});setTimeout(()=>el("tlDecisionReason").focus({preventScroll:true}),250);}
 function decisionHint(){
  const c=claims.find(r=>r.operation_id===el("tlClaim").value),n=el("tlDecisionHint");if(!n)return;
  n.textContent=!c?"":c.actor===me()?"Заявление подали вы ("+c.actor+"): решение принимает другой сотрудник.":"Заявитель: "+c.actor+" · "+c.quantity+" ед. · "+c.custodian_kind+" "+c.custodian_id+(c.source_claim_id?" · исходный долг "+c.source_claim_id:"")+". «Отклонить» освобождает тару и восстанавливает долг, «Списать» уменьшает баланс.";
  el("tlDecide").disabled=busy||!!pending||!!(c&&c.actor===me());
 }
 function verified(intent,r){return r&&r.operation_id===intent.body.operation_id&&r.goods_stock_changed===false&&(intent.path==="/loss-report"?r.status==="REPORTED":r.status===intent.body.outcome);}
 function save(scope,intent){const raw=JSON.stringify(intent);let back;try{localStorage.setItem(scope,raw);back=localStorage.getItem(scope);}catch{back=undefined;}if(back!==raw)throw Error("Не удалось надёжно сохранить операцию на этом устройстве — команда не отправлена.");}
 function removeSaved(scope){try{localStorage.removeItem(scope);return localStorage.getItem(scope)===null;}catch{return false;}}
 async function send(scope){
  if(busy||!pending||pending.damaged)return;const intent=pending;busy=true;controls();let r=null,ok=false;
  try{r=await request(intent.path,intent.body);if(!verified(intent,r))throw Object.assign(Error("Ответ не совпадает с сохранённой операцией; результат не подтверждён. Повторите ту же операцию."),{confirmed:false});ok=true;}
  catch(e){if(scope===key()&&pending===intent){pending.confirmed=e.confirmed===true;try{save(scope,pending);}catch{}say(e.message);}}
  finally{busy=false;controls();}
  if(!ok||scope!==key()||pending!==intent)return;
  if(removeSaved(scope))pending=null;else pending={...intent,confirmed:true};
  if(intent.path==="/loss-decide")focusClaim=intent.body.claim_operation_id;
  const text=r.status==="REPORTED"?"Недостача зарегистрирована ("+r.operation_id+"); спорная тара недоступна до независимого решения.":r.status==="WRITE_OFF"?"Независимое списание проведено ("+r.operation_id+").":"Заявление отклонено ("+r.operation_id+"); тара освобождена, долг восстановлен.";
  controls();if(!(await load(text)))say(text+" Реестр не прочитан — обновите; повторять операцию не нужно.");
 }
 async function prepare(path,make){
  if(busy||pending)return;
  try{const body=make();if(!body.reason||!body.decision_reference)throw Error("Укажите обстоятельства и номер документа.");body.operation_id="TARE.LOSS:"+crypto.randomUUID();
   const intent={path,body};save(key(),intent);pending=intent;await send(key());}
  catch(e){say(e.message);}
 }
 function report(){return prepare("/loss-report",()=>{const row=balances[Number(el("tlBalance").value)],qty=el("tlQty").value;if(!row)throw Error("Обновите баланс.");if(!/^[0-9]{1,18}$/.test(qty)||/^0+$/.test(qty))throw Error("Укажите целое положительное количество.");return{owner_ware_id:ware(),pallet_type_id:row.pallet_type_id,condition:row.condition_code,quantity:qty,expected_version:row.balance_version,reason:el("tlReason").value,decision_reference:el("tlReference").value};});}
 function decide(){return prepare("/loss-decide",()=>{const row=claims.find(r=>r.operation_id===el("tlClaim").value);if(!row)throw Error("Выберите заявление.");if(row.actor===me())throw Error("Заявление подали вы — решение принимает другой сотрудник.");return{claim_operation_id:row.operation_id,outcome:el("tlOutcome").value,reason:el("tlDecisionReason").value,decision_reference:el("tlDecisionReference").value};});}
 function restore(scope){
  let raw;try{raw=localStorage.getItem(scope);}catch{return{damaged:true};}
  if(raw==null)return null;
  try{const p=JSON.parse(raw);if(p&&["/loss-report","/loss-decide"].includes(p.path)&&p.body&&typeof p.body.operation_id==="string")return p;}catch{}
  return{damaged:true};
 }
 // Прямой переход из панели тары: склад и заявление сохраняются, решение не проводится автоматически.
 async function deepLink(){
  if(deepDone||!auth().state.user)return;deepDone=true;
  const q=new URLSearchParams(location.search),id=Number(q.get("warehouse_id"));focusClaim=(q.get("claim_id")||"").trim();
  if(!Number.isSafeInteger(id)||id<1)return;
  if(!(await catalog()))return;
  if(![...el("tlWare").options].some(o=>o.value===String(id))){say("Склад "+id+" недоступен вашей учётной записи.");return;}
  el("tlWare").value=String(id);await load();
 }
 function changed(){const scope=key(),fingerprint=scope+":"+(auth().state.user?.permissions||[]).slice().sort().join(",");if(identity===fingerprint)return;identity=fingerprint;clear();pending=null;el("tlWare").replaceChildren();for(const id of ["tlQty","tlReason","tlReference","tlDecisionReason","tlDecisionReference"])el(id).value="";pending=restore(scope);controls();if(pending?.damaged)say("Сохранённая операция повреждена: новые команды заблокированы. Сверьте заявления и решения по реестру ниже.");setTimeout(deepLink,0);}
 for(const [id,fn] of [["tlCatalog",catalog],["tlLoad",()=>load()],["tlReport",report],["tlDecide",decide]])el(id).addEventListener("click",fn);
 el("tlClaim").addEventListener("change",()=>{focusClaim=el("tlClaim").value;decisionHint();});
 el("tlWare").addEventListener("change",clear);el("tlRetry").addEventListener("click",()=>send(key()));
 el("tlRestart").addEventListener("click",()=>{if(busy)return;if(pending?.damaged&&!window.confirm("Удалить повреждённую запись? Сначала сверьте по реестру, сохранилась ли операция."))return;if(pending?.confirmed||pending?.damaged){if(!removeSaved(key())){say("Запись удалить не удалось — команды остаются заблокированными.");return;}pending=null;clear();controls();say("Обновите баланс и заявления.");}});
 window.addEventListener("wms-admin-auth-ready",changed);changed();
})();
