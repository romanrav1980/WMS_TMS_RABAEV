import {Money,TableWrap,totalsByCurrency} from "./BillingCostsCommon";
import type {Expense,Part,TransportResult,WarehouseSummary} from "./BillingCostsInvoice";

// Сводка счёта по валютам: каждая категория — своя колонка; строки и колонки между собой не складываются.
export function expenseState(e:Expense):"rejected"|"allocated"|"approved"|"pending"{
 if(e.finance_outcome==="REJECT"||e.logist_outcome==="REJECT")return "rejected";
 if(e.allocation_operation_id)return "allocated";
 if(e.finance_outcome==="APPROVE")return "approved";
 return "pending";
}

type Cell={amount?:string;note?:string};

export function BillingCostsSummary({warehouse,transport,expenses,readAt}:{warehouse:Part<WarehouseSummary>;transport:Part<TransportResult>;expenses:Part<Expense[]>;readAt:Date|null}){
 const rows=new Map<string,Record<string,Cell>>();
 const put=(currency:string,key:string,cell:Cell)=>{const r=rows.get(currency)||{};r[key]=cell;rows.set(currency,r);};
 for(const t of warehouse.data?.currency_totals||[])put(t.currency,"warehouse",{amount:t.original_amount});
 for(const t of transport.data?.currency_totals||[]){put(t.currency,"transport",{amount:t.amount});put(t.currency,"transportConfirmed",{amount:t.confirmed_amount});}
 const list=expenses.data||[];
 for(const t of totalsByCurrency(list.filter(e=>["approved","allocated"].includes(expenseState(e))),e=>e.currency,e=>e.amount))put(t.currency,"expApproved",{amount:t.amount,note:t.count+" шт."});
 for(const t of totalsByCurrency(list.filter(e=>expenseState(e)==="pending"),e=>e.currency,e=>e.amount))put(t.currency,"expPending",{amount:t.amount,note:t.count+" шт."});
 const columns:Array<[string,string,Part<unknown>]>=[
  ["warehouse","Складские, исходно",warehouse],["transport","Транспорт, исходно",transport],["transportConfirmed","Транспорт с корректировками",transport],
  ["expApproved","Допрасходы подтверждённые",expenses],["expPending","Допрасходы на согласовании",expenses]];
 const anyLoading=warehouse.loading||transport.loading||expenses.loading;
 return <section className="bc-summary" aria-label="Сводка начислений счёта по валютам">
  <div className="bc-summary-head"><h3>Начисления по валютам</h3><span className="bc-muted">{anyLoading?"Читаем источники…":readAt?"Прочитано "+readAt.toLocaleTimeString("ru-RU"):""}</span></div>
  {rows.size===0&&!anyLoading?<p className="bc-state bc-empty">По доступным складам начислений и расходов нет.</p>:
  <TableWrap label="Итоги по валютам"><table className="bc-table bc-stack"><thead><tr><th scope="col">Валюта</th>{columns.map(([k,t])=><th key={k} scope="col" className="bc-num">{t}</th>)}</tr></thead>
   <tbody>{[...rows.entries()].sort(([a],[b])=>a.localeCompare(b)).map(([currency,r])=><tr key={currency}><th scope="row" data-label="Валюта">{currency}</th>
    {columns.map(([k,title,part])=><td key={k} data-label={title} className="bc-num">{part.loading?<span className="bc-muted">…</span>:part.error?<span className="bc-err-cell" title={part.error}>ошибка чтения</span>:r[k]?.amount?<><Money amount={r[k].amount} currency={currency}/>{r[k].note&&<small className="bc-muted"> · {r[k].note}</small>}</>:<span className="bc-muted">—</span>}</td>)}
   </tr>)}</tbody></table></TableWrap>}
  <p className="bc-note">Суммы разных валют и разных категорий не складываются. Складские затраты — внутренние; нормативный транспорт не прибавляется к прежней сумме счёта перевозчика (колонка «Сумма ₽» в таблице рейсов ниже). Отклонённые расходы в итоги не входят.</p>
 </section>;
}
