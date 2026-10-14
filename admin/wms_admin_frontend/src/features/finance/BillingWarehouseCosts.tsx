import {useEffect,useRef,useState} from "react";
import {BillingTransportCosts} from "./BillingTransportCosts";
import {BillingExtraExpenses} from "./BillingExtraExpenses";
import {BillingCostsSummary} from "./BillingCostsSummary";
import {BlockStatus,Chip,Money,TableWrap,type BlockState} from "./BillingCostsCommon";
import {useInvoiceCosts,type CostGroup,type CostLine,type Part,type WarehouseSummary} from "./BillingCostsInvoice";
import {BasisPanel,downloadBasis,type BasisTarget} from "./BillingCostsBasis";

// Расшифровка существующего счёта (NI07.1): сводка по валютам, складские и транспортные начисления,
// дополнительные расходы. Только чтение источников; расчёт и проведение остаются у владельцев.
function period(row:{rate_date?:string|null;period_mode?:string|null;period_time_zone?:string|null;period_policy_version?:number|null}){
 if(!row.rate_date)return <span className="bc-muted">Ранее проведённое начисление (дата не сохранялась)</span>;
 return <>{row.rate_date}<small className="bc-sub">{row.period_mode==="CASE_ASSEMBLY"?"по началу сборки коробки":"по погрузке, UTC"}{row.period_time_zone?" · "+row.period_time_zone:""}{row.period_policy_version!=null?" · политика v"+row.period_policy_version:""}</small></>;
}

const partState=<T,>(p:Part<T>,empty:(d:T)=>boolean):BlockState=>p.loading?"loading":p.error?"error":p.data&&empty(p.data)?"empty":"ready";

export function BillingWarehouseCosts({invoiceId}:{invoiceId:number}){
 const costs=useInvoiceCosts(invoiceId);
 const [basis,setBasis]=useState<BasisTarget|null>(null);
 const panel=useRef<HTMLDivElement>(null);
 useEffect(()=>{setBasis(null);},[invoiceId]);
 const open=(t:BasisTarget)=>{setBasis(t);requestAnimationFrame(()=>panel.current?.scrollIntoView({block:"nearest",behavior:"smooth"}));};
 const loaded={warehouse:costs.warehouse.data,transport:costs.transport.data,expenses:costs.expenses.data};
 const busy=costs.warehouse.loading||costs.transport.loading||costs.expenses.loading;
 const any=!!(loaded.warehouse?.lines.length||loaded.transport?.items.length||loaded.expenses?.length);
 return <div className="bc-root" aria-label="Расшифровка счёта">
  <div className="bc-root-head"><h3>Расшифровка счёта</h3><div className="bc-actions">
   <button type="button" onClick={()=>downloadBasis(invoiceId,loaded)} disabled={busy||!any} title="Все начисления и расходы счёта с операциями, документами и версиями ставок — из прочитанных данных">Скачать основания (CSV)</button>
   <button type="button" onClick={costs.reload} disabled={busy} title="Перечитать источники начислений этого счёта">Обновить расшифровку</button></div></div>
  <BillingCostsSummary warehouse={costs.warehouse} transport={costs.transport} expenses={costs.expenses} readAt={costs.readAt}/>
  <div ref={panel}>{basis&&<BasisPanel target={basis} loaded={loaded} onOpen={open} onClose={()=>setBasis(null)}/>}</div>
  <WarehouseSection part={costs.warehouse} reload={costs.reload} onBasis={open}/>
  <BillingTransportCosts part={costs.transport} reload={costs.reload} onBasis={open}/>
  <BillingExtraExpenses part={costs.expenses} reload={costs.reload} onBasis={open}/>
 </div>;
}

const sameGroup=(g:CostGroup,l:CostLine)=>l.ware_id===g.ware_id&&(l.rate_date??null)===g.rate_date&&l.cost_code===g.cost_code&&l.currency===g.currency&&l.version_no===g.version_no&&l.rate_value===g.rate_value;

