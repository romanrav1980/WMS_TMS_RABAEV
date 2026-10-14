import {useEffect,useRef,useState} from "react";
export type RoadAdvice={source_hash:string;road_snapshot_signature:string;drive_min:number|null;drive_back_min:number|null};
type Leg={from_address:string;to_address:string;duration_min:string|null;distance_km:string|null;provider:string|null;unknown_reason:string|null};
type Report=RoadAdvice&{depot_address?:string;status:string;legs:Leg[];source_issues:string[]};
const labels:Record<string,string>={MATRIX_PAIR_MISSING:"Нет пары в матрице",MATRIX_PAIR_STALE:"Матрица устарела",
 DISTANCE_SPEED_TIME_IS_ESTIMATE:"Время рассчитано по условной скорости",MATRIX_DURATION_UNKNOWN:"Время неизвестно",
 DEPOT_OR_STOP_REPEATED_WITHOUT_ROAD_LEG:"Адрес отправления совпадает с остановкой",
 STOP_ADDRESS_OR_ORDER_UNKNOWN:"Не задан адрес или порядок остановки",STOP_ORDER_INVALID:"Некорректный порядок остановок",
 DIFFERENT_STOPS_HAVE_EQUAL_ORDER:"У разных остановок одинаковый порядок",TRIP_HAS_NO_DESTINATION_MEMBERS:"В рейсе нет адресов доставки",WAREHOUSE_DEPOT_NOT_CONFIGURED:"База отправления склада не настроена"};
export function TransportRoadLegs({tripId,apiBase,headers,actor,onChoose}:{tripId:number;apiBase:string;headers:HeadersInit;actor:string;onChoose:(v:RoadAdvice)=>void}){
 const [depot,setDepot]=useState(""),[report,setReport]=useState<Report|null>(null),[message,setMessage]=useState(""),[busy,setBusy]=useState(false);
 const generation=useRef(0);
 useEffect(()=>{generation.current++;setDepot("");setReport(null);setMessage("");setBusy(false);return()=>{generation.current++;};},[tripId,apiBase,actor]);
 async function read(){
  const token=++generation.current;setBusy(true);setReport(null);setMessage("");
  try{
   const q=new URLSearchParams({depot_address:depot.trim(),max_age_hours:"24"});
   const r=await fetch(apiBase+"/api/transport/preflight/trips/"+tripId+"/road-legs?"+q,{headers}),v=await r.json();
   if(!r.ok)throw Error(v.detail?.message||"Не удалось прочитать матрицу");
   if(token===generation.current)setReport(v as Report);
  }catch(e){if(token===generation.current)setMessage(e instanceof Error?e.message:"Матрица недоступна");}
  finally{if(token===generation.current)setBusy(false);}
 }
 const usable=report?.status==="ROAD_PROFILE_ESTIMATE_AVAILABLE"&&report.drive_min!==null&&report.drive_back_min!==null&&report.drive_min>0&&report.drive_back_min>0&&report.drive_min<=1440&&report.drive_back_min<=1440;
 return <div><h4>Время по дорожной матрице</h4>
  <label>Адрес отправления (пусто — база склада), код справочника <input maxLength={200} value={depot} onChange={e=>{generation.current++;setDepot(e.target.value);setReport(null);setBusy(false);}}/></label>
  <button disabled={busy} onClick={()=>void read()}>Прочитать существующую матрицу</button>
  {report&&<><p>{report.status==="ROAD_PROFILE_ESTIMATE_AVAILABLE"?"Длительности дорожного профиля доступны":"Дорожное время не определено"}.
   Использованный адрес отправления: {report.depot_address||"не определён"}. Проверка ограничений автомобиля и окон доставки требуется отдельно.</p>
   <table><thead><tr><th>Откуда</th><th>Куда</th><th>км</th><th>мин</th><th>Источник / причина</th></tr></thead><tbody>
    {report.legs.map((leg,i)=><tr key={i}><td>{leg.from_address}</td><td>{leg.to_address}</td><td>{leg.distance_km??"—"}</td><td>{leg.duration_min??"—"}</td><td>{leg.unknown_reason?(labels[leg.unknown_reason]||"Не подтверждено"):leg.provider}</td></tr>)}
   </tbody></table>
   {report.source_issues.map(x=><p key={x}>{labels[x]||"Нужно уточнить исходный маршрут"}</p>)}
   <button disabled={!usable} onClick={()=>onChoose(report)}>Подставить в оценку диспетчера</button>
  </>}
  {message&&<p role="status">{message}</p>}
 </div>;
}
