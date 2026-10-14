(() => {
  const el=id=>document.getElementById(id);
  let orderId=null,epoch=0,cursor=null;
  const scope=()=>JSON.stringify([window.wmsAdminAuth.state.apiBase,window.wmsAdminAuth.state.user?.username]);
  const message=text=>{el('receiptHistoryMessage').textContent=text;};
  function reset(){orderId=null;epoch++;cursor=null;el('receiptHistoryRows').replaceChildren();el('receiptHistoryNext').disabled=true;el('receiptHistoryRefresh').disabled=true;message('Выберите основание поставки.');}
  async function load(id,after=null){
    const token=++epoch,identity=scope();orderId=id;cursor=null;
    el('receiptHistoryNext').disabled=true;el('receiptHistoryRefresh').disabled=true;
    el('receiptHistoryRows').replaceChildren();message('Загрузка принятых паллет…');
    const current=()=>token===epoch&&orderId===id&&identity===scope();
    try{
      const base=(window.wmsAdminAuth.state.apiBase||'http://127.0.0.1:8088').replace(/\/$/,'');
      const path='/api/integrations/sap/supply-orders/'+encodeURIComponent(id)+'/receipt-history?limit=50'+(after?'&after_operation='+encodeURIComponent(after):'');
      const response=await fetch(base+path,{headers:window.wmsAdminAuth.headers()});
      const result=await response.json();
      if(!current())throw new Error('Основание или пользователь изменились. Перечитайте историю.');
      if(!response.ok)throw new Error(typeof result.detail==='string'?result.detail:JSON.stringify(result.detail||result));
      if(result.source?.order_id!==id||result.consistent_snapshot!==true||!Array.isArray(result.receipts))throw new Error('Не удалось подтвердить текущую историю поставки.');
      for(const receipt of result.receipts){
        const row=document.createElement('tr');
        for(const value of[receipt.line_number,receipt.pallet_identifier,receipt.accepted_quantity+' '+receipt.base_uom,receipt.current_warehouse_quantity,receipt.current_warehouse_hard,receipt.supplier_batch,receipt.operation_id]){
          const cell=document.createElement('td');cell.textContent=value??'—';row.appendChild(cell);
        }
        const task=document.createElement('td');
        if(Number.isSafeInteger(receipt.task_id)&&receipt.task_id>0){const link=document.createElement('a');link.href='warehouse-tasks.html?task_id='+receipt.task_id;link.textContent='№'+receipt.task_id+' · '+(receipt.task_status||'Статус не определён');task.appendChild(link);}
        else task.textContent='Задание не определено';
        row.appendChild(task);el('receiptHistoryRows').appendChild(row);
      }
      cursor=result.has_more?result.next_cursor:null;el('receiptHistoryNext').disabled=!cursor;
      message(result.receipts.length?'Показано '+result.receipts.length+' паллет. Принятое количество — исторический факт; остаток и резерв показаны только на складе '+result.warehouse_id+'.':'На этой странице приёмок нет.');
      return result;
    }catch(error){if(current())message(error.message);throw error;}
    finally{if(current())el('receiptHistoryRefresh').disabled=false;}
  }
  window.addEventListener('wms-receipt-selected',event=>{void load(event.detail.order_id).catch(()=>{});});
  window.addEventListener('wms-receipt-selection-reset',reset);
  window.addEventListener('wms-admin-auth-ready',reset);
  el('receiptHistoryRefresh').addEventListener('click',()=>{if(orderId)void load(orderId).catch(()=>{});});
  el('receiptHistoryNext').addEventListener('click',()=>{if(orderId&&cursor)void load(orderId,cursor).catch(()=>{});});
  window.wmsReceiptHistory={load};reset();
})();