function WarehouseSection({part,reload,onBasis}:{part:Part<WarehouseSummary>;reload:()=>void;onBasis:(t:BasisTarget)=>void}){
 const [trip,setTrip]=useState("");
 const data=part.data,state=partState(part,d=>d.lines.length===0);
 const lines=(data?.lines||[]).filter(l=>!trip||String(l.tt_id).includes(trip.trim()));
 return <section className="bc-block" aria-labelledby="bcWarehouseTitle">
  <h4 id="bcWarehouseTitle">Складские затраты рейсов <Chip tone="idle" title="Исходные признанные начисления; коррекции и допрасходы показаны отдельно">исходные</Chip></h4>
  <BlockStatus state={state} error={part.error} empty="Складские начисления по рейсам этого счёта ещё не проведены или склады недоступны вашей учётной записи." onRetry={reload}/>
  {state==="ready"&&data&&<>
   <p className="bc-note">Склады в расчёте: {(data.visible_warehouses||[]).join(", ")||"—"} · строк источников: {data.lines.length}. Ставка и версия зафиксированы при начислении.</p>
   <TableWrap label="Складские начисления по ставке и периоду"><table className="bc-table bc-stack"><thead><tr><th scope="col">Склад</th><th scope="col">Расчётный период</th><th scope="col">Статья</th><th scope="col" className="bc-num">Количество</th><th scope="col" className="bc-num">Ставка · версия</th><th scope="col">Рейсы</th><th scope="col" className="bc-num">Начислено</th><th scope="col"><span className="bc-sr">Основание</span></th></tr></thead>
    <tbody>{data.groups.map((g:CostGroup,i)=><tr key={i}><td data-label="Склад">{g.ware_id}</td><td data-label="Период">{period(g)}</td><td data-label="Статья">{g.cost_code}<small className="bc-sub">{g.basis}</small></td><td data-label="Количество" className="bc-num">{g.quantity}</td><td data-label="Ставка" className="bc-num">{g.rate_value}<small className="bc-sub">версия {g.version_no}</small></td><td data-label="Рейсы">{g.trips.join(", ")}<small className="bc-sub">источников: {g.source_count}</small></td><td data-label="Начислено" className="bc-num"><Money amount={g.amount} currency={g.currency}/></td>
     <td data-label=""><button type="button" className="bc-basis-btn" onClick={()=>onBasis({kind:"warehouse",title:g.cost_code+" · склад "+g.ware_id+" · v"+g.version_no,lines:data.lines.filter(l=>sameGroup(g,l))})}>Основание</button></td></tr>)}</tbody></table></TableWrap>
   <details className="bc-details"><summary>Источники начислений по рейсам ({data.lines.length})</summary>
    <label className="bc-filter">Рейс<input value={trip} onChange={e=>setTrip(e.target.value)} inputMode="numeric" placeholder="Номер рейса"/></label>
    <TableWrap label="Источники складских начислений"><table className="bc-table bc-stack"><thead><tr><th scope="col">Рейс · склад</th><th scope="col">Погрузка</th><th scope="col" className="bc-num">Количество</th><th scope="col" className="bc-num">Ставка</th><th scope="col">Версия</th><th scope="col">Период</th><th scope="col" className="bc-num">Сумма</th><th scope="col"><span className="bc-sr">Основание</span></th></tr></thead>
     <tbody>{lines.map((r:CostLine)=><tr key={r.operation_id+":"+r.load_operation_id+":"+r.cost_code+":"+r.currency+":"+r.rate_date}><td data-label="Рейс · склад">{r.tt_id} · {r.ware_id}<small className="bc-sub">операция {r.operation_id}</small></td><td data-label="Погрузка"><small>{r.load_operation_id}</small></td><td data-label="Количество" className="bc-num">{String(r.quantity)}</td><td data-label="Ставка" className="bc-num">{r.rate_value}{r.components&&<small className="bc-sub">комплектация {r.components.picking_rate} + общие работы {r.components.common_work_rate} ({r.components.month})</small>}</td><td data-label="Версия">{r.version_no}</td><td data-label="Период">{period(r)}</td><td data-label="Сумма" className="bc-num"><Money amount={r.amount} currency={r.currency}/></td>
      <td data-label=""><button type="button" className="bc-basis-btn" onClick={()=>onBasis({kind:"warehouse",title:"рейс "+r.tt_id+" · "+r.cost_code,lines:[r]})}>Основание</button></td></tr>)}</tbody></table></TableWrap>
     {trip&&<p className="bc-note">Показано {lines.length} из {data.lines.length} строк — фильтр по загруженным источникам.</p>}
   </details>
  </>}
 </section>;
}
