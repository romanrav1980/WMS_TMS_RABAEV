(() => {
  const panel=document.createElement('section');panel.id='waveExecution';panel.className='panel wave-execution-panel';
  panel.innerHTML='<header><div><h2>Исполнение волны <span data-wave-number></span></h2><p>Фактические задания, места и причины незавершения</p></div><span data-wave-state class="task-badge">Не выбрана</span></header>'+
    '<div class="wave-execution-toolbar"><label>Волна<input data-wave type="number" min="1" title="Введите ID волны или выберите её в очереди"></label><button data-load title="Перечитать фактическое исполнение выбранной волны">Обновить исполнение</button><label class="wave-execution-filter"><input data-only-blockers type="checkbox" title="Оставить объекты, требующие следующего действия">Только препятствия</label><span>Препятствия: <b data-blockers>—</b></span></div>'+
    '<p role="status" aria-live="polite"></p><div data-items class="rights-table-wrap"></div>'+
    '<div class="wave-execution-decisions"><label>Причина решения<input data-reason maxlength="1000" title="Укажите причину возврата неисполненной потребности в планирование"></label>'+
    '<button data-release title="Завершить только фактически отгруженную волну без незавершённых заданий и резервов">Завершить волну</button>'+
    '<button data-defer title="Сохранить решение по полностью возвращённой потребности исходных заказов">Вернуть потребность в планирование</button>'+
    '<button data-partial title="Закрыть смешанную волну, сохранив отгруженный факт и неисполненную потребность">Завершить частично отгруженную</button>'+
    '<button data-recover hidden title="Архивировать повреждённый локальный запрос и перечитать выбранную волну">Восстановить повреждённый запрос</button></div>';
  (document.querySelector('.admin-page')||document.querySelector('main')||document.body).prepend(panel);
  const el=s=>panel.querySelector(s),input=el('[data-wave]'),status=el('[role=status]'),
    reason=el('[data-reason]'),button=el('[data-release]'),defer=el('[data-defer]'),partial=el('[data-partial]'),
    recover=el('[data-recover]'),filter=el('[data-only-blockers]'),intent=window.wmsWaveExecutionIntent;
  let record=null,request=0,busy=false,identity='',snapshot=null,loading=false;
  const base=()=>window.wmsAdminAuth.state.apiBase.replace(/\/$/,'');
  const same=scope=>window.wmsAdminAuth?.state?.user && scope===intent.scope();
  const can=right=>Boolean(window.wmsAdminAuth?.hasPermission(right));
  function controls(){
    const damaged=Boolean(record?.damaged),pending=record?.value,ready=snapshot&&!loading&&Number(snapshot.wave_id)===Number(input.value);
    input.disabled=busy||Boolean(pending);reason.disabled=busy||Boolean(pending);
    el('[data-load]').disabled=busy;
    button.disabled=busy||damaged||!can('pick_wave_launch')||(!pending&&(!ready||!snapshot.ready||snapshot.completed));
    defer.disabled=busy||damaged||!can('pick_wave_launch')||!can('pick_wave_cancel')||
      (pending?pending.body.disposition!=='RETURNED_TO_PLANNING':!ready||!snapshot.deferred_decision?.eligible);
    partial.disabled=busy||damaged||!can('pick_wave_launch')||!can('pick_wave_cancel')||
      (pending?pending.body.disposition!=='PARTIAL_SHIPPED_RETURNED':!ready||!snapshot.mixed_decision?.eligible);
    if(pending)button.disabled=busy||damaged||!can('pick_wave_launch')||
      Boolean(pending.body.disposition&&!can('pick_wave_cancel'));
    button.textContent=pending?'Повторить сохранённое решение':'Завершить волну';
    recover.hidden=!damaged;recover.disabled=busy;
  }
  function render(data){
    snapshot=data;
    const visible=filter.checked&&!data.completed?{...data,items:data.items.filter(x=>x.reason||x.display_reason)}:data;
    window.wmsWaveExecutionView.render(panel,visible);
    status.textContent=record?.damaged?'Локальный запрос повреждён. Отправка заблокирована до восстановления.':
      data.completed?'Решение завершения сохранено. Исполнение заказа определяется его фактическими местами.':
      data.ready?'Отгрузка подтверждена; незавершённых заданий и резервов нет.':'Устраните препятствия или оформите допустимое решение по неисполненной потребности.';
    controls();
  }
  async function load(){
    if(busy||!can('pick_wave_view'))return;
    const wave=Number(input.value);if(!Number.isSafeInteger(wave)||wave<1){snapshot=null;controls();return;}
    const id=++request,scope=intent.scope();loading=true;snapshot=null;controls();status.textContent='Читаю фактическое исполнение…';
    try{
      const response=await fetch(base()+'/api/picking/waves/'+wave+'/execution',{headers:window.wmsAdminAuth.headers()});
      const data=await response.json();
      if(id!==request||Number(input.value)!==wave||!same(scope))return;
      if(!response.ok)throw new Error(JSON.stringify(data.detail||data));
      if(Number(data.wave_id)!==wave||!Array.isArray(data.items))throw new Error('Ответ не соответствует выбранной волне.');
      loading=false;render(data);
    }catch(error){if(id===request&&same(scope)){loading=false;status.textContent=error.message;controls();}}
  }
  async function release(disposition){
    if(busy||record?.damaged||!can('pick_wave_launch'))return;
    const wave=Number(input.value);if(!Number.isSafeInteger(wave)||wave<1)return;
    let pending=record?.value;
    if(pending&&pending.wave!==wave){status.textContent='Сначала повторите сохранённую волну '+pending.wave;return;}
    if(pending&&disposition&&pending.body.disposition!==disposition){status.textContent='Сначала повторите исходное решение.';return;}
    if((pending?.body.disposition||disposition)&&!can('pick_wave_cancel'))return;
    if(!pending){
      if(loading||!snapshot||Number(snapshot.wave_id)!==wave)return;
      const eligible=disposition==='PARTIAL_SHIPPED_RETURNED'?snapshot.mixed_decision?.eligible:
        disposition==='RETURNED_TO_PLANNING'?snapshot.deferred_decision?.eligible:snapshot.ready&&!snapshot.completed;
      if(!eligible || (disposition&&!reason.value.trim())){status.textContent='Требуются допустимое состояние волны и причина решения.';return;}
      pending={wave,body:{operation_id:'WAVE.FINISH:'+crypto.randomUUID(),...(disposition?{disposition,reason:reason.value.trim()}:{})}};
      try{record=intent.save(pending);}catch(error){status.textContent=error.message;controls();return;}
    }
    const sending=record,scope=intent.scope();
    if(localStorage.getItem(sending.storageKey)!==sending.raw){status.textContent='Сохранённый запрос изменился в другой вкладке. Перечитайте состояние.';rights();return;}
    busy=true;request++;controls();status.textContent='Отправляю сохранённое решение…';
    try{
      const response=await fetch(base()+'/api/picking/waves/'+pending.wave+'/finish-execution',{
        method:'POST',headers:{...window.wmsAdminAuth.headers(),'Content-Type':'application/json'},body:JSON.stringify(pending.body)});
      const data=await response.json();
      if(!same(scope))return;
      if(!response.ok){
        if(data.detail?.outcome_confirmed===true&&!data.detail.operation_id_conflict&&!data.detail.retry_same_operation_id){
          intent.settle(sending);record=null;
        }
        throw new Error(JSON.stringify(data.detail||data));
      }
      if(data.completed!==true||data.status!=="DONE"||Number(data.wave_id)!==pending.wave||data.operation_id!==pending.body.operation_id)throw new Error("Ответ не подтверждает сохранённое решение. Повторите исходный запрос.");
      intent.settle(sending);record=null;status.textContent='Решение подтверждено. Перечитываю фактическое состояние.';
    }catch(error){if(same(scope))status.textContent=error.message+(record?.value?' Повторите тот же сохранённый запрос.':'');}
    finally{busy=false;if(same(scope)){controls();await load();}else rights();}
  }
  function choose(wave){
    if(busy||record?.value){if(record?.value&&record.value.wave!==wave)status.textContent='Сначала завершите сохранённое решение волны '+record.value.wave;return;}
    if(!Number.isSafeInteger(wave)||wave<1)return;
    request++;snapshot=null;input.value=wave;controls();void load();
  }
  function rights(){
    const auth=window.wmsAdminAuth;panel.hidden=!can('pick_wave_view');
    request++;snapshot=null;loading=false;
    if(!auth?.state?.user){identity='';record=null;controls();return;}
    const next=intent.scope();
    if(next!==identity){identity=next;record=null;}
    try{
      record=intent.read();
      if(record.value){input.value=record.value.wave;reason.value=record.value.body.reason||'';}
      else if(!input.value){const wave=Number(new URLSearchParams(location.search).get('wave_id'));if(Number.isSafeInteger(wave)&&wave>0)input.value=wave;}
    }catch(error){status.textContent=error.message;controls();return;}
    controls();if(!panel.hidden&&!busy)void load();
  }
  el('[data-load]').addEventListener('click',()=>{rights();});
  button.addEventListener('click',()=>release());
  defer.addEventListener('click',()=>release('RETURNED_TO_PLANNING'));
  partial.addEventListener('click',()=>release('PARTIAL_SHIPPED_RETURNED'));
  input.addEventListener('change',()=>window.dispatchEvent(new CustomEvent('wms-wave-requested',{detail:{wave_id:Number(input.value)}})));
  filter.addEventListener('change',()=>{if(snapshot)render(snapshot);});
  recover.addEventListener('click',async()=>{
    if(busy||!record?.damaged)return;
    try{intent.archiveDamaged(record);record=null;request++;snapshot=null;status.textContent='Повреждённый исходник сохранён в архиве. Перечитываю волну.';controls();await load();}
    catch(error){status.textContent=error.message;}
  });
  window.addEventListener('storage',event=>{if(event.key===identity&&!busy)rights();});
  window.addEventListener('wms-wave-selection-loading',event=>{
    if(busy||record?.value)return;
    request++;snapshot=null;loading=true;input.value=event.detail?.wave_id||'';
    panel.querySelector('[data-items]').replaceChildren();status.textContent='Читаю выбранную волну…';controls();
  });
  window.addEventListener('wms-wave-selected',event=>choose(Number(event.detail?.wave_id)));
  window.addEventListener('wms-admin-auth-ready',rights);rights();
})();
