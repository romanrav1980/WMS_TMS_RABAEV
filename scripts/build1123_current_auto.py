from pathlib import Path
import json
f={}
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py");s=p.read_text(encoding="utf-8").replace('"pallet_statistics": layout["pallet_statistics"], "stock_changed": False}', '"pallet_statistics": layout["pallet_statistics"], "planned_pallets": layout["pallets"], "stock_changed": False}');f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sap-automatic-preparation.js");s=p.read_text(encoding="utf-8")
needle=" async function recover(){"
read=''' async function readCurrent(){
  if(busy)return;const who=identity(),token=++epoch;proposal=null;busy=true;controls();
  try{
   const order=Number(el('sapAutoOrder').value);
   if(!Number.isSafeInteger(order)||order<1)throw Error('Укажите исходный заказ.');
   const source=await api(String(order),null,'GET');
   if(who!==identity()||token!==epoch)return;
   if(source.customer_order_id!==order)throw Error('Исходный заказ не подтверждён.');
   const saved=source.preparation_json;
   el('sapAutoRows').replaceChildren();
   if(!saved){message('СТ ещё не подготовлена. Укажите пределы и рассчитайте состав.');return;}
   const statistics=saved.pallet_statistics||[];
   el('sapAutoRows').replaceChildren(...statistics.flatMap((stat,i)=>{
    const lines=saved.planned_pallets?.[i]?.lines||[{articul:'Состав в карточке заказа',quantity:'—'}];
    return lines.map(line=>{const tr=document.createElement('tr');tr.append(td(saved.pallet_identifiers[i]),td(stat.assembly_group),
     td(line.articul),td(line.quantity),td(stat.goods_weight_kg),td(stat.goods_volume_m3));return tr;});
   }));
   message('Уже подготовлена СТ '+saved.st_number+', мест: '+saved.pallet_identifiers.length+'. Сохранённый план; физический состав смотрите в карточке грузового места.');
  }catch(e){if(who===identity()&&token===epoch)message(e.message);}
  finally{busy=false;controls();}
 }
'''
s=s.replace(needle,read+needle)
s=s.replace("el('sapAutoRead').addEventListener('click',preview);","el('sapAutoCurrent').addEventListener('click',readCurrent);el('sapAutoRead').addEventListener('click',preview);")
s=s.replace("  el('sapAutoRead').disabled=busy;","  el('sapAutoRead').disabled=busy;el('sapAutoCurrent').disabled=busy;")
s=s.replace("requestAnimationFrame(()=>el('sapAutoPreparation').scrollIntoView({block:'start'}))","requestAnimationFrame(()=>{el('sapAutoPreparation').scrollIntoView({block:'start'});if(linked)readCurrent();})")
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8").replace('<button id="sapAutoRead">','<button id="sapAutoCurrent">Прочитать текущую СТ</button>\n<button id="sapAutoRead">')
s=s.replace('sap-automatic-preparation.js?v=20261013-1121','sap-automatic-preparation.js?v=20261013-1123').replace('sap-automatic-preparation.css?v=20261013-1121','sap-automatic-preparation.css?v=20261013-1123');f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sap-automatic-preparation.css");s=p.read_text(encoding="utf-8")
s+="""\n#sapAutoPreparation.panel{padding:24px;margin:20px 0;background:white;border-radius:12px;box-shadow:0 3px 14px #172c5010}
#sapAutoPreparation h2{font-size:22px;margin:0 0 12px;color:#183450}
#sapAutoPreparation input{padding:10px 12px;border:1px solid #cdd6e2;background:#fafcff;font-size:15px}
#sapAutoPreparation button{padding:10px 16px;border:1px solid #cdd6e2;border-radius:8px;background:#f3f7fd;color:#254d79;cursor:pointer}
#sapAutoPreparation #sapAutoRead,#sapAutoPreparation #sapAutoSave{background:#2277ee;color:white;border-color:#2277ee}
#sapAutoPreparation button:disabled{opacity:.45;cursor:default}
#sapAutoPreparation table th{background:#f4f7fc;color:#58718e;padding:12px;text-align:left}
#sapAutoPreparation table td{padding:12px;border-bottom:1px solid #edf0f4}
#sapAutoMessage:not(:empty){padding:14px;background:#eef5ff;color:#183f6f;border-radius:8px}
"""
f[str(p)]=s
print(json.dumps(f,ensure_ascii=True))
