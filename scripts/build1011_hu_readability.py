from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
p="wiki-raw/wms_admin_ui_reference/warehouse-hus.js";v=read(p)
v=v.replace('  function render(data){','''  const measureText=value=>String(value??"—").replace(/^[.]/,"0.").replace(".",",");
  const typeText=value=>({"ROLL_CAGE":"Ролл-кейдж","PALLET":"Паллета","BOX":"Коробка","BAG":"Мешок","STOCK":"Товарная партия","CASE":"CASE","CONTAINER":"Контейнер"}[value]||value);
  function render(data){''',1)
v=v.replace('[node.depth,node.uid,node.type||node.kind,node.article||"",node.quantity??"",node.hard_quantity??"",node.base_uom||"",node.cell].forEach(value=>{\n        const td=document.createElement("td");td.textContent=String(value);tr.append(td);','''[node.depth,node.uid,typeText(node.type||node.kind),node.article||"",node.quantity??"",node.hard_quantity??"",node.base_uom||"",node.cell].forEach((value,index)=>{
        const td=document.createElement("td");td.textContent=String(value);
        if(index===1&&node.kind==="CASE"&&node.uid!==data.root&&node.sscc){
          const link=document.createElement("a");link.textContent=String(value);link.href="warehouse-hus.html?identifier="+encodeURIComponent(node.sscc)+"#huComposition";td.replaceChildren(link);
        }
        tr.append(td);''',1)
v=v.replace('; подтверждённая масса полного места отсутствует','; расчётная масса состава отсутствует').replace('; масса: ','; расчётная масса состава: ')
v=v.replace('(p.gross_weight_kg??"—")+" кг, "+(p.bounding_volume_m3??"—")','measureText(p.gross_weight_kg)+" кг, "+measureText(p.bounding_volume_m3)')
files[p]=v
p="wiki-raw/wms_admin_ui_reference/warehouse-hus.html";files[p]=read(p).replace('<main class="workspace">','<main class="workspace hu-workspace">',1).replace('warehouse-hus.js?v=20261013-1007','warehouse-hus.js?v=20261013-1011').replace('warehouse-hus.css?v=20261013-1007','warehouse-hus.css?v=20261013-1011')
p="wiki-raw/wms_admin_ui_reference/warehouse-hus.css";files[p]=read(p)+"\n.hu-workspace>.topbar button{padding:9px 14px;border:1px solid #d9e1ec;border-radius:9px;background:white;color:#44546b;cursor:pointer}\n"
print(json.dumps(files,ensure_ascii=True))
