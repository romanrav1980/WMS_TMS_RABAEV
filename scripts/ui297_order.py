from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
assert 'id="orderDeliveryRows"'not in s
panel='<section class="panel" data-permission="customer_fulfillment_view"><h2>Доставка исходной отгрузки</h2><p id="orderDeliveryStatus">Выберите заказ</p><table class="rights-table"><thead><tr><th>Товар</th><th>Ед.</th><th>Отгружено</th><th>Принято магазином</th><th>Недостача магазина</th><th>Отказ</th><th>Повреждено</th><th>Не получено из исходной отгрузки</th><th>Не распределено по владельцам</th><th>Подтверждённая транспортная недостача</th></tr></thead><tbody id="orderDeliveryRows"></tbody></table><p>Транспортная недостача входит в неполученное количество. Она не означает приёмку товара и не списывает складской запас повторно.</p><p id="orderDeliveryCases"></p><p id="orderDeliveryOwners"></p><div id="orderDeliveryLineage"></div></section>'
s=s.replace('</main>',panel+'</main>',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/order-delivery.js");s=p.read_text(encoding="utf-8")
s=s.replace('line.unreceived,line.unattributed]','line.unreceived,line.unattributed,line.confirmed_transport_shortage||"0"]',1)
s=s.replace('  document.getElementById("orderDeliveryCases")','''  document.getElementById("orderDeliveryLineage").replaceChildren(...(result.receipt_lineage||[]).map(row=>{const p=document.createElement("p");p.textContent="Исходная отгрузка "+row.original_load_operation_id+" → окончательная "+row.actual_final_load_operation_id+" · приёмка "+row.receipt_operation_id+" · идентификатор паллеты "+row.lot_uid+(row.original_lot_uid&&row.original_lot_uid!==row.lot_uid?" · исходная паллета "+row.original_lot_uid:"")+(row.confirmed_transport_shortage&&row.confirmed_transport_shortage!=="0"?" · транспортная недостача "+row.confirmed_transport_shortage+" / "+row.transport_shortage_operation_id:"");return p;}));
  document.getElementById("orderDeliveryCases")''',1)
# Clear projection on identity/API changes and use request generation for same-order stale response.
s='let orderDeliveryGeneration=0;\n'+s
s=s.replace(' const scope=orderApiBase()', ' const serial=++orderDeliveryGeneration;const scope=orderApiBase()',1)
s=s.replace('if(orderState.selectedId!==orderId||scope!==','if(serial!==orderDeliveryGeneration||orderState.selectedId!==orderId||scope!==',1)
s+='''\nwindow.addEventListener("wms-admin-auth-ready",()=>{++orderDeliveryGeneration;document.getElementById("orderDeliveryRows").replaceChildren();document.getElementById("orderDeliveryLineage").replaceChildren();document.getElementById("orderDeliveryStatus").textContent="Выберите заказ";document.getElementById("orderDeliveryCases").textContent="";document.getElementById("orderDeliveryOwners").textContent="";});
'''
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
