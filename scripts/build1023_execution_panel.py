from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
p="wiki-raw/wms_admin_ui_reference/customer-orders.html";v=read(p)
start=v.index('              <h3 id="orderExecution">');end=v.index('            <details data-permission=',start)
block=v[start:end]
v=v[:start]+v[end:]
block=block.replace('<h3 id="orderExecution">Фактическое исполнение · <span id="orderExecutionStatus">—</span></h3>','<header><h2 id="orderExecution">Фактическое исполнение заказа</h2><p id="orderExecutionStatus" role="status">Выберите заказ</p></header>',1)
block=block.replace('<table class="rights-table">','<div class="rights-table-wrap"><table class="rights-table">',1).replace('</tbody></table>','</tbody></table></div>',1)
needle='      <article class="panel" data-permission="stock_reservation_view">'
assert v.count(needle)==1
v=v.replace(needle,'<article id="orderExecutionPanel" class="panel" data-permission="customer_fulfillment_view">\n'+block+'</article>\n'+needle,1)
v=v.replace('order-execution.css?v=20261013-1022','order-execution.css?v=20261013-1023').replace('order-execution.js?v=20261013-1021','order-execution.js?v=20261013-1023')
files[p]=v
p="wiki-raw/wms_admin_ui_reference/order-execution.js";v=read(p).replace('status.textContent=(orderExecutionLabels[result.execution_status]','status.textContent="Заказ "+(result.order_no||result.customer_order_id)+" · "+(orderExecutionLabels[result.execution_status]',1);files[p]=v
p="wiki-raw/wms_admin_ui_reference/order-execution.css";files[p]=read(p)+'\n#orderExecutionPanel{margin:20px 24px;padding:20px}#orderExecutionPanel header{display:block;padding:0 0 12px}#orderExecutionPanel h2{margin:0 0 10px}#orderExecutionStatus{font-size:14px;line-height:1.6;color:#52667f}#orderExecutionPanel .rights-table{width:100%}#orderExecutionPanel .rights-table th{white-space:normal}#orderExecutionRows td:last-child{white-space:normal;min-width:220px;max-width:420px}#orderExecutionPanel .rights-table-wrap{border:1px solid #e1eaf4;border-radius:10px}\n'
print(json.dumps(files,ensure_ascii=True))
