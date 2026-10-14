/* Authoritative result of the existing return receipt, followed by existing putaway. */
window.wmsReturnReceiptResult=(()=>{
 const canonical=value=>String(value).replace(/^0+(?=\d)/,'').replace(/(\.\d*?)0+$/,'$1').replace(/\.$/,'');
 function validate(result,body){
  if(result?.operation_id!==body.operation_id||result.pickup_operation_id!==body.pickup_operation_id||result.status!=='RECEIVED_PENDING_PLACEMENT'||
   !Number.isSafeInteger(result.warehouse_id)||result.warehouse_id<1||typeof result.quantity!=='string'||!/^\d+(\.\d+)?$/.test(result.quantity)||
   canonical(result.quantity)!==canonical(body.quantity)||result.base_uom!==body.base_uom||!result.receiving_document_id||typeof result.cell!=='string'||!result.cell)
   throw Error('Ответ не подтверждает исходную приёмку возврата. Повторите сохранённую операцию; новое размещение не открыто.');
  return result;
 }
 function show(host,result){
  const title=document.createElement('h2'),text=document.createElement('p'),link=document.createElement('a'),note=document.createElement('p');
  title.textContent='Возврат принят складом';text.textContent='Документ '+result.receiving_document_id+' · '+result.quantity+' '+result.base_uom+' · ячейка '+result.cell+' · операция '+result.operation_id;
  link.href='store-return-putaway.html?'+new URLSearchParams({warehouse_id:String(result.warehouse_id),receipt_operation_id:result.operation_id});link.textContent='Перейти к размещению этого возврата';
  note.textContent='Откроется существующая очередь принятого склада с выбранной приёмкой. Создание и выполнение задания — отдельные действия; сканы не подставляются.';
  host.replaceChildren(title,text,link,note);host.hidden=false;
 }
 return {validate,show,
  validateTask(result,body){if(result?.operation_id!==body.operation_id||result.receipt_operation_id!==body.receipt_operation_id||!Number.isSafeInteger(result.task_id)||result.task_id<1)throw Error('Ответ не подтверждает исходное задание. Повторите сохранённый запрос.');},
  showTask(host,result){const a=document.createElement('a');a.href='warehouse-tasks.html?task_id='+encodeURIComponent(result.task_id);a.textContent='Открыть созданное задание '+result.task_id;host.replaceChildren(a);}
 };
})();