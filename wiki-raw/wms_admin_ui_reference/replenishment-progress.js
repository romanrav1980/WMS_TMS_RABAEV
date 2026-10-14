(() => {
  const panel=document.createElement('section');panel.className='panel wave-execution-panel';
  panel.innerHTML='<header><h2>Потребность и фактическая подача</h2></header><div class="wave-execution-toolbar"><label>Волна<input type="number" min="1" title="ID волны для просмотра фактически подтверждённого пополнения"></label><button title="Перечитать потребность, подтверждённую подачу и остаток отбора">Обновить факт</button></div><p role="status" aria-live="polite">Выберите волну. Завершение подачи не закрывает потребность заказа.</p><div data-progress class="rights-table-wrap"></div>';
  (document.querySelector('.admin-page')||document.querySelector('main')||document.body).prepend(panel);
  let epoch=0;
  const input=panel.querySelector('input'),status=panel.querySelector('[role=status]'),rowsTarget=panel.querySelector('[data-progress]');
  const scope=()=>JSON.stringify([window.wmsAdminAuth?.state?.apiBase,window.wmsAdminAuth?.state?.user?.username]);
  async function load(){
    const wave=Number(input.value),auth=window.wmsAdminAuth;
    if(!Number.isSafeInteger(wave)||wave<1||!auth?.hasPermission('pick_wave_view'))return;
    const id=++epoch,identity=scope();status.textContent='Читаю фактическое пополнение…';rowsTarget.replaceChildren();
    try{
      const response=await fetch(auth.state.apiBase.replace(/\/$/,'')+'/api/inventory/replenishment-progress?wave_id='+wave+'&limit=50',{headers:auth.headers()});
      const rows=await response.json();
      if(id!==epoch||Number(input.value)!==wave||identity!==scope())return;
      if(!response.ok)throw new Error(JSON.stringify(rows.detail||rows));
      const table=document.createElement('table');table.className='rights-table';
      const head=document.createElement('thead'),tr=document.createElement('tr');
      for(const text of ['Задание / товар','Куда','Потребность','Подача','Подтверждено','Недоподано','Остаток отбора','Вместимость','Причина']){
        const th=document.createElement('th');th.textContent=text;tr.append(th);
      }
      head.append(tr);table.append(head);const body=document.createElement('tbody');table.append(body);
      for(const row of rows){
        const tr=document.createElement('tr');
        for(const value of ['#'+row.pick_wave_replenish_task_id+' / '+row.articul,row.target_cell_code,
          row.demand_base,row.planned_base,row.confirmed_base,row.demand_remaining_base,
          row.case_order_remaining_base??'—',row.capacity_available_base??'Не задана',
          row.status+(row.wait_reason?' / '+row.wait_reason:'')]){
          const td=document.createElement('td');td.textContent=value??'—';tr.append(td);
        }
        body.append(tr);
      }
      rowsTarget.replaceChildren(table);
      status.textContent=rows.length?'Показано '+rows.length+' строк. Количества в базовых единицах каждого товара.'+
        (rows.length===50?' Выборка ограничена первыми50 строками; полный состав смотрите в очереди пополнения.':''):
        'Строк пополнения нет. Это не подтверждение исполнения заказа.';
    }catch(error){if(id===epoch&&identity===scope())status.textContent=error.message;}
  }
  function choose(wave){
    if(!Number.isSafeInteger(wave)||wave<1)return;epoch++;input.value=wave;void load();
  }
  panel.querySelector('button').addEventListener('click',load);
  input.addEventListener('change',()=>window.dispatchEvent(new CustomEvent('wms-wave-requested',{detail:{wave_id:Number(input.value)}})));
  window.addEventListener('wms-wave-selection-loading',event=>{epoch++;input.value=event.detail?.wave_id||'';rowsTarget.replaceChildren();status.textContent='Читаю выбранную волну…';});
  window.addEventListener('wms-wave-selected',event=>choose(Number(event.detail?.wave_id)));
  function rights(){
    epoch++;rowsTarget.replaceChildren();panel.hidden=!window.wmsAdminAuth?.hasPermission('pick_wave_view');
    if(!panel.hidden){if(!input.value)input.value=new URLSearchParams(location.search).get('wave_id')||'';void load();}
  }
  window.addEventListener('wms-admin-auth-ready',rights);rights();
})();
