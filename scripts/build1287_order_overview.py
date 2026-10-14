from pathlib import Path
import json
files={}
root=Path("api/wms_api_server/app/modules")
p=root/"fulfillment/public.py";files[str(p)]=p.read_text(encoding="utf-8")+"\n# Shared source-authority read boundary; native policy remains authoritative.\nfrom .infrastructure.store_source_scope import assert_store_scope as assert_customer_order_warehouse\n"
p=root/"delivery/contracts_orders.py";files[str(p)]=p.read_text(encoding="utf-8").replace("def get(self,order_id: int)","def get(self,order_id: int,actor: str)")
p=root/"delivery/infrastructure/order_delivery.py";s=p.read_text(encoding="utf-8").replace("from ..domain.order_delivery import project_delivery","from ..domain.order_delivery import project_delivery\nfrom ...fulfillment.public import assert_customer_order_warehouse")
s=s.replace("def get(self,order_id: int)","def get(self,order_id: int,actor: str)")
s=s.replace("select ORDER_NO,STATUS from RRL_CUSTOMER_ORDER","select ORDER_NO,STATUS,WARE_ID from RRL_CUSTOMER_ORDER")
s=s.replace('raise LookupError("Customer order not found")','raise LookupError("Customer order not found")\n            assert_customer_order_warehouse(q,actor,"customer_fulfillment_view",header[2])')
files[str(p)]=s
p=root/"delivery/api/order_delivery_routes.py";s=p.read_text(encoding="utf-8").replace("return service.get(order_id)","return service.get(order_id,user.username)").replace("except LookupError as exc:","except PermissionError as exc:\n        raise HTTPException(403,str(exc)) from exc\n    except LookupError as exc:")
files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
s=s.replace('id="orderExecution">Фактическое исполнение заказа','id="orderExecution">Фактический отбор заказа')
s=s.replace("<th>Подтверждено</th><th>Действующий резерв</th><th>Осталось</th>","<th>Отобрано</th><th>Действующий резерв</th><th>Осталось отобрать</th>")
s=s.replace('<section class="panel" data-permission="customer_fulfillment_view"><h2>Доставка исходной отгрузки</h2>','<section id="orderDeliveryPanel" class="panel" data-permission="customer_fulfillment_view"><h2>Отгрузка и приёмка заказа</h2>')
s=s.replace('order-delivery.js?v=20261013-1021','order-delivery.js?v=20261014-1287')
files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/order-delivery.js");s=p.read_text(encoding="utf-8")
s='// Keep the existing delivery projection adjacent to picking; quantities are never inferred from status.\nconst deliveryPanel=document.getElementById("orderDeliveryPanel");\nif(deliveryPanel)document.getElementById("orderExecutionPanel").after(deliveryPanel);\n'+s
s=s.replace('status.textContent=(deliveryLabels[result.delivery_status]', 'if(Number(result.customer_order_id)!==orderId||!Array.isArray(result.quantities))throw new Error("Ответ не соответствует выбранному заказу.");\n  status.textContent=(deliveryLabels[result.delivery_status]')
s=s.replace('WAITING_FOR_RECEIPT:"Ожидает приёмки"','WAITING_FOR_RECEIPT:"Отгруженный товар ожидает приёмки магазином"')
files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/order-execution.css");files[str(p)]=p.read_text(encoding="utf-8")+'\n#orderDeliveryPanel{display:block;overflow-x:auto;border-left:4px solid #2377eb}\n#orderDeliveryStatus{padding:12px;background:#eff6ff;border-radius:10px;line-height:1.5}\n#orderDeliveryPanel .rights-table{min-width:1100px}\n'
print(json.dumps(files,ensure_ascii=True))
