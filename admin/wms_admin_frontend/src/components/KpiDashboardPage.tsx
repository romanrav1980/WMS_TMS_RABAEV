/**
 * KpiDashboardPage — KPI дашборд для руководства.
 * Sprint 108: операционные метрики (флот, регионы)
 * Sprint 109: финансовые метрики (биллинг по ТК)
 */

import { useEffect, useState } from "react";
import { apiFetch } from "../api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface FleetDay { day: string; trips_total: number; trips_closed: number; pallets: number; weight_kg: number; }
interface SummaryKpi { trips_total: number; trips_closed: number; vehicles_used: number; pallets: number; weight_kg: number; avg_pallets_per_trip: number; }
interface RegionRow { region: string; trips: number; pallets: number; weight_kg: number; }
interface BillingSummary { orders_total: number; orders_paid: number; orders_closed: number; total_amount: number; paid_amount: number; unpaid_amount: number; }
interface BillingCompany { company: string; orders: number; amount: number; paid_amount: number; }

function todayIso() { return new Date().toISOString().slice(0, 10); }
function monthStartIso() { const d = new Date(); d.setDate(1); return d.toISOString().slice(0, 10); }
function fmt(n: number) { return n.toLocaleString("ru-RU"); }
function fmtMoney(n: number) { return `${fmt(Math.round(n))} ₽`; }

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

