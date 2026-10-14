// C-0020 (NI06.3): случаи недостачи тары в существующем реестре — исходный долг, заявитель, держатель,
// количество, решение и следующий шаг. Кнопка карточки только выбирает заявление в форме решения.
(() => {
 const holders={WAREHOUSE:"Склад",VEHICLE:"Автомобиль",STORE:"Магазин"};
 function h(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!=null)n.textContent=text;return n;}
 function fact(k,v){const d=h("div");d.append(h("dt",null,k),h("dd",null,v==null||v===""?"—":String(v)));return d;}
 // Следующий шаг: открытое заявление решает другой сотрудник с правом списания; решённое — только история.
 function nextStep(c,me,canDecide){
  if(c.decision_operation_id)return{label:c.outcome==="WRITE_OFF"?"Списано":"Отклонено: тара освобождена",action:null,why:""};
  if(!canDecide)return{label:"Ожидает независимого решения",action:"Принять решение",why:"Нужно право списания тары (tare_writeoff)."};
  if(c.actor===me)return{label:"Ожидает независимого решения",action:"Принять решение",why:"Заявление подали вы — решение принимает другой сотрудник."};
  return{label:"Ожидает независимого решения",action:"Принять решение",why:""};
 }
 function card(c,me,canDecide,onPick,focus){
  const step=nextStep(c,me,canDecide),a=h("article","tl-case"+(c.decision_operation_id?" tl-case-done":"")+(focus?" tl-case-focus":""));
  a.dataset.claim=c.operation_id;a.setAttribute("aria-label","Заявление "+c.decision_reference);
  const head=h("div","tl-case-head");head.append(h("strong",null,"Акт "+c.decision_reference),h("span","tl-chip",step.label));
  const dl=h("dl","tl-facts");
  dl.append(fact("Тип и состояние",c.pallet_type_name+" · "+(c.condition_code==="GOOD"?"пригодная":"повреждённая")),fact("Количество",c.quantity),
   fact("Держатель",(holders[c.custodian_kind]||c.custodian_kind)+" "+c.custodian_id),fact("Заявил",c.actor),
   fact("Исходный долг / выдача",c.source_claim_id),fact("Рейс",c.transport_task_id),
   fact("Решение",c.decision_operation_id?(c.outcome==="WRITE_OFF"?"списание":"отклонение")+" · "+(c.decided_by||"—"):"нет"),fact("Создано",c.created_at?new Date(c.created_at).toLocaleString("ru-RU"):""));
  const basis=h("details");basis.append(h("summary",null,"Основание"),h("p",null,"Заявление: "+c.operation_id),h("p",null,"Обстоятельства: "+(c.reason_text||"—")));
  if(c.decision_operation_id)basis.append(h("p",null,"Решение: "+c.decision_operation_id));
  a.append(head,dl,basis);
  if(step.action){
   const row=h("div","tl-actions"),b=h("button",null,step.action);b.type="button";b.disabled=!!step.why;if(step.why)b.dataset.tlBlocked="1";b.title=step.why||"Выбрать заявление в форме решения; проведение — отдельной кнопкой";
   b.addEventListener("click",()=>onPick(c));row.append(b);if(step.why)row.append(h("small","tl-why",step.why));a.append(row);
  }
  return a;
 }
 function render(host,cases,me,canDecide,onPick,focusId){
  const open=cases.filter(c=>!c.decision_operation_id),done=cases.filter(c=>c.decision_operation_id);
  host.replaceChildren(h("p","tl-note","Заявлений: "+cases.length+" (открыто "+open.length+"). До 200 последних заявлений склада."),
   ...(cases.length?[...open,...done].map(c=>card(c,me,canDecide,onPick,c.operation_id===focusId)):[h("p","tl-note","Заявлений о недостаче нет.")]));
  const target=focusId&&host.querySelector('[data-claim="'+CSS.escape(focusId)+'"]');
  if(target)target.scrollIntoView({block:"center"});
  return !!target;
 }
 window.TareLossCases={render,nextStep};
})();
