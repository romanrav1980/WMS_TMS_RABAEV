import json
from pathlib import Path
files={}
path=Path("wiki-raw/wms_admin_ui_reference/order-picking-workspace.js")
text=path.read_text(encoding="utf-8")
text=text.replace('for(const value of[p.pick_plan_id,p.status,','for(const value of[p.pick_plan_id,({NO_STOCK:"Ожидается товар",PLANNED_FULL:"Обеспечен полностью",PLANNED_PARTIAL:"Обеспечен частично",CANCELLED:"Отменён",DRAFT:"Подготовка"})[p.status]||p.status,',1)
needle='   el("orderPickRows").append(tr);'
change='''   const action=document.createElement("td");
   if(p.status==="NO_STOCK"&&Number(p.task_count)===0&&Number(p.active_reservation_count)===0&&orderCan("pick_plan_cancel")){
    const button=document.createElement("button");button.textContent="Отменить пустой план";button.title="Отменить план без выданных заданий и резервов, чтобы после поступления товара пересчитать обеспечение.";
    button.addEventListener("click",()=>cancelEmpty(p).catch(e=>say(e.message)));action.append(button);
   }
   tr.append(action);
   el("orderPickRows").append(tr);'''
assert needle in text;text=text.replace(needle,change,1)
needle=' async function archive(){'
change=''' async function cancelEmpty(plan){
  if(busy||saved()||!order||plan.customer_order_id!==order.customer_order_id)return;
  busy=true;controls();const identity=orderScope(),orderId=order.customer_order_id;
  try{
   await orderRequest("/api/picking/plans/"+plan.pick_plan_id+"/cancel",{method:"POST",headers:{"Content-Type":"application/json"},body:"{}"});
   if(identity===orderScope()&&orderState.selectedId===orderId){await read();say("Пустой план отменён. После приёмки товара можно создать актуальное обеспечение.");}
  }catch(e){if(identity===orderScope())say(e.message+". Перечитайте состояние плана; автоматического повторного создания нет.");}
  finally{busy=false;controls();}
 }
 async function archive(){'''
assert needle in text;text=text.replace(needle,change,1)
text=text.replace('plans.length?"Показаны существующие планы. Для продолжения используйте действующий план и рабочее место волн."','plans.some(p=>p.status==="NO_STOCK")?"Товар пока не обеспечен. Потребность сохранена; складские задания не выданы. После приёмки отмените пустой план и пересчитайте обеспечение.":plans.length?"Показаны существующие планы. Для продолжения используйте действующий план и рабочее место волн."')
files[str(path)]=text
path=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html")
text=path.read_text(encoding="utf-8").replace('<th>Резервов</th></tr></thead><tbody id="orderPickRows">','<th>Резервов</th><th>Следующее действие</th></tr></thead><tbody id="orderPickRows">',1)
files[str(path)]=text
print(json.dumps(files,ensure_ascii=True))
