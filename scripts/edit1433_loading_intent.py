from pathlib import Path
p=Path('wiki-raw/wms_admin_ui_reference/transport-loading-intent.js')
p.write_text('''/* Preserve the original loading command until its own server result is confirmed. */
(() => {
 const valid = value => {
  if(!value || !Number.isSafeInteger(value.trip_id) || value.trip_id<1 ||
   !/^[A-Za-z0-9_.:-]{1,100}$/.test(value.body?.operation_id||''))return false;
  if(value.path==='/api/inventory/pallet-floor-types')return true;
  if(value.path==='/api/transport/loading/'+value.trip_id+'/depart')return true;
  return ['/api/transport/loading/confirm','/api/transport/loading/confirm-single',
   '/api/transport/loading/confirm-reconciliation'].includes(value.path)&&value.body.transport_task_id===value.trip_id;
 };
 window.wmsLoadingIntent={create:storageKey=>window.wmsCommandIntent.create('',valid,{storageKey}),
  confirms:(saved,result)=>result?.operation_id===saved.body.operation_id};
})();
''',encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/transport-loading.js');s=p.read_text(encoding='utf-8')
s=s.replace('let pending=null,busy=false,composition=null,trip=null,generation=0,identity="";','let pending=null,busy=false,composition=null,trip=null,generation=0,identity="",record=null;')
s=s.replace(' const modeInput=', ' const intent=window.wmsLoadingIntent.create(scope);\n const modeInput=')
s=s.replace('el("loadRetry").hidden=!pending;', 'el("loadRetry").hidden=!pending||!!record?.damaged;el("loadArchive").hidden=!record?.damaged;')
s=s.replace('error.confirmed=r.status<500&&data.detail?.outcome_confirmed!==false;', 'error.confirmed=(r.status===422||data.detail?.outcome_confirmed===true)&&![401,403].includes(r.status)&&!String(data.detail?.message||data.detail?.code||"").includes("CONFLICT");')
s=s.replace('const saved={body,path,trip_id:id};localStorage.setItem(key,JSON.stringify(saved));pending=saved;await send(key);', 'const saved={body,path,trip_id:id};record=intent.save(saved);pending=saved;await send(key);')
s=s.replace('if(!pending||busy)return;const saved=pending,raw=localStorage.getItem(key);', 'if(!pending||busy||record?.damaged)return;const saved=pending,raw=localStorage.getItem(key);')
s=s.replace('   localStorage.removeItem(key);\n   if(key!==scope())return;', '   if(!window.wmsLoadingIntent.confirms(saved,result))throw new Error("Ответ не подтверждает сохранённую операцию. Повторите исходный запрос.");\n   intent.settle({storageKey:key,raw});record=null;\n   if(key!==scope())return;')
s=s.replace('pending={...saved,confirmed_rejection:true};localStorage.setItem(key,JSON.stringify(pending));', 'const rejected={...saved,confirmed_rejection:true},next=JSON.stringify(rejected);localStorage.setItem(key,next);if(localStorage.getItem(key)!==next)throw new Error("Не удалось сохранить подтверждённый отказ.");pending=rejected;record={storageKey:key,raw:next,value:rejected};')
a=s.index('  try{pending=JSON.parse(localStorage.getItem(key)||"null");');b=s.index('\n  const initial=',a)
s=s[:a]+'''  record=null;
  try{if(window.wmsAdminAuth.state.user?.username){record=intent.read();pending=record.damaged?{damaged:true}:record.value;
   if(record.damaged)status("Сохранённая команда повреждена. Новые операции заблокированы. Архивируйте исходный текст и перечитайте рейс.");
   else if(pending){el("tripId").value=String(pending.trip_id);status("Есть неподтверждённая операция. Повторите сохранённые данные.");}
  }}catch(e){pending={damaged:true};status("Не удалось прочитать сохранённую операцию: "+e.message);}controls();'''+s[b:]
a=s.index(' el("loadRetry").addEventListener');s=s[:a]+''' el("loadRetry").addEventListener("click",()=>send(scope()));
 el("loadRestart").addEventListener("click",()=>{try{if(!busy&&pending?.confirmed_rejection){intent.settle(record);record=null;pending=null;controls();status("Исправьте данные. Следующее подтверждение создаст новую операцию.");}}catch(e){status(e.message);}});
 el("loadArchive").addEventListener("click",async()=>{try{if(busy||!record?.damaged)return;intent.archiveDamaged(record);record=null;pending=null;controls();status("Исходный текст сохранён в архиве. Сверьте серверный статус перед новой операцией: архив не отменяет ранее выполненную погрузку.");await refresh();}catch(e){status(e.message);}});
 window.addEventListener("wms-admin-auth-ready",auth);auth();
})();
'''
p.write_text(s,encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/transport-loading.html');s=p.read_text(encoding='utf-8');s=s.replace('<button id="loadRetry"', '<button id="loadArchive" hidden title="Сохранить повреждённый текст в архиве и перечитать серверный статус рейса; выполненную операцию это не отменяет.">Архивировать повреждённый запрос</button><button id="loadRetry"');s=s.replace('<script src="transport-loading.js?v=20261014-1207"></script>', '<script src="wave-command-intent.js"></script><script src="transport-loading-intent.js"></script><script src="transport-loading.js?v=20261014-1433"></script>');p.write_text(s,encoding='utf-8')
