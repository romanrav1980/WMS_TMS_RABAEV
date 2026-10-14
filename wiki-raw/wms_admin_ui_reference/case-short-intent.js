/* Shortage uses the existing SHORT_CREATED journal and its offline_event_id. */
(() => {
 const decimal=value=>String(value??'0').replace(/^0+(?=\d)/,'').replace(/(\.\d*?)0+$/,'$1').replace(/\.$/,'');
 function create(task,line){
  const posted=String(line.picked_qty??'0'),typed=cpTsdEl('cpTsdFactQty').value.trim()||posted;
  if(!/^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(typed)||decimal(typed)!==decimal(posted))
   throw Error('Сначала подтвердите фактически отобранное количество. Сообщение «Нет товара» само не проводит отбор.');
  return {task:task.case_pick_task_id,line:line.case_pick_line_id,route:'short',payload:{picked_qty:posted,
   reason_text:'Нет товара в ячейке',offline_event_id:'CASE.SHORT.UI:'+crypto.randomUUID(),
   resource_id:cpTsd.session?.resource_id||null,resource_session_id:cpTsd.session?.session_id||null,
   equipment_id:cpTsd.session?.equipment_id||null,actor:cpTsdPicker()}};
 }
 const identity=intent=>intent.route==='short'?intent.payload?.offline_event_id:intent.payload?.operation_id;
 const confirms=(intent,result)=>intent.route==='short'?
  result.offline_event_id===identity(intent)&&Number.isSafeInteger(result.case_pick_short_id)&&result.case_pick_short_id>0:
  result.operation_id===identity(intent);
 window.cpCaseShortIntent={create,identity,confirms};
})();
