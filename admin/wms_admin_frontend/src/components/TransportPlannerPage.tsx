import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  AttributionControl, CircleMarker, FeatureGroup, MapContainer,
  Polygon, Polyline, Popup, TileLayer, useMap,
} from "react-leaflet";
import { EditControl } from "react-leaflet-draw";
import type { LatLngExpression } from "leaflet";
import { PlannerAnalyticsTab } from "./PlannerAnalyticsTab";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type PlannerOrder = {
  ST_NUMBER: string;
  ADDR: string | null;
  REGION: string | null;
  RAION: string | null;
  LAT: number | null;
  LON: number | null;
  PALLETS_COUNT: number;
  WEIGHT_KG: number;
  VOLUME_M3: number | null;
  WARE_ID: number;
  TRANSPORT_TYPE: string | null;
  NEEDS_HYDRO_BOARD: number;
  MAX_VEHICLE_TONS: number;
  TW_STRICT: number;
  VERIFY_PERC: number | null;
  STDATE: string | null;
};

type RoutingStatus = {
  provider: string;
  provider_available: boolean;
  total_addresses: number;
  geocoded_count: number;
  ungeocoded_count: number;
};

type TransportType = {
  TRANSPORTTYPE: string;
  NAME: string | null;
};

type VrpRouteStop = {
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
  constraint_notes?: string[];
};

type VrpRouteItem = {
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
  capacity_status?: "ok" | "low" | "over";
  tw_violation_count?: number;
  strict_tw_count?: number;
  vehicle_constraints_ok?: boolean;
  hydro_board_required_count?: number;
  explain_notes?: string[];
};

type ExplainStep = {
  code: string;
  status: "pending" | "running" | "done" | "warning" | "error" | "skipped";
  label: string;
  message: string;
  elapsed_ms?: number | null;
};

type ExplainWarning = {
  code: string;
  severity: "info" | "warning" | "error";
  message: string;
  action?: string | null;
};

type VrpExplain = {
  input?: {
    plan_date?: string;
    orders_total?: number;
    orders_with_coords?: number;
    orders_skipped_no_coords?: number;
    ware_ids?: number[];
    transport_type?: string | null;
  };
  routing?: {
    requested_source?: string;
    active_provider?: string;
    used_provider?: string;
    fallback_used?: boolean;
    matrix_pairs?: number;
    matrix_age_min?: number | null;
  };
  solver?: {
    requested_solver?: string;
    used_solver?: string;
    time_limit_s?: number;
    solve_time_ms?: number;
  };
  constraints?: Record<string, boolean | number | string | null>;
  fleet?: {
    vehicles_total?: number;
    vehicles_used?: number;
    target_routes_per_vehicle?: number;
    target_daily_routes?: number;
    planned_routes?: number;
    avg_utilization_pct?: number;
    min_utilization_pct?: number;
    max_utilization_pct?: number;
    low_utilization_routes?: number;
    over_capacity_routes?: number;
  };
  steps?: ExplainStep[];
  warnings?: ExplainWarning[];
};

type VrpPlan = {
  plan_id: number | null;
  routes: VrpRouteItem[];
  unassigned_sts: string[];
  total_km: number;
  fleet_utilization_pct: number;
  tw_violations: number;
  score: number;
  solver_used: string;
  solve_time_ms: number;
  explain?: VrpExplain | null;
};

type PlanTemplate = {
  plan_id: number;
  plan_date: string;
  score: number;
  jaccard: number;
  routes_count: number;
  matched_sts: number;
  total_current_sts: number;
};

// Cluster (grouped by RAION)
type OrderCluster = {
  raion: string;
  orders: PlannerOrder[];
  centroid: [number, number];
};

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8088";
const API_AUTH = import.meta.env.VITE_ADMIN_BASIC_AUTH || "admin:admin123";

