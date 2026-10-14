/* Unposted CASE input only. Existing casePickIntent remains the command journal. */
window.cpCaseDraft=(()=>{
 let current=null,observed=null,editing=false;
 const host=document.createElement('section'),note=document.createElement('p'),restore=document.createElement('button'),archive=document.createElement('button');
 host.className='panel';host.id='cpTsdInputDraft';restore.type=archive.type='button';restore.textContent='Восстановить ввод';archive.textContent='Отложить старый черновик';
 restore.title='Восстановить локальные сканы только для прежней строки и неизменившихся данных. Ничего не отправляется.';
 archive.title='Сохранить старый ввод в локальном архиве и начать новый. Серверная команда не отменяется.';
 host.append(note,restore,archive);document.getElementById('cpTsdMarking').before(host);
 const ids=['cpTsdScanCell','cpTsdScanProduct','cpTsdScanBox','cpTsdScanContainer','cpTsdFactQty'];
 const identity=()=>JSON.stringify([cpTsdApiBase(),cpTsdUser()]);
 const storageKey=(task,line)=>JSON.stringify(['retailcase.caseInputDraft',cpTsdApiBase(),cpTsdUser(),task,line]);
 const canonical=value=>JSON.stringify(value,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]])):v);
 const active=()=>current&&current.identity===identity()&&current.task===cpTsd.task?.case_pick_task_id&&current.line===cpTsdCurrentLine()?.case_pick_line_id;
 function pending(){return Boolean(localStorage.getItem(JSON.stringify(['retailcase.casePickIntent',cpTsdApiBase(),cpTsdUser()])));}
 function fields(){
  const result=ids.map(id=>({key:id,element:document.getElementById(id)}));
  for(const root of ['cpTsdMarking','cpTsdWeightedBox'])for(const element of document.querySelectorAll('#'+root+' [data-system][data-profile]'))
   result.push({key:JSON.stringify([root,element.dataset.system,element.dataset.profile]),element});
  return result;
 }
 function read(raw){
  if(raw===null)return null;
  if(raw.length>2*1024*1024)throw Error('Черновик превышает допустимый размер.');
  let value;try{value=JSON.parse(raw);}catch{throw Error('Черновик повреждён. Восстановление заблокировано; исходная запись сохранена.');}
  if(value?.schema!==1||typeof value.revision!=='string'||typeof value.signature!=='string'||!Array.isArray(value.fields)||value.fields.length>150||
    !value.fields.every(f=>f&&typeof f.key==='string'&&typeof f.value==='string')||new Set(value.fields.map(f=>f.key)).size!==value.fields.length)
   throw Error('Черновик повреждён. Отложите исходную запись перед новым вводом.');
  return value;
 }
 function render(){
  host.hidden=!active();restore.disabled=archive.disabled=true;if(!active())return;
  try{
   const raw=localStorage.getItem(current.key),record=read(raw);archive.disabled=raw===null||pending();
   if(pending()){note.textContent='Есть незавершённая команда отбора. Сначала повторите её; черновик не заменяет команду.';return;}
   restore.disabled=!record||record.signature!==current.signature;
   note.textContent=!record?'Ввод сохраняется локально для этой строки. После обновления восстановите его явно.':
    record.signature!==current.signature?'Строка, количество или настройки изменились. Старые сканы не восстанавливаются; отложите черновик и сканируйте заново.':
    editing?'Ввод сохранён локально. Отбор подтвердит только сервер.':'Найден черновик этой строки. Восстановите ввод или отложите его перед новым сканированием. Архив весов всегда выбирается заново.';
  }catch(error){note.textContent=error.message;try{archive.disabled=pending()||localStorage.getItem(current.key)===null;}catch{}}
 }
 function save(event){
  if(!active()||!fields().some(f=>f.element===event.target))return;
  try{
   if(pending())throw Error('Сначала повторите неизменённую команду. Новый ввод не сохранён.');
   if(!editing&&observed!==null)throw Error('Сначала восстановите или отложите предыдущий черновик. Новый ввод не сохранён.');
   if(localStorage.getItem(current.key)!==observed)throw Error('Черновик изменён в другой вкладке. Обновите строку перед вводом.');
   const record={schema:1,revision:crypto.randomUUID(),signature:current.signature,fields:fields().map(f=>({key:f.key,value:f.element.value}))};
   const wire=JSON.stringify(record);read(wire);localStorage.setItem(current.key,wire);
   if(localStorage.getItem(current.key)!==wire)throw Error('Не удалось проверить сохранение ввода.');
   observed=wire;editing=true;render();
  }catch(error){note.textContent=error.message+' Проведение этим действием не выполнялось.';}
 }
 restore.addEventListener('click',()=>{
  try{
   if(!active()||pending())throw Error('Нет текущего черновика либо ожидается повтор команды.');
   const raw=localStorage.getItem(current.key),record=read(raw);
   if(!record||record.signature!==current.signature)throw Error('Данные строки изменились. Сканы необходимо повторить.');
   const controls=fields();if(record.fields.some(f=>!controls.some(c=>c.key===f.key)))throw Error('Состав полей профиля изменился.');
   for(const control of controls)control.element.value=record.fields.find(f=>f.key===control.key)?.value||'';
   observed=raw;editing=true;
   for(const control of controls)if(control.element.tagName==='TEXTAREA')control.element.dispatchEvent(new Event('input'));
   render();note.textContent='Локальный ввод восстановлен. Проверьте физическую строку; архив весов выберите заново. Отбор не проведён.';
  }catch(error){note.textContent=error.message;}
 });
 archive.addEventListener('click',()=>{
  try{
   if(!active()||pending())throw Error('Сначала повторите незавершённую команду.');
   const raw=localStorage.getItem(current.key);if(raw===null)return;
   const key=current.key+':archived:'+crypto.randomUUID();localStorage.setItem(key,raw);
   if(localStorage.getItem(key)!==raw||localStorage.getItem(current.key)!==raw)throw Error('Архив не подтверждён или запись изменена.');
   localStorage.removeItem(current.key);if(localStorage.getItem(current.key)!==null)throw Error('Не удалось освободить черновик.');
   observed=null;editing=true;for(const field of fields())field.element.value='';render();note.textContent='Прежний ввод сохранён в локальном архиве. Введите новые сканы; серверный факт не изменён.';
  }catch(error){note.textContent=error.message;}
 });
 document.addEventListener('input',save);window.addEventListener('storage',()=>{if(active())render();});
 window.addEventListener('wms-admin-auth-ready',()=>{current=null;observed=null;editing=false;host.hidden=true;});
 return {
  begin(){current=null;observed=null;editing=false;host.hidden=true;},
  mount(task,line,policy){
   current={task:task.case_pick_task_id,line:line.case_pick_line_id,identity:identity(),key:storageKey(task.case_pick_task_id,line.case_pick_line_id),
    signature:canonical({task:task.case_pick_task_id,sscc:task.sscc,status:task.status,line,policy})};
   editing=false;try{observed=localStorage.getItem(current.key);}catch(error){note.textContent='Хранилище недоступно: '+error.message;host.hidden=false;return;}render();
  },
  capture(task,line){
   const key=storageKey(task,line),raw=localStorage.getItem(key),record=read(raw);
   if(record&&(!active()||current.key!==key||record.signature!==current.signature||!editing||observed!==raw))throw Error('Сначала восстановите или отложите черновик текущей строки.');
   return record?{key,revision:record.revision}:null;
  },
  settle(ticket){
   if(!ticket)return;
   const raw=localStorage.getItem(ticket.key),record=read(raw);
   if(record?.revision===ticket.revision){localStorage.removeItem(ticket.key);if(localStorage.getItem(ticket.key)!==null)throw Error('Сервер подтвердил отбор, но локальный черновик не очищен. Обновите строку.');}
  }
 };
})();