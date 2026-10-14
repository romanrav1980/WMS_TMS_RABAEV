from pathlib import Path
import json
p="wiki-raw/wms_admin_ui_reference/receiving.js";t=Path(p).read_text(encoding="utf-8")
needle="tr.dataset.receiptSelectable='true';tr.tabIndex=0;tr.title='Выбрать строку для приёмки';tr.addEventListener('click',onClick);"
replacement=needle+"""
      const action=document.createElement('td'),button=document.createElement('button');
      button.type='button';button.textContent='Выбрать';button.className='receipt-select-button';
      button.addEventListener('click',event=>{event.stopPropagation();onClick();});
      action.appendChild(button);tr.appendChild(action);"""
assert needle in t;t=t.replace(needle,replacement)
needle="state.line=line;state.policy=null;el('receiptConfirm').disabled=true;"
assert needle in t;t=t.replace(needle,needle+"""
    window.dispatchEvent(new CustomEvent("wms-receipt-line-selected",{detail:line}));
    for(const row of el('receiptLines').children)row.dataset.selected=row.firstElementChild?.textContent===line.line_number?'true':'false';
    message('Загрузка правил приёмки для строки '+line.line_number+'…');""")
t=t.replace('      window.dispatchEvent(new CustomEvent("wms-receipt-line-selected", {detail:line}));','')
t=t.replace("el('receiptConfirm').disabled=!state.line||!state.policy||!window.wmsAdminAuth.hasPermission('warehouse_receipt_confirm');","el('receiptConfirm').disabled=!state.line||!state.policy||Number(state.line.remaining_qty)<=0||!window.wmsAdminAuth.hasPermission('warehouse_receipt_confirm');")
files={p:t}
p="wiki-raw/wms_admin_ui_reference/receiving.html";t=Path(p).read_text(encoding="utf-8").replace('v=20261013-894','v=20261013-912')
t=t.replace('<th>Зона приёмки</th>','<th>Зона приёмки</th><th>Выбор</th>').replace('<th>Предложено паллет</th>','<th>Предложено паллет</th><th>Выбор</th>')
files[p]=t
p="wiki-raw/wms_admin_ui_reference/receiving.css";files[p]=Path(p).read_text(encoding="utf-8")+"\n.receiving-page tr[data-selected=true]{background:#e8f1ff;box-shadow:inset 3px 0 #2874dc}.receipt-select-button{white-space:nowrap}\n"
print(json.dumps(files,ensure_ascii=True))