function apiHeaders(): HeadersInit {
  return { Authorization: `Basic ${btoa(API_AUTH)}`, "Content-Type": "application/json" };
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { headers: apiHeaders(), ...options });
  if (!res.ok) throw new Error(`${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

function todayIso(): string { return new Date().toISOString().slice(0, 10); }
function fmtDate(s: string | null): string { return s ? s.slice(0, 10) : "—"; }

// ---------------------------------------------------------------------------
// Color palettes
// ---------------------------------------------------------------------------

const WARE_COLORS: Record<number, string> = {
  5:    "#3b82f6",
  6:    "#22c55e",
  7:    "#f59e0b",
  9201: "#a855f7",
  9202: "#ef4444",
  9203: "#06b6d4",
};

const ROUTE_COLORS = [
  "#e11d48", "#2563eb", "#16a34a", "#d97706",
  "#7c3aed", "#0891b2", "#be185d", "#15803d",
];

// Cluster polygon colours (semi-transparent)
const CLUSTER_BG_COLORS = [
  "rgba(59,130,246,.12)", "rgba(34,197,94,.12)", "rgba(245,158,11,.12)",
  "rgba(168,85,247,.12)", "rgba(239,68,68,.12)", "rgba(6,182,212,.12)",
];

function wareColor(wareId: number): string { return WARE_COLORS[wareId] ?? "#94a3b8"; }
function routeColor(idx: number): string { return ROUTE_COLORS[idx % ROUTE_COLORS.length]; }
function markerRadius(pallets: number): number { return Math.max(6, Math.min(22, 5 + pallets * 1.4)); }
function fmtDuration(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h > 0 ? `${h}ч ${m}м` : `${m}м`;
}

function fmtPct(value: number | undefined | null): string {
  return `${Number(value || 0).toFixed(1)}%`;
}

function explainStatusLabel(status: ExplainStep["status"]): string {
  return ({
    pending: "Ожидает",
    running: "В работе",
    done: "Готово",
    warning: "Внимание",
    error: "Ошибка",
    skipped: "Пропущено",
  })[status];
}

function buildFallbackExplain(
  plan: VrpPlan | null,
  orders: PlannerOrder[],
  status: RoutingStatus | null,
  filterDate: string,
  solverMode: string,
): VrpExplain | null {
  if (!plan) return null;
  const withCoords = orders.filter(o => o.LAT != null && o.LON != null).length;
  const routeUtils = plan.routes.map(r => r.utilization_pct);
  return {
    input: {
      plan_date: filterDate,
      orders_total: orders.length,
      orders_with_coords: withCoords,
      orders_skipped_no_coords: Math.max(0, orders.length - withCoords),
      transport_type: null,
      ware_ids: [],
    },
    routing: {
      requested_source: "auto",
      active_provider: status?.provider,
      used_provider: status?.provider,
      fallback_used: false,
      matrix_pairs: 0,
      matrix_age_min: null,
    },
    solver: {
      requested_solver: solverMode,
      used_solver: plan.solver_used,
      time_limit_s: 60,
      solve_time_ms: plan.solve_time_ms,
    },
    constraints: {
      capacity_pallets: true,
      capacity_weight: true,
      time_windows: true,
      vehicle_type: true,
      hydro_board: true,
    },
    fleet: {
      vehicles_total: plan.routes.length,
      vehicles_used: plan.routes.length,
      target_routes_per_vehicle: 4,
      target_daily_routes: plan.routes.length * 4,
      planned_routes: plan.routes.length,
      avg_utilization_pct: plan.fleet_utilization_pct,
      min_utilization_pct: routeUtils.length ? Math.min(...routeUtils) : 0,
      max_utilization_pct: routeUtils.length ? Math.max(...routeUtils) : 0,
      low_utilization_routes: routeUtils.filter(v => v < 60).length,
      over_capacity_routes: routeUtils.filter(v => v > 100).length,
    },
    steps: [
      { code: "orders_loaded", status: "done", label: "Заявки загружены", message: `Найдено ${orders.length} СТ, ${withCoords} с координатами` },
      { code: "optimization_done", status: "done", label: "Оптимизация завершена", message: `Построено ${plan.routes.length} рейсов, без рейса ${plan.unassigned_sts.length} СТ` },
    ],
    warnings: plan.unassigned_sts.length
      ? [{ code: "unassigned_sts", severity: "warning", message: `${plan.unassigned_sts.length} СТ не назначены в рейсы`, action: "Проверить ограничения" }]
      : [],
  };
}

function buildExplainReport(plan: VrpPlan | null, explain: VrpExplain | null): string {
  if (!plan || !explain) return "";
  const lines = [
    "Детали расчета MAP/VRP",
    `Дата: ${explain.input?.plan_date || "—"}`,
    `Заявок: ${explain.input?.orders_total ?? 0}, с координатами: ${explain.input?.orders_with_coords ?? 0}`,
    `Рейсов: ${plan.routes.length}, без рейса: ${plan.unassigned_sts.length}`,
    `Пробег: ${plan.total_km.toFixed(1)} км, загрузка: ${plan.fleet_utilization_pct.toFixed(1)}%`,
    `Provider: ${explain.routing?.used_provider || "—"}, solver: ${plan.solver_used}`,
    `Score: ${plan.score.toFixed(1)}, расчет: ${plan.solve_time_ms} мс`,
    "",
    "Ход расчета:",
    ...(explain.steps || []).map(s => `- ${explainStatusLabel(s.status)}: ${s.label} — ${s.message}`),
  ];
  const warnings = explain.warnings || [];
  if (warnings.length) {
    lines.push("", "Предупреждения:", ...warnings.map(w => `- ${w.message}${w.action ? ` (${w.action})` : ""}`));
  }
  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function buildClusters(orders: PlannerOrder[]): OrderCluster[] {
  const map = new Map<string, PlannerOrder[]>();
  for (const o of orders) {
    const raion = o.RAION || "(без района)";
    if (!map.has(raion)) map.set(raion, []);
    map.get(raion)!.push(o);
  }
  const result: OrderCluster[] = [];
  map.forEach((ords, raion) => {
    if (ords.length < 2) return;
    const lat = ords.reduce((s, o) => s + (o.LAT || 0), 0) / ords.length;
    const lon = ords.reduce((s, o) => s + (o.LON || 0), 0) / ords.length;
    result.push({ raion, orders: ords, centroid: [lat, lon] });
  });
  return result;
}

// ---------------------------------------------------------------------------
// MapBoundsAdjuster
// ---------------------------------------------------------------------------

function MapBoundsAdjuster({ orders }: { orders: PlannerOrder[] }) {
  const map = useMap();
  useEffect(() => {
    const pts = orders.filter(o => o.LAT && o.LON).map(o => [o.LAT!, o.LON!] as [number, number]);
    if (pts.length === 0) return;
    try { map.fitBounds(pts, { padding: [30, 30], maxZoom: 12 }); } catch { /* ignore */ }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orders.length]);
  return null;
}

function TransportPlannerExplainDrawer({
  open,
  onClose,
  plan,
  explain,
  solving,
  solveError,
  matrixMessage,
  onCopy,
}: {
  open: boolean;
  onClose: () => void;
  plan: VrpPlan | null;
  explain: VrpExplain | null;
  solving: boolean;
  solveError: string | null;
  matrixMessage: string | null;
  onCopy: () => void;
}) {
  if (!open) return null;
  const warnings = explain?.warnings || [];
  const steps = explain?.steps || [];
  const fleet = explain?.fleet;
  const routing = explain?.routing;
  const solver = explain?.solver;
  const input = explain?.input;
  const statusLabel = solveError ? "Ошибка" : solving ? "Идет расчет" : plan ? "Готово" : "Нет плана";
  const targetRoutes = fleet?.target_daily_routes || 0;
  const plannedRoutes = fleet?.planned_routes || plan?.routes.length || 0;

  return (
    <aside className="planner-explain-drawer" aria-label="Детали расчета">
      <div className="planner-explain-header">
        <div>
          <h2>Детали расчета</h2>
          <span className={`planner-explain-status ${solveError ? "error" : solving ? "running" : "done"}`}>
            {statusLabel}
          </span>
        </div>
        <button className="planner-explain-close" onClick={onClose} title="Закрыть">×</button>
      </div>

      {solveError && (
        <div className="planner-explain-alert error">
          <b>Расчет остановлен</b>
          <span>{solveError}</span>
          {solveError.includes("Failed to fetch") && (
            <small>Браузер мог скрыть backend 500 как Failed to fetch. Проверьте API 8088 и CORS.</small>
          )}
        </div>
      )}

      {matrixMessage && (
        <div className="planner-explain-alert info">
          <b>Матрица расстояний</b>
          <span>{matrixMessage}</span>
        </div>
      )}

      <section className="planner-explain-section">
        <h3>Обзор</h3>
        <div className="planner-explain-grid">
          <span>Дата</span><b>{input?.plan_date || "—"}</b>
          <span>Заявок</span><b>{input?.orders_total ?? "—"}</b>
          <span>С координатами</span><b>{input?.orders_with_coords ?? "—"}</b>
          <span>Рейсов</span><b>{plan?.routes.length ?? 0}</b>
          <span>Без рейса</span><b className={(plan?.unassigned_sts.length || 0) > 0 ? "warn" : ""}>{plan?.unassigned_sts.length ?? 0}</b>
          <span>Пробег</span><b>{plan ? `${plan.total_km.toFixed(0)} км` : "—"}</b>
          <span>Загрузка</span><b>{plan ? fmtPct(plan.fleet_utilization_pct) : "—"}</b>
          <span>Окна</span><b className={(plan?.tw_violations || 0) > 0 ? "warn" : ""}>{plan?.tw_violations ?? 0}</b>
          <span>Score</span><b>{plan ? plan.score.toFixed(1) : "—"}</b>
          <span>Расчет</span><b>{plan ? `${plan.solve_time_ms} мс` : "—"}</b>
        </div>
      </section>

      <section className="planner-explain-section">
        <h3>Параметры</h3>
        <div className="planner-explain-grid">
          <span>Provider</span><b>{routing?.used_provider || routing?.active_provider || "—"}</b>
          <span>Запрошен</span><b>{routing?.requested_source || "—"}</b>
          <span>Fallback</span><b className={routing?.fallback_used ? "warn" : ""}>{routing?.fallback_used ? "да" : "нет"}</b>
          <span>Пар матрицы</span><b>{routing?.matrix_pairs ?? "—"}</b>
          <span>Решатель</span><b>{solver?.used_solver || plan?.solver_used || "—"}</b>
          <span>Режим</span><b>{solver?.requested_solver || "—"}</b>
          <span>Лимит</span><b>{solver?.time_limit_s ? `${solver.time_limit_s} с` : "—"}</b>
          <span>Окна</span><b>{explain?.constraints?.fallback_time_windows ? "часть fallback" : "Oracle/fallback"}</b>
        </div>
      </section>

      <section className="planner-explain-section">
        <h3>Ход расчета</h3>
        <div className="planner-step-list">
          {steps.length === 0 && <div className="planner-explain-empty">Расчет еще не запускался.</div>}
          {steps.map(step => (
            <div key={`${step.code}-${step.label}`} className={`planner-step ${step.status}`}>
              <span>{explainStatusLabel(step.status)}</span>
              <b>{step.label}</b>
              <small>{step.message}</small>
            </div>
          ))}
        </div>
      </section>

      <section className="planner-explain-section">
        <h3>Загрузка автомобилей</h3>
        <div className="planner-explain-grid">
          <span>Машин всего</span><b>{fleet?.vehicles_total ?? "—"}</b>
          <span>Использовано</span><b>{fleet?.vehicles_used ?? "—"}</b>
          <span>Цель 4 рейса/маш.</span><b>{targetRoutes || "—"}</b>
          <span>План требует</span><b className={plannedRoutes > targetRoutes && targetRoutes > 0 ? "warn" : ""}>{plannedRoutes || "—"}</b>
          <span>Средняя</span><b>{fmtPct(fleet?.avg_utilization_pct ?? plan?.fleet_utilization_pct)}</b>
          <span>Минимум</span><b>{fmtPct(fleet?.min_utilization_pct)}</b>
          <span>Максимум</span><b>{fmtPct(fleet?.max_utilization_pct)}</b>
          <span>Низкая загрузка</span><b className={(fleet?.low_utilization_routes || 0) > 0 ? "warn" : ""}>{fleet?.low_utilization_routes ?? 0}</b>
          <span>Перегруз</span><b className={(fleet?.over_capacity_routes || 0) > 0 ? "error" : ""}>{fleet?.over_capacity_routes ?? 0}</b>
        </div>
        <div className="planner-car-list">
          {(plan?.routes || []).slice(0, 150).map(route => (
            <div key={`${route.vehicle_id}-${route.vehicle_num}`} className="planner-car-row">
              <div>
                <b>{route.vehicle_num}</b>
                <span>{route.vehicle_type || "тип не задан"} · {route.stops.length} адресов</span>
              </div>
              <div className="planner-car-load">
                <span>{route.total_pallets}/{route.max_pallets} пал</span>
                <i><em style={{ width: `${Math.min(100, route.utilization_pct)}%` }} /></i>
                <strong className={route.utilization_pct > 100 ? "error" : route.utilization_pct < 60 ? "warn" : ""}>
                  {route.utilization_pct.toFixed(0)}%
                </strong>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="planner-explain-section">
        <h3>Предупреждения</h3>
        {warnings.length === 0 ? (
          <div className="planner-explain-empty">Критичных предупреждений нет.</div>
        ) : (
          <div className="planner-warning-list">
            {warnings.map(w => (
              <div key={`${w.code}-${w.message}`} className={`planner-warning ${w.severity}`}>
                <b>{w.message}</b>
                {w.action && <span>{w.action}</span>}
              </div>
            ))}
          </div>
        )}
      </section>

      <div className="planner-explain-actions">
        <button onClick={onCopy} disabled={!plan}>Скопировать отчет</button>
        <button onClick={onClose}>Открыть план на карте</button>
      </div>
    </aside>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export function TransportPlannerPage({ onBack }: { onBack: () => void }) {
  const [orders, setOrders] = useState<PlannerOrder[]>([]);
  const [status, setStatus] = useState<RoutingStatus | null>(null);
  const [transportTypes, setTransportTypes] = useState<TransportType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [filterDate, setFilterDate] = useState(todayIso());
  const [trTypeFilter, setTrTypeFilter] = useState("");
  const [solverMode, setSolverMode] = useState<"auto" | "cluster" | "savings" | "attention_model">("auto");

  // Map layers
  const [showClusters, setShowClusters] = useState(false);

  // Selected marker & polygon selection
  const [selectedSt, setSelectedSt] = useState<PlannerOrder | null>(null);
  const [polygonSelection, setPolygonSelection] = useState<Set<string>>(new Set());

  // VRP plan state
  const [plan, setPlan] = useState<VrpPlan | null>(null);
  const [solving, setSolving] = useState(false);
  const [solveError, setSolveError] = useState<string | null>(null);
  const [solveElapsed, setSolveElapsed] = useState(0);
  const solveTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [explainOpen, setExplainOpen] = useState(false);
  const [matrixMessage, setMatrixMessage] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Apply plan state
  const [applying, setApplying] = useState(false);
  const [applyDone, setApplyDone] = useState<{ tasks_created: number } | null>(null);

  // Templates
  const [templates, setTemplates] = useState<PlanTemplate[]>([]);
  const [loadingTemplates, setLoadingTemplates] = useState(false);

  // Tab: 'map' | 'analytics'
  const [activeTab, setActiveTab] = useState<"map" | "analytics">("map");

  // Sprint 111 — GPS live positions
  const [vehiclePositions, setVehiclePositions] = useState<{vehicle_id:number;num_plat:string;lat:number;lon:number;speed_kmh:number;last_seen:string}[]>([]);
  useEffect(() => {
    const loadPositions = () =>
      apiFetch<typeof vehiclePositions>("/api/admin/transport/vehicles/positions")
        .then(setVehiclePositions).catch(() => {});
    loadPositions();
    const timer = setInterval(loadPositions, 30000);
    return () => clearInterval(timer);
  }, []); // eslint-disable-line

  // Drag-and-drop editing of plan routes (Sprint 24)
  const [localRoutes, setLocalRoutes] = useState<VrpRouteItem[] | null>(null);
  const [expandedRouteIdx, setExpandedRouteIdx] = useState<number | null>(null);
  const dragSrc = useRef<{ routeIdx: number; stopIdx: number } | null>(null);

  const visibleOrders = orders.filter(o => o.LAT && o.LON);
  const noCoords = orders.filter(o => !o.LAT || !o.LON);
  const totalPallets = visibleOrders.reduce((s, o) => s + o.PALLETS_COUNT, 0);
  const totalWeight = visibleOrders.reduce((s, o) => s + o.WEIGHT_KG, 0);
  const clusters = buildClusters(visibleOrders);

  const loadOrders = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const params = new URLSearchParams({ date: filterDate });
      if (trTypeFilter) params.set("transport_type", trTypeFilter);
      const data = await apiFetch<PlannerOrder[]>(`/api/admin/transport/planner/orders?${params}`);
      setOrders(data);
      setPolygonSelection(new Set());
    } catch (e) {
      setError(String(e));
      setOrders([]);
    } finally { setLoading(false); }
  }, [filterDate, trTypeFilter]);

  useEffect(() => { loadOrders(); }, [loadOrders]);

  useEffect(() => {
    apiFetch<RoutingStatus>("/api/admin/transport/routing/status")
      .then(setStatus).catch(() => setStatus(null));
    apiFetch<TransportType[]>("/api/admin/transport/types")
      .then(setTransportTypes).catch(() => setTransportTypes([]));
  }, []);

  useEffect(() => {
    if (!toastMessage) return;
    const timer = setTimeout(() => setToastMessage(null), 5000);
    return () => clearTimeout(timer);
  }, [toastMessage]);

  const loadTemplates = useCallback(async () => {
    setLoadingTemplates(true);
    try {
      const data = await apiFetch<PlanTemplate[]>(
        `/api/admin/transport/planner/templates?plan_date=${filterDate}&lookback_days=90&min_jaccard=0.5`,
      );
      setTemplates(data);
    } catch {
      setTemplates([]);
    } finally { setLoadingTemplates(false); }
  }, [filterDate]);

  // ---------------------------------------------------------------------------
  // Polygon selection
  // ---------------------------------------------------------------------------

  const handlePolygonCreated = useCallback((e: any) => {
    const layer = e.layer;
    const leaflet = (window as any).L;
    if (!leaflet || !layer) return;
    const selected = new Set<string>();
    for (const o of visibleOrders) {
      const pt = leaflet.latLng(o.LAT!, o.LON!);
      if (layer.getBounds && layer.getBounds().contains(pt)) {
        // More precise: check if point is inside polygon
        if (layer.getLatLngs) {
          selected.add(o.ST_NUMBER);
        }
      }
    }
    setPolygonSelection(selected);
  }, [visibleOrders]);

  const handleClusterClick = useCallback((cluster: OrderCluster) => {
    const stNums = new Set(cluster.orders.map(o => o.ST_NUMBER));
    setPolygonSelection(prev => {
      // Toggle: if all selected → deselect, else select all
      const allSelected = cluster.orders.every(o => prev.has(o.ST_NUMBER));
      if (allSelected) {
        const next = new Set(prev);
        stNums.forEach(s => next.delete(s));
        return next;
      }
      return new Set([...prev, ...stNums]);
    });
  }, []);

  // ---------------------------------------------------------------------------
  // VRP solve
  // ---------------------------------------------------------------------------

  // Sprint 101 — active job id for cancel
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  const handleCancelSolve = useCallback(async () => {
    if (!activeJobId) return;
    try {
      await apiFetch(`/api/admin/transport/planner/solve/${activeJobId}`, { method: "DELETE" });
    } catch { /* ignore */ }
    setActiveJobId(null);
    setSolving(false);
    if (solveTimerRef.current) clearInterval(solveTimerRef.current);
  }, [activeJobId]);

  const handleSolve = useCallback(async () => {
    setSolving(true); setSolveError(null); setPlan(null); setApplyDone(null);
    setMatrixMessage(null);
    setExplainOpen(true);
    setSolveElapsed(0);
    solveTimerRef.current = setInterval(() => setSolveElapsed(s => s + 1), 1000);
    try {
      const body = {
        plan_date: filterDate,
        transport_type: trTypeFilter || null,
        time_limit_s: 60,
        source: "auto",
        solver: solverMode,
      };
      // Sprint 101: new API returns {job_id, stream_url}
      const jobResp = await apiFetch<{ job_id?: string; routes?: unknown[] }>(
        "/api/admin/transport/planner/solve",
        { method: "POST", body: JSON.stringify(body) },
      );
      // Support both old (direct VrpPlan) and new (job_id) response shapes
      if (jobResp.job_id) {
        setActiveJobId(jobResp.job_id);
        // Poll via SSE
        const es = new EventSource(`/api/admin/transport/planner/solve/${jobResp.job_id}/stream`);
        await new Promise<void>((resolve, reject) => {
          es.onmessage = (e) => {
            const msg = JSON.parse(e.data);
            if (msg.type === "done") {
              es.close();
              // Fetch the actual plan result
              apiFetch<{ routes?: unknown[] }>(`/api/admin/transport/planner/metrics?plan_id=${msg.plan_id || ""}`)
                .then(() => {})
                .catch(() => {});
              resolve();
            } else if (msg.type === "error") {
              es.close();
              reject(new Error(msg.detail || "VRP error"));
            } else if (msg.type === "cancelled") {
              es.close();
              resolve();
            }
          };
          es.onerror = () => { es.close(); reject(new Error("SSE connection error")); };
        });
        setActiveJobId(null);
        // Re-fetch latest plan after solve
        try {
          const history = await apiFetch<{ plan_id: number; routes?: unknown[] }[]>(
            `/api/admin/transport/planner/history?date_from=${filterDate}&date_to=${filterDate}`
          );
          if (history.length > 0) {
            const latest = await apiFetch<typeof history[0]>(
              `/api/admin/transport/planner/metrics?plan_id=${history[0].plan_id}`
            );
            if (latest && (latest as unknown as { routes?: unknown[] }).routes) {
              setPlan(latest as unknown as VrpPlan);
              setLocalRoutes(JSON.parse(JSON.stringify((latest as unknown as VrpPlan).routes)));
              setExpandedRouteIdx(null);
              setExplainOpen(true);
            }
          }
        } catch { /* best effort */ }
      } else if ((jobResp as unknown as VrpPlan).routes) {
        // Legacy direct response
        const result = jobResp as unknown as VrpPlan;
        setPlan(result);
        setLocalRoutes(JSON.parse(JSON.stringify(result.routes)));
        setExpandedRouteIdx(null);
        setExplainOpen(true);
      }
    } catch (e) {
      setSolveError(String(e));
      setExplainOpen(true);
    } finally {
      setSolving(false);
      setActiveJobId(null);
      if (solveTimerRef.current) clearInterval(solveTimerRef.current);
    }
  }, [filterDate, trTypeFilter, solverMode]);

  const handleApplyPlan = useCallback(async () => {
    if (!plan?.plan_id) return;
    if (!window.confirm(`Создать ${plan.routes.length} рейсов? Это действие нельзя отменить.`)) return;
    setApplying(true);
    try {
      const body = { plan_id: plan.plan_id, shipment_date: filterDate };
      const result = await apiFetch<{ tasks_created: number }>("/api/admin/transport/planner/apply", {
        method: "POST",
        body: JSON.stringify(body),
      });
      setApplyDone(result);
    } catch (e) {
      setSolveError(String(e));
    } finally {
      setApplying(false);
    }
  }, [plan, filterDate]);

  const handleRebuildMatrix = useCallback(async () => {
    try {
      const res = await apiFetch<{
        pairs: number;
        computed_pairs?: number;
        skipped_pairs?: number;
        source: string;
        addresses: number;
        cached?: boolean;
      }>(
        "/api/admin/transport/distance-matrix/rebuild?source=auto",
        { method: "POST" },
      );
      const computed = res.computed_pairs ?? res.pairs;
      const cachedText = res.cached ? "использован свежий кэш" : `обновлено ${computed} пар`;
      const msg = `Матрица расстояний: ${cachedText}, всего ${res.pairs} пар, провайдер ${res.source}`;
      setMatrixMessage(msg);
      setToastMessage(msg);
      setExplainOpen(true);
      apiFetch<RoutingStatus>("/api/admin/transport/routing/status").then(setStatus).catch(() => null);
    } catch (e) {
      const msg = `Ошибка пересчета матрицы: ${e}`;
      setMatrixMessage(msg);
      setSolveError(msg);
      setExplainOpen(true);
    }
  }, []);

  const handleApplyTemplate = useCallback(async (tmpl: PlanTemplate) => {
    if (!window.confirm(`Применить шаблон от ${tmpl.plan_date} (Jaccard ${(tmpl.jaccard * 100).toFixed(0)}%)?`)) return;
    setApplying(true);
    try {
      const body = { plan_id: tmpl.plan_id, shipment_date: filterDate };
      const result = await apiFetch<{ tasks_created: number }>("/api/admin/transport/planner/apply", {
        method: "POST",
        body: JSON.stringify(body),
      });
      setApplyDone(result);
    } catch (e) {
      setSolveError(String(e));
    } finally { setApplying(false); }
  }, [filterDate]);

  // ---------------------------------------------------------------------------
  // Drag-and-drop route editing (Sprint 24)
  // ---------------------------------------------------------------------------

  function handleDragStart(routeIdx: number, stopIdx: number) {
    dragSrc.current = { routeIdx, stopIdx };
  }

  function handleDrop(targetRouteIdx: number) {
    const src = dragSrc.current;
    if (!src || !localRoutes) return;
    if (src.routeIdx === targetRouteIdx) { dragSrc.current = null; return; }
    const routes = localRoutes.map(r => ({ ...r, stops: [...r.stops] }));
    const [moved] = routes[src.routeIdx].stops.splice(src.stopIdx, 1);
    routes[targetRouteIdx].stops.push(moved);
    // Recalculate metrics for both affected routes
    for (const ri of [src.routeIdx, targetRouteIdx]) {
      const r = routes[ri];
      r.total_pallets = r.stops.reduce((s, stop) => s + stop.pallets, 0);
      r.total_kg = r.stops.reduce((s, stop) => s + stop.weight_kg, 0);
      r.utilization_pct = r.max_pallets > 0
        ? Math.round((r.total_pallets / r.max_pallets) * 100)
        : 0;
    }
    setLocalRoutes(routes);
    dragSrc.current = null;
  }

  function resetLocalRoutes() {
    if (plan) setLocalRoutes(JSON.parse(JSON.stringify(plan.routes)));
  }

  const displayRoutes = localRoutes ?? plan?.routes ?? [];
  const routesModified = localRoutes !== null && plan !== null &&
    JSON.stringify(localRoutes.map(r => r.stops.map(s => s.st_number))) !==
    JSON.stringify(plan.routes.map(r => r.stops.map(s => s.st_number)));

  // Polylines for plan routes
  const routePolylines = displayRoutes.map(route =>
    route.stops.filter(s => s.lat && s.lon).map(s => [s.lat!, s.lon!] as [number, number])
  );
  const currentExplain = plan?.explain || buildFallbackExplain(plan, orders, status, filterDate, solverMode);

  const copyExplainReport = useCallback(async () => {
    const report = buildExplainReport(plan, currentExplain);
    if (!report) return;
    try {
      await navigator.clipboard.writeText(report);
      setToastMessage("Отчет расчета скопирован");
    } catch {
      setToastMessage("Не удалось скопировать отчет");
    }
  }, [plan, currentExplain]);

  return (
    <div className="planner-shell">
      {/* Topbar */}
      <header className="planner-topbar">
        <button className="dispatch-back" onClick={onBack}>◄</button>
        <div className="dispatch-title">
          <h1>Планировщик маршрутов</h1>
          <span className="dispatch-subtitle">Карта + VRP + Аналитика · Sprint 10</span>
        </div>
        <div className="planner-tabs">
          <button className={`planner-tab ${activeTab === "map" ? "active" : ""}`}
            onClick={() => setActiveTab("map")}>Карта</button>
          <button className={`planner-tab ${activeTab === "analytics" ? "active" : ""}`}
            onClick={() => setActiveTab("analytics")}>Аналитика</button>
        </div>
        {(loading || solving) && <span className="dispatch-spinner">●</span>}
        {solving && <span className="planner-solve-timer">Решаем... {solveElapsed}с</span>}
        {/* Sprint 101 — cancel solve */}
        {solving && activeJobId && (
          <button className="planner-cancel-solve-btn" onClick={handleCancelSolve} title="Остановить оптимизатор">
            ✕ Отмена
          </button>
        )}
        {polygonSelection.size > 0 && (
          <span className="planner-polygon-badge">
            ▣ {polygonSelection.size} СТ выделено
          </span>
        )}
        {(error || solveError) && (
          <span className="dispatch-error" title={error || solveError!}
            onClick={() => { setError(null); setSolveError(null); }} style={{ cursor: "pointer" }}>
            ⚠ {(error || solveError)!.slice(0, 100)}
          </span>
        )}
        {status && status.ungeocoded_count > 0 && (
          <span className="planner-nogeo-warn">⚠ {status.ungeocoded_count} адресов без координат</span>
        )}
      </header>

      {activeTab === "analytics" && (
        <div className="planner-analytics-wrap">
          <PlannerAnalyticsTab targetDate={filterDate} />
        </div>
      )}

      <div className="planner-workspace" style={{ display: activeTab === "map" ? "flex" : "none" }}>
        {/* ---- Left filter panel ---- */}
        <aside className="planner-left-panel">
          <div className="dispatch-fp-label">Дата СТ</div>
          <input className="dispatch-fp-input" type="date" value={filterDate}
            onChange={e => setFilterDate(e.target.value)} />

          <div className="dispatch-fp-label">Тип ТС</div>
          <select className="dispatch-fp-select" value={trTypeFilter}
            onChange={e => setTrTypeFilter(e.target.value)}>
            <option value="">Все</option>
            {transportTypes.map(t => (
              <option key={t.TRANSPORTTYPE} value={t.TRANSPORTTYPE}>
                {t.TRANSPORTTYPE}{t.NAME ? ` — ${t.NAME}` : ""}
              </option>
            ))}
          </select>

          <div className="dispatch-fp-label">Решатель</div>
          <select className="dispatch-fp-select" value={solverMode}
            onChange={e => setSolverMode(e.target.value as any)}>
            <option value="auto">auto (OR-Tools / CW)</option>
            <option value="cluster">cluster (DBSCAN)</option>
            <option value="savings">savings (Clarke-Wright)</option>
            <option value="attention_model">🤖 AI (Attention Model)</option>
          </select>

          <div className="planner-layer-toggle">
            <label>
              <input type="checkbox" checked={showClusters} onChange={e => setShowClusters(e.target.checked)} />
              &nbsp;Слой кластеров (по RAION)
            </label>
          </div>

          <button className="dispatch-refresh-btn planner-reload-btn" onClick={loadOrders}>⟳ Обновить</button>

          <div className="dispatch-fp-sep" />

          <div className="planner-stat-block">
            <div className="planner-stat-row"><span>Всего СТ</span><b>{orders.length}</b></div>
            <div className="planner-stat-row"><span>На карте</span><b>{visibleOrders.length}</b></div>
            <div className="planner-stat-row"><span>Паллет</span><b>{totalPallets}</b></div>
            <div className="planner-stat-row"><span>Вес, кг</span><b>{totalWeight.toFixed(0)}</b></div>
            {noCoords.length > 0 && (
              <div className="planner-stat-row planner-stat-warn">
                <span>Без координат</span><b>{noCoords.length}</b>
              </div>
            )}
            {polygonSelection.size > 0 && (
              <div className="planner-stat-row">
                <span>Выделено</span><b>{polygonSelection.size}</b>
              </div>
            )}
          </div>

          <div className="dispatch-fp-sep" />

          <button
            className="planner-solve-btn"
            onClick={handleSolve}
            disabled={solving || visibleOrders.length === 0}
          >
            {solving ? "⏳ Решаем..." : "⚡ Авто-план"}
          </button>
          <button
            className="planner-explain-open-btn"
            onClick={() => setExplainOpen(true)}
            disabled={!plan && !solving && !matrixMessage && !solveError}
          >
            Детали расчета
          </button>

          {plan && !applyDone && (
            <button
              className="planner-apply-btn"
              onClick={handleApplyPlan}
              disabled={applying || !plan.plan_id}
            >
              {applying ? "⏳ Создаём..." : `✓ Применить план (${displayRoutes.length} рейсов)`}
            </button>
          )}

          {applyDone && (
            <div className="planner-apply-done">✅ Создано рейсов: {applyDone.tasks_created}</div>
          )}

          <div className="dispatch-fp-sep" />

          {plan && (
            <div className="planner-metrics-block" onClick={() => setExplainOpen(true)} title="Открыть детали расчета">
              <div className="dispatch-fp-label">Метрики плана</div>
              <div className="planner-stat-row"><span>Рейсов</span><b>{plan.routes.length}</b></div>
              <div className="planner-stat-row"><span>Пробег, км</span><b>{plan.total_km.toFixed(0)}</b></div>
              <div className="planner-stat-row">
                <span>Утилизация</span><b>{plan.fleet_utilization_pct.toFixed(1)}%</b>
              </div>
              <div className="planner-stat-row">
                <span>Нарушений окон</span>
                <b className={plan.tw_violations > 0 ? "planner-warn-val" : ""}>{plan.tw_violations}</b>
              </div>
              <div className="planner-stat-row"><span>Score</span><b>{plan.score.toFixed(1)}</b></div>
              <div className="planner-stat-row planner-solver-row">
                <span>Решатель</span>
                <b className="planner-solver-badge">{plan.solver_used}</b>
              </div>
              <div className="planner-stat-row"><span>Расчёт</span><b>{plan.solve_time_ms} мс</b></div>
              {plan.unassigned_sts.length > 0 && (
                <div className="planner-stat-row planner-stat-warn">
                  <span>Без рейса</span><b>{plan.unassigned_sts.length}</b>
                </div>
              )}
            </div>
          )}

          <div className="dispatch-fp-sep" />

          {/* Warehouse legend */}
          <div className="dispatch-fp-label">Легенда складов</div>
          {Object.entries(WARE_COLORS).map(([wareId, color]) => (
            <div key={wareId} className="planner-legend-row">
              <span className="planner-legend-dot" style={{ background: color }} />
              <span>Склад {wareId}</span>
            </div>
          ))}
          <div className="planner-legend-row">
            <span className="planner-legend-dot" style={{ background: "#94a3b8" }} />
            <span>Прочие</span>
          </div>

          <div className="dispatch-fp-sep" />
          <div className="planner-hint">
            Полигон: нарисуйте зону — СТ внутри выделятся.<br />
            Кластер: кликните на название района.
          </div>

          {status && (
            <div className="planner-provider-badge">
              Геокодинг: <b>{status.provider.toUpperCase()}</b>
              <br />{status.geocoded_count} из {status.total_addresses} геокодировано
              <button className="planner-matrix-btn" onClick={handleRebuildMatrix}>⟳ Матрица</button>
            </div>
          )}
        </aside>

        {/* ---- Map ---- */}
        <div className="planner-map-wrap">
          {orders.length === 0 && !loading && !solving && (
            <div className="planner-no-data">Нет данных. Проверьте дату и фильтры.</div>
          )}
          <MapContainer
            center={[55.75, 37.62]}
            zoom={9}
            style={{ height: "100%", width: "100%" }}
            scrollWheelZoom
            attributionControl={false}
          >
            <AttributionControl
              position="bottomright"
              prefix={false}
            />
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapBoundsAdjuster orders={visibleOrders} />

            {/* Cluster polygons */}
            {showClusters && clusters.map((cluster, idx) => {
              const pts: LatLngExpression[] = cluster.orders
                .filter(o => o.LAT && o.LON)
                .map(o => [o.LAT!, o.LON!]);
              if (pts.length < 3) return null;
              return (
                <Polygon
                  key={cluster.raion}
                  positions={pts}
                  pathOptions={{
                    color: ROUTE_COLORS[idx % ROUTE_COLORS.length],
                    fillColor: CLUSTER_BG_COLORS[idx % CLUSTER_BG_COLORS.length],
                    fillOpacity: 1,
                    weight: 1.5,
                    dashArray: "5 3",
                  }}
                  eventHandlers={{ click: () => handleClusterClick(cluster) }}
                >
                  <Popup>
                    <div style={{ fontSize: 12 }}>
                      <b>{cluster.raion}</b><br />
                      {cluster.orders.length} СТ<br />
                      <button onClick={() => handleClusterClick(cluster)}
                        style={{ marginTop: 4, fontSize: 11 }}>
                        Выделить все
                      </button>
                    </div>
                  </Popup>
                </Polygon>
              );
            })}

            {/* Route polylines */}
            {routePolylines.map((positions, idx) =>
              positions.length > 1 ? (
                <Polyline
                  key={idx}
                  positions={positions}
                  pathOptions={{ color: routeColor(idx), weight: 3, opacity: 0.75 }}
                />
              ) : null
            )}

            {/* Polygon draw tool */}
            <FeatureGroup>
              <EditControl
                position="topright"
                onCreated={handlePolygonCreated}
                draw={{
                  rectangle: false,
                  circle: false,
                  circlemarker: false,
                  marker: false,
                  polyline: false,
                  polygon: { allowIntersection: false },
                }}
                edit={{ edit: false, remove: true }}
              />
            </FeatureGroup>

            {/* Order markers */}
            {visibleOrders.map(o => {
              const isSelected = polygonSelection.has(o.ST_NUMBER);
              return (
                <CircleMarker
                  key={o.ST_NUMBER}
                  center={[o.LAT!, o.LON!]}
                  radius={markerRadius(o.PALLETS_COUNT)}
                  pathOptions={{
                    color: isSelected ? "#f97316" : wareColor(o.WARE_ID),
                    fillColor: isSelected ? "#f97316" : wareColor(o.WARE_ID),
                    fillOpacity: (isSelected || o === selectedSt) ? 1.0 : 0.72,
                    weight: o.TW_STRICT ? 3 : (isSelected ? 2.5 : 1.5),
                    dashArray: o.TW_STRICT ? "4 2" : undefined,
                  }}
                  eventHandlers={{ click: () => setSelectedSt(o) }}
                >
                  <Popup>
                    <div className="planner-popup">
                      <div className="planner-popup-title">СТ {o.ST_NUMBER}</div>
                      <div>{o.REGION ?? o.ADDR ?? "—"}</div>
                      {o.RAION && <div className="planner-popup-muted">{o.RAION}</div>}
                      <div className="planner-popup-sep" />
                      <div><b>{o.PALLETS_COUNT}</b> пал · <b>{o.WEIGHT_KG.toFixed(0)}</b> кг</div>
                      {o.VOLUME_M3 != null && <div>{o.VOLUME_M3.toFixed(2)} м³</div>}
                      <div>Дата: {fmtDate(o.STDATE)}</div>
                      {o.TRANSPORT_TYPE && o.TRANSPORT_TYPE !== "0" && (
                        <div>Тип ТС: {o.TRANSPORT_TYPE}</div>
                      )}
                      {o.TW_STRICT === 1 && <div className="planner-popup-strict">⏰ Жёсткое окно</div>}
                      {o.NEEDS_HYDRO_BOARD === 1 && <div>♿ Нужен гидроборт</div>}
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
            {/* Sprint 111 — GPS vehicle positions */}
            {vehiclePositions.filter(p => p.lat && p.lon).map(p => (
              <CircleMarker
                key={`gps-${p.vehicle_id}`}
                center={[p.lat, p.lon]}
                radius={7}
                pathOptions={{ color: "#f59e0b", fillColor: "#fbbf24", fillOpacity: 0.9, weight: 2 }}
              >
                <Popup>
                  <div><b>🚛 {p.num_plat}</b></div>
                  <div>{p.speed_kmh} км/ч · {p.last_seen?.slice(11,16)}</div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>

        {/* ---- Right plan panel ---- */}
        {(plan && displayRoutes.length > 0) || templates.length > 0 ? (
          <aside className="planner-right-panel">
            {/* Routes list */}
            {plan && displayRoutes.length > 0 && (
              <>
                <div className="planner-rp-title">
                  Рейсов: {displayRoutes.length}
                  {plan.unassigned_sts.length > 0 && (
                    <span className="planner-rp-unassigned"> · {plan.unassigned_sts.length} без рейса</span>
                  )}
                  {routesModified && (
                    <button className="planner-reset-btn" onClick={resetLocalRoutes} title="Сбросить изменения">↺</button>
                  )}
                </div>
                {routesModified && (
                  <div className="planner-modified-hint">Порядок изменён вручную. «Применить план» создаст исходный план.</div>
                )}
                <div className="planner-rp-list">
                  {displayRoutes.map((route, idx) => (
                    <div className="planner-rp-route"
                      key={route.vehicle_id}
                      onDragOver={e => e.preventDefault()}
                      onDrop={() => handleDrop(idx)}>
                      <div className="planner-rp-vehicle"
                        onClick={() => setExpandedRouteIdx(expandedRouteIdx === idx ? null : idx)}
                        style={{ cursor: "pointer" }}>
                        <span className="planner-rp-dot" style={{ background: routeColor(idx) }} />
                        <b>{route.vehicle_num}</b>
                        <span className="planner-rp-type">{route.vehicle_type}</span>
                        <span className="planner-rp-expand-icon">{expandedRouteIdx === idx ? "▲" : "▼"}</span>
                      </div>
                      <div className="planner-rp-stats">
                        <span>{route.total_pallets} пал / {route.max_pallets}</span>
                        <span>{route.total_km.toFixed(0)} км</span>
                        <span>{fmtDuration(route.total_duration_min)}</span>
                      </div>
                      <div className="planner-rp-bar">
                        <div
                          className="planner-rp-bar-fill"
                          style={{
                            width: `${Math.min(100, route.utilization_pct)}%`,
                            background: route.utilization_pct >= 85 ? "#22c55e"
                              : route.utilization_pct >= 60 ? "#f59e0b" : "#ef4444",
                          }}
                        />
                      </div>
                      <div className="planner-rp-util">{route.utilization_pct.toFixed(0)}%</div>
                      <div className="planner-rp-stops">{route.stops.length} адресов</div>
                      {expandedRouteIdx === idx && (
                        <div className="planner-rp-stop-list">
                          {route.stops.map((stop, si) => (
                            <div key={stop.st_number}
                              className="planner-rp-stop-item"
                              draggable
                              onDragStart={() => handleDragStart(idx, si)}>
                              <span className="planner-rp-stop-dot" style={{ background: wareColor(stop.ware_id) }} />
                              <span className="planner-rp-stop-st">{stop.st_number}</span>
                              <span className="planner-rp-stop-addr">{stop.addr ?? "—"}</span>
                              <span className="planner-rp-stop-pal">{stop.pallets}пал</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </>
            )}

            {/* Templates */}
            <div className="planner-rp-sep" />
            <div className="planner-rp-title">
              Похожие маршруты
              <button className="planner-tmpl-load-btn" onClick={loadTemplates} disabled={loadingTemplates}>
                {loadingTemplates ? "..." : "⟳"}
              </button>
            </div>
            {templates.length === 0 && !loadingTemplates && (
              <div className="planner-tmpl-empty">Нажмите ⟳ для поиска</div>
            )}
            {templates.map(tmpl => (
              <div className="planner-tmpl-item" key={tmpl.plan_id}>
                <div className="planner-tmpl-date">{tmpl.plan_date}</div>
                <div className="planner-tmpl-meta">
                  {tmpl.routes_count} рейсов · Jaccard {(tmpl.jaccard * 100).toFixed(0)}%
                </div>
                <div className="planner-tmpl-meta planner-tmpl-match">
                  {tmpl.matched_sts} из {tmpl.total_current_sts} СТ совпадают
                </div>
                <button className="planner-tmpl-apply-btn" onClick={() => handleApplyTemplate(tmpl)}>
                  Применить шаблон
                </button>
              </div>
            ))}
          </aside>
        ) : null}
        <TransportPlannerExplainDrawer
          open={explainOpen}
          onClose={() => setExplainOpen(false)}
          plan={plan}
          explain={currentExplain}
          solving={solving}
          solveError={solveError}
          matrixMessage={matrixMessage}
          onCopy={copyExplainReport}
        />
        {toastMessage && (
          <div className="planner-toast" onClick={() => setToastMessage(null)}>
            {toastMessage}
          </div>
        )}
      </div>
    </div>
  );
}
