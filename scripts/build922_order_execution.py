from pathlib import Path
import json
files={}
p="api/wms_api_server/app/modules/fulfillment/infrastructure/execution_progress.py";t=Path(p).read_text(encoding="utf-8")
t=t.replace('from ..domain.execution_progress import line_progress','from ..domain.execution_progress import line_progress\nfrom ....transaction_gateway import TransactionGateway\nfrom .store_source_scope import assert_store_scope')
needle='    def get(self, order_id: int) -> dict:\n'
assert needle in t
t=t.replace(needle,'''    def get(self, order_id: int, actor: str) -> dict:
        if order_id < 1:
            raise ValueError("Positive order ID required")
        with self.gateway.transaction("Physical order execution READ ONLY current warehouse") as cursor:
            if not getattr(self.gateway,"transaction_bound",False):
                cursor.execute("set transaction read only")
            cursor.execute("select WARE_ID from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=:order_id",order_id=order_id)
            row = cursor.fetchone()
            if row is None:
                raise LookupError("Customer order not found")
            assert_store_scope(cursor,actor,"customer_fulfillment_view",row[0])
            result = OrderExecution(TransactionGateway(cursor))._snapshot(order_id)
            result.update(warehouse_id=row[0],consistent_snapshot=True)
            return result

    def _snapshot(self, order_id: int) -> dict:
''')
files[p]=t
p="api/wms_api_server/app/modules/fulfillment/api/execution_routes.py";t=Path(p).read_text(encoding="utf-8").replace('def get(self, order_id: int)','def get(self, order_id: int, actor: str)').replace('return service.get(order_id)','return service.get(order_id, _user.username)')
t=t.replace('    except LookupError as exc:','    except PermissionError as exc:\n        raise HTTPException(403,str(exc)) from exc\n    except LookupError as exc:')
files[p]=t
files["wiki-raw/wms_admin_ui_reference/order-execution.js"]='''let orderExecutionGeneration=0;
const orderExecutionLabels={PICKED:"Отбор подтверждён",PARTIAL:"Отобрано частично",PENDING:"Ожидается физический отбор",REQUIRES_UOM:"Проверьте единицы товара"};
function resetOrderExecution(){
  orderExecutionGeneration++;
  document.getElementById("orderExecutionRows").replaceChildren();
  document.getElementById("orderExecutionStatus").textContent="Выберите заказ";
}
window.addEventListener("wms-admin-auth-ready",resetOrderExecution);
async function loadOrderExecution(orderId) {
  const target=document.getElementById("orderExecutionRows"),status=document.getElementById("orderExecutionStatus");
  const serial=++orderExecutionGeneration,scope=orderApiBase()+":"+window.wmsAdminAuth.state.user?.username;
  const current=()=>serial===orderExecutionGeneration&&orderState.selectedId===orderId&&scope===orderApiBase()+":"+window.wmsAdminAuth.state.user?.username;
  target.replaceChildren();status.textContent="Загрузка фактического исполнения…";
  void loadOrderDelivery(orderId);
  try{
    const result=await orderRequest("/api/customer-orders/"+orderId+"/execution");
    if(!current())return;
    status.textContent=(orderExecutionLabels[result.execution_status]||result.execution_status)+" · склад "+result.warehouse_id;
    for(const line of result.lines){
      const tr=document.createElement("tr");
      for(const value of[line.line_no,line.articul,line.requested_quantity,line.picked_quantity,line.remaining_quantity,line.base_uom||line.unit_code,line.reason]){
        const td=document.createElement("td");td.textContent=value??"—";tr.append(td);
      }
      target.append(tr);
    }
  }catch(error){if(current())status.textContent=error.message;}
}
'''
p="wiki-raw/wms_admin_ui_reference/customer-orders.html";t=Path(p).read_text(encoding="utf-8").replace('src="order-execution.js"','src="order-execution.js?v=20261013-922"');files[p]=t
print(json.dumps(files,ensure_ascii=True))
