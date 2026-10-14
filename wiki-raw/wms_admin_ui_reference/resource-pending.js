/* Resource commands reuse the shared durable intent store with their legacy keys. */
(() => {
 const actions = {'/api/resources/workload/norms':'NORM','/api/resources/workload/attendance':'ATTENDANCE',
  '/api/resources/workload/attendance/replace':'REPLACE_ATTENDANCE','/api/resources/workload/attendance/cancel':'CANCEL_ATTENDANCE',
  '/api/resources/workload/forecast-scopes':'FORECAST_SCOPE'};
 const operation = body => body && typeof body.operation_id === 'string' && /^[A-Za-z0-9_.:-]{1,100}$/.test(body.operation_id);
 function create(storageKey, kind, retryId, recover) {
  const valid = value => kind === 'wave' ? operation(value) && Number.isSafeInteger(value.wave_id) && value.wave_id>0 :
   value && Object.hasOwn(actions,value.path) && operation(value.body) && Number.isSafeInteger(value.body.warehouse_id) && value.body.warehouse_id>0;
  const store=window.wmsCommandIntent.create('',valid,{storageKey});
  const button=document.createElement('button');button.hidden=true;button.type='button';
  button.textContent='Архивировать повреждённый запрос';
  button.title='Сохранить исходный текст в архиве и перечитать сервер. Архив не отменяет ранее выполненную операцию.';
  document.getElementById(retryId).after(button);
  function read(){
   const key=storageKey(),old=sessionStorage.getItem(key);
   if(localStorage.getItem(key)===null&&old!==null){
    localStorage.setItem(key,old);if(localStorage.getItem(key)!==old)throw Error('Не удалось перенести сохранённый запрос.');
    sessionStorage.removeItem(key);
   }
   const record=store.read();button.hidden=!record.damaged;return record;
  }
  button.onclick=async()=>{try{const record=read();store.archiveDamaged(record);button.hidden=true;await recover();}catch(error){button.title=error.message;}};
  function confirms(saved,result){
   if(kind==='wave')return result?.operation_id===saved.operation_id&&result.wave_id===saved.wave_id&&result.plan_status==='APPROVED'&&result.stock_changed===false;
   return result?.operation_id===saved.body.operation_id&&result.warehouse_id===saved.body.warehouse_id&&
    result.action===actions[saved.path]&&result.stock_changed===false;
  }
  function rejected(error){
   return error.status===422 || (error.status===409&&['WORKLOAD_CONFIG_REJECTED','WAVE_TIME_REJECTED'].includes(error.code)&&!error.message.includes('CONFLICT'));
  }
  return {...store,read,confirms,rejected};
 }
 window.wmsResourcePending={create};
})();
