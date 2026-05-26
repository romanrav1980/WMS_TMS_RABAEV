import "leaflet/dist/leaflet.css";
import { useCallback, useEffect, useState } from "react";
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from "react-leaflet";

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

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8088";
const API_AUTH = import.meta.env.VITE_ADMIN_BASIC_AUTH || "admin:admin123";

function apiHeaders(): HeadersInit {
  return { Authorization: `Basic ${btoa(API_AUTH)}`, "Content-Type": "application/json" };
}

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { headers: apiHeaders() });
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

function wareColor(wareId: number): string {
  return WARE_COLORS[wareId] ?? "#94a3b8";
}

function markerRadius(pallets: number): number {
  return Math.max(6, Math.min(22, 5 + pallets * 1.4));
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

  return (
    <div className="planner-shell">
      {/* Topbar */}
      <header className="planner-topbar">
        <button className="dispatch-back" onClick={onBack}>◄</button>
        <div className="dispatch-title">
          <h1>Планировщик маршрутов</h1>
          <span className="dispatch-subtitle">Карта заказов · Sprint 7</span>
        </div>
        {loading && <span className="dispatch-spinner">●</span>}
        {error && (
          <span className="dispatch-error" title={error} onClick={() => setError(null)} style={{ cursor: "pointer" }}>
            ⚠ {error.slice(0, 100)}
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
            </div>
          )}
        </aside>

        {/* ---- Map ---- */}
        <div className="planner-map-wrap">
          {orders.length === 0 && !loading && (
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
      </div>
    </div>
  );
}
