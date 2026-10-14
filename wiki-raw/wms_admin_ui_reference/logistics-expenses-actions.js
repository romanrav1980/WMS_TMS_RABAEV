// C-0008: связи экрана дополнительных расходов. Кнопка следующего действия только выбирает документ
// в существующей форме и раскрывает её; решение, подпись и проведение — отдельной кнопкой формы.
(() => {
 const P=window.LxPage,M=window.LxModel,el=P.el;
 const find=op=>P.expenses().find(r=>r.operation_id===op);
 const money=(v,c)=>v+" "+c;

 function reveal(sectionId,focusId,hintId,text){
  const s=el(sectionId);s.classList.remove("lx-flash");void s.offsetWidth;s.classList.add("lx-flash");
  s.scrollIntoView({behavior:"smooth",block:"start"});el(hintId).textContent=text;
  setTimeout(()=>el(focusId).focus({preventScroll:true}),250);
 }
 function pick(select,op){
  if(![...el(select).options].some(o=>o.value===op))throw Error("Документ "+op+" отсутствует в списке формы — обновите реестр.");
  el(select).value=op;
 }
 function decisionHint(r){
  if(!r)return"";
  const phase=el("exPhase").value,base="Документ "+(r.document_reference||"—")+" · "+money(r.amount,r.currency)+" · "+(r.object_kind==="TRIP"?"рейс ":"автомобиль ")+r.object_id+". ";
  if(phase==="FINANCE")return base+"Финконтроль: база логиста «"+(r.distribution_basis||"—")+"» сохраняется; решает не тот сотрудник, что логист ("+(r.logist_actor||"—")+"). Сохраните отдельной кнопкой «Сохранить решение».";
  if(r.correction_of_op)return base+"Коррекция сохраняет согласованную базу исходного расхода "+r.correction_of_op+" («"+(find(r.correction_of_op)?.distribution_basis||"—")+"»). Сохраните отдельной кнопкой «Сохранить решение».";
  return base+(r.object_kind==="VEHICLE"?"Расход автомобиля: база «Без распределения».":"Расход рейса: при подтверждении нужна база распределения — проверьте выбор.")+" Сохраните отдельной кнопкой «Сохранить решение».";
 }
 function act(button){
  const op=button.dataset.lxOp,kind=button.dataset.lxAction,r=find(op);if(!r||P.isLocked())return;
  try{
   if(kind==="decide"){
    pick("exExpense",op);el("exPhase").value=button.dataset.lxPhase;el("exOutcome").value="APPROVE";
    if(button.dataset.lxPhase==="FINANCE")el("exBasis").value=r.distribution_basis||"NONE";
    else if(r.correction_of_op&&find(r.correction_of_op)?.distribution_basis)el("exBasis").value=find(r.correction_of_op).distribution_basis;
    else if(r.object_kind==="VEHICLE")el("exBasis").value="NONE";
    else if(el("exBasis").value==="NONE")el("exBasis").value="WEIGHT";
    reveal("lxDecideForm","exDecisionRef","lxDecisionHint",decisionHint(r));
   }else if(kind==="allocate"){
    pick("exAllocation",op);
    reveal("lxAllocForm","exAllocate","lxAllocHint","Выбран "+r.operation_id+": "+money(r.amount,r.currency)+", рейс "+r.object_id+", база «"+(r.distribution_basis||"—")+"». Проведение — кнопкой «Провести распределение».");
   }else if(kind==="correct"){
    pick("exCorrection",op);el("exCorrection").dispatchEvent(new Event("change"));
    reveal("lxReportForm","exAmount","lxReportPreview","Коррекция "+op+": введите изменение со знаком; текущий итог "+money(r.confirmed_total,r.currency)+".");
   }
  }catch(e){P.say(e.message,"error");}
 }
 // Понятное описание того, что будет зарегистрировано: исходник, знак и дельта, итог после подтверждения.
 function reportPreview(){
  const out=el("lxReportPreview"),amount=el("exAmount").value.trim(),v=M.dec(amount);
  const source=find(el("exCorrection").value),norm=P.normativeCosts().find(r=>r.operation_id===el("exNormativeCorrection").value);
  if(!amount){out.textContent="";return;}
  if(!v){out.textContent="Сумма — число с точкой, например 15.50; для коррекции со знаком: -10.00.";return;}
  const origin=source||norm;
  if(origin){
   const total=M.dec(origin.confirmed_total),after=total?M.text(M.add(total,v)):"—";
   out.textContent=(v.n<0n?"Уменьшение ":"Увеличение ")+money(amount,origin.currency)+" к "+(source?"расходу ":"нормативному начислению ")+origin.operation_id+
    ". Исходная запись не меняется; после подтверждения финконтролем итог: "+money(origin.confirmed_total,origin.currency)+" → "+money(after,origin.currency)+(after.startsWith("-")?" — итог не может быть отрицательным, сервер откажет.":".");
   return;
  }
  if(v.n<=0n){out.textContent="Новый расход — положительная сумма. Для уменьшения выберите исходник коррекции.";return;}
  const kind=el("exKind").value==="TRIP"?"рейс ":"автомобиль ";
  out.textContent="Новый расход "+money(amount,el("exCurrency").value.trim().toUpperCase()||"—")+" · "+kind+(el("exObject").value||"—")+" · документ "+(el("exReference").value.trim()||"—")+" от "+(el("exDay").value||"—")+". Дальше: решение логиста, затем финконтроль.";
 }
 function sourceChanged(id,other){
  el(other).value="";
  const source=id==="exCorrection"?find(el(id).value):P.normativeCosts().find(r=>r.operation_id===el(id).value);
  el("exConfirmed").value=source?money(source.confirmed_total,source.currency):"";
  const derived=!!source;
  for(const f of ["exObject","exCurrency"])el(f).readOnly=derived;
  if(source){el("exKind").value=id==="exCorrection"?source.object_kind:"TRIP";el("exObject").value=id==="exCorrection"?source.object_id:source.trip_id;el("exCurrency").value=source.currency;P.articleOptions();}
  reportPreview();
 }
 function wareChanged(){P.clearData();P.say("Склад изменён — обновите реестр.");}
 function filterChanged(){
  P.filter.kind=el("lxKind").value;P.filter.object=el("lxObject").value.trim();P.filter.query=el("lxQuery").value.trim();P.render();
 }

 el("exLoad").addEventListener("click",()=>P.load());
 el("exArticle").addEventListener("click",()=>P.prepare("/articles",()=>{const a=P.articles();if(!a)throw Error("Сначала обновите статьи.");const code=el("exCode").value.trim().toUpperCase();
  return{code,name:el("exName").value.trim(),scope:el("exScope").value,included_in_rate:el("exIncluded").checked,active:el("exActive").checked,expected_version:a.find(r=>r.code===code)?.version_no||0};}));
 el("exReport").addEventListener("click",()=>P.prepare("/report",P.expenseBody));
 el("exDecide").addEventListener("click",()=>P.prepare("/decide",()=>({expense_operation_id:el("exExpense").value,phase:el("exPhase").value,outcome:el("exOutcome").value,distribution_basis:el("exBasis").value,decision_reference:el("exDecisionRef").value.trim(),reason:el("exDecisionReason").value.trim()})));
 el("exAllocate").addEventListener("click",()=>P.prepare("/allocate",()=>({expense_operation_id:el("exAllocation").value})));
 el("exCorrection").addEventListener("change",()=>sourceChanged("exCorrection","exNormativeCorrection"));
 el("exNormativeCorrection").addEventListener("change",()=>sourceChanged("exNormativeCorrection","exCorrection"));
 el("exKind").addEventListener("change",()=>{P.articleOptions();reportPreview();});
 for(const id of ["exAmount","exCurrency","exObject","exReference","exDay"])el(id).addEventListener("input",reportPreview);
 for(const id of ["exExpense","exPhase"])el(id).addEventListener("change",()=>{el("lxDecisionHint").textContent=decisionHint(find(el("exExpense").value));});
 el("exWare").addEventListener("input",wareChanged);
 el("lxKind").addEventListener("change",filterChanged);
 for(const id of ["lxObject","lxQuery"])el(id).addEventListener("input",filterChanged);
 el("exRows").addEventListener("click",e=>{const b=e.target.closest("button[data-lx-action]");if(b&&!b.disabled)act(b);});
 el("exRetry").addEventListener("click",()=>P.send(P.key()));
 el("exRestart").addEventListener("click",()=>P.discard());
 el("lxVerify").addEventListener("click",()=>P.verifyPending());
 el("lxExactFind").addEventListener("click",()=>P.exactSearch());
 el("lxExactId").addEventListener("keydown",e=>{if(e.key==="Enter")P.exactSearch();});
 // Прямая ссылка из сверки дня: ?warehouse_id= открывает реестр склада, ?operation_id= — точный поиск расхода.
 let deepDone=false;
 async function deepLink(){
  if(deepDone||!window.wmsAdminAuth?.state.user)return;deepDone=true;
  const q=new URLSearchParams(location.search),ware=Number(q.get("warehouse_id")),op=(q.get("operation_id")||"").trim();
  if(!Number.isSafeInteger(ware)||ware<1)return;
  el("exWare").value=String(ware);
  if(await P.load()&&op){el("lxExactId").value=op;await P.exactSearch();}
 }
 window.addEventListener("wms-admin-auth-ready",()=>setTimeout(deepLink,0));setTimeout(deepLink,0);
})();
