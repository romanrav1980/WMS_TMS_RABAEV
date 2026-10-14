import {useState} from "react";
import {BlockStatus,Chip,Money,TableWrap,type BlockState} from "./BillingCostsCommon";
import type {Expense,Part} from "./BillingCostsInvoice";
import {expenseState} from "./BillingCostsSummary";
import type {BasisTarget} from "./BillingCostsBasis";

// Дополнительные расходы рейсов счёта: состояние согласования и распределения, коррекции,
// следующий шаг. Ввод и согласование выполняются на существующем экране расходов.
const STATE={
 pending:{tone:"info",label:"Согласование ожидается",next:"Финансовое согласование или отказ"},
 approved:{tone:"warn",label:"Подтверждено, не распределено",next:"Распределить расход по рейсу"},
 allocated:{tone:"ok",label:"Подтверждено и распределено",next:"Действий не требуется"},
 rejected:{tone:"bad",label:"Отклонено",next:"Не входит в итоги; при необходимости — новый расход"}
} as const;
type Filter="all"|keyof typeof STATE;

export function BillingExtraExpenses({part,reload,onBasis}:{part:Part<Expense[]>;reload:()=>void;onBasis:(t:BasisTarget)=>void}){
 const [filter,setFilter]=useState<Filter>("all");
 const rows=part.data||[];
 const state:BlockState=part.loading?"loading":part.error?"error":part.data&&!rows.length?"empty":"ready";
 const counts=rows.reduce((m,r)=>{const s=expenseState(r);m[s]=(m[s]||0)+1;return m;},{} as Record<string,number>);
 const shown=rows.filter(r=>filter==="all"||expenseState(r)===filter);
 return <section className="bc-block" aria-labelledby="bcExpensesTitle"><h4 id="bcExpensesTitle">Дополнительные расходы рейсов</h4>
  <BlockStatus state={state} error={part.error} empty="Дополнительных расходов по рейсам этого счёта нет (по доступным складам)." onRetry={reload}/>
  {state==="ready"&&<>
   <div className="bc-seg" role="group" aria-label="Фильтр по состоянию">
    {(["all","pending","approved","allocated","rejected"] as Filter[]).map(f=><button key={f} type="button" aria-pressed={filter===f} className={filter===f?"bc-active":""} onClick={()=>setFilter(f)}>{f==="all"?"Все":STATE[f].label} <em>{f==="all"?rows.length:counts[f]||0}</em></button>)}
   </div>
   <TableWrap label="Дополнительные расходы"><table className="bc-table bc-stack"><thead><tr><th scope="col">Рейс</th><th scope="col">Статья и документ</th><th scope="col" className="bc-num">Сумма</th><th scope="col">Состояние</th><th scope="col">Дальше</th><th scope="col"><span className="bc-sr">Основание</span></th></tr></thead>
    <tbody>{shown.map(r=>{const s=STATE[expenseState(r)];return <tr key={r.operation_id}>
     <td data-label="Рейс">{r.tt_id}</td>
     <td data-label="Статья и документ">{r.article_name}<small className="bc-sub">документ {r.document_reference||"—"} · операция {r.operation_id}</small>
      {r.cost_correction_of_op&&<small className="bc-sub">коррекция нормативного начисления {r.cost_correction_of_op}</small>}
      {r.correction_of_op&&<small className="bc-sub">коррекция расхода {r.correction_of_op}</small>}
      {r.allocation_operation_id&&<small className="bc-sub">распределено: {r.distribution_basis||"—"}, строк товара {r.goods_lines}</small>}</td>
     <td data-label="Сумма" className="bc-num"><Money amount={r.amount} currency={r.currency}/>{r.amount.startsWith("-")&&<small className="bc-sub">уменьшающая корректировка</small>}</td>
     <td data-label="Состояние"><Chip tone={s.tone}>{s.label}</Chip></td>
     <td data-label="Дальше"><small>{s.next}</small></td>
     <td data-label=""><button type="button" className="bc-basis-btn" onClick={()=>onBasis({kind:"expense",expense:r})}>Основание</button></td>
    </tr>;})}</tbody></table></TableWrap>
   {filter!=="all"&&<p className="bc-note">Показано {shown.length} из {rows.length} — фильтр по загруженным расходам.</p>}
  </>}
  <p className="bc-note">Расходы, относящиеся только к автомобилю, учитываются на автомобиле. Показаны склады, доступные вашей учётной записи; суммы разных валют не складываются. Ввод и согласование — на экране «Дополнительные расходы».</p>
 </section>;
}
