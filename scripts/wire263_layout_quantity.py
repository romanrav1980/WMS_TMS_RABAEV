from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/receiving-layout.js");s=p.read_text(encoding="utf-8").replace('        return row;','''        const td=document.createElement('td'),button=document.createElement('button');
        button.type='button';button.textContent='Использовать количество';
        button.addEventListener('click',()=>window.dispatchEvent(new CustomEvent('wms-receipt-layout-quantity',{
          detail:{order_id:result.order_id,line_number:result.line_number,quantity,source_signature:result.source_signature},
        })));
        td.appendChild(button);row.appendChild(td);return row;''')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/receiving.html");s=p.read_text(encoding="utf-8").replace('<th>Примечание</th></tr></thead><tbody id="receiptLayoutRows">','<th>Примечание</th><th>Приёмка</th></tr></thead><tbody id="receiptLayoutRows">');out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/receiving.js");s=p.read_text(encoding="utf-8").replace("  function rememberOperation(map,id){",'''  window.addEventListener('wms-receipt-layout-quantity',event=>{
    try{
      const value=event.detail;
      if(!state.order||!state.line||value.order_id!==state.order.order_id||value.line_number!==state.line.line_number)
        throw new Error('Выберите актуальные заказ и строку, затем перечитайте предложение.');
      if(state.busy||state.label||state.units.size||state.aggregations.length)
        throw new Error('Количество из предложения выбирается до этикетки и сканирования кодов.');
      const pending=window.wmsReceiptIntent.pending();
      if(pending.some(v=>v.body.operation_id===state.operation||v.body.sscc===el('receiptSscc').value.trim()))
        throw new Error('Сначала повторите исходный неподтверждённый запрос этой паллеты.');
      el('receiptQuantity').value=value.quantity;
      message('Количество выбранной паллеты: '+value.quantity+'. Укажите фактические партию, срок и идентификатор; подтвердите приёмку после сканирования.');
    }catch(error){message(error.message);}
  });
  function rememberOperation(map,id){''')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
