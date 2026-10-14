// C-0008: представление реестра дополнительных расходов: карточки, цепочка стадий, итоги по валютам.
// Только DOM из данных ответа (textContent), без innerHTML с данными сервера.
(() => {
 const M=()=>window.LxModel;
 function h(tag,props,...kids){const n=document.createElement(tag);for(const[k,v]of Object.entries(props||{})){if(v==null||v===false)continue;if(k==="class")n.className=v;else if(k==="text")n.textContent=v;else if(k.startsWith("data-")||k.startsWith("aria-")||k==="role"||k==="title"||k==="type")n.setAttribute(k,v===true?"":v);else n[k]=v;}
  for(const c of kids.flat())if(c!=null&&c!==false)n.append(c instanceof Node?c:document.createTextNode(String(c)));return n;}
 const chip=(tone,text,title)=>h("span",{class:"lx-chip lx-"+tone,text,title});
 const fact=(k,v,title)=>h("div",{title},h("dt",{text:k}),h("dd",{text:v==null||v===""?"—":String(v)}));
 const money=(amount,currency)=>h("span",{class:"lx-money"},amount,h("small",{text:" "+currency}));

 function actionButton(a,op,primary){
  return h("button",{type:"button",class:primary?"lx-primary":"",text:a.label,disabled:!!a.blocked,title:a.blocked||"Выбрать документ в форме ниже. Решение сохраняется только отдельной кнопкой формы.","data-lx-action":a.kind,"data-lx-op":op,"data-lx-phase":a.phase||null,"data-lx-blocked":a.blocked?"1":null,"aria-describedby":a.blocked?"lx-why-"+op:null});
 }
 function card(r,ctx){
  const m=M(),stage=m.stageOf(r),st=m.STAGES[stage],corr=m.isCorrection(r);
  const object=(r.object_kind==="TRIP"?"Рейс ":"Автомобиль ")+r.object_id;
  const amount=h("div",{class:"lx-amount"},money(r.amount,r.currency),
   corr?h("small",{class:"lx-sub",text:(r.amount.startsWith("-")?"уменьшение":"увеличение")+" к "+(r.correction_of_op?"расходу "+r.correction_of_op:"нормативному начислению "+r.cost_correction_of_op)}):null,
   !corr&&r.confirmed_total&&r.confirmed_total!==r.amount?h("small",{class:"lx-sub",text:"текущий итог с коррекциями "+r.confirmed_total+" "+r.currency}):null);
  const head=h("div",{class:"lx-card-head"},
   h("div",{class:"lx-card-title"},h("strong",{text:r.article_name}),h("span",{class:"lx-sub",text:(r.expense_date||"дата не указана")+" · "+object+" · "+r.operation_id})),
   amount,chip(st.tone,st.label));
  const facts=h("dl",{class:"lx-facts"},
   fact("Документ",r.document_reference),fact("Статья",r.article_code),fact("Заявил",r.reporter),
   !corr?fact("Текущий итог",r.confirmed_total?r.confirmed_total+" "+r.currency:null,"Исходная сумма плюс поправки, подтверждённые финансовым контролем"):fact("Ожидаемый итог исходника",r.expected_confirmed_total?r.expected_confirmed_total+" "+r.currency:null,"Итог исходного документа после этой поправки; сверяется сервером при подтверждении"));
  const steps=h("ol",{class:"lx-chain","aria-label":"Стадии расхода"},...m.chain(r).map(s=>h("li",{class:"lx-step lx-step-"+s.state},h("b",{text:s.label}),h("small",{text:s.detail}))));
  const next=m.nextAction(r,ctx),fix=m.correctionAction(r,ctx);
  const why=[next,fix].find(a=>a&&a.blocked);
  const actions=h("div",{class:"lx-actions"},
   next?actionButton(next,r.operation_id,true):h("span",{class:"lx-sub",text:stage==="rejected"?"Отказ подтверждён — в итоги не входит. Нужен новый расход с новым документом.":stage==="done"?(r.object_kind==="VEHICLE"?"Утверждён на автомобиль, на товар не распределяется.":"Распределён на фактически перевезённый товар."):""}),
   fix?actionButton(fix,r.operation_id,false):null,
   why?h("small",{class:"lx-why",id:"lx-why-"+r.operation_id,text:why.blocked}):null);
  return h("article",{class:"lx-card lx-card-"+stage,"data-lx-card":r.operation_id,"aria-label":r.article_name+", "+object+", "+st.label},head,facts,steps,actions);
 }
 function render(host,rows,ctx){
  host.replaceChildren(...(rows.length?rows.map(r=>card(r,ctx)):[h("p",{class:"lx-empty",text:ctx.emptyText})]));
 }
 function totals(host,rows){
  const m=M(),confirmed=m.sumByCurrency(rows.filter(r=>r.finance_outcome==="APPROVE")),pending=m.sumByCurrency(rows.filter(r=>["await_logist","await_finance"].includes(m.stageOf(r))));
  const cur=[...new Set([...confirmed,...pending].map(t=>t.currency))].sort();
  if(!cur.length){host.replaceChildren();return;}
  const find=(list,c)=>list.find(t=>t.currency===c);
  host.replaceChildren(h("table",{class:"lx-totals"},h("caption",{text:"Итоги загруженного окна по валютам (валюты не складываются, отклонённые не входят)"}),
   h("thead",null,h("tr",null,h("th",{scope:"col",text:"Валюта"}),h("th",{scope:"col",text:"Подтверждено финконтролем"}),h("th",{scope:"col",text:"На согласовании"}))),
   h("tbody",null,...cur.map(c=>{const a=find(confirmed,c),b=find(pending,c);return h("tr",null,h("th",{scope:"row",text:c}),
    h("td",{"data-label":"Подтверждено",text:a?a.amount+" · "+a.count+" шт.":"—"}),h("td",{"data-label":"На согласовании",text:b?b.amount+" · "+b.count+" шт.":"—"}));}))));
 }
 function counters(host,rows,current,onPick){
  const m=M(),count=s=>s==="all"?rows.length:rows.filter(r=>m.stageOf(r)===s).length;
  host.replaceChildren(...["all","await_logist","await_finance","await_allocation","done","rejected"].map(s=>h("button",{type:"button",class:s===current?"lx-active":"","aria-pressed":String(s===current),onclick:()=>onPick(s)},s==="all"?"Все":m.STAGES[s].label,h("em",{text:" "+count(s)}))));
 }
 window.LxView={h,render,totals,counters};
})();
