import {useEffect, useRef, useState} from "react";
import {TransportRoadLegs} from "./TransportRoadLegs";
type Context = {version: number; source_hash: string; route_status: string;
  last_input?: {drive_min: number; drive_back_min: number; source_reference: string; reason: string}};
type Intent = {operation_id: string; trip_id: number; expected_version: number; source_hash: string;
  drive_min: number; drive_back_min: number; source_reference: string; reason: string};
export function TransportRouteInput({tripId, apiBase, headers, actor}: {
  tripId: number; apiBase: string; headers: HeadersInit; actor: string;
}) {
  const [context, setContext] = useState<Context | null>(null);
  const [drive, setDrive] = useState("");
  const [back, setBack] = useState("");
  const [source, setSource] = useState("");
  const [reason, setReason] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const generation = useRef(0);
  const key = "retailcase.trip.route.pending:" + JSON.stringify([apiBase, actor]);
  useEffect(() => {
    generation.current++; setContext(null); setMessage(""); setBusy(false);
    setDrive(""); setBack(""); setSource(""); setReason("");
    return () => {generation.current++;};
  }, [tripId, apiBase, actor]);
  async function read() {
    const token = ++generation.current; setBusy(true); setMessage("");
    try {
      const r = await fetch(`${apiBase}/api/transport/preflight/trips/${tripId}/route-context`, {headers});
      const b = await r.json();
      if (!r.ok) throw new Error(b.detail?.message || "Не удалось прочитать маршрут");
      if (token === generation.current) setContext(b as Context);
    } catch (e) {if (token === generation.current) setMessage(e instanceof Error ? e.message : "Ошибка чтения");}
    finally {if (token === generation.current) setBusy(false);}
  }
  function recover() {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) throw new Error("Нет неподтверждённого запроса.");
      const value = JSON.parse(raw) as Intent;
      if (value.trip_id !== tripId) throw new Error(`Откройте рейс #${value.trip_id} для повторения исходного запроса.`);
      setDrive(String(value.drive_min)); setBack(String(value.drive_back_min));
      setSource(value.source_reference); setReason(value.reason);
      setMessage("Исходные поля восстановлены. Прочитайте контекст и повторите запрос.");
    } catch (e) {setMessage(e instanceof Error ? e.message : "Не удалось восстановить запрос");}
  }
  async function apply() {
    if (!context || !actor) return;
    const token = ++generation.current; setBusy(true); setMessage("");
    try {
      const raw = localStorage.getItem(key);
      const intent: Intent = raw ? JSON.parse(raw) : {
        operation_id: "TT.ROUTE.UI:" + crypto.randomUUID(), trip_id: tripId,
        expected_version: context.version, source_hash: context.source_hash,
        drive_min: Number(drive), drive_back_min: Number(back),
        source_reference: source.trim(), reason: reason.trim(),
      };
      if (intent.trip_id !== tripId || intent.drive_min !== Number(drive)
        || intent.drive_back_min !== Number(back) || intent.source_reference !== source.trim()
        || intent.reason !== reason.trim()) throw new Error("Восстановите исходный неподтверждённый запрос.");
      localStorage.setItem(key, JSON.stringify(intent));
      const h = new Headers(headers); h.set("Content-Type", "application/json");
      const r = await fetch(`${apiBase}/api/transport/preflight/route-inputs`, {
        method: "POST", headers: h, body: JSON.stringify(intent),
      });
      const b = await r.json();
      if (!r.ok) {
        if ([400,404,409,422].includes(r.status)) localStorage.removeItem(key);
        throw new Error(b.detail?.message || "Результат не подтверждён; повторите исходный запрос.");
      }
      localStorage.removeItem(key);
      if (token === generation.current) {
        setContext(null); setMessage("Длительности сохранены, прежние операции пересчитаны. Утвердите время изменённого плана заново.");
      }
    } catch (e) {if (token === generation.current) setMessage(e instanceof Error ? e.message : "Ошибка сохранения");}
    finally {if (token === generation.current) setBusy(false);}
  }
  const valid = [drive, back].every(v => Number.isInteger(Number(v)) && Number(v) > 0 && Number(v) <= 1440);
  return <section style={{borderTop: "1px solid #e2e8f0", paddingTop: 8}}>
    <strong>Длительность маршрута этого рейса</strong>{" "}
    <button disabled={busy} onClick={() => void read()}>Прочитать маршрут</button>{" "}
    <button disabled={busy} onClick={recover}>Восстановить неподтверждённый запрос</button>
    {context && <div>
      <p>{context.route_status === "CURRENT_DISPATCH_ESTIMATE" ? "Текущая оценка диспетчера"
        : context.route_status === "SOURCE_CHANGED" ? "Исходные данные изменились" : "Оценка не задана"} · версия {context.version}</p>
      {context.last_input && <p>Последняя оценка: {context.last_input.drive_min} + {context.last_input.drive_back_min} мин.
        {" "}{context.last_input.source_reference}</p>}
      <label>К клиентам, мин <input type="number" min="1" max="1440" step="1" value={drive} onChange={e => setDrive(e.target.value)}/></label>{" "}
      <label>Обратно, мин <input type="number" min="1" max="1440" step="1" value={back} onChange={e => setBack(e.target.value)}/></label>
      <input aria-label="Источник длительности маршрута" maxLength={500} value={source} onChange={e => setSource(e.target.value)} placeholder="Источник оценки"/>
      <input aria-label="Основание изменения маршрута" maxLength={500} value={reason} onChange={e => setReason(e.target.value)} placeholder="Основание"/>
      <button disabled={busy || !valid || source.trim().length < 8 || reason.trim().length < 8} onClick={() => void apply()}>Сохранить и пересчитать операции</button>
      <p>Оценка диспетчера. Дорожная обстановка, окна магазинов и допуск водителя отдельно не подтверждаются.
        После начала исполнения или погрузки пересчёт запрещён.</p>
    </div>}
    {/* Расчёт окон и прибытия показывает единый TransportRouteSchedule в preflight (C-0037). */}
    <TransportRoadLegs tripId={tripId} apiBase={apiBase} headers={headers} actor={actor} onChoose={value=>{
      if(!context||context.source_hash!==value.source_hash){setMessage("Перечитайте текущий маршрут перед использованием матрицы.");return;}
      setDrive(String(value.drive_min));setBack(String(value.drive_back_min));
      setSource("Дорожная матрица, снимок "+value.road_snapshot_signature);
      setMessage("Время подставлено для рассмотрения. Укажите основание и подтвердите оценку отдельно.");
    }}/>
    {message && <p role="status">{message}</p>}
  </section>;
}
