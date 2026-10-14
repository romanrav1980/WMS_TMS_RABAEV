from pathlib import Path
import json,re
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
p="wiki-raw/wms_admin_ui_reference/customer-orders.js";v=read(p)
start=v.index('  orderEl("orderDetails").textContent = JSON.stringify({');end=v.index('  renderOrderLines();',start)
v=v[:start]+'  renderOrderHeader(orderState.detail);\n'+v[end:]
needle='function renderOrderLines() {';assert v.count(needle)==1
header='''function renderOrderHeader(detail){
  const labels={NEW:"Новый",CREATED:"Создан",PLANNED:"Подготовлен",PICKING:"В отборе",PICKED:"Собран",SHIPPED:"Отгружен",CANCELLED:"Отменён"};
  const fields=[["Заказ",detail.order_no||detail.customer_order_id],["Клиент",detail.customer_name||detail.customer_id],
    ["Дата отгрузки",detail.shipment_date||"Не задана"],["Маршрут",detail.route_id||"Не назначен"],
    ["Ворота",detail.dock_id||"Не назначены"],["Документ",labels[detail.status]||detail.status||"—"]];
  orderEl("orderDetails").replaceChildren(...fields.map(([title,value])=>{
    const box=document.createElement("div"),caption=document.createElement("small"),text=document.createElement("strong");
    box.className="order-metadata-field";caption.textContent=title;text.textContent=String(value);box.append(caption,text);return box;
  }));
}
'''
v=v.replace(needle,header+needle,1)
v+='\nif(window.wmsAdminAuth?.state?.user?.username)orderInit();\n';files[p]=v
p="wiki-raw/wms_admin_ui_reference/customer-orders.html";v=read(p)
v=v.replace('<link rel="stylesheet" href="styles.css?v=20260517-cleanui" />','<link rel="stylesheet" href="styles.css?v=20260517-cleanui" /><link rel="stylesheet" href="order-execution.css?v=20261013-1022" />',1)
v=re.sub(r'<pre([^>]*id="orderDetails"[^>]*)>\s*</pre>',r'<div\1></div>',v,count=1)
v=v.replace('customer-orders.js?v=20260517-cleanui','customer-orders.js?v=20261013-1022')
files[p]=v
print(json.dumps(files,ensure_ascii=True))
