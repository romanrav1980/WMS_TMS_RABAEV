/* Existing group command journal: exact replay, no second business command store. */
window.wmsInterwarehouseGroupIntent=(()=>{
 const wires=new WeakMap(),paths={'/group-plan':'source_load_operation_id','/unload':'plan_operation_id','/group-receive':'plan_operation_id','/group-placement':'receipt_operation_id','/release-custody':'receipt_operation_id','/group-onward':'receipt_operation_id'};
 const error=()=>Error('Сохранённая межскладская команда повреждена. Отправка запрещена; архивируйте исходник и перечитайте серверное состояние.');
 function decode(key,raw){
  let intent;try{intent=JSON.parse(raw);}catch{throw error();}
  const body=intent?.body,ref=paths[intent?.path];
  if(!ref||!body||typeof body.operation_id!=='string'||!/^[A-Za-z0-9_.:-]{1,100}$/.test(body.operation_id)||typeof body[ref]!=='string'||!body[ref]||body[ref].length>100||
   typeof intent.scanKey!=='string'||!intent.scanKey.startsWith(key+':scans:')||(intent.confirmed!==undefined&&typeof intent.confirmed!=='boolean'))throw error();
  if(intent.path==='/group-receive'&&(!Array.isArray(body.items)||body.items.length<2||body.items.length>200||!Array.isArray(body.scans)||body.scans.length>20000))throw error();
  wires.set(intent,raw);return intent;
 }
 function current(key,intent){if(!wires.has(intent)||localStorage.getItem(key)!==wires.get(intent))throw Error('Сохранённая команда изменена другой вкладкой. Обновите страницу; новая операция не отправлена.');}
 function write(key,intent){const raw=JSON.stringify(intent);decode(key,raw);localStorage.setItem(key,raw);if(localStorage.getItem(key)!==raw)throw Error('Не удалось подтвердить запись исходной команды. Отправка остановлена.');wires.set(intent,raw);return intent;}
 return {
  load(key){const raw=localStorage.getItem(key);return raw===null?null:decode(key,raw);},
  prepare(key,intent){if(localStorage.getItem(key)!==null)throw Error('Сначала восстановите сохранённую команду.');return write(key,intent);},
  check:current,
  result(intent,result){if(result?.operation_id!==intent.body.operation_id)throw Error('Ответ не соответствует исходной операции. Повторите сохранённый запрос.');},
  rejected(key,intent,confirmed){current(key,intent);return write(key,{...intent,confirmed:confirmed===true});},
  complete(key,intent){current(key,intent);localStorage.removeItem(key);if(localStorage.getItem(key)!==null)throw Error('Команда выполнена, но локальный журнал не освобождён. Повторите исходную операцию.');},
  async archive(key,refresh,isCurrent){
   const raw=localStorage.getItem(key);if(raw===null)throw Error('Исходник изменился. Обновите страницу.');
   const archive=key+':archive:'+crypto.randomUUID();localStorage.setItem(archive,raw);
   if(localStorage.getItem(archive)!==raw)throw Error('Архив не подтверждён.');
   await refresh();if(!isCurrent()||localStorage.getItem(key)!==raw)throw Error('Контекст или исходник изменён; блокировка сохранена.');
   localStorage.removeItem(key);if(localStorage.getItem(key)!==null)throw Error('Журнал не освобождён.');
  }
 };
})();