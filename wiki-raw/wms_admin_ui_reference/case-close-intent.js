/* Close uses the existing CASE metadata journal, with a durable command identity. */
(()=>{
 const valid=v=>Boolean(v&&Number.isSafeInteger(v.task)&&v.task>0&&v.body&&/^CASE.CLOSE.UI:[A-Za-z0-9-]+$/.test(v.body.operation_id)&&Number.isSafeInteger(v.body.expected_content_version)&&v.body.expected_content_version>=0);
 const intent=window.wmsCommandIntent.create('nicora.caseClose:',valid);let busy=false;
 const button=()=>cpTsdEl('cpTsdClose');
 const archive=document.createElement('button');archive.type='button';archive.textContent='Архив повреждённого закрытия';archive.title='Сохранить повреждённый локальный запрос; факт на сервере не меняется.';archive.hidden=true;button().after(archive);
 function record(){try{return intent.read();}catch{return null;}}
 function refresh(){const r=record();archive.hidden=!r?.damaged;archive.disabled=busy;button().textContent=r?.value?'Повторить закрытие #'+r.value.task:'Закрыть сборку';button().disabled=busy||Boolean(r?.damaged)||(!r?.value&&(['WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP','SHIPPED','CANCELLED'].includes(cpTsd.task?.status)||!cpTsd.task?.lines?.length||cpTsd.task.lines.some(x=>!['PICKED','SHORT_PICKED','CANCELLED'].includes(x.status))));}
 const original=cpTsdTaskAction;
 cpTsdTaskAction=async function(action){
  if(action!=='close-pallet')return original(action);
  if(busy||window.cpTsdStockBusy)return;
  let r=intent.read();
  if(r.damaged)throw Error('Запрос закрытия повреждён. Сохраните его для разбора; новая команда заблокирована.');
  if(!r.value){
   const t=cpTsd.task;if(!t)throw Error('Выберите сборку.');
   if(localStorage.getItem(JSON.stringify(['nicora.casePickIntent',cpTsdApiBase(),cpTsdUser()])))throw Error('Сначала повторите сохранённый отбор.');
   if(window.wmsCaseType?.hasPending())throw Error('Сначала повторите изменение типа паллеты.');
   r=intent.save({task:t.case_pick_task_id,body:{operation_id:'CASE.CLOSE.UI:'+crypto.randomUUID(),expected_content_version:t.content_version}});
  }
  const current=()=>intent.scope()===r.storageKey&&localStorage.getItem(r.storageKey)===r.raw;
  const deliveryKey=r.storageKey+':delivery',priorUnknown=Boolean(localStorage.getItem(deliveryKey));
  localStorage.setItem(deliveryKey,'unknown');busy=true;window.cpTsdStockBusy=true;refresh();
  try{
   const result=await cpTsdFetch('/api/case-pick/tasks/'+r.value.task+'/close-pallet',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(r.value.body)});
   if(!current())return;
   if(result.operation_id!==r.value.body.operation_id||result.case_pick_task_id!==r.value.task||result.physical_stock_changed!==false||!['WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP'].includes(result.status))throw Error('Ответ не подтверждает закрытие. Повторите исходную команду.');
   intent.settle(r);localStorage.removeItem(deliveryKey);const task=await cpTsdFetch('/api/case-pick/tasks/'+r.value.task);
   if(intent.scope()!==r.storageKey)return;cpTsd.task=task;cpTsdRender();cpTsdSetState('Сборка закрыта. Следующий этап — контроль и привязка к СТ.');
  }catch(error){if(intent.scope()===r.storageKey){
   const known=['CASE_OPEN_LINES_REMAIN','CASE_PENDING_SHORT_DECISION_REQUIRED','CASE_CONTENT_VERSION_CHANGED','CASE_TASK_ACTOR_CONFLICT','CASE_LINE_QUANTITY_STATE_CONFLICT','CASE_PHYSICAL_QUANTITY_MISMATCH'].includes(error.detail);
   if(!priorUnknown&&error.status===409&&known&&current()){intent.settle(r);localStorage.removeItem(deliveryKey);cpTsdSetState(error.message+' Исправьте причину и перечитайте сборку.');}
   else cpTsdSetState(error.message+' Сохранённый запрос закрытия доступен для повтора.');}}
  finally{busy=false;window.cpTsdStockBusy=false;refresh();}
 };
 archive.addEventListener('click',()=>{if(busy)return;const r=record();if(r?.damaged){intent.archiveDamaged(r);refresh();cpTsdSetState('Повреждённый запрос закрытия сохранён в архиве. Перечитайте факт сборки.');}});
 window.cpCaseClose={hasPending:()=>Boolean(record()?.raw)};
 window.addEventListener('wms-admin-auth-ready',refresh);window.addEventListener('wms-case-render',refresh);
})();
