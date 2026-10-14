let orderExecutionGeneration=0;
const orderExecutionLabels={PICKED:"Отбор подтверждён",PARTIAL:"Отобрано частично",PENDING:"Ожидается физический отбор",REQUIRES_UOM:"Проверьте единицы товара",OVER_PICKED:"Превышение отбора — требуется разбор",SHORT_CLOSED:"Отбор закрыт с недостачей",PARTIAL_REFUSED:"Есть недостача; другие строки ещё в работе",CANCELLED:"Все строки отменены; физический факт показан отдельно",RESERVED:"Запас закреплён; физический отбор не подтверждён"};
function resetOrderExecution(){
  orderExecutionGeneration++;
  document.getElementById("orderExecutionRows").replaceChildren();
  document.getElementById("orderExecutionStatus").textContent="Выберите заказ";
}
window.addEventListener("wms-admin-auth-ready",resetOrderExecution);
window.addEventListener("wms-order-context-changed",resetOrderExecution);
async function loadOrderExecution(orderId) {
  const target=document.getElementById("orderExecutionRows"),status=document.getElementById("orderExecutionStatus");
  const serial=++orderExecutionGeneration,scope=orderApiBase()+":"+window.wmsAdminAuth.state.user?.username;
  const current=()=>serial===orderExecutionGeneration&&orderState.selectedId===orderId&&scope===orderApiBase()+":"+window.wmsAdminAuth.state.user?.username;
  target.replaceChildren();status.textContent="Загрузка фактического исполнения…";
  void loadOrderDelivery(orderId);
  try{
    const result=await orderRequest("/api/customer-orders/"+orderId+"/execution");
    if(!current())return;
    status.textContent="Заказ "+(result.order_no||result.customer_order_id)+" · "+(orderExecutionLabels[result.execution_status]||result.execution_status)+" · склад "+result.warehouse_id+" · активных строк "+result.active_line_count+", отменено "+result.cancelled_line_count;
    for(const line of result.lines){
      const tr=document.createElement("tr");
      tr.dataset.executionStatus=line.status;
      const base=line.base_uom||"базовая ед. не определена";
      const quantity=(value,unit)=>value==null?"—":String(value)+" "+unit;
      const state={PICKED:"Подтверждено",OVER_PICKED:"Превышение",CANCELLED:"Отменено",REFUSED:"Недостача",PARTIAL_REFUSED:"Частично / недостача",RESERVED:"Резерв",WAIT_STOCK:"Нет запаса",PARTIAL:"Частично",REQUIRES_UOM:"Единицы не согласованы"}[line.status]||line.status;
      for(const value of[line.line_no,line.articul,quantity(line.requested_quantity,line.requested_uom||line.base_uom||line.unit_code),
        quantity(line.picked_quantity,base),quantity(line.hard_quantity,base),
        (line.status==="CANCELLED"||line.row_status==="CANCELLED")?"— (отменено)":quantity(line.remaining_quantity,base),state,line.reason]){
        const td=document.createElement("td");td.textContent=value??"—";tr.append(td);
      }
      target.append(tr);
    }
  }catch(error){if(current())status.textContent=error.message;}
}
