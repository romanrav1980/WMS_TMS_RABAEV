export type VrpRouteStop = {
  st_number: string;
  addr: string | null;
  lat: number | null;
  lon: number | null;
  pallets: number;
  weight_kg: number;
  ware_id: number;
  tw_from?: number;
  tw_to?: number;
  tw_strict?: boolean;
  arrival_min?: number | null;
  departure_min?: number | null;
  tw_violation_min?: number;
  distance_from_prev_km?: number | null;
  duration_from_prev_min?: number | null;
  duration_from_prev_basis?: string;
  constraint_notes?: string[];
};

export type VrpRouteItem = {
  vehicle_id: number;
  vehicle_num: string;
  vehicle_type: string;
  max_pallets: number;
  total_pallets: number;
  total_kg: number;
  total_km: number;
  total_duration_min: number;
  utilization_pct: number;
  stops: VrpRouteStop[];
  depot_basis?: string;
  road_profile_legs?: number;
  schedule_status?: string;
  operational_admission?: boolean;
  capacity_status?: "ok" | "low" | "over";
  tw_violation_count?: number;
  strict_tw_count?: number;
  vehicle_constraints_ok?: boolean;
  hydro_board_required_count?: number;
  explain_notes?: string[];
};

export function invalidateSchedule(route: VrpRouteItem): void {
  route.schedule_status = "STALE_AFTER_ROUTE_EDIT";
  route.operational_admission = false;
  route.total_duration_min = 0;
  route.stops = route.stops.map(stop => ({
    ...stop, arrival_min: null, departure_min: null,
    distance_from_prev_km: null, duration_from_prev_min: null,
    duration_from_prev_basis:"UNRECORDED",
    constraint_notes: ["SCHEDULE_STALE_RECALCULATE"],
  }));
}

export function PlannerSchedule({ route }: { route: VrpRouteItem }) {
  const available = route.schedule_status === "RELATIVE_SOLVER_SCHEDULE";
  return <div className="planner-hint">
    {(route.road_profile_legs??0)>0&&<span>Дорожных участков из матрицы: {route.road_profile_legs}. </span>}
    {available
      ? "Расчётное обслуживание: минуты от начала смены 06:00. "+(route.depot_basis==="CONFIGURED_WAREHOUSE_REFERENCE"?"Настроенный адрес отправления склада.":"Виртуальное депо.")+" Допуск рейса требует проверки."
      : route.schedule_status === "STALE_AFTER_ROUTE_EDIT"
        ? "Маршрут изменён: расписание требуется пересчитать."
        : "Расписание не рассчитано; временные окна не проверены."}
  </div>;
}

export function PlannerStopTime({ stop }: { stop: VrpRouteStop }) {
  if (stop.arrival_min == null || stop.departure_min == null) return null;
  return <span title="Минуты от начала смены 06:00; не подтверждённый допуск рейса">
    {stop.duration_from_prev_min!=null&&<>До остановки {stop.duration_from_prev_min} мин ({stop.duration_from_prev_basis==="ROAD_PROFILE_ESTIMATE"?"дорожный профиль":stop.duration_from_prev_basis==="UNRECORDED"?"источник не сохранён":"расчётная скорость"}). </>}
    Обслуживание +{stop.arrival_min}–{stop.departure_min} мин
    {(stop.tw_violation_min ?? 0) > 0 && ` · вне окна ${stop.tw_violation_min} мин`}
  </span>;
}


export function transferPlannerStop(
  current: VrpRouteItem[], sourceRoute: number, sourceStop: number, destination: number,
): VrpRouteItem[] {
  const routes = current.map(route => ({ ...route, stops: [...route.stops] }));
  const [moved] = routes[sourceRoute].stops.splice(sourceStop, 1);
  routes[destination].stops.push(moved);
  for (const index of [sourceRoute, destination]) {
    const route = routes[index];
    invalidateSchedule(route);
    route.total_pallets = route.stops.reduce((sum, stop) => sum + stop.pallets, 0);
    route.total_kg = route.stops.reduce((sum, stop) => sum + stop.weight_kg, 0);
    route.utilization_pct = route.max_pallets > 0
      ? Math.round(route.total_pallets / route.max_pallets * 100) : 0;
  }
  return routes;
}
