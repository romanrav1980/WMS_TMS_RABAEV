/* Navigation uses current server assignment; it never grants physical admission. */
(() => {
 let panel;
 function render(parent,snapshot,blocked){
  if(!panel){panel=document.createElement('div');panel.className='qc-actions';parent.querySelector('.qc-toolbar').after(panel);}
  panel.replaceChildren();panel.hidden=true;
  if(!snapshot||blocked||!window.wmsAdminAuth.hasPermission('transport_dispatch_view'))return;
  panel.hidden=false;
  const note=document.createElement('span');
  if(snapshot.weight_exemption?.eligible){const proof=document.createElement('span');proof.textContent='Освобождение от веса: целая неизменённая паллета. Проверки маркировки и состава сохраняются.';proof.title='Основание: '+snapshot.weight_exemption.reason+'; исходная приёмка '+snapshot.weight_exemption.receipt_operation_id;panel.append(proof);}
  if(snapshot.ready!==true&&snapshot.required!==false){note.textContent='До погрузки требуется допуск текущего состава.';panel.append(note);return;}
  const assignment=snapshot.transport_assignment;
  if(assignment?.state!=='ASSIGNED'||!Number.isSafeInteger(assignment.transport_task_id)||assignment.transport_task_id<1){
   note.textContent=assignment?.state==='UNASSIGNED'?'Для СТ ещё не назначен рейс. Назначьте его в существующем диспетчере.':'Назначение рейса недоступно; перечитайте СТ после назначения в диспетчере.';panel.append(note);return;
  }
  const a=document.createElement('a');a.textContent='Открыть погрузку рейса '+assignment.transport_task_id;
  a.href='transport-loading.html?trip_id='+assignment.transport_task_id;
  a.title='Показать текущее назначение и факты рейса. Допуск состава и физические сканы проверяются отдельно при погрузке.';
  panel.append(a);
 }
 window.wmsQualityNext={render};
})();
