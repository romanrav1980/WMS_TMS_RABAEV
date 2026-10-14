import {useEffect,useRef,useState,type ReactNode} from "react";
import {apiFetch} from "../../api";
import {Chip,Money,readError} from "./BillingCostsCommon";
import type {CostLine,Expense,TransportItem,TransportResult,WarehouseSummary} from "./BillingCostsInvoice";

// Основание любой суммы счёта (NI07.1): документ или исходное начисление, из которого она получена.
// Используются только существующие GET: история ставок склада, факты транспортного начисления,
// реестр расходов склада и нормативные основания коррекций. Ничего не начисляется и не меняется.

export type BasisTarget=
 |{kind:"warehouse";title:string;lines:CostLine[]}
 |{kind:"transport";item:TransportItem}
 |{kind:"expense";expense:Expense};

type RateVersion={version_no:number;rate_value:string;effective_from:string|null;basis:string|null;reason_text:string|null;decision_reference:string|null;actor:string|null};
type Facts={departure?:Record<string,unknown>|null;unloads:Array<{load_operation_id:string;address:string;receipt_operation_id:string;method:string;rolling_difficult:boolean;loader_present:boolean;evidence_reference:string|null;started_at_instant:string;finished_at_instant:string}>;missing:Array<{reason:string;address?:string;load_operation_id?:string}>;complete:boolean};
type ExpenseRow={operation_id:string;article_code:string;expense_date:string|null;document_reference:string|null;reporter:string|null;logist_operation_id:string|null;logist_outcome:string|null;logist_actor:string|null;finance_operation_id:string|null;finance_outcome:string|null;allocation_operation_id:string|null;confirmed_total:string|null};

export type Loaded={warehouse:WarehouseSummary|null;transport:TransportResult|null;expenses:Expense[]|null};

// Склад рейса по уже прочитанным начислениям того же счёта (в строке расхода API склад не возвращает).
function wareOfTrip(trip:number,loaded:Loaded):number|undefined{
 return loaded.warehouse?.lines.find(l=>l.tt_id===trip)?.ware_id??loaded.transport?.items.find(i=>i.trip_id===trip)?.warehouse_id;
}

function useLazy<T>(key:string|null,load:()=>Promise<T>){
 const [state,setState]=useState<{data:T|null;error:string;loading:boolean}>({data:null,error:"",loading:false});
 const epoch=useRef(0);
 useEffect(()=>{
  const current=++epoch.current;
  if(!key){setState({data:null,error:"",loading:false});return;}
  setState({data:null,error:"",loading:true});
  load().then(data=>{if(current===epoch.current)setState({data,error:"",loading:false});})
   .catch(e=>{if(current===epoch.current)setState({data:null,error:readError(e,"основания"),loading:false});});
  // eslint-disable-next-line react-hooks/exhaustive-deps
 },[key]);
 return state;
}

const Row=({k,v}:{k:string;v:ReactNode})=><div><dt>{k}</dt><dd>{v??"—"}</dd></div>;

function WarehouseBasis({target}:{target:Extract<BasisTarget,{kind:"warehouse"}>}){
 const first=target.lines[0];
 const key=first?first.ware_id+":"+first.currency:null;
 const history=useLazy<RateVersion[]>(key,()=>apiFetch(`/api/finance/logistics-costs/warehouses/${first.ware_id}/rates/history?currency=${first.currency}&limit=100`));
 const versions=new Set(target.lines.map(l=>l.version_no));
 const used=(history.data||[]).filter(v=>versions.has(v.version_no));
 return <>
  <h5>Исходные начисления ({target.lines.length})</h5>
  <ul className="bc-basis-list">{target.lines.map(l=><li key={l.operation_id+l.load_operation_id+l.cost_code+l.rate_date}>
   Рейс <b>{l.tt_id}</b> · склад {l.ware_id} · {String(l.quantity)} × {l.rate_value} = <Money amount={l.amount} currency={l.currency}/>
   <small className="bc-sub">операция начисления {l.operation_id} · погрузка {l.load_operation_id} · версия ставки {l.version_no}</small></li>)}</ul>
  <h5>Версия ставки — основание расчёта</h5>
  {history.loading?<p className="bc-state bc-loading">Читаем историю ставок…</p>:history.error?<p className="bc-state bc-error">{history.error}</p>:
   used.length===0?<p className="bc-state bc-empty">Версия {[...versions].join(", ")} не найдена среди последних 100 версий ставки склада {first?.ware_id}.</p>:
   used.map(v=><dl key={v.version_no} className="bc-facts"><Row k="Версия" v={v.version_no}/><Row k="Ставка" v={v.rate_value}/><Row k="Действует с" v={v.effective_from}/><Row k="Основа" v={v.basis}/><Row k="Документ решения" v={v.decision_reference}/><Row k="Причина" v={v.reason_text}/><Row k="Автор" v={v.actor}/></dl>)}
 </>;
}

