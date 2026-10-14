from pathlib import Path
import json
p="wiki-raw/wms_admin_ui_reference/receiving.js";t=Path(p).read_text(encoding="utf-8")
a=t.index('  function row(');b=t.index('  const sourceDocument',a)
t=t[:a]+'''  function row(values,selection) {
    const tr=document.createElement('tr');
    for(const value of values){const td=document.createElement('td');td.textContent=String(value??'');tr.appendChild(td);}
    if(selection){
      tr.dataset.receiptSelectable='true';tr.dataset.orderId=selection.order_id;
      if(selection.line_number!=null){tr.dataset.lineNumber=selection.line_number;tr.dataset.articul=selection.articul;}
      tr.tabIndex=0;tr.title=selection.line_number!=null?'Выбрать товарную позицию':'Выбрать заказ SAP';
      const action=document.createElement('td'),button=document.createElement('button');
      button.type='button';button.textContent='Выбрать';button.className='receipt-select-button';
      action.appendChild(button);tr.appendChild(action);
    }
    return tr;
  }
  function bindSelection(id){
    const container=el(id);
    const select=event=>{
      const selected=event.target?.closest('tr[data-receipt-selectable]');
      if(!selected||!container.contains(selected))return;
      if(event.type==='keydown'){
        if(event.key!=='Enter'&&event.key!==' ')return;
        event.preventDefault();
      }
      const data=selected.dataset;
      if(data.lineNumber!=null)void selectLine({line_number:data.lineNumber,articul:data.articul},data.orderId);
      else void selectOrder(data.orderId);
    };
    container.addEventListener('click',select);container.addEventListener('keydown',select);
  }
  bindSelection('receiptOrders');bindSelection('receiptLines');
'''+t[b:]
old='()=>selectOrder(o.order_id))';assert old in t;t=t.replace(old,'{order_id:o.order_id})')
old='()=>selectLine(l,order.order_id))';assert old in t;t=t.replace(old,'{order_id:order.order_id,line_number:l.line_number,articul:l.articul})')
files={p:t}
p="wiki-raw/wms_admin_ui_reference/receiving.html";t=Path(p).read_text(encoding="utf-8").replace('v=20261013-944','v=20261013-946');files[p]=t
print(json.dumps(files,ensure_ascii=True))
