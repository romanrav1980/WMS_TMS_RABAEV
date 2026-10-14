(() => {
  const panel=document.createElement('section');panel.className='panel wave-execution-panel';
  panel.innerHTML='<header><h2>Допуск отбора</h2></header><div class="wave-execution-toolbar"><label>Волна<input type="number" min="1" title="Выберите волну для проверки резерва в ячейках отбора"></label><button data-load title="Перечитать покрытие выбранных заданий и физическое пополнение">Показать готовность</button><button data-release title="Разрешить отбор только после серверной проверки резерва и завершения пополнения">Разрешить отбор</button><button data-recover hidden title="Сохранить повреждённый запрос в архиве и перечитать волну">Восстановить запрос</button></div><p role="status" aria-live="polite">Выберите волну.</p><div data-items class="rights-table-wrap"></div>';
  (document.querySelector('.admin-page')||document.querySelector('main')||document.body).prepend(panel);
  const input=panel.querySelector('input'),status=panel.querySelector('[role=status]'),
    button=panel.querySelector('[data-release]'),recover=panel.querySelector('[data-recover]'),
    target=panel.querySelector('[data-items]'),intent=window.wmsWavePickIntent;
  let record=null,request=0,busy=false,identity='',snapshot=null,loading=false;
  const can=right=>Boolean(window.wmsAdminAuth?.hasPermission(right));
  const same=scope=>window.wmsAdminAuth?.state?.user&&scope===intent.scope();
  const base=()=>window.wmsAdminAuth.state.apiBase.replace(/\/$/,'');
  function controls(){
    const pending=record?.value,damaged=Boolean(record?.damaged);
    input.disabled=busy||Boolean(pending);panel.querySelector('[data-load]').disabled=busy;
    button.disabled=busy||damaged||!can('pick_wave_launch')||
      (!pending&&(loading||!snapshot||Number(snapshot.wave_id)!==Number(input.value)||!snapshot.ready||Boolean(snapshot.released_at)));
    button.textContent=pending?'Повторить сохранённый допуск':'Разрешить отбор';
    recover.hidden=!damaged;recover.disabled=busy;
  }
  function render(data){
    snapshot=data;target.replaceChildren();
    const table=document.createElement('table');table.className='rights-table';
    const head=document.createElement('thead'),tr=document.createElement('tr');
    for(const text of ['Товар / ячейка','Требуется','Покрыто','Не хватает','Ед.','Причина']){
      const th=document.createElement('th');th.textContent=text;tr.append(th);
    }
    head.append(tr);table.append(head);const body=document.createElement('tbody');table.append(body);
    for(const item of data.tasks||[]){
      const tr=document.createElement('tr');
      const reason=(item.reservations||[]).filter(r=>r.reason).map(r=>r.reason+' / '+r.uid).join('; ');
      for(const value of [item.article+' / '+item.cell,item.required_base,item.covered_base,item.missing_base,item.base_uom||'BASE',reason||'—']){
        const td=document.createElement('td');td.textContent=value??'—';tr.append(td);
      }
      body.append(tr);
    }
    target.append(table);
    for(const item of data.open_replenishments||[]){
      const p=document.createElement('p');p.className='wave-execution-demand';
      p.textContent=(item.can_cancel_before_release?'Потребность уже покрыта; план снимается без движения. ':'')+
        'Пополнение #'+item.replenishment_id+': '+item.article+' → '+item.target+', '+item.quantity+'; '+item.status+
        '; исполнитель '+(item.assigned_to||'не назначен')+'. ';
      if(Number.isSafeInteger(item.warehouse_task_id)&&item.warehouse_task_id>0){
        const a=document.createElement('a');a.href='warehouse-tasks.html?task_id='+item.warehouse_task_id+'#warehouseTaskDetail';
        a.textContent='Задание #'+item.warehouse_task_id;a.title='Открыть физическое исполнение пополнения';p.append(a);
      }
      target.append(p);
    }
    status.textContent=record?.damaged?'Сохранённый допуск повреждён. Отправка заблокирована до восстановления.':
      data.released_at?'Отбор разрешён: '+data.released_at+'; '+(data.released_by||''):
      data.ready?'Пополнение подтверждено, выбранный состав покрыт допустимым резервом.':'Отбор ожидает пополнения или покрытия резерва.';
    if(record?.value)status.textContent+=' Есть сохранённый запрос; повтор использует тот же идентификатор.';
    controls();
  }
  async function load(){
    if(busy||!can('pick_wave_view'))return;
    const wave=Number(input.value);if(!Number.isSafeInteger(wave)||wave<1){snapshot=null;controls();return;}
    const id=++request,scope=intent.scope();loading=true;snapshot=null;target.replaceChildren();controls();status.textContent='Проверяю фактическое покрытие…';
    try{
      const response=await fetch(base()+'/api/picking/waves/'+wave+'/pick-readiness',{headers:window.wmsAdminAuth.headers()});
      const data=await response.json();if(id!==request||Number(input.value)!==wave||!same(scope))return;
      if(!response.ok)throw new Error(JSON.stringify(data.detail||data));
      if(Number(data.wave_id)!==wave||!Array.isArray(data.tasks))throw new Error('Ответ не соответствует выбранной волне.');
      loading=false;render(data);
    }catch(error){if(id===request&&same(scope)){loading=false;status.textContent=error.message;controls();}}
  }
  async function release(){
    if(busy||record?.damaged||!can('pick_wave_launch'))return;
    const wave=Number(input.value);if(!Number.isSafeInteger(wave)||wave<1)return;
    if(record?.value&&record.value.wave!==wave)return;
    if(!record?.value){
      if(loading||!snapshot||!snapshot.ready||snapshot.released_at||Number(snapshot.wave_id)!==wave)return;
      try{record=intent.save({wave,body:{operation_id:'WAVE.PICK:'+crypto.randomUUID()}});}
      catch(error){status.textContent=error.message;controls();return;}
    }
    const sending=record,scope=intent.scope();
    if(localStorage.getItem(sending.storageKey)!==sending.raw){rights();status.textContent='Сохранённый запрос изменился в другой вкладке.';return;}
    busy=true;request++;controls();status.textContent='Отправляю сохранённый допуск…';
    try{
      const response=await fetch(base()+'/api/picking/waves/'+sending.value.wave+'/release-picking',{
        method:'POST',headers:{...window.wmsAdminAuth.headers(),'Content-Type':'application/json'},body:JSON.stringify(sending.value.body)});
      const data=await response.json();if(!same(scope))return;
      if(!response.ok){
        if(data.detail?.outcome_confirmed===true&&!data.detail.operation_id_conflict&&!data.detail.retry_same_operation_id){
          intent.settle(sending);record=null;
        }
        throw new Error(JSON.stringify(data.detail||data));
      }
      if(Number(data.wave_id)!==sending.value.wave||!data.released_at||
        data.command_operation_id!==sending.value.body.operation_id)
        throw new Error('Ответ не подтверждает сохранённый допуск. Повторите исходный запрос.');
      intent.settle(sending);record=null;
    }catch(error){if(same(scope))status.textContent=error.message+(record?.value?' Повторите тот же сохранённый запрос.':'');}
    finally{busy=false;if(same(scope)){controls();await load();}else rights();}
  }
  function choose(wave){
    if(busy||record?.value){if(record?.value&&record.value.wave!==wave)status.textContent='Сначала повторите допуск волны '+record.value.wave;return;}
    if(!Number.isSafeInteger(wave)||wave<1)return;request++;snapshot=null;input.value=wave;controls();void load();
  }
  function rights(){
    request++;snapshot=null;loading=false;panel.hidden=!can('pick_wave_view');target.replaceChildren();
    if(!window.wmsAdminAuth?.state?.user){identity='';record=null;controls();return;}
    const next=intent.scope();if(next!==identity){identity=next;record=null;}
    try{
      record=intent.read();if(record.value)input.value=record.value.wave;
      else if(!input.value)input.value=new URLSearchParams(location.search).get('wave_id')||'';
    }catch(error){status.textContent=error.message;controls();return;}
    controls();if(!panel.hidden&&!busy)void load();
  }
  panel.querySelector('[data-load]').addEventListener('click',rights);
  button.addEventListener('click',release);input.addEventListener('change',()=>window.dispatchEvent(new CustomEvent('wms-wave-requested',{detail:{wave_id:Number(input.value)}})));
  recover.addEventListener('click',async()=>{if(busy||!record?.damaged)return;try{intent.archiveDamaged(record);record=null;controls();await load();}catch(error){status.textContent=error.message;}});
  window.addEventListener('storage',event=>{if(event.key===identity&&!busy)rights();});
  window.addEventListener('wms-wave-selection-loading',event=>{
    if(busy||record?.value)return;
    request++;snapshot=null;loading=true;input.value=event.detail?.wave_id||'';
    panel.querySelector('[data-items]').replaceChildren();status.textContent='Читаю выбранную волну…';controls();
  });
  window.addEventListener('wms-wave-selected',event=>choose(Number(event.detail?.wave_id)));
  window.addEventListener('wms-admin-auth-ready',rights);rights();
})();
