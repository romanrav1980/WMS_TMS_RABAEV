import { useEffect, useRef, useState } from "react";

type Check = { status: string; code?: string; result?: { warnings?: string[] } };
type Route = {
  vehicle_id: number; current_vehicle_num?: string | null; status: string;
  source_blockers: { code: string; st_number?: string }[];
  capacity_and_type: Check; current_native_application: Check;
};
type Preflight = { plan_id: number; status: string; already_applied: boolean; routes: Route[] };

const REASONS: Record<string, string> = {
  PLAN_ST_NOT_FOUND: "СТ отсутствует в текущих данных",
  PLAN_ST_FOREIGN_OR_SHIPPED: "СТ уже отгружена или назначена другому рейсу",
  PLAN_VEHICLE_ID_PLATE_CONFLICT: "Сохранённая машина не соответствует текущему госномеру",
  PLAN_CURRENT_VEHICLE_NOT_FOUND: "Машина отсутствует",
  PLAN_ACTIVE_VEHICLE_CAPACITY_REQUIRED: "Машина заблокирована либо её вместимость не задана",
  PLAN_PALLET_CAPACITY_EXCEEDED: "Превышена паллетная вместимость",
  PLAN_WEIGHT_CAPACITY_EXCEEDED: "Превышена грузоподъёмность",
  PLAN_DECLARED_WEIGHT_REQUIRED: "Плановая масса части товара отсутствует",
  PLAN_ADDRESS_VEHICLE_TYPE_OR_HYDRO_CONFLICT: "Тип машины или гидроборт не соответствует адресу",
  PLAN_ADDRESS_VEHICLE_LIMIT_EXCEEDED: "Машина превышает ограничение адреса по тоннажу",
  PLAN_STRICT_TIME_SCHEDULE_REQUIRED: "Строгие временные окна требуют подтверждённого расписания",
  PLAN_ACTIVE_UNBILLED_TRIP_REQUIRED: "Рейс отменён, отгружен или передан в биллинг",
};

function reason(code?: string): string | undefined {
  return code ? REASONS[code] || code : undefined;
}

export function PlannerPreflight({ planId, request }: {
  planId: number | null | undefined; request: (path: string) => Promise<Preflight>;
}) {
  const [result, setResult] = useState<Preflight | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const generation = useRef(0);
  useEffect(() => {
    generation.current++; setResult(null); setError(""); setBusy(false);
    return () => { generation.current++; };
  }, [planId]);
  async function refresh() {
    if (!planId || busy) return;
    const sequence = ++generation.current;
    setBusy(true); setError(""); setResult(null);
    try {
      const response = await request(`/api/transport/preflight/plans/${planId}`);
      if (sequence === generation.current) setResult(response);
    } catch (reason) {
      if (sequence === generation.current) setError(String(reason));
    } finally {
      if (sequence === generation.current) setBusy(false);
    }
  }
  if (!planId) return null;
  return <div className="planner-hint">
    <button onClick={refresh} disabled={busy}>{busy ? "Проверка…" : "Проверить текущие ограничения"}</button>
    {error && <p role="alert">{error}</p>}
    {result && <>
      <p>{result.already_applied ? "План уже применён. " : ""}Проверено: {result.routes.length} маршрутов.</p>
      {result.routes.map((route, index) => <div key={index}>
        <b>{route.current_vehicle_num || `Машина №${route.vehicle_id}`}</b>
        {[...route.source_blockers.map(item => `${reason(item.code)}${item.st_number ? ": " + item.st_number : ""}`),
          reason(route.capacity_and_type.code), reason(route.current_native_application.code),
          ...(route.capacity_and_type.result?.warnings || [])].filter(Boolean)
          .map((message, item) => <div key={item}>{message}</div>)}
        {route.status !== "BLOCKED" && <div>Текущие правила вместимости и назначения проверены.</div>}
      </div>)}
      <p>Проверка только читает данные. Расписание, водитель и готовность склада требуют подтверждения; применение повторно проверяет текущие ограничения.</p>
    </>}
  </div>;
}

export function PlannerMapHint() {
  return <div className="planner-hint">Полигон: нарисуйте зону — СТ внутри выделятся.<br />Кластер: кликните на название района.</div>;
}
