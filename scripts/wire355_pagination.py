from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/logistics-costs.html");s=p.read_text(encoding="utf-8").replace('<div id="lcHistory"></div>','<div id="lcHistory"></div><button id="lcMoreHistory" hidden title="Загрузить следующую страницу более ранних версий ставки">Более ранние версии</button>',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/logistics-costs.js");s=p.read_text(encoding="utf-8").replace("serial=0,rates=null;","serial=0,rates=null,history=null;",1)
start=s.index(' el("lcReadHistory").addEventListener');end=s.index('\n el("lcCalculate").addEventListener',start)
s=s[:start]+""" async function readHistory(more=false){await read(async current=>{const ware=positive("lcWare"),c=currency();if(more&&(!history||history.ware!==ware||history.currency!==c||!history.next))throw Error("Обновите историю для выбранного склада и валюты.");const before=more?history.next:0;const result=await request("/warehouses/"+ware+"/rates/history?currency="+encodeURIComponent(c)+"&limit=100&before_version="+before);if(!current())return;const nodes=result.rows.map(r=>{const p=document.createElement("p"),v=r.components;p.textContent="Версия "+r.version_no+" · с "+r.effective_from+" · "+r.rate_value+" / BOX"+(v?" = комплектация "+v.picking_rate+" + общие работы "+v.common_work_rate+" ("+v.common_work_amount+" / "+v.basis_boxes+" коробок)":"");return p;});if(more)el("lcHistory").append(...nodes);else el("lcHistory").replaceChildren(...nodes);history={ware,currency:c,next:result.next_before_version};el("lcMoreHistory").hidden=!history.next;say(history.next?"Страница истории прочитана. Можно загрузить более ранние версии.":"Все версии выбранной ставки прочитаны.");});}
 el("lcReadHistory").addEventListener("click",()=>readHistory(false));el("lcMoreHistory").addEventListener("click",()=>readHistory(true));"""+s[end:]
s=s.replace('pending=null;rates=null;for(const id','pending=null;rates=null;history=null;el("lcMoreHistory").hidden=true;for(const id',1)
s=s.replace('++serial;rates=null;el("lcRates").replaceChildren();','++serial;rates=null;history=null;el("lcMoreHistory").hidden=true;el("lcHistory").replaceChildren();el("lcRates").replaceChildren();',1)
s=s.replace(' el("lcRetry").addEventListener',' el("lcCurrency").addEventListener("input",()=>{++serial;history=null;el("lcMoreHistory").hidden=true;el("lcHistory").replaceChildren();});\n el("lcRetry").addEventListener',1)
out[p.as_posix()]=s
print(json.dumps(out))
