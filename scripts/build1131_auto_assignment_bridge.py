from pathlib import Path
import json
f={}
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
s=s.replace('<details data-permission="customer_order_import">','<details data-permission="customer_order_import" id="sapAssignment">',1)
s=s.replace('<summary>Подготовить СТ из заказа SAP</summary>','<summary>Подготовка СТ и назначение в существующий рейс</summary>',1)
s=s.replace('<button id="sapAssignSt" type="button">Добавить СТ в рейс</button>','<button id="sapTripReview" type="button">Показать ограничения рейса</button><button id="sapAssignSt" type="button">Добавить СТ в рейс</button><p id="sapTripReviewMessage" role="status"></p>')
s=s.replace('<button id="sapAutoCurrent">','<a id="sapAutoAssignment" hidden>Открыть карточку СТ и назначение рейса</a>\n<button id="sapAutoCurrent">')
s=s.replace('customer-orders.js?v=20261013-1045','customer-orders.js?v=20261013-1131').replace('sap-automatic-preparation.js?v=20261013-1124','sap-automatic-preparation.js?v=20261013-1131')
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sap-automatic-preparation.js");s=p.read_text(encoding="utf-8")
s=s.replace(" function clear(){epoch++;proposal=null;"," function clear(){el('sapAutoAssignment').hidden=true;epoch++;proposal=null;")
needle=" async function readCurrent(){"
s=s.replace(needle," function assignmentLink(order){el('sapAutoAssignment').href='customer-orders.html?order_id='+encodeURIComponent(order)+'#sapAssignment';el('sapAutoAssignment').hidden=false;}\n"+needle)
s=s.replace("   const statistics=saved.pallet_statistics||[];","   assignmentLink(order);const statistics=saved.pallet_statistics||[];")
s=s.replace("   intent.settle(record);proposal=null;\n   message('Подготовлена", "   intent.settle(record);proposal=null;assignmentLink(command.order_id);\n   message('Подготовлена")
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.js");s=p.read_text(encoding="utf-8")
s=s.replace('orderBind("sapAssignSt",assignPreparedSt);','orderBind("sapAssignSt",assignPreparedSt);orderBind("sapTripReview",reviewPreparedTrip);')
s=s.replace('orderEl("orderDetailStatus").textContent="Выберите заказ";','orderEl("sapTripReviewMessage").textContent="";orderEl("orderDetailStatus").textContent="Выберите заказ";')
s=s.replace('    if(scope===orderScope()&&orderState.selectedId===initial&&window.location.hash==="#orderExecution")',
'''    if(scope===orderScope()&&orderState.selectedId===initial&&window.location.hash==="#sapAssignment"){
      await loadSapLayout();
      if(scope===orderScope()&&orderState.selectedId===initial){
        orderEl("sapAssignment").open=true;orderEl("sapAssignment").scrollIntoView({block:"start"});
      }
    }
    if(scope===orderScope()&&orderState.selectedId===initial&&window.location.hash==="#orderExecution")''')
s=s.replace('  orderState.selectedId=orderId;orderState.detail=null;', '  orderEl("sapTripReviewMessage").textContent="";orderState.selectedId=orderId;orderState.detail=null;')
s += '''
async function reviewPreparedTrip(){
 const id=orderState.selectedId,scope=orderScope(),serial=orderDetailGeneration,trip=Number(orderEl('sapTripId').value);
 const prepared=orderState.preparations.get(id)?.result;
 if(!prepared||!Number.isSafeInteger(trip)||trip<1)throw Error('Прочитайте подготовленную СТ и укажите существующий рейс.');
 orderEl('sapTripReviewMessage').textContent='Читаются текущие ограничения ТМС.';
 const result=await orderRequest('/api/transport/preflight/trips/'+trip,{method:'POST',
  headers:{'Content-Type':'application/json'},body:JSON.stringify({additional_st_numbers:[prepared.st_number]})});
 if(scope!==orderScope()||serial!==orderDetailGeneration||id!==orderState.selectedId||trip!==Number(orderEl('sapTripId').value))return;
 if(result.trip_id!==trip||result.read_only!==true||!Array.isArray(result.routes))throw Error('Результат рейса не подтверждён.');
 const route=result.routes[0],capacity=route?.capacity_and_type?.result;
 const blockers=[...(route?.source_blockers||[]).map(x=>x.code),
  ...(route?.capacity_and_type?.status==='BLOCKED'?[route.capacity_and_type.code]:[])];
 const warnings=capacity?.warnings||[];
 orderEl('sapTripReviewMessage').textContent=
  (blockers.length?'Ограничения: '+blockers.join('; '):'Вместимость проверена действующими правилами ТМС.')+
  (capacity?' Плановых мест: '+capacity.declared_places+', масса: '+capacity.declared_weight_kg+' кг.':'')+
  (warnings.length?' '+warnings.join('; '):'')+
  ' Назначение проверяет текущие данные повторно. Погрузка, температурный режим и разрешение выезда подтверждаются отдельно.';
}
orderEl('sapTripId').addEventListener('input',()=>{orderEl('sapTripReviewMessage').textContent='';});
'''
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sap-automatic-preparation.css");f[str(p)]=p.read_text(encoding="utf-8")+"\n#sapAutoAssignment:not([hidden]){display:inline-block;margin:8px 14px 12px 0;color:#1765c3;font-weight:600}#sapAssignment{scroll-margin-top:110px}\n"
p=Path("wiki/components/nicora_ni021_auto_preparation_20261013.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n1131: prepared UI bridge savedauto→selected order/sapAssignment/current preparation receipt→existing assignendpoint. Explicit readonly preflight uses existing native capacity/type/source service; not operational/departure admission. Runtime pending; no second order/tripmapping.\n"
p=Path("wiki/index.md");f[str(p)]="- [Auto→existing trip assignment1131](components/nicora_ni021_auto_preparation_20261013.md): current receipt link and explicit original TMS capacity review prepared; no second writer.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 /1131: prepared UI auto result→existing order/assignment; saved receipt reread and existing readonly TMS preflight. NoDBwrite/newassignmentengine, native rules reused; runtime pending.\n"
print(json.dumps(f,ensure_ascii=True))
