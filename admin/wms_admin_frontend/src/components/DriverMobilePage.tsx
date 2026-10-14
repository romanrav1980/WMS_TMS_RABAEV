/**
 * DriverMobilePage — мобильный интерфейс водителя (PWA).
 * Sprint 103: страница «Мои рейсы» — список рейсов на день
 * Sprint 104: отметка факта операций (Начать / Готово)
 */

import { DriverLogin, useDriverWorkspace } from "../features/transport";
import { TarePanel } from '../features/inventory';
import { StoreReceiptPanel, ReturnCustodyPanel } from "../features/delivery";
import { DriverDateSelector } from "./DriverDateSelector";

// Sprint 105 — register service worker for offline support
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/driver-sw.js").catch(() => {});
  });
}

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
  const {driverId,tripDate,setTripDate,trips,loading,error,setError,selectedTrip,tripSts,tripOps,
    opLoading,activeView,setActiveView,login,logout,selectTrip,markOp,pending,retry}=useDriverWorkspace();
  if (!driverId) return <DriverLogin onLogin={login} busy={loading} error={error}/>;

  return (
    <div className="driver-shell">
      <header className="driver-header">
        <span className="driver-logo">🚛</span>
        <span className="driver-title">Водитель #{driverId}</span>
        <button className="driver-logout" onClick={logout} disabled={opLoading} aria-label="Выйти">✕</button>
      </header>

      {error && <div className="driver-error" onClick={() => setError(null)}>⚠ {error}</div>}

      {pending && <div className="driver-pending" role="status">
        <strong>Ожидает подтверждения: рейс #{pending.trip}</strong>
        <p>Отметка сохранена на этом устройстве. Повтор не изменит первоначальное время.</p>
        <button disabled={opLoading} onClick={()=>void retry()}>Повторить сохранённую отметку</button>
      </div>}
      {loading && activeView !== "trips" && <div className="driver-loading" role="status">Загрузка рейса…</div>}
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

      {selectedTrip && !loading && activeView === "sts" && <StoreReceiptPanel key={selectedTrip.task_id} tripId={selectedTrip.task_id} addresses={[...new Set(tripSts.map(st=>st.addr))]} />}
      {selectedTrip && !loading && activeView === "sts" && <ReturnCustodyPanel key={"return:"+selectedTrip.task_id} tripId={selectedTrip.task_id} addresses={[...new Set(tripSts.map(st=>st.addr))]} />}
      {selectedTrip && !loading && activeView === "sts" && <TarePanel key={"tare:"+selectedTrip.task_id} tripId={selectedTrip.task_id} addresses={[...new Set(tripSts.map(st=>st.addr))]} />}

      {/* Date selector */}
      {activeView === "trips" && (
        <DriverDateSelector date={tripDate} onChange={setTripDate} />
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
                <span>⚖ {t.loaded_weight_kg!==null? t.loaded_weight_kg+" кг · погружено":Number(t.weight_kg || 0)>0?t.weight_kg+" кг · план":"Масса не указана"}</span>
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
            <div key={`${st.st_number}:${st.addr}:${i}`} className="driver-st-card">
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
          {!loading && tripOps.length === 0 && <div className="driver-empty">Операции рейса ещё не запланированы диспетчером.</div>}
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
                    disabled={opLoading || !!pending}
                  >Начать</button>
                )}
                {op.status === "in_progress" && (
                  <button
                    className="driver-op-btn driver-op-done"
                    onClick={() => markOp(op.op_id, "done")}
                    disabled={opLoading || !!pending}
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
