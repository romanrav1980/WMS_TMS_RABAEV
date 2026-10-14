(()=>{
 const host=document.getElementById("returnHistory");if(!host)return;
 const el=(tag,text,cls)=>{const n=document.createElement(tag);n.textContent=text;if(cls)n.className=cls;return n;};
 const disposition={REUSE:"Исправный возврат",SUPPLIER:"Возврат поставщику",DISPOSAL:"Утилизация"};
 const driverUrl=new URL(location.href);driverUrl.port="3000";driverUrl.pathname="/";driverUrl.search="";driverUrl.hash="";
 function stage(a,p){
  if(!a.return_document)return "Ожидает документа SAP";
  if(!p.warehouse_progress_visible)return "Этап склада недоступен в текущих полномочиях";
  if(p.disposal_operation_id)return "Утилизация проведена";
  if(p.supplier_dispatch_operation_id)return "Отгружено поставщику";
  if(p.placement_operation_id)return a.disposition==="REUSE"?"Размещено по назначению":a.disposition==="SUPPLIER"?(p.supplier_st_id?"СТ поставщику подготовлена":"Подготовить возвратную СТ"):"Оформить утилизацию";
  if(p.warehouse_receipt_operation_id)return "Принято складом · требуется размещение";
  if(p.pickup_operation_id)return "У водителя · требуется складская приёмка";
  if(p.handover_operation_id)return "Передано магазином · ожидает подписи водителя";
  if(p.transport_operation_id)return "Вывоз запланирован · ожидает передачи магазином";
  return "SAP получен · требуется назначить вывоз";
 }
 function link(text,page,ware,extra={}){
  const a=el("a",text,"return-progress-link");a.title="Открыть существующий рабочий экран; выбор ничего не проводит";
  a.href=page+"?"+new URLSearchParams({...extra,...(ware?{warehouse_id:String(ware)}:{})});return a;
 }
 window.wmsReturnProgress={
  clear(){host.replaceChildren();},
  render(data){
   host.replaceChildren();host.append(el("h2","Путь согласованного возврата"));
   if(!data.approvals.length){host.append(el("p","Согласованных возвратов этой приёмки пока нет."));return;}
   host.append(el("p",data.has_older_approvals?"Показаны последние 100 согласований; имеются более ранние записи.":"Показаны согласования выбранной исходной приёмки."));
   for(const a of data.approvals){
    const p=a.progress||{},card=el("article","","return-progress-card");
    card.append(el("span",stage(a,p),"return-progress-status"),el("h3",(disposition[a.disposition]||a.disposition)+" · "+a.quantity+" "+a.base_uom));
    card.append(el("p","Решение: "+a.decision_reference+" · "+a.approved_by),el("p","Основание SAP: "+(a.return_document||"ожидается")+(a.ware_id?" · склад "+a.ware_id:"")));
    if(p.warehouse_progress_visible){
     const steps=el("ol","","return-progress-steps");
     for(const [label,done]of [["Вывоз в рейсе",p.transport_operation_id],["Передача магазином",p.handover_operation_id],["Приёмка водителем",p.pickup_operation_id],["Приёмка складом",p.warehouse_receipt_operation_id],["Размещение",p.placement_operation_id]]){
      steps.append(el("li",(done?"✓ ":"○ ")+label,done?"done":""));
     }
     card.append(steps);
     if(p.tt_id)card.append(el("p","Рейс вывоза №"+p.tt_id));
     if(p.warehouse_receipt_operation_id)card.append(el("p","Принято "+p.received_quantity+" "+p.base_uom+" · партия "+(p.observed_batch||"не указана")+" · срок "+(p.expiry_date||"не указан")));
     if(p.target_cell)card.append(el("p","Размещено: "+p.target_cell));else if(p.receive_cell)card.append(el("p","Зона приёмки: "+p.receive_cell));
     const actions=el("div","","return-progress-actions");
     if(!p.transport_operation_id)actions.append(link("Назначить вывоз","store-return-transport.html",a.ware_id,{approval_id:a.operation_id}));
     else if(!p.pickup_operation_id)actions.append(link("Рабочее место водителя",driverUrl.href,null,{page:"driver"}));
     else if(!p.warehouse_receipt_operation_id)actions.append(link("Приёмка возвратов","store-return-receiving.html",a.ware_id));
     else if(!p.placement_operation_id){
      actions.append(link("Размещение возвратов","store-return-putaway.html",a.ware_id));
      if(p.task_id)actions.append(link("Задание №"+p.task_id+" · "+p.task_status,"warehouse-tasks.html",null,{task_id:p.task_id}));
     }else if(a.disposition==="SUPPLIER")actions.append(link("Возврат поставщику","supplier-return.html",a.ware_id));
     else if(a.disposition==="DISPOSAL")actions.append(link("Акт и решение об утилизации","return-disposal.html",a.ware_id));
     card.append(actions);
     if(p.supplier_st_id)card.append(el("p","СТ поставщику: "+p.supplier_st_id+" · "+p.supplier_st_identifier));
    }
    const detail=el("details",""),summary=el("summary","Идентификаторы и происхождение");summary.title="Показать сохранённые факты для сверки";detail.append(summary);
    detail.append(el("p","Согласование: "+a.operation_id));
    for(const [key,label]of [["transport_operation_id","План вывоза"],["handover_operation_id","Передача магазина"],["pickup_operation_id","Приёмка водителя"],["warehouse_receipt_operation_id","Приёмка склада"],["placement_operation_id","Размещение"],["disposal_operation_id","Утилизация"],["supplier_dispatch_operation_id","Отгрузка поставщику"]])if(p[key])detail.append(el("p",label+": "+p[key]));
    if(p.uid_pallet)detail.append(el("p","Идентификатор паллеты: "+p.uid_pallet));
    card.append(detail);host.append(card);
   }
   host.append(el("p","Физический факт и исходящее сообщение не подтверждают получение SAP или государственной системой. Отгрузка поставщику не означает его приёмку.","return-progress-note"));
  }
 };
})();
