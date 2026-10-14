import {TransportTariffSources} from "./TransportTariffSources";
import {BlockStatus,Chip,Money,TableWrap,type BlockState} from "./BillingCostsCommon";
import type {Part,TransportItem,TransportResult} from "./BillingCostsInvoice";
import type {BasisTarget} from "./BillingCostsBasis";

// Нормативные транспортные начисления счёта: источник — проведённая нормативная операция рейса
// (версия нормы, выезд, статьи). Исходный итог и итог с корректировками показываются отдельно.
const names:Record<string,string>={TRANSPORT_VEHICLE:"Автомобиль",TRANSPORT_POINT:"Точки доставки",UNLOAD_PALLET:"Выгрузка паллетой",UNLOAD_ROLL_CAGE:"Закатывание тележки",UNLOAD_MANUAL:"Ручная выгрузка",UNLOAD_EXTRA_LOADER:"Грузчик при затруднённом закатывании"};
const basisName=(b:string)=>b==="TRIP"?"рейс":b==="POINT"?"адрес":b==="PLACE"?"место":b;

function instant(iso?:string){
 if(!iso)return "—";
 const d=new Date(iso);
 return Number.isNaN(d.getTime())?iso:d.toLocaleString("ru-RU");
}

function TransportItemCard({item,onBasis}:{item:TransportItem;onBasis:(t:BasisTarget)=>void}){
 const corrected=item.total!==null&&item.confirmed_total!==null&&item.total!==item.confirmed_total;
 const norm=item.norm||{version:0};
 return <details className="bc-card">
  <summary>
   <span className="bc-card-title">Рейс {item.trip_id} · склад {item.warehouse_id}</span>
   <span className="bc-card-sums">исходно <Money amount={item.total} currency={item.currency}/>{corrected&&<> → с корректировками <Money amount={item.confirmed_total} currency={item.currency}/></>}</span>
   {corrected?<Chip tone="warn" title="После проведения есть подтверждённые корректировки">есть корректировка</Chip>:<Chip tone="ok">без корректировок</Chip>}
   {item.complete===false&&<Chip tone="bad" title="При расчёте не хватило фактов">неполные факты</Chip>}
  </summary>
  <button type="button" className="bc-basis-btn" onClick={()=>onBasis({kind:"transport",item})}>Основание: факты рейса и норма</button>
  <dl className="bc-facts">
   <div><dt>Норма</dt><dd>версия {norm.version}{norm.effective_from?" · с "+norm.effective_from:""}{norm.currency?" · "+norm.currency:""}</dd></div>
   <div><dt>Класс машины</dt><dd>{[norm.vehicle_type,norm.vehicle_size_class].filter(Boolean).join(" · ")||"—"}</dd></div>
   <div><dt>Выгрузка начисляется</dt><dd>{norm.unload_charge_basis==="POINT"?"за адрес":norm.unload_charge_basis==="PLACE"?"за место":"не настроено"}</dd></div>
   <div><dt>Исходный тариф</dt><dd>{[norm.source?.price_name,norm.source?.company].filter(Boolean).join(" / ")||"—"}</dd></div>
   <div><dt>Выезд</dt><dd>{instant(item.departure?.departed_at_instant)}{item.departure?.vehicle_number?" · "+item.departure.vehicle_number:""}</dd></div>
   <div><dt>Мест / адресов</dt><dd>{item.load_count??"—"} / {item.destination_count??"—"}</dd></div>
   <div><dt>Операция</dt><dd><small>{item.operation_id}</small></dd></div>
   <div><dt>Округление</dt><dd>{item.amount_rounding==="HALF_UP_2_PER_ARTICLE"?"по статье, до копеек (HALF_UP)":item.amount_rounding||"—"}</dd></div>
  </dl>
  <TableWrap label={"Статьи рейса "+item.trip_id}><table className="bc-table bc-stack"><thead><tr><th scope="col">Статья</th><th scope="col">Единица</th><th scope="col" className="bc-num">Количество</th><th scope="col" className="bc-num">Ставка</th><th scope="col" className="bc-num">Сумма</th></tr></thead>
   <tbody>{item.lines.map(line=><tr key={line.cost_code}><td data-label="Статья">{names[line.cost_code]||line.cost_code}</td><td data-label="Единица">{basisName(line.basis)}</td><td data-label="Количество" className="bc-num">{line.quantity}</td><td data-label="Ставка" className="bc-num">{line.rate}</td><td data-label="Сумма" className="bc-num"><Money amount={line.amount} currency={item.currency}/></td></tr>)}</tbody></table></TableWrap>
 </details>;
}

export function BillingTransportCosts({part,reload,onBasis}:{part:Part<TransportResult>;reload:()=>void;onBasis:(t:BasisTarget)=>void}){
 const data=part.data;
 const state:BlockState=part.loading?"loading":part.error?"error":data&&!data.items.length?"empty":"ready";
 return <section className="bc-block" aria-labelledby="bcTransportTitle"><h4 id="bcTransportTitle">Нормативные транспортные затраты <Chip tone="idle">внутренние</Chip></h4>
  <BlockStatus state={state} error={part.error} empty="Транспортные начисления по рейсам этого счёта ещё не проведены." onRetry={reload}/>
  {state==="ready"&&data&&<>
   <p className="bc-note">{data.currency_totals.map(t=><span key={t.currency} className="bc-pair">{t.currency}: исходно {t.amount}, с корректировками {t.confirmed_amount}</span>)}</p>
   {data.items.map(item=><TransportItemCard key={item.operation_id} item={item} onBasis={onBasis}/>)}
  </>}
  {data&&data.sources.length>0&&<details className="bc-details"><summary>Тарифы и нормы рейсов счёта ({data.sources.length})</summary>
   {data.sources.map(source=><TransportTariffSources key={source.trip+":"+source.warehouse} {...source}/>)}
  </details>}
  <p className="bc-note">Это внутренние нормативные затраты. Прежняя сумма счёта перевозчика хранится отдельно; прибавлять к ней эти статьи нельзя.</p>
 </section>;
}
