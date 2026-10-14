from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
s=s.replace('<section class="panel" data-permission="pick_plan_view"><h2>Складское обеспечение выбранного заказа</h2>','<section class="panel order-picking-panel" id="orderPickingPanel" data-permission="pick_plan_view"><h2>Складское обеспечение выбранного заказа</h2>')
needle='<a id="orderPickWaves"'
assert s.count(needle)==1
s=s.replace(needle,'<a id="orderPickReceiving" hidden data-permission="sap_supply_view" title="Открыть основания SAP для приёмки на склад этого заказа. Сам заказ клиента не является основанием приёмки.">Открыть приёмку склада →</a>\n'+needle)
s=s.replace('</head>','<link rel="stylesheet" href="order-picking-workspace.css"></head>')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/order-picking-workspace.js");s=p.read_text(encoding="utf-8")
s=s.replace('function controls(){','function controls(){el("orderPickReceiving").hidden=!order||!Number.isSafeInteger(order.ware_id);')
needle='  el("orderPickWaves").href='
assert s.count(needle)==1
s=s.replace(needle,'  el("orderPickReceiving").href="receiving.html?warehouse_id="+encodeURIComponent(detail.ware_id);\n'+needle)
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/receiving.js");s=p.read_text(encoding="utf-8")
needle='  const sourceOrder=sourceQuery.get'
assert s.count(needle)==1
s=s.replace(needle,'''  const linkedWarehouse=sourceQuery.get('warehouse_id');
  if(linkedWarehouse&&/^[1-9][0-9]*$/.test(linkedWarehouse)&&Number.isSafeInteger(Number(linkedWarehouse)))
    el('receiptWarehouse').value=linkedWarehouse;
'''+needle)
out[str(p)]=s
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");plan=json.loads(p.read_text(encoding="utf-8"))
def deadline(obj):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if k=="deadlineMoscow":obj[k]="2026-10-14T18:45:00+03:00"
   else:deadline(v)
 elif isinstance(obj,list):
  for v in obj:deadline(v)
deadline(plan);out[str(p)]=json.dumps(plan,ensure_ascii=False,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
