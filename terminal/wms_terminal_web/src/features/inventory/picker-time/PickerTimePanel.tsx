import {useEffect,useState} from "react";
import type {AssemblyCredentials} from "../assembly/contracts";
import {NativeHelp} from "../../platform";
import type {Context,Sessions} from "../case-work/contracts";
import type {Action} from "./contracts";
import {usePickerTime} from "./usePickerTime";
import "./picker-time.css";
const labels:Record<Action,string>={ACTUAL_SHIFT_START:"Начать фактическую смену",ACTUAL_SHIFT_FINISH:"Завершить фактическую смену",WORK_START:"Начать учёт сборки",PAUSE:"Начать паузу",RESUME:"Продолжить после паузы",WORK_FINISH:"Завершить учёт сборки"};
export function PickerTimePanel({credentials,context,sessions,metadataBlocked}:{credentials:AssemblyCredentials;context:Context|null;sessions:Sessions|null;metadataBlocked:boolean}){
 const time=usePickerTime(credentials),[selection,setSelection]=useState(""),[reason,setReason]=useState("");
 useEffect(()=>{setSelection(context?.assigned_to===credentials.username&&context.resource_session_id?String(context.resource_session_id):"");},[context?.resource_session_id,context?.task_id]);
 const current=time.current,pending=time.journal?.pending;
 const session=current?.shift_state==="OPEN"?current.resource_session_id:Number(selection)||null;
 const source=current?.work_state!=="IDLE"?current?.source_id??null:context?.task_id??null;
 const own=context?.assigned_to===credentials.username;
 const unavailable=time.busy||time.blocked||!!pending||metadataBlocked;
 const ready=!unavailable&&!!current&&!!session&&(current.shift_state==="OPEN"||!!sessions?.items.some(s=>s.ready&&s.resource_session_id===session))&&Array.from(reason.trim()).length>=8&&Array.from(reason).length<=500;
 const actions:Action[]=!current?[]:current.shift_state==="OFF"?["ACTUAL_SHIFT_START"]:current.work_state==="IDLE"?["WORK_START","ACTUAL_SHIFT_FINISH"]:current.work_state==="WORK"?["PAUSE","WORK_FINISH"]:["RESUME","WORK_FINISH"];
 const submit=(action:Action)=>{if(session)void time.submit(action,session,action.startsWith("ACTUAL_SHIFT_")?null:source,reason);};
 return <section className="cw-card pt-panel" aria-label="Фактическое время оператора">
  <details><summary title="Показать явную регистрацию смены, сборки и пауз; товарные количества не меняются" data-help-id="picker-time.open">Фактическое время · {pending?"ожидается квитанция":current?current.shift_state==="OPEN"?"смена открыта":"смена закрыта":"нет подтверждения"}</summary>
   <div className="pt-heading"><h2>Смена, сборка и паузы</h2><NativeHelp articleId="picker-actual-time" credentials={credentials}/></div>
   <p className="cw-muted">Ручные отметки времени. Страница и сигнал терминала не начинают работу; товар не проводится.</p>
   {time.error&&<p role="alert" className="cw-error">{time.error}</p>}
   {current&&<p role="status">Смена: {current.shift_state==="OPEN"?"открыта":"закрыта"} · сборка: {current.work_state==="WORK"?"идёт":current.work_state==="PAUSED"?"пауза":"не начата"} · версия {current.stream_version}
    {current.resource_session_id&&<> · сессия №{current.resource_session_id}</>}{current.source_id&&<> · {current.source_kind} №{current.source_id}</>}</p>}
   <p className="cw-warning">Полнота времени сборки не подтверждена: KPI — нет данных. Смена: только закрытые подтверждённые интервалы, включая паузы.</p>
   {pending?<div className="cw-warning"><b>Исход запроса неизвестен</b><p>{labels[pending.body.action]} · сессия {pending.body.resource_session_id}. Новое действие запрещено; исходная сессия сохранена.</p>
    <details><summary title="Показать ID исходного неизменного запроса" data-help-id="picker-time.pending.id">Номер запроса</summary><code>{pending.body.operation_id}</code></details>
    <button disabled={time.busy} onClick={()=>void time.readReceipt()} title="Только прочитать квитанцию исходной операции; 404 не очищает журнал" data-help-id="picker-time.receipt">Прочитать результат</button>
    <button disabled={time.busy} onClick={()=>void time.retry()} title="Повторить прежние байты с прежним operation_id; новые отметки не создаются" data-help-id="picker-time.retry">Повторить исходный запрос</button></div>:<>
    {current?.shift_state!=="OPEN"&&<label className="cw-field">Своя рабочая сессия<select value={selection} disabled={unavailable} onChange={e=>setSelection(e.target.value)} title="Выбрать свою проверенную сессию текущего задания; сервер проверит её заново" data-help-id="picker-time.session"><option value="">Выберите сессию</option>{sessions?.items.map(s=><option disabled={!s.ready} key={s.resource_session_id} value={s.resource_session_id}>{s.resource_code} · №{s.resource_session_id}</option>)}</select></label>}
    <label className="cw-field">Комментарий к отметке<textarea rows={2} maxLength={500} value={reason} disabled={unavailable} onChange={e=>setReason(e.target.value)} title="Укажите явную причину отметки времени, минимум 8 значимых символов" data-help-id="picker-time.reason"/></label>
    <div className="pt-actions">{actions.map(action=><button key={action} disabled={!ready||(action==="WORK_START"&&(!own||!source||context?.resource_session_id!==session))||(!action.startsWith("ACTUAL_SHIFT_")&&!source)} onClick={()=>submit(action)} title={labels[action]+". Сервер фиксирует собственное время и проверяет текущий доступ, сессию и источник; товар не меняется."} data-help-id={"picker-time."+action.toLowerCase()}>{labels[action]}</button>)}</div>
   </>}
   {metadataBlocked&&!pending&&<p className="cw-muted">Новые отметки недоступны, пока операция задания не подтверждена или данные задания не проверены.</p>}
   {time.journal?.last&&<p className="cw-muted">Последняя квитанция: {labels[time.journal.last.intent.body.action]} · {time.journal.last.ack.outcome==="APPLIED"?"подтверждено":"отклонено"}{time.journal.last.ack.error_code?" · "+time.journal.last.ack.error_code:""}</p>}
   <button disabled={time.busy} onClick={time.refresh} title="Прочитать серверное состояние и сохранённую квитанцию; новые факты не создаются" data-help-id="picker-time.refresh">Обновить время</button>
  </details>
 </section>;
}
