import {useEffect,useRef,useState} from "react";
type Snapshot={temporal?:{status:string};delivery_windows?:{status:string;return_at?:string|null};warehouse_placed_deliveries:number;incoming_accounted_placed_deliveries?:number;loading_start_at:string|null;
  incoming:{expected_deliveries:number;ready_deliveries:number;plans?:{operation_id:string;receipt_complete:number;received_quantity:string;short_quantity:string;shortage_resolved:number;confirmed_short_quantity:string}[]};
  loading:{pending_st_ids:number[];loaded_place_count:number};
  blockers:{code:string;plan_operation_id?:string}[]};
const reasons:Record<string,string>={
 COORDINATION_INCOMING_RECEIPT_INCOMPLETE:"Межскладская поставка принята не полностью; недостача остаётся открытой",
 COORDINATION_TIME_NOT_CURRENT_APPROVED:"Время плана рейса не утверждено или изменилось",
 COORDINATION_LOADING_STAGE_REQUIRED:"Нет однозначного времени начала погрузки",
 COORDINATION_ORIGINAL_ST_MEMBERS_REQUIRED:"В рейсе нет назначенных СТ",
 COORDINATION_PHYSICAL_LOADING_PENDING:"Есть СТ без подтверждённой погрузки",
 COORDINATION_WAREHOUSE_PLACEMENT_PENDING:"Ожидаемый товар ещё не размещён",
 COORDINATION_TEMPERATURE_HOLD:"Приостановлено решение по температуре",
 COORDINATION_READY_PROMISE_AFTER_LOADING:"Обещанное размещение позже начала погрузки",
 COORDINATION_ACTUAL_PLACEMENT_AFTER_LOADING:"Фактическое размещение позже начала погрузки",
 COORDINATION_EXPECTED_CARGO_NOT_LOADED:"Ожидаемые межскладские паллеты ещё не погружены",
 COORDINATION_RESOURCE_CONFLICT:"Машина или водитель заняты другим рейсом",
 COORDINATION_DRIVER_DAY_LIMIT_EXCEEDED:"Превышен плановый дневной лимит движения",
 COORDINATION_DRIVER_DAY_INCOMPLETE:"Есть рейсы водителя с неактуальным или неполным планом",
 DELIVERY_HARD_WINDOW_MISSED:"Строгое окно доставки пропущено",
 DELIVERY_SOFT_WINDOW_MISSED:"Плановое окно доставки пропущено",
 DELIVERY_WINDOW_MISSING:"Окно доставки не задано",
 DESTINATION_UNLOAD_NORM_UNKNOWN:"Норматив разгрузки неизвестен",
 WAREHOUSE_DEPOT_NOT_CONFIGURED:"База отправления не настроена",
 COORDINATION_PLANNED_TRIP_REQUIRED:"Рейс уже не находится в состоянии планирования",
};
export function TransportCoordination({tripId,apiBase,headers,actor}:{
 tripId:number;apiBase:string;headers:HeadersInit;actor:string;
}){
 const [result,setResult]=useState<Snapshot|null>(null);
 const [error,setError]=useState("");
 const [busy,setBusy]=useState(false);
 const generation=useRef(0);
 useEffect(()=>{generation.current++;setResult(null);setError("");setBusy(false);
   return()=>{generation.current++;};},[tripId,apiBase,actor]);
 async function load(){
  const token=++generation.current;setBusy(true);setError("");setResult(null);
  try{
   const r=await fetch(`${apiBase}/api/transport/preflight/trips/${tripId}/coordination`,{headers});
   const body=await r.json();
   if(!r.ok)throw new Error(typeof body.detail?.message==="string"?body.detail.message:"Проверка недоступна");
   if(token===generation.current)setResult(body as Snapshot);
  }catch(e){if(token===generation.current)setError(e instanceof Error?e.message:"Ошибка проверки");}
  finally{if(token===generation.current)setBusy(false);}
 }
 return <section style={{borderTop:"1px solid #e2e8f0",paddingTop:8}}>
  <strong>Согласованность склада и рейса</strong>{" "}
  <button disabled={busy} onClick={()=>void load()}>{busy?"Проверяем…":"Проверить готовность"}</button>
  {error&&<p role="alert">{error}</p>}
  {result&&<div>
   <p>Ожидается поставок: {result.incoming.expected_deliveries};
    {" "}полностью принято и размещено: {result.warehouse_placed_deliveries};
    {" "}принятая часть размещена и расхождение разрешено: {result.incoming_accounted_placed_deliveries??result.warehouse_placed_deliveries};
    {" "}погружено ожидаемых поставок: {result.incoming.ready_deliveries}.</p>
   {result.incoming.plans?.filter(p=>p.receipt_complete===0&&p.shortage_resolved===1).map(p=><p key={p.operation_id}>Поставка {p.operation_id}: принято {p.received_quantity}, подтверждена недостача {p.confirmed_short_quantity}. Полная физическая приёмка не подтверждена.</p>)}
   <p>Погруженных мест в истории: {result.loading.loaded_place_count};
    {" "}СТ без подтверждённой погрузки: {result.loading.pending_st_ids.length}.</p>
   {result.delivery_windows&&<p>Окна доставки: {result.delivery_windows.status==="CURRENT_APPROVED_REGION_REQUIRED"?"нужно актуальное утверждение времени":result.delivery_windows.status==="NO_EARLIEST_WINDOW_VIOLATION"?"ранняя оценка укладывается в окна":result.delivery_windows.status==="WINDOW_VIOLATION"?"есть опоздания":"недостаточно данных"}. Возврат: {result.delivery_windows.return_at||"не рассчитан"}.</p>}
   {result.loading_start_at&&<p>Плановое начало погрузки: {result.loading_start_at}</p>}
   {result.blockers.length?<ul>{result.blockers.map((b,i)=><li key={i}>
     {reasons[b.code]||b.code}{b.plan_operation_id?` · ${b.plan_operation_id}`:""}
   </li>)}</ul>:<p>Записанные этапы склада и погрузки выполнены.</p>}
   <p>Перед выездом система повторно проверяет текущий состав, контроль и вместимость.
    Эта сводка не разрешает выезд.</p>
  </div>}
 </section>;
}
