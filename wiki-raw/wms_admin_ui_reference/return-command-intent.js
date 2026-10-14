/* Recovery of existing return receive/putaway keys. No second command queue. */
window.wmsReturnCommandIntent=(()=>{
 const wires=new WeakMap();
 const failure=()=>Error('Сохранённая команда возврата повреждена. Архивируйте исходник и перечитайте склад; новая операция заблокирована.');
 function parse(key,kind,raw){
  let value;try{value=JSON.parse(raw);}catch{throw failure();}const b=value?.body,ref=kind==='receive'?'pickup_operation_id':'receipt_operation_id';
  if(!b||typeof b.operation_id!=='string'||!/^[A-Za-z0-9_.:-]{1,100}$/.test(b.operation_id)||typeof b[ref]!=='string'||!b[ref]||b[ref].length>100||
   (value.confirmed!==undefined&&typeof value.confirmed!=='boolean')||kind==='receive'&&(!/^\d+(\.\d+)?$/.test(b.quantity)||typeof b.quantity!=='string'||typeof b.base_uom!=='string'||!b.base_uom))throw failure();
  wires.set(value,raw);return value;
 }
 function check(key,value){if(!wires.has(value)||localStorage.getItem(key)!==wires.get(value))throw Error('Исходная команда изменена другой вкладкой. Перечитайте страницу; повтор с другим содержимым запрещён.');}
 function write(key,kind,value){const raw=JSON.stringify(value);parse(key,kind,raw);localStorage.setItem(key,raw);if(localStorage.getItem(key)!==raw)throw Error('Запись исходной команды не подтверждена чтением. Отправка остановлена.');wires.set(value,raw);return value;}
 return {
  load(key,kind){const raw=localStorage.getItem(key);return raw===null?null:parse(key,kind,raw);},
  prepare(key,kind,value){if(localStorage.getItem(key)!==null)throw Error('В журнале уже есть команда; перечитайте страницу.');return write(key,kind,value);},check,
  confirmed(key,kind,value,confirmed){check(key,value);return write(key,kind,{...value,confirmed:confirmed===true});},
  complete(key,value){check(key,value);localStorage.removeItem(key);if(localStorage.getItem(key)!==null)throw Error('Журнал не освобождён. Повторите прежнюю операцию.');},
  async archive(key,refresh,current){
   const raw=localStorage.getItem(key);if(raw===null)throw Error('Исходник изменился; перечитайте страницу.');
   const archive=key+':archive:'+crypto.randomUUID();localStorage.setItem(archive,raw);if(localStorage.getItem(archive)!==raw)throw Error('Архив не подтверждён.');
   await refresh();if(!current()||localStorage.getItem(key)!==raw)throw Error('Контекст или исходник изменился. Журнал сохранён.');
   localStorage.removeItem(key);if(localStorage.getItem(key)!==null)throw Error('Журнал не освобождён.');
  }
 };
})();