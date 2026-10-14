import {useEffect,useRef,useState} from "react";
import {apiFetch} from "../../api";
import type {TransportNorm} from "./TransportNormPublisher";
type Page={warehouse_id:number;source_price_id:number;items:Array<{version:number;actor:string;created_at:string;reason:string;decision_reference:string;norm:TransportNorm}>;has_more:boolean;next_before_version:number|null};
export function TransportNormHistory({warehouse,source}:{warehouse:number;source:number}){
 const epoch=useRef(0),running=useRef(false);
 const [page,setPage]=useState<Page|null>(null),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 useEffect(()=>{epoch.current++;setPage(null);setBusy(false);setMessage("");return()=>{epoch.current++;};},[warehouse,source]);
 async function read(before?:number){
  if(running.current)return;running.current=true;const version=++epoch.current;setBusy(true);setMessage("");
  try{
   const result=await apiFetch<Page>(`/api/finance/logistics-costs/warehouses/${warehouse}/transport-norms/${source}/history?limit=30`+(before?`&before_version=${before}`:""));
   if(version===epoch.current)setPage(result);
  }catch(e){if(version===epoch.current)setMessage(String(e));}
  finally{running.current=false;if(version===epoch.current)setBusy(false);}
 }
 const current=page?.warehouse_id===warehouse&&page.source_price_id===source?page:null;
 return <details><summary title="Посмотреть сохранённые редакции транспортной нормы и основания изменений">История транспортной нормы {source}</summary>
  <button type="button" title="Получить последние 30 редакций нормы" disabled={busy} onClick={()=>void read()}>Последние редакции</button>
  {current&&<><table><thead><tr><th>Версия / действие</th><th>Ставки</th><th>Условия</th><th>Кем утверждено / основание</th></tr></thead><tbody>
   {current.items.map(r=><tr key={r.version}><td>{r.version} / {r.norm.effective_from}<small>{r.norm.currency}, {r.norm.timezone_region}</small></td>
    <td>Автомобиль {r.norm.source.vehicle_rate}, час {r.norm.source.hour_rate}, точка {r.norm.source.point_rate}</td>
    <td>{r.norm.vehicle_size_class}; {r.norm.unload_charge_basis==="PLACE"?"за место":r.norm.unload_charge_basis==="POINT"?"за адрес":"единица не задана"}; паллета {r.norm.pallet_unload_rate??"не задано"}; тележка {r.norm.rolling_unload_rate}, вручную {r.norm.manual_unload_rate}, грузчик {r.norm.loader_rate}</td>
    <td>{r.actor} / {r.created_at}<small>{r.reason}; {r.decision_reference}</small></td></tr>)}
  </tbody></table>{!current.items.length&&<p>Опубликованных редакций нет.</p>}
  {current.has_more&&current.next_before_version!==null&&<button type="button" title="Получить предыдущие 30 редакций по номеру версии" disabled={busy} onClick={()=>void read(current.next_before_version!)}>Предыдущие редакции</button>}</>}
  {message&&<p role="alert">{message}</p>}
 </details>;
}
