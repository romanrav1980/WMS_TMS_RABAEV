// C-0008: модель рабочего экрана дополнительных расходов. Только вычисления над ответом
// GET /api/finance/logistics-expenses/warehouses/{ware}; правила сервера остаются единственными.
(() => {
 // Точная десятичная арифметика над строками API: без float, валюты не смешиваются.
 function dec(s){const m=/^(-?)(\d+)(?:\.(\d+))?$/.exec(String(s??"").trim());if(!m)return null;const f=m[3]||"";return{n:BigInt((m[1]||"")+m[2]+f),scale:f.length};}
 function add(a,b){const s=Math.max(a.scale,b.scale);return{n:a.n*10n**BigInt(s-a.scale)+b.n*10n**BigInt(s-b.scale),scale:s};}
 function text(v){const neg=v.n<0n,abs=(neg?-v.n:v.n).toString().padStart(v.scale+1,"0");const i=abs.slice(0,abs.length-v.scale),f=v.scale?"."+abs.slice(-v.scale):"";return(neg?"-":"")+i+f;}
 function sumByCurrency(rows){const m=new Map();for(const r of rows){const v=dec(r.amount);if(!v)continue;const o=m.get(r.currency)||{currency:r.currency,total:{n:0n,scale:0},count:0};o.total=add(o.total,v);o.count++;m.set(r.currency,o);}
  return[...m.values()].sort((a,b)=>a.currency.localeCompare(b.currency)).map(o=>({currency:o.currency,amount:text(o.total),count:o.count}));}
 const isCorrection=r=>!!(r.correction_of_op||r.cost_correction_of_op);

 const STAGES={
  await_logist:{label:"Ожидает логиста",tone:"info"},
  await_finance:{label:"Ожидает финконтроля",tone:"info"},
  await_allocation:{label:"Подтверждён, ждёт распределения",tone:"warn"},
  done:{label:"Завершён",tone:"ok"},
  rejected:{label:"Отклонён",tone:"bad"}
 };
 function stageOf(r){
  if(r.logist_outcome==="REJECT"||r.finance_outcome==="REJECT")return"rejected";
  if(!r.logist_operation_id)return"await_logist";
  if(!r.finance_operation_id)return"await_finance";
  if(r.object_kind==="TRIP"&&!r.allocation_operation_id)return"await_allocation";
  return"done";
 }
 // Цепочка «зарегистрирован → логист → финконтроль → распределён»; расход автомобиля завершается утверждением.
 function chain(r){
  const step=(label,state,detail)=>({label,state,detail});
  const decision=(outcome,actor,op,ref)=>outcome?(outcome==="APPROVE"?"утверждено":"отклонено")+(actor?" · "+actor:"")+(ref?" · документ "+ref:"")+" · "+op:"";
  const steps=[step("Зарегистрирован","done",(r.reporter||"—")+" · "+(r.expense_date||"—"))];
  steps.push(step("Логист",r.logist_outcome==="REJECT"?"rejected":r.logist_operation_id?"done":"current",decision(r.logist_outcome,r.logist_actor,r.logist_operation_id,r.logist_decision_reference)||"решения нет"));
  const fState=r.logist_outcome==="REJECT"?"skipped":r.finance_outcome==="REJECT"?"rejected":r.finance_operation_id?"done":r.logist_operation_id?"current":"todo";
  steps.push(step("Финконтроль",fState,r.finance_operation_id?decision(r.finance_outcome,r.finance_actor,r.finance_operation_id,r.finance_decision_reference):fState==="skipped"?"не требуется":"решения нет"));
  if(r.object_kind==="VEHICLE")steps.push(step("Только автомобиль",r.finance_outcome==="APPROVE"?"done":stageOf(r)==="rejected"?"skipped":"todo","на товар не распределяется"));
  else steps.push(step("Распределён",r.allocation_operation_id?"done":r.finance_outcome==="APPROVE"?"current":stageOf(r)==="rejected"?"skipped":"todo",r.allocation_operation_id?r.allocation_operation_id+" · база "+(r.distribution_basis||"—"):"база логиста: "+(r.distribution_basis||"не выбрана")));
  return steps;
 }
 // Следующее действие: какая существующая форма нужна, какое право и почему действие может быть недоступно.
 function nextAction(r,ctx){
  const can=p=>ctx.has(p),me=ctx.user;
  const stage=stageOf(r);
  if(stage==="await_logist")return{kind:"decide",phase:"LOGIST",label:"Решение логиста",permission:"calc_tt_price",blocked:can("calc_tt_price")?"":"Нужно право логиста (calc_tt_price) на этот склад"};
  if(stage==="await_finance")return{kind:"decide",phase:"FINANCE",label:"Решение финконтроля",permission:"create_tt_price",
   blocked:!can("create_tt_price")?"Нужно право финансового контроля (create_tt_price)":me&&r.logist_actor===me?"Финконтроль выполняет другой сотрудник: логистом были вы":""};
  if(stage==="await_allocation")return{kind:"allocate",label:"Распределить на товар",permission:"calc_tt_price",blocked:can("calc_tt_price")?"":"Нужно право распределения (calc_tt_price)"};
  return null;
 }
 function correctionAction(r,ctx){
  if(isCorrection(r)||r.finance_outcome!=="APPROVE")return null;
  return{kind:"correct",label:"Скорректировать",permission:"edit_bill_tt",blocked:ctx.has("edit_bill_tt")?"":"Нужно право регистрации расходов (edit_bill_tt)"};
 }
 function matches(r,f){
  if(f.stage!=="all"&&stageOf(r)!==f.stage)return false;
  if(f.kind!=="all"&&r.object_kind!==f.kind)return false;
  if(f.object&&String(r.object_id)!==f.object)return false;
  if(!f.query)return true;
  const q=f.query.toLowerCase();
  return[r.operation_id,r.document_reference,r.article_name,r.article_code,r.reporter,r.logist_actor,r.correction_of_op,r.cost_correction_of_op].some(v=>String(v??"").toLowerCase().includes(q));
 }
 window.LxModel={dec,add,text,sumByCurrency,isCorrection,STAGES,stageOf,chain,nextAction,correctionAction,matches};
})();