function TransportBasis({item}:{item:TransportItem}){
 const facts=useLazy<Facts>(item.operation_id,()=>apiFetch(`/api/finance/logistics-costs/trips/${item.trip_id}/transport-cost-facts?warehouse_id=${item.warehouse_id}`));
 const dep=(facts.data?.departure||item.departure||{}) as Record<string,unknown>;
 return <>
  <dl className="bc-facts"><Row k="Операция начисления" v={item.operation_id}/><Row k="Норма" v={"версия "+item.norm?.version}/><Row k="Выезд (операция)" v={String(dep.departure_operation_id??"—")}/><Row k="Машина" v={String(dep.vehicle_number??dep.vehicle_id??"—")}/></dl>
  <h5>Факты расчёта: приёмки и выгрузки</h5>
  {facts.loading?<p className="bc-state bc-loading">Читаем факты рейса…</p>:facts.error?<p className="bc-state bc-error">{facts.error}</p>:facts.data&&<>
   {!facts.data.complete&&<p className="bc-state bc-error">Факты неполные: {facts.data.missing.map(m=>m.reason+(m.address?" ("+m.address+")":"")).join("; ")}</p>}
   <ul className="bc-basis-list">{facts.data.unloads.map(u=><li key={u.receipt_operation_id+u.address}>
    {u.address} · {u.method==="PALLET"?"паллетой":u.method==="ROLL_CAGE"?"тележкой":u.method==="MANUAL"?"вручную":u.method}{u.rolling_difficult?" · затруднённо":""}{u.loader_present?" · с грузчиком":""}
    <small className="bc-sub">приёмка {u.receipt_operation_id} · погрузка {u.load_operation_id} · документ-доказательство {u.evidence_reference||"—"}</small></li>)}</ul>
   {facts.data.unloads.length===0&&<p className="bc-state bc-empty">Фактов выгрузки нет.</p>}
  </>}
 </>;
}

function ExpenseBasis({expense,loaded,onOpen}:{expense:Expense;loaded:Loaded;onOpen:(t:BasisTarget)=>void}){
 const ware=wareOfTrip(expense.tt_id,loaded);
 const list=useLazy<ExpenseRow[]>(ware?expense.operation_id+":"+ware:null,()=>apiFetch(`/api/finance/logistics-expenses/warehouses/${ware}`));
 const row=list.data?.find(r=>r.operation_id===expense.operation_id);
 const correctedCost=expense.cost_correction_of_op?loaded.transport?.items.find(i=>i.operation_id===expense.cost_correction_of_op):undefined;
 const correctedExpense=expense.correction_of_op?loaded.expenses?.find(e=>e.operation_id===expense.correction_of_op):undefined;
 return <>
  <dl className="bc-facts"><Row k="Документ-основание" v={expense.document_reference||"не указан"}/><Row k="Операция расхода" v={expense.operation_id}/><Row k="Рейс" v={expense.tt_id}/><Row k="Сумма" v={<Money amount={expense.amount} currency={expense.currency}/>}/>
   {expense.allocation_operation_id&&<Row k="Распределение" v={expense.allocation_operation_id+" · "+(expense.distribution_basis||"—")+" · строк "+expense.goods_lines}/>}</dl>
  {(expense.cost_correction_of_op||expense.correction_of_op)&&<><h5>Исходное начисление, которое корректируется</h5>
   {correctedCost?<button type="button" onClick={()=>onOpen({kind:"transport",item:correctedCost})}>Открыть основание начисления {correctedCost.operation_id} (рейс {correctedCost.trip_id})</button>:
    correctedExpense?<button type="button" onClick={()=>onOpen({kind:"expense",expense:correctedExpense})}>Открыть исходный расход {correctedExpense.operation_id}</button>:
    <p className="bc-note">Исходная операция {expense.cost_correction_of_op||expense.correction_of_op} не входит в этот счёт; её основание — в реестре затрат склада.</p>}</>}
  <h5>Решения по расходу</h5>
  {!ware?<p className="bc-state bc-empty">Склад расхода не возвращён API счёта и не определяется по начислениям этого рейса. Решения доступны на экране «Дополнительные расходы»; запрошено расширение ответа (K-0007).</p>:
   list.loading?<p className="bc-state bc-loading">Читаем реестр расходов склада {ware}…</p>:list.error?<p className="bc-state bc-error">{list.error}</p>:
   !row?<p className="bc-state bc-empty">Расход не найден среди последних 100 записей склада {ware}.</p>:
   <dl className="bc-facts"><Row k="Дата расхода" v={row.expense_date}/><Row k="Заявил" v={row.reporter}/><Row k="Логист" v={row.logist_outcome?row.logist_outcome+" · "+(row.logist_actor||"")+" · "+row.logist_operation_id:"решения нет"}/><Row k="Финансы" v={row.finance_outcome?row.finance_outcome+" · "+row.finance_operation_id:"решения нет"}/><Row k="Итог с коррекциями" v={row.confirmed_total}/></dl>}
 </>;
}

