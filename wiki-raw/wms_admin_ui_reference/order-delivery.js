// Keep the existing delivery projection adjacent to picking; quantities are never inferred from status.
const deliveryPanel=document.getElementById("orderDeliveryPanel");
if(deliveryPanel)document.getElementById("orderExecutionPanel").after(deliveryPanel);
let orderDeliveryGeneration=0;
const deliveryLabels={WAITING_FOR_SHIPMENT:"Ожидает отгрузки",WAITING_FOR_RECEIPT:"Отгруженный товар ожидает приёмки магазином",PARTIALLY_ACCEPTED:"Принято частично",
 RECEIVED_SHIPPED_VOLUME:"Отгруженная часть принята",ACCEPTED_WITH_OPEN_CASE:"Количество принято, разбирательство открыто",NEEDS_OWNER_ALLOCATION:"Требуется распределение по владельцам"};
async function loadOrderDelivery(orderId){
 const target=document.getElementById("orderDeliveryRows"),status=document.getElementById("orderDeliveryStatus");
 const serial=++orderDeliveryGeneration;const scope=orderApiBase()+":"+window.wmsAdminAuth.state.user?.username;
 target.replaceChildren();status.textContent="Загрузка…";
 try {
  const result=await orderRequest("/api/customer-orders/"+orderId+"/delivery");
  if(serial!==orderDeliveryGeneration||orderState.selectedId!==orderId||scope!==orderApiBase()+":"+window.wmsAdminAuth.state.user?.username)return;
  if(Number(result.customer_order_id)!==orderId||!Array.isArray(result.quantities))throw new Error("Ответ не соответствует выбранному заказу.");
  status.textContent=(deliveryLabels[result.delivery_status]||result.delivery_status)+"; неотгруженных исполнений: "+result.unshipped_fulfillments;
  for(const line of result.quantities){
   const tr=document.createElement("tr");
   for(const value of [line.article,line.base_uom,line.shipped,line.accepted,line.missing,line.refused,line.damaged,line.unreceived,line.unattributed,line.confirmed_transport_shortage||"0",line.historical_transport_shortage||"0",line.recovered_transport_quantity||"0"]){
    const td=document.createElement("td");td.textContent=value;tr.append(td);
   }
   target.append(tr);
  }
  document.getElementById("orderDeliveryLineage").replaceChildren(...(result.receipt_lineage||[]).map(row=>{const p=document.createElement("p");p.textContent="Исходная отгрузка "+row.original_load_operation_id+" → окончательная "+row.actual_final_load_operation_id+" · приёмка "+row.receipt_operation_id+" · идентификатор паллеты "+row.lot_uid+(row.original_lot_uid&&row.original_lot_uid!==row.lot_uid?" · исходная паллета "+row.original_lot_uid:"")+(row.historical_transport_shortage&&row.historical_transport_shortage!=="0"?" · транспортная недостача "+row.historical_transport_shortage+" / "+row.transport_shortage_operation_id:"");p.textContent+=(row.is_corrective_receipt?" · повторная доставка найденного груза":"")+(row.recovered_transport_quantity&&row.recovered_transport_quantity!=="0"?" · найдено "+row.recovered_transport_quantity:"");return p;}));
  document.getElementById("orderDeliveryCases").textContent=result.open_case_ids.length?"Открытые разбирательства: "+result.open_case_ids.join(", "):"";
  document.getElementById("orderDeliveryOwners").textContent=result.needs_owner_allocation.length?"Частичная приёмка общего листа требует явного распределения по исходным заказам. Принятое количество не распределено автоматически.":"";
 }catch(error){if(serial===orderDeliveryGeneration&&orderState.selectedId===orderId&&scope===orderApiBase()+":"+window.wmsAdminAuth.state.user?.username)status.textContent=error.message;}
}

function resetOrderDelivery(){++orderDeliveryGeneration;document.getElementById("orderDeliveryRows").replaceChildren();document.getElementById("orderDeliveryLineage").replaceChildren();document.getElementById("orderDeliveryStatus").textContent="Выберите заказ";document.getElementById("orderDeliveryCases").textContent="";document.getElementById("orderDeliveryOwners").textContent="";}
window.addEventListener("wms-admin-auth-ready",resetOrderDelivery);
window.addEventListener("wms-order-context-changed",resetOrderDelivery);
