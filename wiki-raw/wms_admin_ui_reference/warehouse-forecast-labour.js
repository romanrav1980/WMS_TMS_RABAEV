/* Resource-owned, server-calculated labour estimates; no browser arithmetic. */
(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 const labels={APPLIED:"Рассчитано",FORECAST_BLOCKED:"Прогноз количества заблокирован",NO_SCOPE_MAPPING:"Вид работы не связан с участком",SCOPE_MAPPING_INACTIVE:"Связь с участком отключена",NO_NORM:"Нет нормы для артикула и единицы",NORM_INACTIVE:"Последняя норма отключена",NORM_INVALID:"Некорректная норма"};
 const scope=()=>auth().state.apiBase+"|"+auth().state.user?.username+"|"+el("wfWare").value+"|"+el("wfScope").value;
 const valid=v=>Boolean(v&&v.body&&/^FORECAST.SCOPE:[A-Za-z0-9-]+$/.test(v.body.operation_id)&&Number.isSafeInteger(v.body.warehouse_id)&&v.body.warehouse_id>0&&["CASE_DISPATCH","FULLPAL_DISPATCH","OUTBOUND_WORKLOAD"].includes(v.body.work_scope)&&typeof v.body.site_code==="string"&&v.body.site_code.length>0&&v.body.site_code.length<=50&&Number.isSafeInteger(v.body.expected_version)&&v.body.expected_version>=0&&typeof v.body.active==="boolean"&&typeof v.body.reason==="string"&&v.body.reason.trim().length>=3);
 const intent=window.wmsCommandIntent.create("nicora.forecastScope:",valid,{invalid:"Некорректная связь вида работы с участком."});
 let config=null,configScope="",busy=false,sequence=0;
 const message=text=>{el("wfNormMessage").textContent=text;};
 const quantity=v=>String(v).replace(/(\.\d*?)0+$/,"$1").replace(/\.$/,"");
 function node(tag,text){const n=document.createElement(tag);n.textContent=text;return n;}
 function clear(){el("wfLabourResult").replaceChildren();config=null;configScope="";el("wfNormSites").replaceChildren();el("wfNormCurrent").textContent="Прочитайте текущие настройки выбранного склада.";sequence++;refresh();}
 function refresh(){
  if(!auth().state.user)return;
  const record=intent.read(),permission=auth().hasPermission("resource_shift_edit");
  el("wfNormSave").disabled=busy||!permission||!config||configScope!==scope()||!!record.raw;
  el("wfNormRetry").hidden=!record.value;el("wfNormRetry").disabled=busy||!permission;
  el("wfNormArchive").hidden=!record.damaged;el("wfNormArchive").disabled=busy;
  el("wfNormLoad").disabled=busy||!auth().hasPermission("resource_shift_view");
 }
 async function request(path,body){
  const r=await fetch(auth().state.apiBase.replace(/\/$/,"")+path,{method:body?"POST":"GET",headers:{...auth().headers(),"Content-Type":"application/json"},...(body?{body:JSON.stringify(body)}:{})});
  const data=await r.json();if(!r.ok){const e=Error(data.detail?.message||data.detail||"Ошибка запроса");e.status=r.status;throw e;}return data;
 }
 async function load(){
  const selected=scope(),serial=++sequence,ware=Number(el("wfWare").value);
  if(!Number.isSafeInteger(ware)||ware<1){message("Укажите склад.");return;}
  busy=true;refresh();
  try{
   const data=await request("/api/resources/workload/warehouses/"+ware);
   if(selected!==scope()||serial!==sequence)return;
   if(data.warehouse_id!==ware||!Array.isArray(data.norms)||!Array.isArray(data.forecast_scopes))throw Error("Неверный ответ настроек.");
   config=data;configScope=selected;const current=data.forecast_scopes.find(x=>x.work_scope===el("wfScope").value);
   el("wfNormCurrent").textContent=current?"Участок "+current.site_code+" · версия "+current.version_no+(current.active?"":" · отключено"):"Связь ещё не настроена · версия 0";
   const sites=[...new Set(data.norms.filter(x=>x.active===1).map(x=>x.site_code))];if(current&&!sites.includes(current.site_code))sites.push(current.site_code);
   el("wfNormSites").replaceChildren(...sites.map(site=>{const o=node("option",site);o.value=site;return o;}));
   if(current)el("wfNormSites").value=current.site_code;
   el("wfNormActive").checked=current?current.active===1:true;message("Настройки прочитаны. Применение — только по кнопке.");
  }catch(e){if(selected===scope())message(String(e));}finally{busy=false;refresh();}
 }
 async function send(record){
  if(busy)return;const selected=scope(),marker=record.storageKey+":unknown",prior=Boolean(localStorage.getItem(marker));
  busy=true;localStorage.setItem(marker,"1");refresh();
  try{
   const r=await request("/api/resources/workload/forecast-scopes",record.value.body),b=record.value.body;
   if(intent.scope()!==record.storageKey||localStorage.getItem(record.storageKey)!==record.raw)return;
   if(r.operation_id!==b.operation_id||r.warehouse_id!==b.warehouse_id||r.work_scope!==b.work_scope||r.site_code!==b.site_code||r.action!=="FORECAST_SCOPE"||r.stock_changed!==false)throw Error("Ответ не подтверждает исходную настройку.");
   intent.settle(record);localStorage.removeItem(marker);
   if(selected===scope()){config=null;configScope="";el("wfRead").dispatchEvent(new Event("nicora-invalidate"));el("wfLabourResult").replaceChildren();message("Связь сохранена. Перечитайте настройки и рассчитайте прогноз заново.");}
  }catch(e){
   if(intent.scope()===record.storageKey){
    const known=e.status===409&&/WORKLOAD_SCOPE_(VERSION_CHANGED|FIELDS_REQUIRED|ACTIVE_SITE_NORM_REQUIRED)/.test(String(e));
    if(known&&!prior){intent.settle(record);localStorage.removeItem(marker);config=null;configScope="";message(String(e)+" Перечитайте настройки и исправьте данные.");}
    else message(String(e)+" Повторите сохранённую команду.");
   }
  }finally{busy=false;refresh();}
 }
 el("wfNormLoad").onclick=()=>void load();
 el("wfNormSave").onclick=()=>{
  try{
   if(busy||!config||configScope!==scope())throw Error("Сначала прочитайте текущие настройки.");
   const current=config.forecast_scopes.find(x=>x.work_scope===el("wfScope").value);
   const record=intent.save({body:{operation_id:"FORECAST.SCOPE:"+crypto.randomUUID(),warehouse_id:Number(el("wfWare").value),work_scope:el("wfScope").value,site_code:el("wfNormSites").value,active:el("wfNormActive").checked,expected_version:current?.version_no||0,reason:el("wfNormReason").value.trim()}});
   void send(record);
  }catch(e){message(String(e));refresh();}
 };
 el("wfNormRetry").onclick=()=>{const record=intent.read();if(record.value)void send(record);};
 el("wfNormArchive").onclick=()=>{try{intent.archiveDamaged(intent.read());clear();message("Повреждённый запрос сохранён в локальном архиве. Перечитайте настройки.");}catch(e){message(String(e));}};
 el("wfWare").addEventListener("input",clear);el("wfScope").addEventListener("change",clear);
 window.addEventListener("wms-admin-auth-ready",clear);
 window.warehouseForecastLabour={
  clear:()=>el("wfLabourResult").replaceChildren(),
  render(result){
   const area=el("wfLabourResult"),data=result.labour_estimate;area.replaceChildren();
   if(!data){area.append(node("p","Сервер не вернул расчёт трудозатрат."));return;}
   const full=data.total_person_hours!==null;
   area.append(node("p",full?"Расчётные трудозатраты: "+quantity(data.total_person_hours)+" чел·ч":data.known_person_hours!==null?"Частичный итог: "+quantity(data.known_person_hours)+" чел·ч; полный итог не определён.":"Трудозатраты не рассчитаны."));
   area.append(node("p","Рядов с нормой: "+data.covered_series+"; без расчёта: "+data.uncovered_series+"."));
   if(data.mapping)area.append(node("p","Участок "+data.mapping.site_code+" · версия связи "+data.mapping.version_no+" · "+data.mapping.reason));
   for(const row of data.rows){
    const block=node("details",""),title=node("summary",row.article+" · "+row.base_uom+" · "+(row.estimated_person_hours!==null?quantity(row.estimated_person_hours)+" чел·ч":labels[row.status]||row.status));block.append(title);
    block.append(node("p","Прогноз: "+(row.forecast_quantity??"не рассчитан")+". "+(labels[row.status]||row.status)));
    if(row.norm)block.append(node("p","Норма "+row.norm.base_per_hour+" "+row.base_uom+"/ч · версия "+row.norm.version_no+" · "+row.norm.reason+" · "+row.norm.operation_id));
    area.append(block);
   }
  }
 };
 if(auth().state.user)refresh();
})();
