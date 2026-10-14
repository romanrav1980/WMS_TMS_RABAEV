(() => {
"use strict";
const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
const base=()=>auth()?.state.apiBase.replace(/\/$/,"")||"";
const scope=()=>"interwarehouse-groups:"+base()+":"+(auth()?.state.user?.username||"");
let identity="",epoch=0,busy=false,pending=null,detail=null,proof=null,scans=[],queueCursor=null,scanDamaged=false,scanObserved=null;
const status=text=>el("ggStatus").textContent=text;
const journal=window.wmsInterwarehouseGroupIntent;
function controls(){
 document.querySelectorAll("main button,main input,main select,main textarea").forEach(n=>n.disabled=busy||!!pending);
 el("ggRetry").hidden=!pending||!!pending.damaged;el("ggRetry").disabled=busy;
 el("ggRecover").hidden=!pending?.damaged;el("ggRecover").disabled=busy;if(pending?.damaged)el("ggWare").disabled=busy;
 if(scanDamaged){el("ggScan").disabled=true;el("ggReceive").disabled=true;}
 el("ggCorrect").hidden=!pending?.confirmed;el("ggCorrect").disabled=busy;
}
async function request(path,body){
 const r=await fetch(base()+"/api/inventory/interwarehouse"+path,{method:body?"POST":"GET",headers:auth().headers(body?{"Content-Type":"application/json"}:{}),...(body?{body:JSON.stringify(body)}:{})});
 const d=await r.json();
 if(!r.ok){const e=Error(typeof d.detail==="string"?d.detail:d.detail?.message||"Ответ операции не подтверждён");
 e.confirmed=r.status===422||(r.status<500&&d.detail?.outcome_confirmed===true&&d.detail?.operation_id===body?.operation_id);throw e;}
 return d;
}
function scanKey(){return scope()+":scans:"+el("ggPlan").value;}
function count(){el("ggScanCount").textContent="Сканов единиц: "+scans.filter(s=>!s.level).length+" · агрегатов: "+scans.filter(s=>s.level).length+" · матрица единиц/профилей: "+(detail?detail.lots.reduce((n,l)=>n+l.physical_unit_count*l.profiles.length,0):"загрузите состав");}
function restoreScans(){scans=[];scanDamaged=false;scanObserved=null;let invalid=false;try{
 scanObserved=localStorage.getItem(scanKey());const saved=JSON.parse(scanObserved||"[]");
 if(!Array.isArray(saved)||saved.length>21000||saved.some(s=>!s||typeof s.code!=="string"||!s.code||s.code.length>4000||typeof s.system_code!=="string"||typeof s.profile_code!=="string"||(s.level!==undefined&&!["BOX","PALLET"].includes(s.level))))throw Error("Invalid scans");
 scans=saved;
}catch{invalid=true;scanDamaged=true;}count();controls();if(invalid)status("Сохранённый черновик сканов повреждён. Проверьте исходные данные; операция не выполнялась.");}
function taskLink(task){
 el("ggTask").replaceChildren();
 if(task){const a=document.createElement("a");a.href="warehouse-tasks.html?task_id="+encodeURIComponent(task);a.textContent="Открыть складское задание "+task;el("ggTask").append(a);}
}
async function send(savedScope){
 if(busy||!pending||pending.damaged)return;
 const intent=pending;busy=true;controls();
 try{
  journal.check(savedScope,intent);const result=await request(intent.path,intent.body);journal.result(intent,result);journal.complete(savedScope,intent);
  if(savedScope!==scope()||pending!==intent)return;
  pending=null;
  if(intent.path==="/group-receive"){const raw=localStorage.getItem(intent.scanKey);if(raw!==null&&raw===intent.scanSnapshot)localStorage.removeItem(intent.scanKey);scans=[];count();}
  taskLink(result.task_id);status(result.task_id?"Задание создано. Выполните его в разделе складских заданий.":"Операция подтверждена. Обновите состояние грузового места.");
  detail=null;proof=null;
 }catch(e){
  if(savedScope===scope()&&pending===intent){try{pending=journal.rejected(savedScope,intent,e.confirmed===true);status(e.message);}catch(storageError){try{pending=journal.load(savedScope)||intent;}catch{pending={damaged:true};}status(e.message+" "+storageError.message);}}
 }finally{busy=false;controls();}
}
async function post(path,body){
 if(busy||pending)return;
 const intent={path,body,scanKey:scanKey(),scanSnapshot:localStorage.getItem(scanKey())};try{pending=journal.prepare(scope(),intent);}catch(error){try{pending=journal.load(scope());}catch{pending={damaged:true};}controls();throw error;}await send(scope());
}
async function read(action){
 if(busy||pending)return;const stamp=++epoch,savedScope=scope();busy=true;controls();
 try{await action(()=>stamp===epoch&&savedScope===scope());}
 catch(e){if(stamp===epoch&&savedScope===scope())status(e.message);}
 finally{busy=false;controls();}
}
function positiveInt(id){const value=Number(el(id).value);if(!Number.isSafeInteger(value)||value<1)throw Error("Укажите склад и существующий рейс");return value;}
function planId(){const value=el("ggPlan").value;if(!value||!detail||detail.plan.operation_id!==value)throw Error("Загрузите актуальный состав выбранного места");return value;}
function op(kind){return "INTERWARE.GROUP."+kind+":"+crypto.randomUUID();}
function loadQueue(next=false){return read(async current=>{
 const ware=positiveInt("ggWare"),cursor=next?queueCursor:null;
 if(next&&!cursor)return;
 const rows=await request("/group-warehouses/"+ware+"?limit=100"+(cursor?"&after_operation_id="+encodeURIComponent(cursor):""));if(!current()||ware!==Number(el("ggWare").value))return;
 queueCursor=rows.length===100?rows[rows.length-1].operation_id:null;el("ggNext").hidden=!queueCursor;
 el("ggPlan").replaceChildren(...rows.map(r=>new Option(r.pallet_identifier+" · товаров "+r.stock_leaf_count+" · "+(r.target_cell?"размещено":r.receipt_operation_id?"принято":r.unload_operation_id?"выгружено":"ожидается"),r.operation_id)));
 detail=null;el("ggProfile").replaceChildren();el("ggLots").replaceChildren();el("ggState").textContent="На странице грузовых мест: "+rows.length;restoreScans();
});}
el("ggRefresh").addEventListener("click",()=>loadQueue());
el("ggNext").addEventListener("click",()=>loadQueue(true));
el("ggDetail").addEventListener("click",()=>read(async current=>{
 const plan=el("ggPlan").value;if(!plan)throw Error("Выберите план");
 const result=await request("/group-plans/"+encodeURIComponent(plan));if(!current()||plan!==el("ggPlan").value)return;
 if(Number(result.plan.target_warehouse_id)!==Number(el("ggWare").value))throw Error("План относится к другому принимающему складу. Обновите очередь.");detail=result;
 el("ggLots").replaceChildren(...result.lots.map((lot,index)=>{
  const section=document.createElement("section"),text=document.createElement("p"),label=document.createElement("label"),input=document.createElement("input");
  text.textContent=lot.article+" · "+lot.quantity+" "+lot.base_uom+" · "+(lot.profiles.length?lot.profiles.map(p=>p.system_code+"/"+p.profile_code).join(", "):"без маркировки");
  label.textContent="Штрихкод товара";input.id="ggBarcode"+index;input.autocomplete="off";label.append(input);section.append(text,label);return section;
 }));
 const profiles=[];for(const lot of result.lots)for(const p of lot.scan_profiles||lot.profiles)profiles.push(new Option(lot.article+" · "+p.system_code+"/"+p.profile_code+" · "+(p.scan_mode||"UNIT"),JSON.stringify({system_code:p.system_code,profile_code:p.profile_code,scan_mode:p.scan_mode||"UNIT"})));
 el("ggProfile").replaceChildren(...profiles);selectScanMode();el("ggState").textContent=result.delivered?"Принято покупателем":result.loaded_members===result.lots.length?"Все товары погружены на второе плечо":result.target_cell?"Размещено в "+result.target_cell:result.receipt_operation_id?"Принято в "+result.receive_cell:"Ожидается физическая приёмка";
 el("ggVersion").value=result.current_content_version??"";
 if(result.receive_cell)el("ggFrom").value=result.receive_cell;
 el("ggTo").placeholder=result.plan.outbound_dock;
 if(result.onward)el("ggOnwardResult").textContent=result.onward.members.map(m=>"СТ "+m.st_number+" · "+m.article+" "+m.quantity+" "+m.base_uom+" · рейс "+m.target_trip_id).join(" / ");
 else el("ggOnwardResult").textContent="";
 taskLink(result.placement_task_id);restoreScans();
}));
el("ggProof").addEventListener("click",()=>read(async current=>{
 const load=el("ggSource").value.trim();if(!load)throw Error("Укажите факт погрузки");
 const result=await request("/source-loads/"+encodeURIComponent(load)+"/group-proof");if(!current()||load!==el("ggSource").value.trim())return;
 proof=result;el("ggSourceSummary").textContent=result.source.lots.map(l=>l.article+" "+l.quantity+" "+l.base_uom).join(" · ");
}));
el("ggPlanSave").addEventListener("click",async()=>{try{
 if(!proof||proof.source.source_load_operation_id!==el("ggSource").value.trim())throw Error("Загрузите исходный состав");
 const arrival=el("ggArrival").value.trim(),ready=el("ggReady").value.trim(),reason=el("ggReason").value.trim(),reference=el("ggReference").value.trim();
 if(!/[Zz]$|[+-]\d\d:\d\d$/.test(arrival)||!/[Zz]$|[+-]\d\d:\d\d$/.test(ready)||!reason||!reference)throw Error("Заполните сроки с часовым поясом и основание");
 await post("/group-plan",{operation_id:op("PLAN"),source_load_operation_id:proof.source.source_load_operation_id,expected_source_signature:proof.source_signature,target_warehouse_id:positiveInt("ggWare"),target_trip_id:positiveInt("ggTrip"),inbound_dock:el("ggDock").value.trim(),arrival_due:arrival,ready_due:ready,reason,decision_reference:reference});
}catch(e){status(e.message);}});
el("ggUnload").addEventListener("click",async()=>{try{await post("/unload",{operation_id:op("UNLOAD"),plan_operation_id:planId(),scan_pallet:el("ggPallet").value.trim(),scan_vehicle:el("ggVehicle").value.trim(),scan_dock:el("ggUnloadDock").value.trim()});}catch(e){status(e.message);}});
function selectScanMode(){try{const p=JSON.parse(el("ggProfile").value);if(["UNIT","BOX","PALLET"].includes(p.scan_mode))el("ggScanMode").value=p.scan_mode;}catch{}}
el("ggProfile").addEventListener("change",selectScanMode);
el("ggScan").addEventListener("click",()=>{if(busy||pending)return;try{
 planId();if(scanDamaged)throw Error("Повреждённый состав сканов требует явного архивирования кнопкой очистки.");const code=el("ggCode").value;if(!code)throw Error("Отсканируйте QR");const profile=JSON.parse(el("ggProfile").value),mode=el("ggScanMode").value;
 if(profile.scan_mode!==mode&&!(mode==="UNIT"&&profile.scan_mode==="UNIT")&&profile.scan_mode!=="UNIT_OR_AGGREGATION")throw Error("Способ сканирования не разрешён текущей карточкой товара");
 if(scans.some(s=>s.code===code&&s.system_code===profile.system_code&&s.profile_code===profile.profile_code))throw Error("Этот скан уже добавлен");
 const evidence={system_code:profile.system_code,profile_code:profile.profile_code,code,...(mode==="UNIT"?{}:{level:mode})};
 const values=scans.filter(s=>!!s.level===!!evidence.level);if(values.length>=(evidence.level?1000:20000))throw Error("Превышена граница состава сканов");
 const next=[...scans,evidence],wire=JSON.stringify(next);if(localStorage.getItem(scanKey())!==scanObserved)throw Error("Сканы изменены другой вкладкой. Перечитайте состав.");localStorage.setItem(scanKey(),wire);if(localStorage.getItem(scanKey())!==wire)throw Error("Запись сканов не подтверждена. Приёмка не отправлена.");scanObserved=wire;scans=next;el("ggCode").value="";count();
}catch(e){status(e.message);}});
el("ggClearScans").addEventListener("click",()=>{if(!busy&&!pending){try{const key=scanKey(),raw=localStorage.getItem(key);if(raw!==scanObserved)throw Error("Сканы изменены другой вкладкой. Перечитайте состав.");if(raw!==null){const archive=key+":archive:"+crypto.randomUUID();localStorage.setItem(archive,raw);if(localStorage.getItem(archive)!==raw||localStorage.getItem(key)!==raw)throw Error("Архив сканов не подтверждён.");}localStorage.removeItem(key);if(localStorage.getItem(key)!==null)throw Error("Сканы не освобождены.");scanObserved=null;scanDamaged=false;scans=[];count();controls();status("Прежние сканы сохранены в архив; сканируйте состав заново.");}catch(error){status(error.message);}}});
el("ggReceive").addEventListener("click",async()=>{try{
 const plan=planId();if(scanDamaged||localStorage.getItem(scanKey())!==scanObserved)throw Error("Сохранённые сканы повреждены или изменены. Перечитайте состав.");const items=detail.lots.map((l,i)=>({uid:l.uid,article:l.article,quantity:l.quantity,base_uom:l.base_uom,scan_article:el("ggBarcode"+i).value.trim()}));
 if(items.some(i=>!i.scan_article))throw Error("Отсканируйте каждый товар");
 await post("/group-receive",{operation_id:op("RECEIVE"),plan_operation_id:plan,scan_pallet:el("ggPallet").value.trim(),scan_cell:el("ggCell").value.trim(),items,scans:scans.filter(s=>!s.level).map(s=>({...s})),...(scans.some(s=>s.level)?{aggregation_scans:scans.filter(s=>s.level).map(s=>({...s}))}:{})});
}catch(e){status(e.message);}});
el("ggPlacement").addEventListener("click",async()=>{try{
 planId();if(!detail.receipt_operation_id)throw Error("Сначала подтвердите приёмку");
 const version=Number(el("ggVersion").value);if(!el("ggVersion").value||!Number.isSafeInteger(version)||version<0)throw Error("Укажите текущую версию состава");
 await post("/group-placement",{operation_id:op("PLACEMENT"),receipt_operation_id:detail.receipt_operation_id,expected_version:version,scan_container:el("ggPallet").value.trim(),scanned_from_cell:el("ggFrom").value.trim(),scanned_to_cell:el("ggTo").value.trim(),measurements:{origin:"MANUAL_CONFIRMED",content_version:version,gross_weight_kg:el("ggWeight").value.trim(),width_m:el("ggWidth").value.trim(),depth_m:el("ggDepth").value.trim(),height_m:el("ggHeight").value.trim()}});
}catch(e){status(e.message);}});
el("ggCustody").addEventListener("click",async()=>{try{
 planId();if(!detail.receipt_operation_id)throw Error("Сначала подтвердите приёмку");
 await post("/release-custody",{operation_id:op("CUSTODY"),receipt_operation_id:detail.receipt_operation_id});
}catch(e){status(e.message);}});
el("ggOnward").addEventListener("click",async()=>{try{
 planId();if(!detail.custody_operation_id)throw Error("Подтвердите передачу ответственности");
 const reason=el("ggOnwardReason").value.trim(),reference=el("ggOnwardReference").value.trim();if(!reason||!reference)throw Error("Укажите основание и документ");
 await post("/group-onward",{operation_id:op("ONWARD"),receipt_operation_id:detail.receipt_operation_id,reason,decision_reference:reference});
}catch(e){status(e.message);}});
el("ggRetry").addEventListener("click",()=>send(scope()));
el("ggCorrect").addEventListener("click",()=>{if(!busy&&pending?.confirmed){try{journal.complete(scope(),pending);pending=null;controls();status("Исправьте данные перед новой операцией");}catch(error){status(error.message);}}});
el("ggPlan").addEventListener("change",()=>{epoch++;detail=null;el("ggLots").replaceChildren();el("ggState").textContent="";restoreScans();});
for(const id of ["ggWare","ggSource"])el(id).addEventListener("input",()=>{epoch++;detail=null;proof=null;el("ggLots").replaceChildren();el("ggState").textContent="";el("ggSourceSummary").textContent="";if(id==="ggWare"){el("ggPlan").replaceChildren();queueCursor=null;el("ggNext").hidden=true;}});
function changed(){
 const fp=scope()+":"+(auth()?.state.user?.permissions||[]).slice().sort().join(",");
 if(fp===identity)return;identity=fp;epoch++;queueCursor=null;el("ggNext").hidden=true;detail=null;proof=null;pending=null;scans=[];scanDamaged=false;scanObserved=null;
 document.querySelectorAll("main input,main textarea").forEach(n=>n.value="");el("ggPlan").replaceChildren();el("ggLots").replaceChildren();el("ggState").textContent="";el("ggSourceSummary").textContent="";el("ggProfile").replaceChildren();taskLink(null);
 try{pending=journal.load(scope());}catch(error){pending={damaged:true};status(error.message);}count();controls();
}
el("ggRecover").addEventListener("click",async()=>{
 if(busy||!pending?.damaged)return;const savedScope=scope(),stamp=++epoch;
 try{
  const ware=positiveInt("ggWare");busy=true;controls();
  await journal.archive(savedScope,()=>request("/group-warehouses/"+ware+"?limit=100"),()=>savedScope===scope()&&stamp===epoch);
  pending=null;detail=null;proof=null;busy=false;controls();await loadQueue();
  status("Исходник сохранён в архив. Текущее состояние перечитано. Архивирование не отменяет и не подтверждает прежнюю операцию; выберите место и проверьте его факты.");
 }catch(error){if(savedScope===scope())status(error.message);}finally{busy=false;controls();}
});
window.addEventListener("storage",event=>{if(event.key===scope()&&!busy){try{pending=journal.load(scope());}catch(error){pending={damaged:true};status(error.message);}detail=null;proof=null;controls();}});
window.addEventListener("wms-admin-auth-ready",changed);changed();
let initialLinkRead=false;
function openLinkedPlan(){
 if(initialLinkRead||!auth()?.state.user||busy||pending)return;
 const query=new URLSearchParams(location.search),ware=Number(query.get("warehouse_id")),plan=query.get("plan_id");
 if(!Number.isSafeInteger(ware)||ware<1||!plan||plan.length>100)return;
 initialLinkRead=true;el("ggWare").value=String(ware);
 el("ggPlan").replaceChildren(new Option("Место из межскладского маршрута",plan));
 el("ggDetail").click();
}
window.addEventListener("wms-admin-auth-ready",openLinkedPlan);openLinkedPlan();
})();