export function KpiDashboardPage({ onBack }: { onBack: () => void }) {
  const [activeTab, setActiveTab] = useState<"ops" | "billing">("ops");
  const [dateFrom, setDateFrom] = useState(monthStartIso());
  const [dateTo, setDateTo] = useState(todayIso());

  return (
    <div className="kpi-shell">
      <header className="kpi-topbar">
        <button className="kpi-back" onClick={onBack}>◄</button>
        <div className="kpi-title">
          <h1>KPI Дашборд</h1>
          <span className="kpi-subtitle">Аналитика транспортного модуля</span>
        </div>
        <div className="kpi-date-range">
          <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
          <span>—</span>
          <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} />
        </div>
      </header>

      <div className="kpi-tabs">
        <button className={`kpi-tab-btn${activeTab === "ops" ? " kpi-tab-active" : ""}`} onClick={() => setActiveTab("ops")}>
          📊 Операционные метрики
        </button>
        <button className={`kpi-tab-btn${activeTab === "billing" ? " kpi-tab-active" : ""}`} onClick={() => setActiveTab("billing")}>
          💰 Финансы (Биллинг)
        </button>
      </div>

      <div className="kpi-content">
        {activeTab === "ops"
          ? <OpsTab dateFrom={dateFrom} dateTo={dateTo} />
          : <BillingTab dateFrom={dateFrom} dateTo={dateTo} />}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Ops Tab — Sprint 108
// ---------------------------------------------------------------------------

function OpsTab({ dateFrom, dateTo }: { dateFrom: string; dateTo: string }) {
  const [summary, setSummary] = useState<SummaryKpi | null>(null);
  const [fleetDays, setFleetDays] = useState<FleetDay[]>([]);
  const [regions, setRegions] = useState<RegionRow[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!dateFrom || !dateTo) return;
    setLoading(true);
    Promise.all([
      apiFetch<SummaryKpi>(`/api/admin/transport/kpi/summary?date_from=${dateFrom}&date_to=${dateTo}`),
      apiFetch<FleetDay[]>(`/api/admin/transport/kpi/fleet?date_from=${dateFrom}&date_to=${dateTo}`),
      apiFetch<RegionRow[]>(`/api/admin/transport/kpi/regions?date_from=${dateFrom}&date_to=${dateTo}`),
    ]).then(([s, f, r]) => { setSummary(s); setFleetDays(f); setRegions(r); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [dateFrom, dateTo]);

  const maxPallets = Math.max(...fleetDays.map(d => d.pallets), 1);

  return (
    <div className="kpi-section">
      {loading && <div className="kpi-loading">Загрузка…</div>}

      {/* Summary cards */}
      {summary && (
        <div className="kpi-cards">
          <div className="kpi-card">
            <div className="kpi-card-value">{fmt(summary.trips_total)}</div>
            <div className="kpi-card-label">Рейсов создано</div>
          </div>
          <div className="kpi-card kpi-card-green">
            <div className="kpi-card-value">{fmt(summary.trips_closed)}</div>
            <div className="kpi-card-label">Отгружено</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-card-value">{fmt(summary.pallets)}</div>
            <div className="kpi-card-label">Паллет доставлено</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-card-value">{summary.avg_pallets_per_trip}</div>
            <div className="kpi-card-label">Ср. паллет на рейс</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-card-value">{fmt(summary.vehicles_used)}</div>
            <div className="kpi-card-label">Машин задействовано</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-card-value">{fmt(Math.round(summary.weight_kg / 1000))} т</div>
            <div className="kpi-card-label">Суммарный вес</div>
          </div>
        </div>
      )}

      <div className="kpi-row">
        {/* Sparkline chart */}
        <div className="kpi-chart-card">
          <div className="kpi-chart-title">Паллет по дням</div>
          <div className="kpi-bar-chart">
            {fleetDays.map(d => (
              <div key={d.day} className="kpi-bar-col" title={`${d.day}: ${d.pallets} палл, ${d.trips_total} рейсов`}>
                <div className="kpi-bar" style={{ height: `${Math.round((d.pallets / maxPallets) * 100)}%` }} />
                <div className="kpi-bar-label">{d.day.slice(8)}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Regions table */}
        <div className="kpi-chart-card">
          <div className="kpi-chart-title">Топ регионов по паллетам</div>
          <table className="kpi-table">
            <thead><tr><th>Регион</th><th>Рейсов</th><th>Паллет</th><th>Вес, т</th></tr></thead>
            <tbody>
              {regions.map(r => (
                <tr key={r.region}>
                  <td>{r.region}</td>
                  <td className="kpi-num">{r.trips}</td>
                  <td className="kpi-num">{fmt(r.pallets)}</td>
                  <td className="kpi-num">{Math.round(r.weight_kg / 1000)}</td>
                </tr>
              ))}
              {regions.length === 0 && !loading && (
                <tr><td colSpan={4} className="kpi-empty">Нет данных</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Billing Tab — Sprint 109
// ---------------------------------------------------------------------------

function BillingTab({ dateFrom, dateTo }: { dateFrom: string; dateTo: string }) {
  const [summary, setSummary] = useState<BillingSummary | null>(null);
  const [byCompany, setByCompany] = useState<BillingCompany[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!dateFrom || !dateTo) return;
    setLoading(true);
    Promise.all([
      apiFetch<BillingSummary>(`/api/admin/transport/kpi/billing?date_from=${dateFrom}&date_to=${dateTo}`),
      apiFetch<BillingCompany[]>(`/api/admin/transport/kpi/billing/by-company?date_from=${dateFrom}&date_to=${dateTo}`),
    ]).then(([s, c]) => { setSummary(s); setByCompany(c); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [dateFrom, dateTo]);

  const maxAmount = Math.max(...byCompany.map(c => c.amount), 1);

  return (
    <div className="kpi-section">
      {loading && <div className="kpi-loading">Загрузка…</div>}

      {summary && (
        <div className="kpi-cards">
          <div className="kpi-card">
            <div className="kpi-card-value">{fmt(summary.orders_total)}</div>
            <div className="kpi-card-label">Счетов выставлено</div>
          </div>
          <div className="kpi-card kpi-card-green">
            <div className="kpi-card-value">{fmt(summary.orders_paid)}</div>
            <div className="kpi-card-label">Счетов оплачено</div>
          </div>
          <div className="kpi-card kpi-card-blue">
            <div className="kpi-card-value">{fmtMoney(summary.total_amount)}</div>
            <div className="kpi-card-label">Итого к оплате</div>
          </div>
          <div className="kpi-card kpi-card-green">
            <div className="kpi-card-value">{fmtMoney(summary.paid_amount)}</div>
            <div className="kpi-card-label">Оплачено</div>
          </div>
          <div className="kpi-card kpi-card-amber">
            <div className="kpi-card-value">{fmtMoney(summary.unpaid_amount)}</div>
            <div className="kpi-card-label">Не оплачено</div>
          </div>
        </div>
      )}

      <div className="kpi-row">
        {/* Companies bar chart */}
        <div className="kpi-chart-card kpi-chart-wide">
          <div className="kpi-chart-title">Расходы по транспортным компаниям</div>
          {byCompany.map(c => (
            <div key={c.company} className="kpi-hbar-row">
              <div className="kpi-hbar-label">{c.company}</div>
              <div className="kpi-hbar-track">
                <div className="kpi-hbar-paid" style={{ width: `${Math.round((c.paid_amount / maxAmount) * 100)}%` }} />
                <div className="kpi-hbar-total" style={{ width: `${Math.round((c.amount / maxAmount) * 100)}%` }} />
              </div>
              <div className="kpi-hbar-value">{fmtMoney(c.amount)}</div>
            </div>
          ))}
          {byCompany.length === 0 && !loading && <div className="kpi-empty">Нет данных</div>}
          <div className="kpi-legend">
            <span className="kpi-leg-paid">Оплачено</span>
            <span className="kpi-leg-total">Итого</span>
          </div>
        </div>
      </div>
    </div>
  );
}
