from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/"admin/wms_admin_frontend/src/components/TransportPlannerPage.tsx"
s=p.read_text(encoding="utf-8")
a=s.index('type VrpRouteStop = {');b=s.index('\n};',s.index('type VrpRouteItem = {',a))+4
types=s[a:b].replace('type VrpRouteStop','export type VrpRouteStop').replace('type VrpRouteItem','export type VrpRouteItem')
types=types.replace('  capacity_status?:','  schedule_status?: string;\n  operational_admission?: boolean;\n  capacity_status?:')
target=root/"admin/wms_admin_frontend/src/components/PlannerSchedule.tsx"
target.write_text(types+'''
export function invalidateSchedule(route: VrpRouteItem): void {
  route.schedule_status = "STALE_AFTER_ROUTE_EDIT";
  route.operational_admission = false;
  route.total_duration_min = 0;
  route.stops = route.stops.map(stop => ({
    ...stop, arrival_min: null, departure_min: null,
    distance_from_prev_km: null, duration_from_prev_min: null,
    constraint_notes: ["SCHEDULE_STALE_RECALCULATE"],
  }));
}

export function PlannerSchedule({ route }: { route: VrpRouteItem }) {
  const available = route.schedule_status === "RELATIVE_SOLVER_SCHEDULE";
  return <div className="planner-hint">
    {available
      ? "Расчётное обслуживание: минуты от начала смены 06:00. Виртуальное депо; допуск рейса требует проверки."
      : route.schedule_status === "STALE_AFTER_ROUTE_EDIT"
        ? "Маршрут изменён: расписание требуется пересчитать."
        : "Расписание не рассчитано; временные окна не проверены."}
  </div>;
}

export function PlannerStopTime({ stop }: { stop: VrpRouteStop }) {
  if (stop.arrival_min == null || stop.departure_min == null) return null;
  return <span title="Минуты от начала смены 06:00; не подтверждённый допуск рейса">
    Обслуживание +{stop.arrival_min}–{stop.departure_min} мин
    {(stop.tw_violation_min ?? 0) > 0 && ` · вне окна ${stop.tw_violation_min} мин`}
  </span>;
}
''',encoding="utf-8")
s=s[:a]+'import { PlannerSchedule, PlannerStopTime, invalidateSchedule, type VrpRouteItem } from "./PlannerSchedule";\n'+s[b:]
s=s.replace('      const r = routes[ri];','      const r = routes[ri];\n      invalidateSchedule(r);',1)
s=s.replace('                      <div className="planner-rp-stops">','                      <PlannerSchedule route={route} />\n                      <div className="planner-rp-stops">',1)
s=s.replace('<span className="planner-rp-stop-addr">{stop.addr ?? "—"}</span>','<span className="planner-rp-stop-addr">{stop.addr ?? "—"}</span>\n                              <PlannerStopTime stop={stop} />',1)
p.write_text(s,encoding="utf-8")
p=root/"api/wms_api_server/requirements.txt"
s=p.read_text(encoding="utf-8");p.write_text(s+'\n# Existing CVRPTW planner runtime (162)\nortools==9.15.6755\n',encoding="utf-8")
