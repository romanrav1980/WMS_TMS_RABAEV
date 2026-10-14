(() => {
  const el=id=>document.getElementById(id);
  let current=null,epoch=0,busy=false;
  function scope(){
    const auth=window.wmsAdminAuth,actor=auth.state.user?.username||'';
    if(!actor)throw new Error('Войдите в систему.');
    return {base:(auth.state.apiBase||'http://127.0.0.1:8088').replace(/\/$/,''),actor};
  }
  function fields(){return {warehouse_id:Number(el('storeCalWare').value),store_code:el('storeCalStore').value.trim(),
    delivery_date:el('storeCalDate').value};}
  function message(text){el('storeCalMessage').textContent=text;}
  async function api(path,body,method='GET'){
    const before=scope(),r=await fetch(before.base+path,{method,headers:window.wmsAdminAuth.headers(body?{'Content-Type':'application/json'}:{}),
      body:body?JSON.stringify(body):undefined}),data=await r.json();
    if(JSON.stringify(before)!==JSON.stringify(scope()))throw new Error('Пользователь изменился. Перечитайте календарь.');
    if(!r.ok)throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail||data));
    return data;
  }
  function invalidate(){current=null;epoch++;message('Перечитайте календарь выбранных склада, магазина и даты.');}
  for(const id of ['storeCalWare','storeCalStore','storeCalDate'])el(id).addEventListener('input',invalidate);
  window.addEventListener('wms-admin-auth-ready',invalidate);
  async function read(){
    if(busy)return;
    const token=++epoch,f=fields();busy=true;
    try{
      const value=await api(`/api/integrations/sap/store-orders/warehouses/${f.warehouse_id}/stores/${encodeURIComponent(f.store_code)}/calendar-context?delivery_date=${f.delivery_date}`);
      if(token!==epoch)return;
      current={...value,fields:f};
      el('storeCalOffset').value=value.utc_offset_minutes??'';
      el('storeCalDays').value=value.delivery_weekdays??'';
      el('storeCalSameDay').checked=Boolean(value.allow_same_day);
      message(`Недельный календарь: ${value.configured?'настроен':'не настроен'}. Исключение даты: ${value.exception_status}; версия ${value.version}.`+
        (value.last_exception?' '+value.last_exception.reason:''));
    }catch(e){if(token===epoch)message(e.message);}finally{busy=false;}
  }
  async function configure(){
    if(busy)return;busy=true;const token=++epoch,f=fields();
    try{
      await api(`/api/integrations/sap/store-orders/warehouses/${f.warehouse_id}/stores/${encodeURIComponent(f.store_code)}/calendar`,
        {utc_offset_minutes:Number(el('storeCalOffset').value),delivery_weekdays:el('storeCalDays').value.split(',').map(v=>Number(v.trim())),
         allow_same_day:el('storeCalSameDay').checked},'PUT');
      if(token===epoch){current=null;message('Недельный календарь сохранён. Перечитайте выбранную дату.');}
    }catch(e){if(token===epoch)message(e.message);}finally{busy=false;}
  }
  async function publish(){
    if(busy||!current){message('Сначала прочитайте актуальную дату.');return;}
    const token=++epoch;busy=true;
    try{
      const auth=scope(),key='retailcase.store.calendar.pending:'+JSON.stringify(auth),raw=localStorage.getItem(key),f=fields();
      if(JSON.stringify(f)!==JSON.stringify(current.fields))throw new Error('Выбор изменился. Перечитайте дату.');
      const body=raw?JSON.parse(raw):{operation_id:'STORE.CAL.UI:'+crypto.randomUUID(),...f,expected_version:current.version,
        day_state:el('storeCalState').value,source_reference:el('storeCalReference').value.trim(),reason:el('storeCalReason').value.trim()};
      if(body.warehouse_id!==f.warehouse_id||body.store_code!==f.store_code||body.delivery_date!==f.delivery_date
        ||body.day_state!==el('storeCalState').value||body.source_reference!==el('storeCalReference').value.trim()
        ||body.reason!==el('storeCalReason').value.trim())throw new Error('Восстановите исходный неподтверждённый запрос.');
      localStorage.setItem(key,JSON.stringify(body));
      await api('/api/integrations/sap/store-orders/calendar-exceptions',body,'POST');
      localStorage.removeItem(key);
      if(token===epoch){current=null;message('Исключение даты сохранено. Уже отложенные заказы автоматически не допускаются.');}
    }catch(e){if(token===epoch)message(e.message);}finally{busy=false;}
  }
  function recover(){
    try{
      const body=JSON.parse(localStorage.getItem('retailcase.store.calendar.pending:'+JSON.stringify(scope()))||'null');
      if(!body)throw new Error('Нет неподтверждённого запроса.');
      el('storeCalWare').value=body.warehouse_id;el('storeCalStore').value=body.store_code;el('storeCalDate').value=body.delivery_date;
      el('storeCalState').value=body.day_state;el('storeCalReference').value=body.source_reference;el('storeCalReason').value=body.reason;
      invalidate();message('Исходные поля восстановлены. Прочитайте дату и повторите запрос.');
    }catch(e){message(e.message);}
  }
  el('storeCalRead').addEventListener('click',read);el('storeCalConfigure').addEventListener('click',configure);
  el('storeCalPublish').addEventListener('click',publish);el('storeCalRecover').addEventListener('click',recover);
})();
