// C-0010: надёжное хранение намерения команды и установление её результата.
// Команда отправляется только если намерение записано и прочитано обратно без искажений;
// повреждённую запись нельзя обойти удалением и новой командой, пока результат не установлен.
(() => {
 const PATHS=["/articles","/report","/decide","/allocate"];
 // Запись с обязательной проверкой чтением; любая ошибка хранилища — отказ отправлять команду.
 function save(key,intent){
  const raw=JSON.stringify(intent);let back;
  try{localStorage.setItem(key,raw);back=localStorage.getItem(key);}catch{back=undefined;}
  if(back!==raw)throw Error("Не удалось надёжно сохранить операцию на этом устройстве — команда не отправлена. Проверьте настройки браузера (хранилище сайта) и повторите.");
 }
 // Удаление считается выполненным, только если запись действительно исчезла.
 function remove(key){
  try{localStorage.removeItem(key);return localStorage.getItem(key)===null;}catch{return false;}
 }
 function idsIn(raw){return[...new Set(String(raw).match(/EXPENSE:[0-9a-f-]{36}/gi)||[])];}
 // Чтение: целая запись → намерение; нечитаемое хранилище или искажённая запись → повреждение с найденными ID.
 function read(key){
  let raw;
  try{raw=localStorage.getItem(key);}catch{return{damaged:true,unreadable:true,ids:[],ware:null};}
  if(raw==null)return null;
  try{const p=JSON.parse(raw);if(p&&PATHS.includes(p.path)&&p.body&&typeof p.body==="object"&&(p.path==="/articles"||typeof p.body.operation_id==="string"))return p;}catch{}
  const ware=/"warehouse_id"\s*:\s*(\d+)/.exec(raw);
  return{damaged:true,ids:idsIn(raw),ware:ware?Number(ware[1]):null};
 }
 // Строка реестра, в которой операция видна: сам расход, решение стадии или распределение.
 function holder(rows,op){
  return rows.find(r=>[r.operation_id,r.logist_operation_id,r.finance_operation_id,r.allocation_operation_id].includes(op));
 }
 // Установить результат по точному поиску на сервере (за пределами окна 100), не отправляя команду.
 async function establish(p,find,ware,loaded){
  if(p.damaged){
   if(!p.ids.length)return{established:false,text:"В повреждённой записи нет ID операции — результат установить нельзя. Сверьте реестр по документу вручную."};
   if(!ware)return{established:false,text:"Укажите склад и обновите реестр, затем проверьте ID "+p.ids.join(", ")+"."};
   for(const id of p.ids){
    const row=holder(loaded,id)||(await find(ware,id))[0];
    if(row)return{established:true,row,text:"Операция "+id+" найдена на сервере (расход "+row.operation_id+"). Результат установлен — запись можно закрыть."};
   }
   return{established:false,text:"Операции "+p.ids.join(", ")+" на складе "+ware+" не найдены ни в загруженном окне, ни точным поиском. Результат не установлен — новые команды заблокированы."};
  }
  const b=p.body,op=b.operation_id,w=b.warehouse_id||ware;
  if(!w)return{established:false,text:"Укажите склад и обновите реестр для проверки."};
  if(p.path==="/report"){const row=(await find(w,op))[0];return row?{established:true,row,text:"Расход "+op+" есть на сервере — регистрация выполнена."}:{established:false,text:"Расход "+op+" на сервере не найден. Повторите ту же операцию — дубль не создастся."};}
  const row=(await find(w,b.expense_operation_id))[0];
  const done=row&&(p.path==="/allocate"?row.allocation_operation_id===op:[row.logist_operation_id,row.finance_operation_id].includes(op));
  if(done)return{established:true,row,text:"Операция "+op+" есть на сервере — результат установлен."};
  return{established:false,text:"Операция "+op+" по расходу "+b.expense_operation_id+" на сервере не найдена"+(row?"":" (сам расход в этом складе не найден)")+". Повторите ту же операцию."};
 }
 window.LxIntent={save,remove,read,establish,holder};
})();
