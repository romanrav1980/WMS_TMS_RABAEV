import {useEffect,useRef,useState} from "react";
type Stop={address:string;st_numbers:string[];window_from:string|null;window_to:string|null;arrival_at:string|null;service_finish_at:string|null;wait_min:string|null;late_min:string|null;issues:string[]};
type Segment={code:string;start_at:string;finish_at:string;duration_min?:string;address?:string};
type Report={segments?:Segment[];warnings?:{code:string;address?:string}[];status:string;stops:Stop[];return_at:string|null;depot_address:string|null;issues:{code:string;address?:string}[]};
const labels:Record<string,string>={ROUTE_ROAD_MISSING_STALE_OR_UNSUPPORTED:"Обновите дорожные данные",ROUTE_ORDER_INVALID:"Уточните порядок адресов",DELIVERY_WINDOW_MISSING_OR_DISJOINT:"Задайте пересекающиеся окна СТ",DESTINATION_RULE_INVALID:"Уточните норматив и правило окна адресата",DRIVER_TRIP_DRIVE_LIMIT:"Превышено 540 минут вождения",ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE:"Увеличьте плановое время возврата с учётом перерывов",DELIVERY_WINDOW_MISSING:"Окно доставки не задано",DELIVERY_WINDOWS_HAVE_NO_INTERSECTION:"Окна СТ не пересекаются",
 DESTINATION_ADDRESS_NOT_UNIQUE:"Адрес отсутствует или неоднозначен",DESTINATION_UNLOAD_NORM_UNKNOWN:"Норматив разгрузки неизвестен",DESTINATION_WINDOW_POLICY_UNKNOWN:"Не задана строгость окна",
 DESTINATION_ROAD_DURATION_UNKNOWN:"Дорожное время неизвестно",PREVIOUS_ROUTE_TIME_UNKNOWN:"Время предыдущего этапа неизвестно",
 DELIVERY_HARD_WINDOW_MISSED:"Строгое окно пропущено",DELIVERY_SOFT_WINDOW_MISSED:"Плановое окно пропущено",ROUTE_RETURN_TIME_UNKNOWN:"Возврат не рассчитан",
 ROUTE_DEPARTURE_STAGE_UNKNOWN:"Начало движения неизвестно",WAREHOUSE_DEPOT_NOT_CONFIGURED:"База склада не настроена"};
export function TransportDeliveryWindows({tripId,apiBase,headers,actor}:{tripId:number;apiBase:string;headers:HeadersInit;actor:string}){
 const [zone,setZone]=useState(""),[report,setReport]=useState<Report|null>(null),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 const generation=useRef(0);
 useEffect(()=>{generation.current++;setReport(null);setZone("");setBusy(false);setMessage("");return()=>{generation.current++;};},[tripId,apiBase,actor]);
 async function read(){
  const token=++generation.current;setBusy(true);setReport(null);setMessage("");
  try{
   const q=new URLSearchParams({time_zone:zone});
   const r=await fetch(apiBase+"/api/transport/preflight/trips/"+tripId+"/delivery-windows?"+q,{headers}),v=await r.json();
   if(!r.ok)throw Error(v.detail?.message||"Не удалось прочитать окна");
   if(token===generation.current)setReport(v as Report);
  }catch(e){if(token===generation.current)setMessage(e instanceof Error?e.message:"Оценка недоступна");}
  finally{if(token===generation.current)setBusy(false);}
 }
 return <div><h4>Окна доставки текущего рейса</h4>
  <label>Часовой пояс времени СТ <select value={zone} onChange={e=>{generation.current++;setZone(e.target.value);setReport(null);setBusy(false);}}>
   <option value="">Выберите явно</option><option value="UTC">UTC</option><option value="Europe/Moscow">Москва</option><option value="Asia/Tbilisi">Тбилиси</option>
  </select></label>
  <button disabled={busy||!zone} onClick={()=>void read()}>Оценить прибытие и разгрузку</button>
  {report&&<><p>База: {report.depot_address||"не настроена"}. {report.status==="NO_EARLIEST_WINDOW_VIOLATION"?"В ранней оценке окна соблюдены":report.status==="WINDOW_VIOLATION"?"Есть пропущенные окна":"Недостаточно данных"}.</p>
   <p>Единый расчёт учитывает движение, перерывы по 15 минут после 120 минут вождения, ожидание окна и разгрузку. Это проектные нормы; допуск к выезду оформляется отдельно.</p>
   <table><thead><tr><th>Адрес / СТ</th><th>Окно</th><th>Прибытие</th><th>Конец разгрузки</th><th>Ожидание / опоздание, мин</th><th>Причина</th></tr></thead><tbody>
    {report.stops.map(s=><tr key={s.address}><td>{s.address} / {s.st_numbers.join(", ")}</td><td>{s.window_from||"—"} — {s.window_to||"—"}</td><td>{s.arrival_at||"—"}</td><td>{s.service_finish_at||"—"}</td><td>{s.wait_min??"—"} / {s.late_min??"—"}</td><td>{s.issues.map(x=>labels[x]||"Нужно уточнение").join("; ")}</td></tr>)}
   </tbody></table><p>Возврат на базу: {report.return_at||"не рассчитан"}.</p>
   {report.issues.map((x,i)=><p key={i} role="alert">{x.address?x.address+": ":""}{labels[x.code]||x.code}</p>)}
   {report.warnings?.map((x,i)=><p key={"warning"+i}>Предупреждение: {x.address} — {labels[x.code]||x.code}</p>)}
   {report.segments&&<details><summary>Движение, перерывы и работы по времени</summary><table><thead><tr><th>Действие</th><th>Начало</th><th>Конец</th></tr></thead><tbody>{report.segments.map((s,i)=><tr key={i}><td>{{DRIVE:"Движение",REST:"Отдых",WAIT:"Ожидание",UNLOAD:"Разгрузка"}[s.code]||s.code}</td><td>{s.start_at}</td><td>{s.finish_at}</td></tr>)}</tbody></table></details>}
  </>}{message&&<p role="status">{message}</p>}
 </div>;
}
