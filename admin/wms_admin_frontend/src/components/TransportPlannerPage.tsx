import "leaflet/dist/leaflet.css";
import { useCallback, useEffect, useRef, useState } from "react";
import { CircleMarker, MapContainer, Polyline, Popup, TileLayer, useMap } from "react-leaflet";

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
// Warehouse color palette (matches dispatch §3.4)
// ---------------------------------------------------------------------------

const WARE_COLORS: Record<number, string> = {
  5:    "#3b82f6",
  6:    "#22c55e",
  7:    "#f59e0b",
  9201: "#a855f7",
  9202: "#ef4444",
  9203: "#06b6d4",
};

// Route polyline palette (one colour per route, cycling)
const ROUTE_COLORS = [
  "#e11d48", "#2563eb", "#16a34a", "#d97706",
  "#7c3aed", "#0891b2", "#be185d", "#15803d",
];

function wareColor(wareId: number): string {
  return WARE_COLORS[wareId] ?? "#94a3b8";
}

function routeColor(idx: number): string {
  return ROUTE_COLORS[idx % ROUTE_COLORS.length];
}

function markerRadius(pallets: number): number {
  return Math.max(6, Math.min(22, 5 + pallets * 1.4));
}

function fmtDuration(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h > 0 ? `${h}ч ${m}м` : `${m}м`;
}

// ---------------------------------------------------------------------------
// MapBoundsAdjuster — авто-зум под видимые маркеры
// ---------------------------------------------------------------------------

