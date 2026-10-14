import {TransportCostConduct} from "./TransportCostConduct";
import {useEffect,useRef,useState} from "react";
import {apiFetch} from "../../api";
type Preview={trip_id:number;warehouse_id:number;currency:string|null;complete:boolean;total:string|null;cost_posted:boolean;confirmed_total?:string;norm:{version:number}|null;lines:Array<{cost_code:string;quantity:number;rate:string;amount:string}>;missing:Array<{reason:string;address?:string}>};
const reasons:Record<string,string>={ACTUAL_UNLOADING_REQUIRED:"Нет завершённой выгрузки",CONFIRMED_BILLABLE_HOURS_REQUIRED:"Нет подтверждённого оплачиваемого времени",EXPLICIT_UNLOAD_NORM_REQUIRED:"Не задана единица начисления или ставка паллеты",MIXED_METHOD_AT_POINT:"На адресе использованы разные способы выгрузки",EXTRA_LOADER_CHARGE_RULE_REQUIRED:"Не определено договорное правило дополнительного грузчика"};
export function TransportCostPreview({trip,warehouse,source}:{trip:number;warehouse:number;source:number}){
 const epoch=useRef(0),running=useRef(false);
 const [preview,setPreview]=useState<Preview|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState("");
 useEffect(()=>{epoch.current++;setPreview(null);setError("");setBusy(false);return()=>{epoch.current++;};},[trip,warehouse,source]);
 async function read(forRecovery=false){
  if(running.current)return;running.current=true;const version=++epoch.current;setBusy(true);setError("");setPreview(null);
  try{
   const saved=await apiFetch<{recognized:Preview|null;confirmed_total:string}>("/api/finance/logistics-costs/trips/"+trip+"/transport-costs?warehouse_id="+warehouse);
   const result=(saved.recognized?{...saved.recognized,confirmed_total:saved.confirmed_total}:null)??await apiFetch<Preview>("/api/finance/logistics-costs/trips/"+trip+"/transport-cost-preview?warehouse_id="+warehouse+"&source_price_id="+source);
   if(version===epoch.current)setPreview(result);
  }catch(e){if(version===epoch.current)setError(String(e));if(forRecovery)throw e;}
  finally{running.current=false;if(version===epoch.current)setBusy(false);}
 }
 const current=preview?.trip_id===trip&&preview.warehouse_id===warehouse?preview:null;
 return <details><summary>Расчёт по фактам рейса, тариф {source}</summary>
  <button type="button" title="Получить расчёт по сохранённым фактам выезда, приёмки и выгрузки" disabled={busy} onClick={()=>void read()}>{busy?"Расчёт…":"Рассчитать по фактам"}</button>
  {error&&<p role="alert">{error}</p>}
  {current&&<><p>{current.complete?"Расчёт подготовлен":"Начисление требует данных"}. Валюта: {current.currency||"не определена"}.</p>
   {current.missing.map((m,i)=><p key={i}>{reasons[m.reason]||m.reason}{m.address?": "+m.address:""}</p>)}
   <table><thead><tr><th>Статья</th><th>Количество</th><th>Ставка</th><th>Сумма</th></tr></thead><tbody>{current.lines.map((line,i)=><tr key={i}><td>{line.cost_code}</td><td>{line.quantity}</td><td>{line.rate}</td><td>{line.amount}</td></tr>)}</tbody></table>
   {!current.cost_posted&&current.complete&&current.norm&&current.currency&&<TransportCostConduct trip={trip} warehouse={warehouse} source={source} version={current.norm.version} currency={current.currency} onRefresh={()=>read(true)}/>}
   {current.cost_posted&&<p>Подтверждённый итог с корректировками: {current.confirmed_total} {current.currency}.</p>}
   <p>Исходное начисление: {current.total??"не определено"}. {current.cost_posted?"Затраты проведены и сохранены.":"Предварительный расчёт; расходы ещё не проведены."}</p>
  </>}
 </details>;
}
