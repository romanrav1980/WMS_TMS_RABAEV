from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/st-deferral.js");t=p.read_text(encoding="utf-8")
anchor=" function pending(){"
assert anchor in t
t=t.replace(anchor,''' function showSummary(v){
  const panel=el('sdOverview');panel.hidden=!v;
  if(!v){panel.replaceChildren();return;}
  const prepared=v.physical_preparation,waiting=prepared&&!prepared.physical_move_required;
  const cards=[['Текущий рейс',String(v.source_trip_id)],['Дата отгрузки',v.source_trip.shipment_date],
   ['Паллет в СТ',String(v.members.length)],['Состояние товара',prepared?(waiting?'В ячейке ожидания':'Отобран, требуется перемещение'):'Отбор ещё не завершён']];
  panel.replaceChildren(...cards.map(([label,value],index)=>{
   const card=document.createElement('div');card.className='summary-card'+(index===3&&waiting?' is-ready':'');
   const title=document.createElement('span'),text=document.createElement('strong');title.textContent=label;text.textContent=value;
   card.append(title,text);return card;
  }));
 }
'''+anchor)
t=t.replace("context=null;controls();","context=null;showSummary(null);controls();")
t=t.replace("return;context=v;","return;context=v;showSummary(v);")
t=t.replace("localStorage.removeItem(key());context=null;","localStorage.removeItem(key());context=null;showSummary(null);")
t=t.replace("epoch++;context=null;next=null;","epoch++;context=null;showSummary(null);next=null;")
out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.css");t=p.read_text(encoding="utf-8")
out[str(p)]=t+"\n.day-page [hidden]{display:none!important}\n"
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");t=p.read_text(encoding="utf-8")
t=t.replace('id="stTransfer" data-permission="transport_dispatch_edit"','id="stTransfer" data-permission="transport_dispatch_view"')
t=t.replace('<button id="sdSave"','<button data-permission="transport_dispatch_edit" id="sdSave"')
t=t.replace('<button id="sdRetry"','<button data-permission="transport_dispatch_edit" id="sdRetry"')
t=t.replace('id="waitingArea">','id="waitingArea" data-permission="warehouse_task_view">')
t=t.replace('<button id="swPlan"','<button data-permission="warehouse_task_edit" id="swPlan"')
t=t.replace('<button id="swRetry"','<button data-permission="warehouse_task_edit" id="swRetry"')
out[str(p)]=t
print(json.dumps(out,ensure_ascii=True))
