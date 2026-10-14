/* Operator navigation over the existing interwarehouse commands and projections. */
(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 const host=el("iwRows"),main=document.querySelector("main");
 const board=document.createElement("section");board.className="iw-board";
 board.innerHTML='<div class="iw-board-heading"><div><span class="iw-eyebrow">Два плеча · один груз</span><h2>Маршрут межскладского места</h2></div><a href="interwarehouse-groups.html">Составные грузовые места →</a></div><div class="iw-filters"><label>Поиск паллеты, товара или рейса<input id="iwFlowSearch" type="search" placeholder="Идентификатор / артикул / рейс"></label><label>Дата прибытия по плану<input id="iwFlowDate" type="date"></label><label>Этап<select id="iwFlowStage"><option value="">Все этапы</option><option value="WAIT_UNLOAD">Ожидает выгрузки</option><option value="WAIT_RECEIVE">Ожидает приёмки</option><option value="WAIT_PLACE">Требуется размещение</option><option value="WAIT_CUSTODY">Передача ответственности</option><option value="WAIT_ONWARD">Подготовка второго плеча</option><option value="ONWARD_PREPARED">Следующая СТ подготовлена</option><option value="HOLD">Температурная остановка</option></select></label></div><p id="iwFlowCount" role="status">Выберите склад и обновите планы.</p><div class="iw-flow-layout"><div id="iwFlowList" class="iw-flow-list"></div><div id="iwFlowDetail" class="iw-flow-detail"><p>Выберите грузовое место, чтобы увидеть оба плеча и следующее действие.</p></div></div><div class="iw-group-overview"><h3>Составные места принимающего склада</h3><p id="iwGroupMessage">Появятся после обновления планов.</p><div id="iwGroupLinks"></div></div>';
 host.before(board);host.hidden=true;
 let rows=[],selected=null,epoch=0,identity="",currentWare=null;
 const stages={WAIT_UNLOAD:"Ожидает выгрузки",WAIT_RECEIVE:"Выгружено · требуется приёмка",WAIT_PLACE:"Принято · требуется размещение",WAIT_CUSTODY:"Размещено · передать ответственность",WAIT_ONWARD:"Подготовить СТ следующего плеча",ONWARD_PREPARED:"СТ следующего плеча подготовлена",HOLD:"Работа приостановлена по температуре"};
 const stage=r=>r.temperature_decision==="HOLD"?"HOLD":r.onward_st_identifier?"ONWARD_PREPARED":r.custody_release_operation_id?"WAIT_ONWARD":r.placed_task_id?"WAIT_CUSTODY":r.receipt_operation_id?"WAIT_PLACE":r.unload_operation_id?"WAIT_RECEIVE":"WAIT_UNLOAD";
 const node=(tag,text,cls)=>{const n=document.createElement(tag);n.textContent=text;if(cls)n.className=cls;return n;};
 const link=(text,url)=>{const a=node("a",text,"iw-link");a.href=url;a.title="Открыть существующий экран: "+text;return a;};
 const fingerprint=()=>auth().state.apiBase+"|"+auth().state.user?.username+"|"+(auth().state.user?.permissions||[]).slice().sort().join(",");
 function invalidate(message="Параметры изменились. Обновите планы."){
  epoch++;rows=[];selected=null;currentWare=null;el("iwFlowList").replaceChildren();el("iwFlowDetail").replaceChildren(node("p",message));el("iwFlowCount").textContent=message;el("iwGroupLinks").replaceChildren();el("iwGroupMessage").textContent="Обновите планы выбранного склада.";
 }
 function openForm(target){
  const control=el(target);if(!control)return;
  const gate=control.closest("[data-permission]");if(gate&&!auth().hasPermission(gate.dataset.permission)){el("iwFlowCount").textContent="Для этого действия требуется право "+gate.dataset.permission;return;}
  const parent=control.closest("details");if(parent)parent.open=true;
  control.closest("section.panel")?.scrollIntoView({behavior:"smooth",block:"start"});control.focus({preventScroll:true});
 }
 function selectOption(id,value){
  const control=el(id);if(!control||![...control.options].some(o=>o.value===String(value)))return false;
  if(control.value!==String(value)){control.value=String(value);control.dispatchEvent(new Event("change",{bubbles:true}));}return true;
 }
 function prepare(row,target,selector,value){
  if(el("iwLoad").disabled){el("iwFlowCount").textContent="Сначала завершите или повторите сохранённую операцию.";return;}
  if(!rows.some(r=>r.operation_id===row.operation_id)||Number(el("iwWare").value)!==currentWare)return;
  if(selector&&!selectOption(selector,value)){el("iwFlowCount").textContent="Действие больше недоступно. Обновите планы.";return;}
  // Select document identity only. Vehicle, pallet, location and product scans stay operator input.
  openForm(target);
 }
 function detail(row){
  selected=row.operation_id;const area=el("iwFlowDetail");area.replaceChildren();
  area.append(node("span",stages[stage(row)],"iw-state "+(stage(row)==="HOLD"?"iw-hold":"")),node("h3",row.pallet_identifier));
  const route=node("div","","iw-route");
  route.append(node("p","Склад "+row.source_ware_id+" · рейс "+row.source_tt_id),node("strong","→"),node("p","Склад "+row.target_ware_id+" · рейс "+row.target_tt_id));area.append(route);
  area.append(node("p",(row.article||"Состав по плану")+" · "+(row.quantity??"—")+" "+(row.base_uom||"")));
  area.append(node("p","Ворота: "+row.inbound_dock+" → "+row.outbound_dock),node("p","Прибытие: "+row.arrival_due),node("p","Готовность: "+row.ready_due));
  const list=node("ol","","iw-timeline");
  for(const [title,done]of [["Выгрузка",row.unload_operation_id],["Приёмка",row.receipt_operation_id],["Размещение у исходящих ворот",row.placed_task_id],["Передача ответственности",row.custody_release_operation_id],["СТ второго плеча",row.onward_st_identifier]])list.append(node("li",(done?"✓ ":"○ ")+title,done?"done":""));
  area.append(list);
  if(row.receipt_operation_id)area.append(node("p","Принято: "+row.received_quantity+" "+row.base_uom+" · недостача: "+(row.short_quantity||"0")));
  if(row.incident_kind&&!row.incident_close_operation_id)area.append(node("p","Открытое сообщение: "+row.incident_detail,"iw-warning"));
  if(row.temperature_decision==="HOLD")area.append(node("p","Требуется решение ответственного по температуре; этапы не подтверждаются этой карточкой.","iw-warning"));
  const actions=node("div","","iw-actions"),button=(text,target,selector,value)=>{const b=node("button",text);b.type="button";b.title="Открыть форму; проведение потребует отдельного подтверждения и фактических сканов";b.onclick=()=>prepare(row,target,selector,value);actions.append(b);};
  const key=stage(row);
  if(key==="HOLD")button("Открыть температурное решение","iwThermalKind","iwThermalPlan",row.operation_id);
  else if(key==="WAIT_UNLOAD"||key==="WAIT_RECEIVE")button(key==="WAIT_UNLOAD"?"Перейти к выгрузке":"Перейти к приёмке",key==="WAIT_UNLOAD"?"iwVehicle":"iwBarcode","iwPhysicalPlan",row.operation_id);
  else if(key==="WAIT_PLACE"){
   const task=row.placement_plan_task_id;
   if(task)actions.append(link("Исполнить задание №"+task,"warehouse-tasks.html?task_id="+encodeURIComponent(task)));
   button(task?"Изменить план размещения":"Открыть размещение","iwPlacementReceipt","iwPlacementReceipt",row.receipt_operation_id);
  }else if(key==="WAIT_CUSTODY")button("Открыть передачу ответственности","iwRelease","iwCustodyReceipt",row.receipt_operation_id);
  else if(key==="WAIT_ONWARD")button("Подготовить следующую СТ","iwOnwardReason","iwOnwardReceipt",row.receipt_operation_id);
  actions.append(link("Погрузка рейса №"+row.target_tt_id,"transport-loading.html?trip_id="+encodeURIComponent(row.target_tt_id)));
  button("История / расхождения","iwDecisionHistory","iwDecisionHistoryPlan",row.operation_id);
  area.append(actions,node("p","Подготовленная СТ не означает фактическую погрузку, выезд или приёмку магазином.","iw-note"));
  const evidence=node("details","");evidence.append(node("summary","Идентификаторы и основание"),node("p",row.operation_id),node("p","Исходная погрузка: "+row.source_load_operation_id),node("p","Решение: "+(row.latest_decision_reference||row.decision_reference||"—")));area.append(evidence);
  document.querySelectorAll(".iw-flow-list button").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.plan===selected)));
 }
 function render(){
  const query=el("iwFlowSearch").value.trim().toLocaleLowerCase(),date=el("iwFlowDate").value,phase=el("iwFlowStage").value;
  const visible=rows.filter(r=>(!query||[r.pallet_identifier,r.article,r.source_tt_id,r.target_tt_id,r.operation_id].join(" ").toLocaleLowerCase().includes(query))&&(!date||String(r.arrival_due).slice(0,10)===date)&&(!phase||stage(r)===phase));
  el("iwFlowCount").textContent="Отдельных мест: "+visible.length+" из "+rows.length+". Окно исходного списка — до 100; фильтр действует внутри него.";
  el("iwFlowList").replaceChildren(...visible.map(r=>{
   const b=node("button","","iw-flow-card");b.type="button";b.title="Показать маршрут и доступные действия для этого места";b.dataset.plan=r.operation_id;b.setAttribute("aria-pressed",String(selected===r.operation_id));
   b.append(node("strong",r.pallet_identifier),node("span",r.source_ware_id+" → "+r.target_ware_id+" · рейс "+r.target_tt_id),node("small",stages[stage(r)]));b.onclick=()=>detail(r);return b;
  }));
  if(!visible.length)el("iwFlowList").append(node("p","В этом окне нет мест по выбранным условиям."));
  if(selected&&!visible.some(r=>r.operation_id===selected)){selected=null;el("iwFlowDetail").replaceChildren(node("p","Выберите грузовое место."));}
 }
 async function groups(ware,serial,who){
  try{
   const r=await fetch(auth().state.apiBase.replace(/\/$/,"")+"/api/inventory/interwarehouse/group-warehouses/"+ware+"?limit=100",{headers:auth().headers()});
   const data=await r.json();if(serial!==epoch||who!==fingerprint()||currentWare!==ware)return;
   if(!r.ok||!Array.isArray(data))throw Error(data.detail?.message||"Не удалось прочитать составные места.");
   el("iwGroupMessage").textContent="Показано: "+data.length+" · принимающий склад "+ware+(data.length===100?" · продолжение доступно в экране составных мест.":".");
   el("iwGroupLinks").replaceChildren(...data.map(row=>link(row.pallet_identifier+" · "+(row.target_cell?"размещено":row.receipt_operation_id?"принято":row.unload_operation_id?"выгружено":"ожидается")+" · товаров "+row.stock_leaf_count,"interwarehouse-groups.html?warehouse_id="+ware+"&plan_id="+encodeURIComponent(row.operation_id))));
  }catch(e){if(serial===epoch)el("iwGroupMessage").textContent=String(e);}
 }
 window.wmsInterwarehouseWorkspace={
  invalidate,
  render(data,ware){rows=data;currentWare=ware;const serial=++epoch;render();const found=rows.find(r=>r.operation_id===selected);if(found)detail(found);else el("iwFlowDetail").replaceChildren(node("p","Выберите грузовое место."));void groups(ware,serial,fingerprint());}
 };
 for(const id of ["iwFlowSearch","iwFlowDate","iwFlowStage"])el(id).addEventListener(id==="iwFlowSearch"?"input":"change",render);
 el("iwWare").addEventListener("input",()=>invalidate());el("iwHistory").addEventListener("change",()=>invalidate());
 window.addEventListener("wms-admin-auth-ready",()=>{const next=fingerprint();if(next!==identity){identity=next;invalidate("Выберите склад и обновите планы.");}});
 for(const section of [...main.querySelectorAll(":scope > section.panel")]){
  const heading=section.querySelector("h2");if(!heading||section.contains(board))continue;
  const fold=document.createElement("details");fold.className="iw-tool";if(section.dataset.permission)fold.dataset.permission=section.dataset.permission;
  fold.append(node("summary",heading.textContent));section.before(fold);fold.append(section);
 }
})();