export function BasisPanel({target,loaded,onOpen,onClose}:{target:BasisTarget;loaded:Loaded;onOpen:(t:BasisTarget)=>void;onClose:()=>void}){
 const title=target.kind==="warehouse"?"Складское начисление: "+target.title:target.kind==="transport"?"Транспортное начисление рейса "+target.item.trip_id:"Дополнительный расход: "+target.expense.article_name;
 return <section className="bc-basis" aria-label="Основание суммы" tabIndex={-1}>
  <div className="bc-basis-head"><h4>Основание · {title}</h4><button type="button" onClick={onClose} aria-label="Закрыть основание">×</button></div>
  {target.kind==="warehouse"&&<WarehouseBasis target={target}/>}
  {target.kind==="transport"&&<TransportBasis item={target.item}/>}
  {target.kind==="expense"&&<ExpenseBasis expense={target.expense} loaded={loaded} onOpen={onOpen}/>}
  <p className="bc-note"><Chip tone="idle">только чтение</Chip> Основания читаются из действующих реестров; сумма и проводка здесь не меняются.</p>
 </section>;
}

// Выгрузка всех оснований счёта из уже прочитанных данных — доступна всегда, без новых запросов.
export function basisCsv(invoiceId:number,loaded:Loaded):string{
 const rows:string[][]=[["Категория","Рейс","Склад","Операция","Основание","Версия/норма","Количество","Ставка","Сумма","Валюта"]];
 for(const l of loaded.warehouse?.lines||[])rows.push(["Складское",String(l.tt_id),String(l.ware_id),l.operation_id,"погрузка "+l.load_operation_id,"ставка v"+l.version_no,String(l.quantity),l.rate_value,l.amount,l.currency]);
 for(const i of loaded.transport?.items||[])for(const line of i.lines)rows.push(["Транспорт: "+line.cost_code,String(i.trip_id),String(i.warehouse_id),i.operation_id,"выезд "+(i.departure?.departure_operation_id||"—"),"норма v"+i.norm?.version,String(line.quantity),line.rate,line.amount,i.currency]);
 for(const e of loaded.expenses||[])rows.push(["Допрасход: "+e.article_name,String(e.tt_id),"",e.operation_id,"документ "+(e.document_reference||"—")+(e.cost_correction_of_op?" · коррекция "+e.cost_correction_of_op:e.correction_of_op?" · коррекция "+e.correction_of_op:""),e.finance_outcome||"на согласовании","","",e.amount,e.currency]);
 const esc=(v:string)=>/[";\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;
 return "﻿"+`Основания счёта ${invoiceId}\n`+rows.map(r=>r.map(esc).join(";")).join("\n");
}

export function downloadBasis(invoiceId:number,loaded:Loaded){
 const url=URL.createObjectURL(new Blob([basisCsv(invoiceId,loaded)],{type:"text/csv;charset=utf-8"}));
 const a=document.createElement("a");a.href=url;a.download=`osnovaniya_scheta_${invoiceId}.csv`;a.click();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
}
