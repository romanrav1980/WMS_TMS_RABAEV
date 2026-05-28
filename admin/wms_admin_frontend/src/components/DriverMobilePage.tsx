/**
 * DriverMobilePage — мобильный интерфейс водителя (PWA).
 * Sprint 103: страница «Мои рейсы» — список рейсов на день
 * Sprint 104: отметка факта операций (Начать / Готово)
 */

import { useEffect, useState, useCallback } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Trip {
  task_id: number;
  shipment_date: string;
  num_plat: string;
  transport_type: string;
  condition: string;
  note: string;
  price: number;
  st_count: number;
  weight_kg: number;
}

interface TripSt {
  st_number: string;
  addr: string;
  ord: number;
  time_from: string;
  time_to: string;
  load_type: string;
  pallet_count: number;
}

interface TripOp {
  op_id: number;
  operation_code: string;
  ord: number;
  plan_start: string;
  plan_end: string;
  fact_start: string;
  fact_end: string;
  note: string;
  status: "pending" | "in_progress" | "done";
}

function todayIso() { return new Date().toISOString().slice(0, 10); }

const OP_LABELS: Record<string, string> = {
  DOCK_ASSIGN: "Постановка на ворота",
  WAIT_LOAD: "Ожидание погрузки",
  LOADING: "Погрузка",
  CLOSE_GATE: "Закрытие ворот",
  DOCUMENTS: "Документы",
  DEPART: "Уход в рейс",
  DRIVE: "Переезд",
  UNLOAD: "Выгрузка",
  LOAD_RETURNS: "Загрузка возвратов",
  DRIVE_BACK: "Возврат на склад",
  RETURN_HANDOVER: "Сдача возвратов",
  CLEAN_RETURNS: "Очистка от возвратов",
  REST: "Отдых / Перерыв",
};

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export function DriverMobilePage() {
  const [driverId, setDriverId] = useState<number | null>(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id") || params.get("driver_id");
    return id ? parseInt(id) : null;
  });
  const [inputId, setInputId] = useState("");
  const [tripDate, setTripDate] = useState(todayIso());
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTrip, setSelectedTrip] = useState<Trip | null>(null);
  const [tripSts, setTripSts] = useState<TripSt[]>([]);
  const [tripOps, setTripOps] = useState<TripOp[]>([]);
  const [opLoading, setOpLoading] = useState(false);
  const [activeView, setActiveView] = useState<"trips" | "sts" | "ops">("trips");

  const fetchTrips = useCallback(async (id: number, dt: string) => {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`/api/driver/trips?driver_id=${id}&trip_date=${dt}`);
      if (!res.ok) throw new Error(await res.text());
      setTrips(await res.json());
    } catch (e) { setError(String(e)); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    if (driverId) fetchTrips(driverId, tripDate);
  }, [driverId, tripDate, fetchTrips]);

  const selectTrip = async (trip: Trip) => {
    setSelectedTrip(trip);
    setActiveView("ops");
    try {
      const [stsRes, opsRes] = await Promise.all([
        fetch(`/api/driver/trips/${trip.task_id}/sts?driver_id=${driverId}`),
        fetch(`/api/driver/trips/${trip.task_id}/ops?driver_id=${driverId}`),
      ]);
      setTripSts(await stsRes.json());
      setTripOps(await opsRes.json());
    } catch (e) { setError(String(e)); }
  };

  const markOp = async (opId: number, action: "start" | "done") => {
    setOpLoading(true);
    try {
      await fetch(`/api/driver/ops/${opId}/${action}?driver_id=${driverId}`, { method: "POST" });
      if (selectedTrip) {
        const opsRes = await fetch(`/api/driver/trips/${selectedTrip.task_id}/ops?driver_id=${driverId}`);
        setTripOps(await opsRes.json());
      }
    } catch (e) { setError(String(e)); }
    finally { setOpLoading(false); }
  };

  // Driver ID entry screen
  if (!driverId) {
    return (
      <div className="driver-login">
        <div className="driver-login-card">
          <div className="driver-login-logo">🚛</div>
          <h1>ТМС Водитель</h1>
          <p>Введите ваш ID водителя</p>
          <input
            type="number"
            value={inputId}
            onChange={e => setInputId(e.target.value)}
            placeholder="ID водителя"
            onKeyDown={e => e.key === "Enter" && inputId && setDriverId(parseInt(inputId))}
          />
          <button onClick={() => inputId && setDriverId(parseInt(inputId))}>Войти</button>
        </div>
      </div>
    );
  }

  return (
    <div className="driver-shell">
      <header className="driver-header">
        <span className="driver-logo">🚛</span>
        <span className="driver-title">Водитель #{driverId}</span>
        <button className="driver-logout" onClick={() => { setDriverId(null); setTrips([]); }}>✕</button>
      </header>

      {error && <div className="driver-error" onClick={() => setError(null)}>⚠ {error}</div>}

      {/* Navigation tabs */}
      <div className="driver-tabs">
        <button
          className={`driver-tab${activeView === "trips" ? " driver-tab-active" : ""}`}
          onClick={() => setActiveView("trips")}
        >📋 Рейсы</button>
        {selectedTrip && (
          <>
            <button
              className={`driver-tab${activeView === "sts" ? " driver-tab-active" : ""}`}
              onClick={() => setActiveView("sts")}
            >📦 Адреса</button>
            <button
              className={`driver-tab${activeView === "ops" ? " driver-tab-active" : ""}`}
              onClick={() => setActiveView("ops")}
            >⚙ Операции</button>
          </>
        )}
      </div>

      {/* Date selector */}
      {activeView === "trips" && (
        <div className="driver-date-row">
          <button onClick={() => {
            const d = new Date(tripDate); d.setDate(d.getDate() - 1);
            setTripDate(d.toISOString().slice(0, 10));
          }}>◄</button>
          <input type="date" value={tripDate} onChange={e => setTripDate(e.target.value)} />
          <button onClick={() => {
            const d = new Date(tripDate); d.setDate(d.getDate() + 1);
            setTripDate(d.toISOString().slice(0, 10));
          }}>►</button>
          <button onClick={() => setTripDate(todayIso())} className="driver-today-btn">Сегодня</button>
        </div>
      )}

      {/* Trips list */}
      {activeView === "trips" && (
        <div className="driver-list">
          {loading && <div className="driver-loading">Загрузка…</div>}
          {!loading && trips.length === 0 && (
            <div className="driver-empty">Нет рейсов на {tripDate}</div>
          )}
          {trips.map(t => (
            <div
              key={t.task_id}
              className={`driver-trip-card${selectedTrip?.task_id === t.task_id ? " driver-trip-selected" : ""}`}
              onClick={() => selectTrip(t)}
            >
              <div className="driver-trip-header">
                <span className="driver-trip-id">Рейс #{t.task_id}</span>
                <span className={`driver-trip-cond driver-cond-${t.condition?.toLowerCase()}`}>
                  {t.condition || "Активен"}
                </span>
              </div>
              <div className="driver-trip-plate">{t.num_plat} · {t.transport_type}</div>
              <div className="driver-trip-stats">
                <span>📦 {t.st_count} адресов</span>
                <span>⚖ {t.weight_kg.toFixed(0)} кг</span>
              </div>
              {t.note && <div className="driver-trip-note">{t.note}</div>}
            </div>
          ))}
        </div>
      )}

      {/* Stop addresses */}
      {activeView === "sts" && selectedTrip && (
        <div className="driver-list">
          <div className="driver-section-title">Рейс #{selectedTrip.task_id} · Адреса</div>
          {tripSts.map((st, i) => (
            <div key={st.st_number} className="driver-st-card">
              <div className="driver-st-ord">{st.ord || i + 1}</div>
              <div className="driver-st-info">
                <div className="driver-st-addr">{st.addr}</div>
                <div className="driver-st-meta">
                  СТ {st.st_number} · {st.pallet_count} палл
                  {st.time_from && <span> · {st.time_from}–{st.time_to}</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Operations list with fact marking */}
      {activeView === "ops" && selectedTrip && (
        <div className="driver-list">
          <div className="driver-section-title">Рейс #{selectedTrip.task_id} · Операции</div>
          {tripOps.map(op => (
            <div key={op.op_id} className={`driver-op-card driver-op-${op.status}`}>
              <div className="driver-op-info">
                <div className="driver-op-name">{OP_LABELS[op.operation_code] ?? op.operation_code}</div>
                <div className="driver-op-times">
                  {op.plan_start && <span>план: {op.plan_start.slice(11,16)}–{op.plan_end?.slice(11,16)}</span>}
                  {op.fact_start && <span className="driver-op-fact"> факт: {op.fact_start.slice(11,16)}{op.fact_end && `–${op.fact_end.slice(11,16)}`}</span>}
                </div>
              </div>
              <div className="driver-op-actions">
                {op.status === "pending" && (
                  <button
                    className="driver-op-btn driver-op-start"
                    onClick={() => markOp(op.op_id, "start")}
                    disabled={opLoading}
                  >Начать</button>
                )}
                {op.status === "in_progress" && (
                  <button
                    className="driver-op-btn driver-op-done"
                    onClick={() => markOp(op.op_id, "done")}
                    disabled={opLoading}
                  >Готово ✓</button>
                )}
                {op.status === "done" && <span className="driver-op-check">✓</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
