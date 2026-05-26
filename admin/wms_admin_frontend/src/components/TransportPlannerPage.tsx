import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  CircleMarker, FeatureGroup, MapContainer,
  Polygon, Polyline, Popup, TileLayer, useMap,
} from "react-leaflet";
import { EditControl } from "react-leaflet-draw";
import type { LatLngExpression } from "leaflet";

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
  const [solverMode, setSolverMode] = useState<"auto" | "cluster" | "savings">("auto");

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

  // Apply plan state
  const [applying, setApplying] = useState(false);
  const [applyDone, setApplyDone] = useState<{ tasks_created: number } | null>(null);

  // Templates
  const [templates, setTemplates] = useState<PlanTemplate[]>([]);
  const [loadingTemplates, setLoadingTemplates] = useState(false);

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

  const handleSolve = useCallback(async () => {
    setSolving(true); setSolveError(null); setPlan(null); setApplyDone(null);
    setSolveElapsed(0);
    solveTimerRef.current = setInterval(() => setSolveElapsed(s => s + 1), 1000);
    try {
      const body = {
        plan_date: filterDate,
        transport_type: trTypeFilter || null,
        time_limit_s: 30,
        source: "auto",
        solver: solverMode,
      };
      const result = await apiFetch<VrpPlan>("/api/admin/transport/planner/solve", {
        method: "POST",
        body: JSON.stringify(body),
      });
      setPlan(result);
    } catch (e) {
      setSolveError(String(e));
    } finally {
      setSolving(false);
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
      const res = await apiFetch<{ pairs: number; source: string; addresses: number }>(
        "/api/admin/transport/distance-matrix/rebuild?source=auto",
        { method: "POST" },
      );
      alert(`Матрица пересчитана: ${res.pairs} пар, провайдер ${res.source}`);
      apiFetch<RoutingStatus>("/api/admin/transport/routing/status").then(setStatus).catch(() => null);
    } catch (e) {
      alert(`Ошибка: ${e}`);
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

  // Polylines for plan routes
  const routePolylines = plan?.routes.map(route =>
    route.stops.filter(s => s.lat && s.lon).map(s => [s.lat!, s.lon!] as [number, number])
  ) ?? [];

  return (
    <div className="planner-shell">
      {/* Topbar */}
      <header className="planner-topbar">
        <button className="dispatch-back" onClick={onBack}>◄</button>
        <div className="dispatch-title">
          <h1>Планировщик маршрутов</h1>
          <span className="dispatch-subtitle">Карта + кластеры + VRP · Sprint 9</span>
        </div>
        {(loading || solving) && <span className="dispatch-spinner">●</span>}
        {solving && <span className="planner-solve-timer">Решаем... {solveElapsed}с</span>}
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

      <div className="planner-workspace">
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

          {plan && !applyDone && (
            <button
              className="planner-apply-btn"
              onClick={handleApplyPlan}
              disabled={applying || !plan.plan_id}
            >
              {applying ? "⏳ Создаём..." : `✓ Применить план (${plan.routes.length} рейсов)`}
            </button>
          )}

          {applyDone && (
            <div className="planner-apply-done">✅ Создано рейсов: {applyDone.tasks_created}</div>
          )}

          <div className="dispatch-fp-sep" />

          {plan && (
            <div className="planner-metrics-block">
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
          >
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
          </MapContainer>
        </div>

        {/* ---- Right plan panel ---- */}
        {(plan && plan.routes.length > 0) || templates.length > 0 ? (
          <aside className="planner-right-panel">
            {/* Routes list */}
            {plan && plan.routes.length > 0 && (
              <>
                <div className="planner-rp-title">
                  Рейсов: {plan.routes.length}
                  {plan.unassigned_sts.length > 0 && (
                    <span className="planner-rp-unassigned"> · {plan.unassigned_sts.length} без рейса</span>
                  )}
                </div>
                <div className="planner-rp-list">
                  {plan.routes.map((route, idx) => (
                    <div className="planner-rp-route" key={route.vehicle_id}>
                      <div className="planner-rp-vehicle">
                        <span className="planner-rp-dot" style={{ background: routeColor(idx) }} />
                        <b>{route.vehicle_num}</b>
                        <span className="planner-rp-type">{route.vehicle_type}</span>
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
      </div>
    </div>
  );
}
