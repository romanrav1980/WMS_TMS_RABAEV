import {useEffect,useRef,useState} from "react";
import {archiveDamaged,pendingKey,readPending,savePending,settlePending,type PendingState,type TimeApprovalIntent} from "./TransportTimeApprovalIntent";
import {TransportTimeApprovalPending} from "./TransportTimeApprovalPending";
type Zone = "" | "UTC" | "Europe/Moscow" | "Asia/Tbilisi";
type Context = {version:number;source_hash:string;approval_status:string;
  last_approval?:{time_zone:string;actor:string;reason:string}};
// Отказ, подтверждённый существующим контрактом сервера (команда не принята): запись можно удалить.
const CONFIRMED_REFUSAL=[400,404,409,422];
export function TransportTimeApproval({tripId,zone,apiBase,headers,actor}:{
  tripId:number;zone:Zone;apiBase:string;headers:HeadersInit;actor:string;
}) {
  const [context,setContext]=useState<Context|null>(null);
  const [reason,setReason]=useState("");
  const [loadedReview,setLoadedReview]=useState(false);
  const [message,setMessage]=useState("");
  const [busy,setBusy]=useState(false);
  const [pending,setPending]=useState<PendingState>({kind:"none"});
  const version=useRef(0);
  const key=pendingKey(apiBase,actor);
  useEffect(()=>{
    version.current++;setContext(null);setMessage("");setBusy(false);
    const saved=actor?readPending(key):{kind:"none" as const};setPending(saved);
    // Поля восстанавливаются из сохранённой команды того же рейса — для точного повтора ничего не нужно угадывать.
    if(saved.kind==="valid"&&saved.intent.trip_id===tripId){setReason(saved.intent.reason);setLoadedReview(saved.intent.approval_phase==="AFTER_LOADING_REVIEW");}
    return()=>{version.current++;};
  },[tripId,zone,actor,apiBase,key]);
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
  // Отправка точной сохранённой команды; удаление записи — только после подтверждённого результата.
  async function send(intent:TimeApprovalIntent,stored:string) {
    const token=++version.current;setBusy(true);setMessage("");
    try {
      const requestHeaders=new Headers(headers);requestHeaders.set("Content-Type","application/json");
      let r:Response;
      try{r=await fetch(`${apiBase}/api/transport/preflight/time-approvals`,{method:"POST",headers:requestHeaders,body:JSON.stringify(intent)});}
      catch{throw new Error("Сервер не ответил. Результат неизвестен — повторите сохранённое утверждение.");}
      let b:{operation_id?:string;trip_id?:number;actor?:string;detail?:{code?:string;message?:string}|string}|null=null;
      try{b=await r.json();}catch{b=null;}
      if(!r.ok){
        const detail=typeof b?.detail==="object"?b.detail:null;
        // Подтверждённый отказ — только структурированный ответ API {detail:{code,message}}; HTML 404 прокси
        // или неполное тело не доказывают отказ команды: запись сохраняется как неизвестный результат.
        if(CONFIRMED_REFUSAL.includes(r.status)&&typeof detail?.code==="string"&&/^[A-Z][A-Z0-9_]{2,}$/.test(detail.code)){
          settlePending(key,stored);if(token===version.current)setPending(readPending(key));
          throw new Error((detail?.message||"Утверждение отклонено")+(detail?.code?" ("+detail.code+")":"")+". Отказ подтверждён — прочитайте актуальный план и исправьте ввод.");
        }
        throw new Error("Результат не подтверждён (HTTP "+r.status+"). Повторите сохранённое утверждение.");
      }
      if(!b||b.operation_id!==intent.operation_id||b.trip_id!==intent.trip_id||b.actor!==actor)
        throw new Error("Ответ не подтверждает исходную команду. Повторите сохранённое утверждение.");
      const cleared=settlePending(key,stored);
      if(token===version.current){
        setPending(readPending(key));setContext(null);
        setMessage("Решение сохранено ("+intent.operation_id+")."+(cleared?" Перечитайте актуальный план.":" Запись команды не удалось очистить — новые утверждения заблокированы до проверки хранилища."));
      }
    } catch(e){if(token===version.current)setMessage(e instanceof Error?e.message:"Решение не подтверждено");}
    finally{if(token===version.current)setBusy(false);}
  }
  async function approve() {
    if(!context||!zone||!actor||pending.kind!=="none")return;
    const intent:TimeApprovalIntent={operation_id:"TT.TIME.UI:"+crypto.randomUUID(),trip_id:tripId,
      expected_version:context.version,source_hash:context.source_hash,time_zone:zone,reason:reason.trim(),
      ...(loadedReview?{approval_phase:"AFTER_LOADING_REVIEW" as const}:{})};
    let stored:string;
    try{stored=savePending(key,intent);}catch(e){setMessage(e instanceof Error?e.message:"Команда не сохранена");return;}
    setPending({kind:"valid",intent,raw:stored});await send(intent,stored);
  }
  function retry() {
    if(pending.kind!=="valid"||pending.intent.trip_id!==tripId||pending.intent.time_zone!==zone)return;
    void send(pending.intent,pending.raw);
  }
  function archive() {
    if(pending.kind!=="damaged")return;
    if(!window.confirm("Сохранить повреждённую команду в архив? Убедитесь по статусу рейсов, что прежнее утверждение не нужно повторять."))return;
    if(archiveDamaged(key,pending.raw)){setPending(readPending(key));setMessage("Повреждённая команда сохранена в архив. Можно прочитать план и утвердить заново.");}
    else setMessage("Архив не создан: запись изменилась или хранилище недоступно.");
  }
  const blocked=pending.kind!=="none";
  return <div style={{borderTop:"1px solid #e2e8f0",paddingTop:8}}>
    <strong>Утверждение маршрута и времени</strong>{" "}
    <button disabled={busy} onClick={()=>void current()}>Прочитать актуальный план</button>
    <TransportTimeApprovalPending pending={pending} tripId={tripId} zone={zone} busy={busy} onRetry={retry} onArchive={archive}/>
    {context&&<div>
      <p>{context.approval_status==="APPROVED"?"Маршрут и время утверждены":
        context.approval_status==="SOURCE_CHANGED"?"План изменился после утверждения":"Утверждения нет"}
        {" · версия "}{context.version}</p>
      {context.last_approval&&<p>Последнее решение: {context.last_approval.time_zone},
        {" "}{context.last_approval.actor} — {context.last_approval.reason}</p>}
      <input aria-label="Основание утверждения времени" value={reason} maxLength={500} disabled={blocked}
        onChange={e=>setReason(e.target.value)} placeholder="Основание утверждения"/>
      <label><input type="checkbox" checked={loadedReview} disabled={blocked} onChange={e=>setLoadedReview(e.target.checked)}/>
        Проверить время после полной подтверждённой погрузки</label>
      <button disabled={busy||blocked||!zone||reason.trim().length<8} title={blocked?"Сначала завершите сохранённое утверждение":undefined}
        onClick={()=>void approve()}>Утвердить маршрут и время</button>
      <p>Проверяются текущая дорога, окна, перерывы и занятость ресурсов. Назначение СТ вручную или автопланировщиком остаётся черновиком до этого шага. Допуск машины
        и готовность склада проверяются отдельно.</p>
    </div>}
    {message&&<p role="status">{message}</p>}
  </div>;
}
