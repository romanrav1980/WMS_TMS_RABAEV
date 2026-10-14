import {useEffect,useRef,useState} from "react";
import {clock,issueText,minutesBetween,SEGMENT_LABELS,statusView,weeklyText,WINDOW_SOURCES,type ScheduleReport,type ScheduleStop} from "./TransportRouteScheduleView";
import "./TransportRouteSchedule.css";

// C-0033: серверный маршрут рейса (native RRL_TT_ROUTE_SCHEDULE через /delivery-windows) — остановки, переезды,
// ожидание, разгрузка, перерывы, источник окон и причины. Ничего не рассчитывает и не утверждает.
const Issue=({code}:{code:string})=><span className="trs-issue">{issueText(code)}<details><summary>код</summary><code>{code}</code></details></span>;

// Окно, выбранное расчётом (уже в поясе отчёта); настроенная неделя магазина — отдельной справкой, интервалы не склеиваются.
function windowsOf(s:ScheduleStop,zone:string,day:string){
  const chosen=!s.window_from&&!s.window_to?<span className="trs-muted">не задано</span>:<span>{clock(s.window_from,zone,day)} — {clock(s.window_to,zone,day)}</span>;
  const weekly=weeklyText(s);
  return <>{chosen}{weekly&&<small className="trs-weekly">Настроенная неделя: {weekly}</small>}</>;
}

export function TransportRouteSchedule({tripId,zone,apiBase,headers}:{tripId:number;zone:string;apiBase:string;headers:HeadersInit}){
  const [report,setReport]=useState<ScheduleReport|null>(null),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
  const generation=useRef(0);
  // Смена рейса или часового пояса сбрасывает результат; старый ответ не перекрывает новый.
  useEffect(()=>{generation.current++;setReport(null);setBusy(false);setMessage("");return()=>{generation.current++;};},[tripId,zone,apiBase]);
  async function read(){
    if(!zone)return;const token=++generation.current;setBusy(true);setReport(null);setMessage("");
    try{
      const r=await fetch(apiBase+"/api/transport/preflight/trips/"+tripId+"/delivery-windows?"+new URLSearchParams({time_zone:zone}),{headers});
      let v:unknown=null;try{v=await r.json();}catch{v=null;}
      const detail=(v as {detail?:{message?:string}|string}|null)?.detail;
      if(!r.ok)throw new Error((typeof detail==="object"&&detail?.message)||(typeof detail==="string"?detail:"")||"Маршрут не рассчитан (HTTP "+r.status+")");
      const preview=v as ScheduleReport|null;
      if(!preview||!Array.isArray(preview.stops))throw new Error("Ответ сервера не содержит маршрута.");
      if(token===generation.current)setReport(preview);
    }catch(e){if(token===generation.current)setMessage(e instanceof Error?e.message:"Маршрут недоступен");}
    finally{if(token===generation.current)setBusy(false);}
  }
  const tz=report?.time_zone||zone,day=report?.departure_at?clock(report.departure_at,tz).slice(0,5):undefined;
  const st=report?statusView(report.status):null;
  return <div className="trs">
    <h4>Расчётный маршрут сервера</h4>
    <button disabled={busy||!zone} title={zone?"Прочитать маршрут, рассчитанный сервером; рейс не меняется":"Сначала выберите часовой пояс выше"} onClick={()=>void read()}>
      {busy?"Читаем маршрут…":"Показать расчётный маршрут"}</button>
    {!zone&&<p className="trs-muted">Выберите часовой пояс плановых дат выше.</p>}
    {report&&st&&<>
      <p className={"trs-status trs-"+st.tone} role="status">{st.text}</p>
      <dl className="trs-facts">
        <div><dt>Часовой пояс</dt><dd>{tz}{report.destination_time_zones_verified===false?" · пояса адресатов не проверены":""}</dd></div>
        <div><dt>Выезд</dt><dd>{clock(report.departure_at,tz)}</dd></div>
        <div><dt>Возврат на базу</dt><dd>{report.return_at?clock(report.return_at,tz,day):"не рассчитан"}</dd></div>
        <div><dt>Вождение, мин</dt><dd>{report.drive_min??"—"}</dd></div>
        <div><dt>База</dt><dd>{report.depot_address||"не настроена"}</dd></div>
        <div><dt>Расчёт</dt><dd>{report.estimate_basis||"—"}{report.policy_id?" · "+report.policy_id:""}</dd></div>
      </dl>
      {report.issues.length>0&&<div className="trs-block trs-bad-block" role="alert"><strong>Препятствия</strong><ul>{report.issues.map((x,i)=><li key={i}>{x.address?x.address+": ":""}<Issue code={x.code}/></li>)}</ul></div>}
      {!!report.warnings?.length&&<div className="trs-block trs-warn-block"><strong>Предупреждения</strong><ul>{report.warnings.map((x,i)=><li key={i}>{x.address?x.address+": ":""}<Issue code={x.code}/></li>)}</ul></div>}
      <div className="trs-table-wrap"><table className="trs-table"><thead><tr><th>Адрес / СТ</th><th>Окно приёма</th><th>Прибытие</th><th>Разгрузка</th><th>Ожидание / опоздание, мин</th><th>Причины</th></tr></thead>
        <tbody>{report.stops.map((s,i)=><tr key={s.address+i}>
          <td data-label="Адрес / СТ"><strong>{s.address}</strong><small>{s.st_numbers.join(", ")}</small></td>
          <td data-label="Окно приёма">{windowsOf(s,tz,day||"")}<small>{s.window_strict==null?"строгость не задана":Number(s.window_strict)?"строгое окно — пропуск запрещён":"плановое окно — пропуск даёт предупреждение"}
            {s.window_source?" · "+(WINDOW_SOURCES[s.window_source]||s.window_source):""}</small></td>
          <td data-label="Прибытие">{clock(s.arrival_at,tz,day)}</td>
          <td data-label="Разгрузка">{s.service_start_at||s.service_finish_at?clock(s.service_start_at??null,tz,day)+" — "+clock(s.service_finish_at,tz,day):"—"}<small>норма {s.unload_norm_min??"—"} мин</small></td>
          <td data-label="Ожидание / опоздание, мин">{s.wait_min??"—"} / {s.late_min??"—"}</td>
          <td data-label="Причины">{s.issues.length?s.issues.map(c=><Issue key={c} code={c}/>):<span className="trs-muted">нет</span>}</td>
        </tr>)}</tbody></table></div>
      {!!report.segments?.length&&<details className="trs-block"><summary>Лента: дорога, перерывы, ожидание и работы</summary>
        <ol className="trs-timeline">{report.segments.map((s,i)=>{const m=minutesBetween(s.start_at,s.finish_at);return <li key={i} className={"trs-seg trs-seg-"+s.code.toLowerCase()}>
          <span>{clock(s.start_at,tz,day)} — {clock(s.finish_at,tz,day)}</span><b>{SEGMENT_LABELS[s.code]||s.code}</b><small>{s.duration_min??(m!=null?String(m):"—")} мин{s.address?" · "+s.address:""}</small></li>;})}</ol></details>}
      <p className="trs-muted">Перерывы и пределы вождения — проектные нормы расчёта{report.legal_compliance_verified===false?", соответствие законодательству не проверено":""}. Расчёт не является допуском к выезду; утверждение маршрута — отдельным действием ниже.</p>
    </>}
    {message&&<p className="trs-status trs-bad" role="status">{message}</p>}
  </div>;
}
