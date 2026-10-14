import {TransportCostPreview} from "./TransportCostPreview";
import {useEffect,useRef,useState} from "react";
import {apiFetch} from "../../api";
import {TransportNormPublisher} from "./TransportNormPublisher";
import {TransportNormHistory} from "./TransportNormHistory";
import type {TransportNorm as Norm} from "./TransportNormPublisher";
type Candidate={id:number;price_name:string;company:string;vehicle_rate:string;hour_rate:string;point_rate:string;match_kind:string;published_norm:Norm|null};
type Source={trip_id:number;warehouse_id:number;carrier:string|null;vehicle_type:string;legacy_region_key:string;candidates:Candidate[];selection_state:string;actual_receipt_count:number;receipt_address_count:number};
export function TransportTariffSources({trip,warehouse}:{trip:number;warehouse:number}){
 const epoch=useRef(0);
 const [data,setData]=useState<Source|null>(null),[error,setError]=useState(""),[busy,setBusy]=useState(false);
 useEffect(()=>{epoch.current++;setData(null);setError("");setBusy(false);return()=>{epoch.current++;};},[trip,warehouse]);
 async function read(throwErrors=false){
  const requestEpoch=++epoch.current;setBusy(true);setError("");
  try{const result=await apiFetch<Source>(`/api/finance/logistics-costs/trips/${trip}/transport-tariff-sources?warehouse_id=${warehouse}`);if(requestEpoch===epoch.current)setData(result);}
  catch(e){if(requestEpoch===epoch.current)setError(e instanceof Error?e.message:"Не удалось прочитать тариф.");if(throwErrors)throw e;}
  finally{if(requestEpoch===epoch.current)setBusy(false);}
 }
 const current=data?.trip_id===trip&&data.warehouse_id===warehouse?data:null;
 return <section aria-label="Тариф перевозки">
  <button type="button" title="Прочитать исходные тарифы и опубликованные версии без начисления расходов" onClick={()=>void read()} disabled={busy}>{busy?"Загрузка…":`Тариф перевозки рейса ${trip}, склад ${warehouse}`}</button>
  {error&&<p role="alert">{error}</p>}
  {current&&<><p>Перевозчик: {current.carrier||"не указан"}. Тип машины: {current.vehicle_type}. Региональный ключ: {current.legacy_region_key}.</p>
   {current.candidates.length===0?<p>Подходящий транспортный тариф не настроен.</p>:<table><thead><tr><th>Исходный тариф</th><th>Автомобиль</th><th>Час</th><th>Точка</th><th>Последняя опубликованная норма</th></tr></thead>
    <tbody>{current.candidates.map((r,i)=><tr key={r.id+":"+i}><td>{r.price_name} / {r.company}</td><td>{r.vehicle_rate}</td><td>{r.hour_rate}</td><td>{r.point_rate}</td>
    <td>{r.published_norm?<>{r.published_norm.currency}, версия {r.published_norm.version}, с {r.published_norm.effective_from}; класс {r.published_norm.vehicle_size_class}<small>Сохранённые ставки: автомобиль {r.published_norm.source.vehicle_rate}, час {r.published_norm.source.hour_rate}, точка {r.published_norm.source.point_rate}.</small><small>Начисление {r.published_norm.unload_charge_basis==="POINT"?"за адрес":r.published_norm.unload_charge_basis==="PLACE"?"за место":"не настроено"}, паллетой {r.published_norm.pallet_unload_rate??"не задано"}. Выгрузка тележки {r.published_norm.rolling_unload_rate}, вручную {r.published_norm.manual_unload_rate}, дополнительный грузчик {r.published_norm.loader_rate}.</small></>:"Валюта, период и нормы выгрузки требуют настройки"}</td></tr>)}</tbody></table>}
   {current.candidates.map((r,i)=><TransportNormPublisher key={warehouse+":"+r.id+":"+i} warehouse={warehouse} source={r.id} vehicleType={current.vehicle_type} norm={r.published_norm} onPublished={()=>read(true)}/>)}
   {current.candidates.map((r,i)=><TransportCostPreview key={warehouse+":"+r.id+":"+i} warehouse={warehouse} trip={trip} source={r.id}/>)}
   {current.candidates.map((r,i)=><TransportNormHistory key={warehouse+":"+r.id+":"+i} warehouse={warehouse} source={r.id}/>)}
   <p>Зафиксировано приёмок: {current.actual_receipt_count}, адресов: {current.receipt_address_count}. Способ выгрузки и работа грузчика подтверждаются отдельно. Просмотр тарифа не начисляет расходы.</p>
  </>}
 </section>;
}
