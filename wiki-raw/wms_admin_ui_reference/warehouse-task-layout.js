(() => {
 const main=document.querySelector('main.workspace');if(!main)return;
 const panels=[...main.querySelectorAll(':scope > section.panel')];if(!panels.length)return;
 const tools=document.createElement('details');tools.className='warehouse-task-tools';
 const summary=document.createElement('summary');summary.textContent='Дополнительные операции со складским заданием';
 summary.title='Открыть назначение ресурса, сканирование маркировки и подготовку к отгрузке';
 const content=document.createElement('div');content.className='warehouse-task-tools-content';
 tools.append(summary,content);for(const panel of panels)content.appendChild(panel);main.appendChild(tools);
 function focusLinkedPanel(){
  const id=window.location.hash.slice(1)||(new URLSearchParams(window.location.search).has('qc_shipment')?'outgoingQuality':'');
  const target=id?document.getElementById(id):null;
  if(target&&content.contains(target)){tools.open=true;target.scrollIntoView({block:'start'});}
 }
 window.addEventListener('wms-admin-auth-ready',()=>requestAnimationFrame(focusLinkedPanel));
 focusLinkedPanel();

 for(const button of main.querySelectorAll('button'))if(!button.title)button.title=button.textContent.trim();
 for(const field of main.querySelectorAll('input,select'))if(!field.title){
   const label=field.closest('label');field.title=field.getAttribute('aria-label')||label?.childNodes[0]?.textContent.trim()||field.placeholder||'Параметр задания';
 }
})();
