import {phaseLabel,type PendingState} from "./TransportTimeApprovalIntent";

// C-0032: незавершённое утверждение времени после перезагрузки — что именно сохранено и как его завершить.
export function TransportTimeApprovalPending({pending,tripId,zone,busy,onRetry,onArchive}:{
  pending:PendingState;tripId:number;zone:string;busy:boolean;onRetry:()=>void;onArchive:()=>void;
}) {
  if(pending.kind==="none")return null;
  const box={border:"1px solid #f2e2b8",background:"#fff8e8",borderRadius:8,padding:"8px 10px",margin:"6px 0",color:"#5c4510"} as const;
  if(pending.kind==="damaged")return <div role="status" style={box}>
    <strong>Сохранённая команда утверждения повреждена.</strong> Новое утверждение заблокировано: результат прежней команды неизвестен.
    Сверьте статус рейсов, затем сохраните запись в архив для разбора.
    <div><button disabled={busy} onClick={onArchive}>Сохранить повреждённую запись в архив</button></div>
  </div>;
  const i=pending.intent,otherTrip=i.trip_id!==tripId,otherZone=!otherTrip&&i.time_zone!==zone;
  return <div role="status" style={box} aria-label="Незавершённое утверждение времени">
    <strong>Есть незавершённое утверждение маршрута и времени.</strong>
    <dl style={{display:"grid",gridTemplateColumns:"max-content 1fr",gap:"2px 10px",margin:"6px 0"}}>
      <dt>Рейс</dt><dd style={{margin:0}}>#{i.trip_id}</dd>
      <dt>Часовой пояс</dt><dd style={{margin:0}}>{i.time_zone}</dd>
      <dt>Основание</dt><dd style={{margin:0,overflowWrap:"anywhere"}}>{i.reason}</dd>
      <dt>Фаза</dt><dd style={{margin:0}}>{phaseLabel(i)}</dd>
      <dt>Версия плана</dt><dd style={{margin:0}}>{i.expected_version}</dd>
      <dt>Операция</dt><dd style={{margin:0,overflowWrap:"anywhere"}}>{i.operation_id}</dd>
    </dl>
    {otherTrip?<p style={{margin:0}}>Команда относится к рейсу #{i.trip_id}. Откройте этот рейс, чтобы повторить её; новое утверждение для рейса #{tripId} заблокировано до результата.</p>
     :otherZone?<p style={{margin:0}}>Выберите часовой пояс «{i.time_zone}» в поле выше — повтор возможен только с исходным часовым поясом.</p>
     :<button disabled={busy} onClick={onRetry}>Повторить сохранённое утверждение</button>}
  </div>;
}
