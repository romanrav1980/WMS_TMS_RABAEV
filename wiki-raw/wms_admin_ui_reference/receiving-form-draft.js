/* Before-send form recovery. The existing receipt intent owns every sent command. */
window.wmsReceiptFormDraft={create(adapter){
 let current=null,observed=null,editing=false,restoring=false;
 const host=document.createElement('section'),note=document.createElement('p'),restore=document.createElement('button'),archive=document.createElement('button');
 host.id='receiptFormDraft';host.className='panel';restore.type=archive.type='button';restore.textContent='Восстановить ввод паллеты';archive.textContent='Отложить черновик и вводить заново';
 restore.title='Восстановить ещё не отправленные данные при неизменных основании SAP, строке и правилах товара. Приёмка не проводится.';
 archive.title='Сохранить прежний ввод в локальном архиве. Уже отправленная команда не отменяется.';
 host.append(note,restore,archive);document.getElementById('receiptSuggestion').before(host);
 const canonical=value=>JSON.stringify(value,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]])):v);
 const scope=()=>window.wmsReceiptIntent.scope();
 const active=()=>current&&scope()===current.scope;
 const pending=()=>window.wmsReceiptIntent.pending().filter(x=>decodeURIComponent(x.path.split('/')[4])===current.order&&x.body.line_number===current.line);
 function read(raw){
  if(raw===null)return null;
  if(raw.length>2*1024*1024)throw Error('Черновик паллеты слишком велик.');
  let value;try{value=JSON.parse(raw);}catch{throw Error('Черновик ввода повреждён. Сохраните его в архив; новая отправка заблокирована.');}
  if(value?.schema!==1||typeof value.revision!=='string'||typeof value.signature!=='string'||!value.data)throw Error('Черновик ввода повреждён.');
  return value;
 }
 function ready(){
  if(!active())throw Error('Загрузите текущий заказ, строку и правила товара.');
  if(pending().length)throw Error('Для этой строки есть неподтверждённая приёмка. Сначала повторите исходный запрос.');
 }
 function render(){
  try{
   host.hidden=!active();restore.disabled=archive.disabled=true;if(!active())return;
   const raw=localStorage.getItem(current.key),record=read(raw),waiting=pending().length;
   archive.disabled=raw===null||Boolean(waiting);
   if(waiting){note.textContent='Приоритет у сохранённой команды приёмки: повторите её исходный запрос. Черновик не создаёт вторую приёмку.';return;}
   const valid=record?.signature===current.signature&&adapter.valid(record.data,current.policy);
   restore.disabled=!record||!valid;
   note.textContent=!record?'Неотправленные данные паллеты сохраняются локально. Восстановление после обновления выполняется явно.':
    !valid?'Основание, остаток строки или профиль изменились либо черновик повреждён. Восстановление запрещено; отложите старый ввод.':
    editing?'Ввод паллеты сохранён локально; товар ещё не принят.':'Найден неотправленный ввод этой строки. Восстановите его или отложите перед новым сканированием.';
  }catch(error){host.hidden=false;note.textContent=error.message;try{archive.disabled=!active()||pending().length>0||localStorage.getItem(current.key)===null;}catch{archive.disabled=true;}}
 }
 function save(){
  if(restoring||!current||adapter.busy())return;
  try{
   ready();const raw=localStorage.getItem(current.key);
   if(raw!==observed)throw Error('Черновик изменён другой вкладкой. Перечитайте строку.');
   if(!editing&&raw!==null)throw Error('Сначала восстановите или отложите найденный черновик. Ввод не перезаписан.');
   const data=adapter.capture();if(!adapter.valid(data,current.policy))throw Error('Не удалось сохранить введённые сканы: проверьте размер кода и профиль.');
   const wire=JSON.stringify({schema:1,revision:crypto.randomUUID(),signature:current.signature,data});read(wire);
   localStorage.setItem(current.key,wire);if(localStorage.getItem(current.key)!==wire)throw Error('Запись ввода не подтверждена чтением.');
   observed=wire;editing=true;render();
  }catch(error){note.textContent=error.message;}
 }
 function archiveCurrent(){
  if(!current)return true;
  try{
   const raw=localStorage.getItem(current.key);if(raw===null)return true;ready();
   const key=current.key+':archived:'+crypto.randomUUID();localStorage.setItem(key,raw);
   if(localStorage.getItem(key)!==raw||localStorage.getItem(current.key)!==raw)throw Error('Архив не подтверждён или запись изменилась.');
   localStorage.removeItem(current.key);if(localStorage.getItem(current.key)!==null)throw Error('Не удалось освободить черновик.');observed=null;editing=true;render();return true;
  }catch(error){note.textContent=error.message;return false;}
 }
 restore.addEventListener('click',()=>{
  try{
   ready();const raw=localStorage.getItem(current.key),record=read(raw);
   if(record?.signature!==current.signature||!adapter.valid(record.data,current.policy))throw Error('Текущий контекст или данные не совпадают с черновиком.');
   restoring=true;adapter.apply(record.data);observed=raw;editing=true;render();
   note.textContent='Ввод восстановлен. Проверьте паллету, партию, срок и коды. Это не приёмка товара и не подтверждение печати.';
  }catch(error){note.textContent=error.message;}finally{restoring=false;}
 });
 archive.addEventListener('click',()=>{if(archiveCurrent())adapter.reset();});
 document.getElementById('receiptPalletFields').addEventListener('input',event=>{if(adapter.fields.includes(event.target.id))save();});
 document.getElementById('receiptPalletFields').addEventListener('change',event=>{if(adapter.fields.includes(event.target.id))save();});
 window.addEventListener('wms-receipt-pending-changed',render);window.addEventListener('storage',render);
 window.addEventListener('wms-receipt-selection-reset',()=>{current=null;observed=null;editing=false;host.hidden=true;});
 window.addEventListener('wms-admin-auth-ready',()=>{current=null;observed=null;editing=false;host.hidden=true;});
 host.hidden=true;
 return {
  begin(){current=null;observed=null;editing=false;host.hidden=true;},
  mount(order,line,policy){
   current={scope:scope(),order:order.order_id,line:line.line_number,policy,
    key:JSON.stringify(['retailcase.receipt.form',scope(),order.ware_id,order.order_id,line.line_number]),
    signature:canonical({warehouse:order.ware_id,order:order.order_id,revision:order.revision,receipt_state:order.receipt_state,receive_cell:order.receive_cell,line,policy})};
   editing=false;try{observed=localStorage.getItem(current.key);}catch(error){observed=null;note.textContent=error.message;}render();
  },save,archiveCurrent,
  assertPostable(){
   ready();const raw=localStorage.getItem(current.key),record=read(raw);
   if(record&&(!editing||raw!==observed||record.signature!==current.signature||!adapter.valid(record.data,current.policy)))throw Error('Восстановите или отложите черновик перед новой приёмкой.');
  },
  submitted(intent){
   if(!current||!intent?.storage_key||!intent.path.endsWith('/'+encodeURIComponent(current.order)+'/pallets')||intent.body.line_number!==current.line)return;
   const stored=window.wmsReceiptIntent.pending().find(x=>x.storage_key===intent.storage_key);
   if(!stored||JSON.stringify(stored.body)!==JSON.stringify(intent.body))throw Error('Исходный запрос не подтверждён в журнале. Отправка остановлена.');
   if(localStorage.getItem(current.key)===observed){localStorage.removeItem(current.key);if(localStorage.getItem(current.key)!==null)throw Error('Команда сохранена, но локальный ввод не освобождён. Используйте повтор исходного запроса.');observed=null;editing=false;}render();
  }
 };
}};