import {useEffect,useRef,useState} from "react";
type Zone = "" | "UTC" | "Europe/Moscow" | "Asia/Tbilisi";
type Context = {version:number;source_hash:string;approval_status:string;
  last_approval?:{time_zone:string;actor:string;reason:string}};
type Intent = {operation_id:string;trip_id:number;expected_version:number;
  source_hash:string;time_zone:string;reason:string;approval_phase?:"AFTER_LOADING_REVIEW"};
export function TransportTimeApproval({tripId,zone,apiBase,headers,actor}:{
  tripId:number;zone:Zone;apiBase:string;headers:HeadersInit;actor:string;
}) {
  const [context,setContext]=useState<Context|null>(null);
  const [reason,setReason]=useState("");
  const [loadedReview,setLoadedReview]=useState(false);
  const [message,setMessage]=useState("");
  const [busy,setBusy]=useState(false);
  const version=useRef(0);
  useEffect(()=>{
    version.current++;setContext(null);setMessage("");setBusy(false);
    return()=>{version.current++;};
  },[tripId,zone,actor,apiBase]);
  const key="nicora.trip.time.pending:"+JSON.stringify([apiBase,actor]);
  async function current() {
    const token=++version.current;setBusy(true);setMessage("");
    try {
      const r=await fetch(`${apiBase}/api/transport/preflight/trips/${tripId}/time-context`,{headers});
      const b=await r.json();
      if(!r.ok)throw new Error(typeof b.detail?.message==="string"?b.detail.message:"Не удалось прочитать план");
      if(token===version.current)setContext(b as Context);
    } catch(e){if(token===version.current)setMessage(e instanceof Error?e.message:"Ошибка чтения");}
    finally{if(token===version.current)setBusy(false);}
  }
  async function approve() {
    if(!context||!zone||!actor)return;
    const token=++version.current;setBusy(true);setMessage("");
    try {
      const raw=localStorage.getItem(key);
      const intent:Intent=raw?JSON.parse(raw):{
        operation_id:"TT.TIME.UI:"+crypto.randomUUID(),trip_id:tripId,
        expected_version:context.version,source_hash:context.source_hash,time_zone:zone,reason:reason.trim(),
        ...(loadedReview?{approval_phase:"AFTER_LOADING_REVIEW" as const}:{}),
      };
      if(intent.trip_id!==tripId||intent.time_zone!==zone||intent.reason!==reason.trim()
        ||(intent.approval_phase==="AFTER_LOADING_REVIEW")!==loadedReview)
        throw new Error("Не подтверждён предыдущий запрос. Верните исходный рейс, часовой пояс и основание: "+
          JSON.stringify({рейс:intent.trip_id,часовой_пояс:intent.time_zone,основание:intent.reason}));
      const stored=JSON.stringify(intent);
      localStorage.setItem(key,stored);
      if(localStorage.getItem(key)!==stored)throw new Error("Не удалось сохранить команду утверждения");
      const requestHeaders=new Headers(headers);requestHeaders.set("Content-Type","application/json");
      const r=await fetch(`${apiBase}/api/transport/preflight/time-approvals`,{
        method:"POST",headers:requestHeaders,body:JSON.stringify(intent),
      });
      const b=await r.json();
      if(!r.ok){
        if([400,404,409,422].includes(r.status)&&localStorage.getItem(key)===stored)localStorage.removeItem(key);
        throw new Error(typeof b.detail?.message==="string"?b.detail.message:"Решение не подтверждено; повторите исходный запрос");
      }
      if(b.operation_id!==intent.operation_id||b.trip_id!==intent.trip_id||b.actor!==actor)
        throw new Error("Ответ не подтверждает исходную команду. Повторите запрос.");
      if(localStorage.getItem(key)===stored)localStorage.removeItem(key);
      if(token===version.current){
        setContext(null);setMessage("Решение сохранено. Перечитайте актуальный план.");
      }
    } catch(e){if(token===version.current)setMessage(e instanceof Error?e.message:"Решение не подтверждено");}
    finally{if(token===version.current)setBusy(false);}
  }
  return <div style={{borderTop:"1px solid #e2e8f0",paddingTop:8}}>
    <strong>Утверждение маршрута и времени</strong>{" "}
    <button disabled={busy} onClick={()=>void current()}>Прочитать актуальный план</button>
    {context&&<div>
      <p>{context.approval_status==="APPROVED"?"Маршрут и время утверждены":
        context.approval_status==="SOURCE_CHANGED"?"План изменился после утверждения":"Утверждения нет"}
        {" · версия "}{context.version}</p>
      {context.last_approval&&<p>Последнее решение: {context.last_approval.time_zone},
        {" "}{context.last_approval.actor} — {context.last_approval.reason}</p>}
      <input aria-label="Основание утверждения времени" value={reason} maxLength={500}
        onChange={e=>setReason(e.target.value)} placeholder="Основание утверждения"/>
      <label><input type="checkbox" checked={loadedReview} onChange={e=>setLoadedReview(e.target.checked)}/>
        Проверить время после полной подтверждённой погрузки</label>
      <button disabled={busy||!zone||reason.trim().length<8}
        onClick={()=>void approve()}>Утвердить маршрут и время</button>
      <p>Проверяются текущая дорога, окна, перерывы и занятость ресурсов. Назначение СТ вручную или автопланировщиком остаётся черновиком до этого шага. Допуск машины
        и готовность склада проверяются отдельно.</p>
    </div>}
    {message&&<p role="status">{message}</p>}
  </div>;
}
