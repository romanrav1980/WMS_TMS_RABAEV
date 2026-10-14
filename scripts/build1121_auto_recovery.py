from pathlib import Path
import json
f={}
p=Path("wiki-raw/wms_admin_ui_reference/sap-automatic-preparation.js");s=p.read_text(encoding="utf-8")
s=s.replace("  el('sapAutoRead').disabled=busy;","  el('sapAutoRead').disabled=busy;\n  el('sapAutoRecover').hidden=!record?.damaged;el('sapAutoRecover').disabled=busy;")
needle=" function clear(){epoch++;"
recovery=''' async function recover(){
  if(busy)return;let record;const who=identity();
  try{record=intent.read();if(!record.damaged)throw Error('Повреждённой команды нет.');
   const order=Number(el('sapAutoOrder').value);
   if(!Number.isSafeInteger(order)||order<1)throw Error('Укажите исходный заказ для чтения его текущего состояния.');
   busy=true;controls();const current=await api(String(order),null,'GET');
   if(who!==identity())return;
   if(current.customer_order_id!==order)throw Error('Исходный заказ не подтверждён.');
   intent.archiveDamaged(record);proposal=null;
   message('Исходник сохранён в архиве; текущий заказ прочитан. Сверьте существующие СТ перед новым расчётом.');
  }catch(e){if(who===identity())message(e.message);}
  finally{busy=false;controls();}
 }
'''
s=s.replace(needle,recovery+needle)
s=s.replace("el('sapAutoResolve').addEventListener('click',()=>send(true));","el('sapAutoResolve').addEventListener('click',()=>send(true));\n el('sapAutoRecover').addEventListener('click',recover);")
s=s.replace("window.addEventListener('wms-admin-auth-ready',clear);","window.addEventListener('wms-admin-auth-ready',()=>{clear();if(location.hash==='#sapAutoPreparation')requestAnimationFrame(()=>el('sapAutoPreparation').scrollIntoView({block:'start'}));});")
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
s=s.replace('<p id="sapAutoPending"','<button id="sapAutoRecover" hidden>Прочитать заказ и архивировать повреждённый запрос</button>\n<p id="sapAutoPending"')
s=s.replace('sap-automatic-preparation.js?v=20261013-1115','sap-automatic-preparation.js?v=20261013-1121')
s=s.replace('</head>','<link rel="stylesheet" href="sap-automatic-preparation.css?v=20261013-1121">\n</head>')
f[str(p)]=s
f["wiki-raw/wms_admin_ui_reference/sap-automatic-preparation.css"]='''#sapAutoPreparation.panel{display:block;grid-column:1/-1;scroll-margin-top:110px;border-top:4px solid #2277ee}
#sapAutoPreparation .inline-form{display:grid;grid-template-columns:repeat(4,minmax(180px,1fr));gap:16px;margin:20px 0}
#sapAutoPreparation label{display:flex;flex-direction:column;gap:8px;font-weight:600}
#sapAutoPreparation input{min-height:42px;border-radius:8px}
#sapAutoPreparation table{width:100%;margin:18px 0}
#sapAutoPreparation button{margin:4px 8px 4px 0;min-height:40px}
#sapAutoPreparation p{line-height:1.6;max-width:1050px}
#sapAutoPending:not(:empty){padding:12px;background:#fff6df;border-radius:8px}
@media(max-width:1050px){#sapAutoPreparation .inline-form{grid-template-columns:repeat(2,minmax(180px,1fr))}}
@media(max-width:600px){#sapAutoPreparation .inline-form{grid-template-columns:1fr}#sapAutoPreparation{overflow-x:auto}}
'''
print(json.dumps(f,ensure_ascii=True))
