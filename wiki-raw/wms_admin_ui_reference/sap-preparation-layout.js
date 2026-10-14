(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 const scope=()=>JSON.stringify([auth().state.apiBase,auth().state.user?.username]);
 let proposal=null,epoch=0,busy=false;
 const key=()=> 'sap-st-preparation:'+scope();
 const autoPending=()=>!!localStorage.getItem('sap-auto-preparation:'+auth().state.apiBase+':'+auth().state.user?.username);
 const pending=()=>{const raw=localStorage.getItem(key());return raw?JSON.parse(raw):null;};
 function controls(){let p;try{p=pending();}catch{}el('splSave').disabled=busy||!proposal||!!p||autoPending();el('splRetry').disabled=busy||!p;el('splResolve').disabled=busy||!p;
  el('splPending').textContent=p?'Сохранена команда '+p.body.operation_id+' для исходного заказа #'+p.order_id+'. Повтор создаёт прежнюю укладку.':'';}
 async function api(path,options={}){
  const identity=scope(),r=await fetch(auth().state.apiBase.replace(/\/$/,'')+'/api/integrations/sap/store-orders/'+path,
   {...options,headers:auth().headers(options.headers||{})});
  let v;try{v=await r.json();}catch{throw Error('Ответ не подтверждён. Повторите сохранённую команду.');}
  if(identity!==scope())throw Error('Пользователь изменился.');
  if(!r.ok)throw Error(v.detail?.message||v.detail||'Операция отклонена.');return v;
 }
 function input(value,kind){const i=document.createElement('input');i.value=value;i.dataset.kind=kind;i.inputMode='decimal';return i;}
 function td(value){const t=document.createElement('td');if(value instanceof Node)t.appendChild(value);else t.textContent=String(value);return t;}
 async function read(manual=false){
  const token=++epoch,identity=scope(),order=Number(el('splOrder').value);proposal=null;controls();
  try{
   if(!Number.isSafeInteger(order)||order<1)throw Error('Укажите исходный заказ.');
   const counts={};if(manual)for(const tr of el('splArticleRows').children){const n=Number(tr.querySelector('input').value);if(!Number.isSafeInteger(n)||n<1||n>100)throw Error('Число паллет: целое от 1 до 100.');counts[tr.dataset.article]=n;}
   const v=await api(order+'/preparation-layout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({article_pallet_counts:counts})});
   if(token!==epoch||identity!==scope())return;proposal=v;
   el('splArticleRows').replaceChildren(...v.articles.map(a=>{const tr=document.createElement('tr');tr.dataset.article=a.articul;
    for(const value of [a.articul,a.pallet_norm??'Не задана',a.whole_pack_quantity,input(a.pallet_count,'count')])tr.appendChild(td(value));return tr;}));
   el('splPalletRows').replaceChildren(...v.pallets.flatMap((p,i)=>p.lines.map(line=>{const tr=document.createElement('tr');tr.dataset.pallet=String(i);tr.dataset.article=line.articul;
    tr.append(td(i+1),td(line.articul),td(input(line.quantity,'quantity')));return tr;})));
   el('splMessage').textContent='Предложено паллет: '+v.pallets.length+'. Количество можно изменить с сохранением всего исходного заказа и целых коробок. Смешанная укладка и физическая вместимость не подтверждены.';controls();
  }catch(e){if(token===epoch&&identity===scope())el('splMessage').textContent=e.message;}
 }
 async function send(resolve=false){
  if(busy)return;const identity=scope();let command;
  try{if(autoPending())throw Error('Сначала выясните исход автоматической подготовки.');command=pending();if(!command){
   if(resolve||!proposal)throw Error('Сначала прочитайте предложение.');
   const pallets=proposal.pallets.map(()=>({lines:[]}));
   for(const tr of el('splPalletRows').children){const quantity=tr.querySelector('input').value.trim();
    if(!/^\d+(\.\d{1,6})?$/.test(quantity)||!/[1-9]/.test(quantity))throw Error('Укажите положительное количество до 6 знаков после точки.');
    pallets[Number(tr.dataset.pallet)].lines.push({articul:tr.dataset.article,quantity});}
   command={order_id:proposal.customer_order_id,body:{operation_id:'SAPPREP:'+crypto.randomUUID(),pallets}};
   localStorage.setItem(key(),JSON.stringify(command));
  }}catch(e){el('splMessage').textContent=e.message;return;}
  busy=true;controls();
  try{const v=await api(command.order_id+'/prepare-st'+(resolve?'/resolve':''),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(command.body)});
   if(identity!==scope())return;
   if(resolve&&v.state==='NOT_PREPARED'){
    localStorage.removeItem(key());window.dispatchEvent(new Event('sap-manual-preparation-settled'));proposal=null;el('splMessage').textContent='После ожидания исходной команды сервер подтвердил: СТ не подготовлена. Перечитайте предложение перед новым решением.';return;
   }
   const result=resolve?v.result:v;
   if(result.customer_order_id!==command.order_id||result.status!=='ST_PREPARED')throw Error('Результат не подтверждён. Сохранённая команда остаётся.');
   localStorage.removeItem(key());window.dispatchEvent(new Event('sap-manual-preparation-settled'));proposal=null;el('splMessage').textContent='Подготовлена прежняя СТ '+result.st_number+', паллет: '+result.pallet_identifiers.length+'. Физический отбор и остатки не изменены.';
  }catch(e){if(identity===scope())el('splMessage').textContent=e.message+' Сохранённая команда остаётся для точного повтора.';}
  finally{busy=false;controls();}
 }
 el('splRead').addEventListener('click',()=>read());el('splRecalculate').addEventListener('click',()=>read(true));
 el('splSave').addEventListener('click',()=>send());el('splRetry').addEventListener('click',()=>send());el('splResolve').addEventListener('click',()=>send(true));
 function clear(){epoch++;proposal=null;el('splArticleRows').replaceChildren();el('splPalletRows').replaceChildren();controls();}
 el('splOrder').addEventListener('input',clear);window.addEventListener('wms-admin-auth-ready',clear);
 window.addEventListener('sap-store-source-selected',event=>{el('splOrder').value=event.detail.order_id;clear();});
 window.addEventListener('storage',controls);window.addEventListener('sap-auto-preparation-settled',controls);
 controls();
})();