function MapBoundsAdjuster({ orders }: { orders: PlannerOrder[] }) {
  const map = useMap();
  useEffect(() => {
    const pts = orders.filter(o => o.LAT && o.LON).map(o => [o.LAT!, o.LON!] as [number, number]);
    if (pts.length === 0) return;
    try {
      map.fitBounds(pts, { padding: [30, 30], maxZoom: 12 });
    } catch { /* ignore invalid bounds */ }
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

  // Selected marker
  const [selectedSt, setSelectedSt] = useState<PlannerOrder | null>(null);

  // VRP plan state
  const [plan, setPlan] = useState<VrpPlan | null>(null);
  const [solving, setSolving] = useState(false);
  const [solveError, setSolveError] = useState<string | null>(null);
  const [solveElapsed, setSolveElapsed] = useState(0);
  const solveTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Apply plan state
  const [applying, setApplying] = useState(false);
  const [applyDone, setApplyDone] = useState<{ tasks_created: number } | null>(null);

  // Stats
  const visibleOrders = orders.filter(o => o.LAT && o.LON);
  const noCoords = orders.filter(o => !o.LAT || !o.LON);
  const totalPallets = visibleOrders.reduce((s, o) => s + o.PALLETS_COUNT, 0);
  const totalWeight = visibleOrders.reduce((s, o) => s + o.WEIGHT_KG, 0);

  const loadOrders = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const params = new URLSearchParams({ date: filterDate });
      if (trTypeFilter) params.set("transport_type", trTypeFilter);
      const data = await apiFetch<PlannerOrder[]>(`/api/admin/transport/planner/orders?${params}`);
      setOrders(data);
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
  }, [filterDate, trTypeFilter]);

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
      apiFetch<RoutingStatus>("/api/admin/transport/routing/status")
        .then(setStatus).catch(() => null);
    } catch (e) {
      alert(`Ошибка: ${e}`);
    }
  }, []);

  // Build polyline positions from plan routes
  const routePolylines = plan?.routes.map(route => {
    const pts: [number, number][] = route.stops
      .filter(s => s.lat && s.lon)
      .map(s => [s.lat!, s.lon!]);
    return pts;
  }) ?? [];

  return (
    <div className="planner-shell">
      {/* Topbar */}
      <header className="planner-topbar">
        <button className="dispatch-back" onClick={onBack}>◄</button>
        <div className="dispatch-title">
          <h1>Планировщик маршрутов</h1>
          <span className="dispatch-subtitle">Карта заказов + VRP-оптимизатор · Sprint 8</span>
        </div>
        {(loading || solving) && <span className="dispatch-spinner">●</span>}
        {solving && (
          <span className="planner-solve-timer">Решаем... {solveElapsed}с</span>
        )}
        {(error || solveError) && (
          <span className="dispatch-error" title={error || solveError!}
            onClick={() => { setError(null); setSolveError(null); }} style={{ cursor: "pointer" }}>
            ⚠ {(error || solveError)!.slice(0, 100)}
          </span>
        )}
        {status && status.ungeocoded_count > 0 && (
          <span className="planner-nogeo-warn" title="Адресов без координат — не будут показаны на карте">
            ⚠ {status.ungeocoded_count} адресов без координат
          </span>
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

          <button className="dispatch-refresh-btn planner-reload-btn" onClick={loadOrders}>
            ⟳ Обновить
          </button>

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
          </div>

          <div className="dispatch-fp-sep" />

          {/* VRP Controls */}
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
            <div className="planner-apply-done">
              ✅ Создано рейсов: {applyDone.tasks_created}
            </div>
          )}

          <div className="dispatch-fp-sep" />

          {/* Plan metrics */}
          {plan && (
            <div className="planner-metrics-block">
              <div className="dispatch-fp-label">Метрики плана</div>
              <div className="planner-stat-row">
                <span>Рейсов</span><b>{plan.routes.length}</b>
              </div>
              <div className="planner-stat-row">
                <span>Пробег, км</span><b>{plan.total_km.toFixed(0)}</b>
              </div>
              <div className="planner-stat-row">
                <span>Утилизация парка</span>
                <b>{plan.fleet_utilization_pct.toFixed(1)}%</b>
              </div>
              <div className="planner-stat-row">
                <span>Нарушений окон</span>
                <b className={plan.tw_violations > 0 ? "planner-warn-val" : ""}>{plan.tw_violations}</b>
              </div>
              <div className="planner-stat-row">
                <span>Score</span><b>{plan.score.toFixed(1)}</b>
              </div>
              <div className="planner-stat-row planner-solver-row">
                <span>Решатель</span>
                <b className="planner-solver-badge">{plan.solver_used}</b>
              </div>
              <div className="planner-stat-row">
                <span>Время расчёта</span><b>{plan.solve_time_ms} мс</b>
              </div>
              {plan.unassigned_sts.length > 0 && (
                <div className="planner-stat-row planner-stat-warn">
                  <span>Не распределено СТ</span><b>{plan.unassigned_sts.length}</b>
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
            Размер кружка пропорционален числу паллет.
            Нажмите на маркер — карточка СТ.
          </div>

          {status && (
            <div className="planner-provider-badge">
              Геокодинг: <b>{status.provider.toUpperCase()}</b>
              <br />{status.geocoded_count} из {status.total_addresses} геокодировано
              <button className="planner-matrix-btn" onClick={handleRebuildMatrix}
                title="Пересчитать матрицу расстояний">⟳ Матрица</button>
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

            {/* Order markers */}
            {visibleOrders.map(o => (
              <CircleMarker
                key={o.ST_NUMBER}
                center={[o.LAT!, o.LON!]}
                radius={markerRadius(o.PALLETS_COUNT)}
                pathOptions={{
                  color: wareColor(o.WARE_ID),
                  fillColor: wareColor(o.WARE_ID),
                  fillOpacity: o === selectedSt ? 1.0 : 0.72,
                  weight: o.TW_STRICT ? 3 : 1.5,
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
                    {o.VERIFY_PERC != null && <div>Сборка: {o.VERIFY_PERC}%</div>}
                    {o.TRANSPORT_TYPE && o.TRANSPORT_TYPE !== "0" && (
                      <div>Тип ТС: {o.TRANSPORT_TYPE}</div>
                    )}
                    {o.TW_STRICT === 1 && (
                      <div className="planner-popup-strict">⏰ Жёсткое окно</div>
                    )}
                    {o.NEEDS_HYDRO_BOARD === 1 && (
                      <div>♿ Нужен гидроборт</div>
                    )}
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>

        {/* ---- Right plan panel ---- */}
        {plan && plan.routes.length > 0 && (
          <aside className="planner-right-panel">
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
          </aside>
        )}
      </div>
    </div>
  );
}
