/* Actor/task scoped server scans. Saving a draft never posts stock. */
(() => {
  let scope='',epoch=0,context=null,savedDraft=null,scans=[],busy=false;
  const panel=document.createElement('section');panel.className='panel';panel.id='warehouseTaskScanPanel';
  panel.innerHTML='<h2>Марки частичного перемещения</h2><button data-action="load">Загрузить профиль и сохранённые сканы</button> <select aria-label="Профиль маркировки"></select> <input aria-label="Уникальный код штуки" placeholder="QR / Data Matrix штуки"> <button data-action="add">Добавить скан</button> <button data-action="save">Сохранить на сервере</button> <button data-action="retry">Повторить сохранение</button><button data-action="archive" hidden>Архивировать повреждённый запрос</button><p role="status"></p><pre></pre>';
  (document.querySelector('main')||document.body).prepend(panel);
  const auth=()=>window.wmsAdminAuth;
  const task=()=>typeof warehouseTaskState!=='undefined'?warehouseTaskState.selectedTask?.task_id:
    (typeof rtTsdCurrent==='function'?rtTsdCurrent()?.task_id:null);
  const identity=()=>JSON.stringify([auth()?.state.apiBase,auth()?.state.user?.username,task()]);
  const message=text=>panel.querySelector('p').textContent=text;
  function render(){
    panel.querySelector('pre').textContent=scans.length+' сканов в форме'+(savedDraft?' / серверный набор '+savedDraft:' / набор не подтверждён');
    panel.querySelectorAll('button,input,select').forEach(control=>control.disabled=busy);
    panel.hidden=!auth()?.hasPermission('warehouse_task_execute');
    const repair=panel.querySelector('[data-action="archive"]');repair.hidden=true;
    if(task()&&auth()?.state.user){try{
      const raw=localStorage.getItem('wms.task.scans:'+auth().state.apiBase+':'+auth().state.user.username+':'+task());
      if(raw!==null){try{repair.hidden=validBody(JSON.parse(raw));}catch{repair.hidden=false;}}
    }catch{message('Хранилище недоступно. Отправка требует сохранённого исходного запроса.');}}

  }
  function reset(){
    scope=identity();epoch++;context=null;savedDraft=null;scans=[];busy=false;
    panel.querySelector('select').replaceChildren();panel.querySelector('input').value='';
    message('Выберите задание и загрузите его профиль. Незавершённый запрос сохранён отдельно для прежнего пользователя и задания.');render();
  }
  function sync(){if(scope!==identity())reset();}
  function capture(){
    sync();const id=task(),actor=auth()?.state.user?.username;
    if(!id||!actor||!auth().hasPermission('warehouse_task_execute'))throw Error('Выберите задание и войдите с правом исполнения.');
    return {id,actor,scope,epoch,base:auth().state.apiBase.replace(/\/$/,''),headers:auth().headers(),
      key:'wms.task.scans:'+auth().state.apiBase+':'+actor+':'+id};
  }
  const active=s=>s.scope===identity()&&s.epoch===epoch;
  async function api(s,path,body){
    const response=await fetch(s.base+'/api/warehouse-tasks/'+s.id+path,{method:body?'POST':'GET',
      headers:{...s.headers,...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined});
    const data=await response.json();if(!response.ok)throw Error(JSON.stringify(data.detail||data));return data;
  }
  function validBody(body){
    return body&&typeof body.draft_id==='string'&&body.draft_id.length>0&&body.draft_id.length<=100&&
      /^[A-F0-9]{64}$/.test(body.profile_signature)&&Number.isSafeInteger(body.expected_stock_version)&&body.expected_stock_version>=0&&
      Array.isArray(body.scans)&&body.scans.length>0&&body.scans.length<=10000&&body.scans.every(scan=>
        scan&&['system_code','profile_code','code'].every(key=>typeof scan[key]==='string'&&scan[key].length>0));
  }
  async function load(s){
    savedDraft=null;context=null;scans=[];panel.querySelector('select').replaceChildren();
    const next=await api(s,'/scan-context');if(!active(s))return;
    if(next.task_id!==s.id||!Array.isArray(next.profiles))throw Error('Ответ профиля относится к другому заданию.');
    const existing=await api(s,'/scan-draft');if(!active(s))return;
    if(existing&&(existing.task_id!==s.id||existing.actor!==s.actor||!validBody(existing.request)||existing.draft_id!==existing.request.draft_id))throw Error('Набор сканов не соответствует заданию или пользователю.');
    context=next;scans=existing?existing.request.scans:[];
    if(existing&&existing.profile_signature===next.profile_signature&&existing.stock_version===next.stock_version&&
       existing.request.profile_signature===next.profile_signature&&existing.request.expected_stock_version===next.stock_version)savedDraft=existing.draft_id;
    const select=panel.querySelector('select');select.replaceChildren();
    next.profiles.filter(profile=>['UNIT','UNIT_OR_AGGREGATION'].includes(profile.scan_mode)).forEach(profile=>{
      const option=document.createElement('option');option.value=JSON.stringify({system_code:profile.system_code,profile_code:profile.profile_code});
      option.textContent=profile.system_code+'/'+profile.profile_code+' v'+profile.profile_version+' ('+profile.scan_mode+')';select.append(option);
    });
    message(existing&&!savedDraft?'Сохранённые сканы устарели: состав или профиль изменился. Повторно проверьте набор перед сохранением.':
      next.marking_required?'Маркированный товар: ШК товара не заменяет уникальную марку.':'Маркировка по карточке товара не требуется.');
  }
  async function save(s,retry){
    if(!context)throw Error('Загрузите профиль выбранного задания.');
    const pending=localStorage.getItem(s.key);
    if(pending&&!retry)throw Error('Сначала повторите сохранённый запрос.');
    if(retry&&!pending)throw Error('Незавершённого запроса нет.');
    const body=retry?JSON.parse(pending):{draft_id:'TASK.SCAN:'+crypto.randomUUID(),profile_signature:context.profile_signature,
      expected_stock_version:context.stock_version,scans};
    if(!validBody(body))throw Error('Сохранённый запрос повреждён или набор пуст. Отправка не выполнена.');
    const wire=JSON.stringify(body);localStorage.setItem(s.key,wire);
    if(localStorage.getItem(s.key)!==wire)throw Error('Не удалось надёжно сохранить запрос. Отправка не выполнена.');
    savedDraft=null;
    const result=await api(s,'/scan-draft',body);if(!active(s))return;
    if(result.draft_id!==body.draft_id)throw Error('Сервер вернул другой набор. Запрос сохранён для расследования и повтора.');
    if(localStorage.getItem(s.key)!==wire)throw Error('Локальный запрос изменён в другой вкладке. Обновите профиль.');
    localStorage.removeItem(s.key);if(localStorage.getItem(s.key)!==null)throw Error('Ответ получен, но запрос не очищен. Повтор безопасен с прежним ID.');
    await load(s);if(!active(s))return;
    if(savedDraft===body.draft_id)message('Сканы подтверждены сервером. Остаток изменится только при подтверждении задания.');
  }
  async function archive(s){
    const raw=localStorage.getItem(s.key);if(raw===null)throw Error('Повреждённый запрос не найден.');
    let valid=false;try{valid=validBody(JSON.parse(raw));}catch{}
    if(valid)throw Error('Запрос имеет правильный формат. Повторите его без изменения идентификатора.');
    const archived=s.key+':damaged:'+crypto.randomUUID();localStorage.setItem(archived,raw);
    if(localStorage.getItem(archived)!==raw||localStorage.getItem(s.key)!==raw)throw Error('Архив не подтверждён или исходник изменён.');
    localStorage.removeItem(s.key);if(localStorage.getItem(s.key)!==null)throw Error('Архив сохранён, но исходник не освобождён.');
    await load(s);if(active(s))message('Исходник сохранён в архиве. Показан текущий серверный набор; товарное движение не выполнялось.');
  }
  async function run(action){
    sync();if(busy)return;let s;
    try{
      s=capture();busy=true;render();
      if(action==='load')await load(s);
      if(action==='archive')await archive(s);
      if(action==='save'||action==='retry')await save(s,action==='retry');
      if(action==='add'){
        if(!context)throw Error('Загрузите профиль выбранного задания.');
        if(localStorage.getItem(s.key))throw Error('Сначала повторите сохранение.');
        const input=panel.querySelector('input'),select=panel.querySelector('select');
        if(!input.value||!select.value)throw Error('Выберите профиль и отсканируйте уникальный код.');
        scans.push({...JSON.parse(select.value),code:input.value});savedDraft=null;input.value='';message('Добавлено в форму. Сохраните набор на сервере.');
      }
    }catch(error){if(!s||active(s))message(error.message);}
    finally{if(s&&active(s)){busy=false;render();}else sync();}
  }
  panel.querySelectorAll('button').forEach(button=>{button.title=button.textContent;button.addEventListener('click',()=>run(button.dataset.action));});
  panel.querySelector('input').title='Отсканируйте уникальную марку штуки выбранного профиля';panel.querySelector('select').title='Выберите систему и профиль маркировки товара';
  panel.querySelector('input').addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();run('add');}});
  window.warehouseTaskScans={draftId(id){
    sync();if(id!==task()||context?.task_id!==id||busy)return null;
    try{return localStorage.getItem(capture().key)?null:savedDraft;}catch{return null;}
  }};
  window.addEventListener('warehouse-task-selected',sync);
  window.addEventListener('wms-admin-auth-ready',reset);
  const tsdId=document.getElementById('rtTsdTaskId');if(tsdId)new MutationObserver(sync).observe(tsdId,{childList:true,characterData:true,subtree:true});
  reset();
})();