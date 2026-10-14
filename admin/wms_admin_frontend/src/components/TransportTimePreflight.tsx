import { useEffect, useRef, useState } from "react";
import { TransportTimeApproval } from "./TransportTimeApproval";
import { TransportRouteSchedule } from "./TransportRouteSchedule";
import { TransportCoordination } from "./TransportCoordination";
import { TransportRouteInput } from "./TransportRouteInput";
import { TransportDriverRest, type DriverRestResult } from "./TransportDriverRest";
import { TransportDriverDay, type DriverDayResult } from "./TransportDriverDay";
type Zone = "" | "UTC" | "Europe/Moscow" | "Asia/Tbilisi";
type Result = {
  driver_rest: DriverRestResult; driver_days: DriverDayResult;
  time_zone: string; time_approval_status: string;
  status: string; start_at: string | null; finish_at: string | null;
  conflicts: {trip_id: number; vehicle_conflict: boolean; driver_conflict: boolean;
    operation: {operation_id: number; operation_code: string; plan_start_at: string | null;
      plan_end_at: string | null; fact_start_at: string | null; fact_end_at: string | null}}[];
  issues: {code: string; operation_id?: number; trip_id?: number}[];
};
const labels: Record<string, string> = {
  TIME_ORIGINAL_OPERATIONS_REQUIRED: "Нет плановой цепочки операций",
  TIME_OPERATION_INTERVAL_INVALID: "Некорректное время операции",
  TIME_POSITIVE_WINDOW_REQUIRED: "Продолжительность рейса не задана",
  TIME_VEHICLE_REQUIRED: "Не назначена машина",
  TIME_DRIVER_REQUIRED: "Не назначен водитель",
  TIME_DELETED_TRIP: "Рейс отменён",
  TIME_SOURCE_APPROVAL_CHANGED: "План рейса изменился после утверждения времени",
  TIME_OTHER_APPROVAL_CHANGED: "План другого рейса изменился после утверждения времени",
};
export function TransportTimePreflight({tripId, apiBase, headers, actor}: {
  tripId: number; apiBase: string; headers: HeadersInit; actor: string;
}) {
  const [zone, setZone] = useState<Zone>("");
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const generation = useRef(0);
  useEffect(() => {
    generation.current += 1; setResult(null); setError(""); setBusy(false);
    return () => { generation.current += 1; };
  }, [tripId, zone]);
  async function check() {
    const request = ++generation.current;
    setBusy(true); setResult(null); setError("");
    try {
      const requestHeaders = new Headers(headers);
      requestHeaders.set("Content-Type", "application/json");
      const response = await fetch(`${apiBase}/api/transport/preflight/trips/${tripId}/time`, {
        method: "POST", headers: requestHeaders,
        body: JSON.stringify({time_zone: zone}),
      });
      const body = await response.json();
      if (request !== generation.current) return;
      if (!response.ok) throw new Error(typeof body.detail?.message === "string"
        ? body.detail.message : "Не удалось проверить занятость");
      setResult(body as Result);
    } catch (e) {
      if (request === generation.current) setError(e instanceof Error ? e.message : "Ошибка проверки");
    } finally {
      if (request === generation.current) setBusy(false);
    }
  }
  return <section style={{padding: 12, borderTop: "1px solid #e2e8f0"}}>
    <strong>Занятость машины и водителя</strong>
    <p>Укажите часовой пояс прежних плановых дат рейса.</p>
    <select aria-label="Часовой пояс плановых дат" value={zone}
      onChange={e => setZone(e.target.value as Zone)}>
      <option value="">Выберите часовой пояс</option>
      <option value="Asia/Tbilisi">Тбилиси</option>
      <option value="Europe/Moscow">Москва</option>
      <option value="UTC">UTC</option>
    </select>{" "}
    <button disabled={!zone || busy} onClick={() => void check()}>
      {busy ? "Проверяем…" : "Проверить пересечения"}
    </button>
    {error && <p role="alert">{error}</p>}
    {result && <div>
      <TransportDriverRest value={result.driver_rest}/>
      <TransportDriverDay value={result.driver_days}/>
      <p>Часовой пояс расчёта: {result.time_zone}
        {result.time_approval_status === "APPROVED" ? " (утверждён для этого плана)" : " (выбран для проверки)"}</p>
      <p>{result.status === "NO_RECORDED_OCCUPANCY_CONFLICT"
        ? "Пересечений в записанных операциях не найдено."
        : "Обнаружены пересечения или неполные данные."}</p>
      <ul>{result.issues.map((issue, i) => <li key={i}>{labels[issue.code] || issue.code}
        {issue.operation_id ? ` (#${issue.operation_id})` : ""}</li>)}
        {result.conflicts.map(conflict => <li key={`${conflict.trip_id}:${conflict.operation.operation_id}`}>
          Рейс #{conflict.trip_id}: {conflict.vehicle_conflict ? "машина" : ""}
          {conflict.vehicle_conflict && conflict.driver_conflict ? " и " : ""}
          {conflict.driver_conflict ? "водитель" : ""}; {conflict.operation.operation_code}
          {" "}{conflict.operation.fact_start_at || conflict.operation.plan_start_at}
          {" — "}{conflict.operation.fact_start_at && !conflict.operation.fact_end_at
            ? "факт завершения не зафиксирован"
            : conflict.operation.fact_end_at || conflict.operation.plan_end_at}
        </li>)}</ul>
      <p>Для допуска рейса ещё нужны подтверждённое расписание, проверка отдыха водителя
        и готовности склада. Эта проверка не изменяет рейс.</p>
    </div>}
    <TransportRouteSchedule tripId={tripId} zone={zone} apiBase={apiBase} headers={headers}/>
    <TransportRouteInput tripId={tripId} apiBase={apiBase} headers={headers} actor={actor}/>
    <TransportTimeApproval tripId={tripId} zone={zone} apiBase={apiBase} headers={headers} actor={actor}/>
    <TransportCoordination tripId={tripId} apiBase={apiBase} headers={headers} actor={actor}/>
  </section>;
}
