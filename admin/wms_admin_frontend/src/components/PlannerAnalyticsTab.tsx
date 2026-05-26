/**
 * PlannerAnalyticsTab.tsx — Sprint 10: история планов, Score-график, прогноз спроса.
 */

import { useCallback, useEffect, useState } from "react";

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
function isoMinus(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type PlanHistoryItem = {
  plan_id: number;
  plan_date: string;
  solver: string;
  score: number;
  routes: number;
  total_km: number;
  fleet_utilization_pct: number;
  tw_violations: number;
  applied: boolean;
};

type DemandForecast = {
  target_date: string;
  day_of_week: number;
  forecast_sts: number;
  confidence: "high" | "medium" | "low" | "none";
  samples: number;
  sample_counts: number[];
  stddev: number;
};

type ObjWeights = {
  alpha: number;  // utilization weight
  beta: number;   // km weight
  gamma: number;  // tw_violations weight
};

const DAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];
const CONFIDENCE_COLOR: Record<string, string> = {
  high: "#16a34a", medium: "#d97706", low: "#ef4444", none: "#94a3b8",
};

// ---------------------------------------------------------------------------
// Sparkline — simple SVG bar chart
// ---------------------------------------------------------------------------

function Sparkline({ values, color = "#2563eb" }: { values: number[]; color?: string }) {
  if (!values.length) return null;
  const max = Math.max(...values, 1);
  const w = 160;
  const h = 36;
  const bw = Math.floor(w / values.length) - 2;
  return (
    <svg width={w} height={h} style={{ display: "block" }}>
      {values.map((v, i) => {
        const bh = Math.max(2, Math.round((v / max) * (h - 4)));
        const x = i * (bw + 2);
        const y = h - bh;
        return <rect key={i} x={x} y={y} width={bw} height={bh} rx={1} fill={color} opacity={0.82} />;
      })}
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Main tab
// ---------------------------------------------------------------------------

export function PlannerAnalyticsTab({ targetDate }: { targetDate: string }) {
  const [histDateFrom, setHistDateFrom] = useState(isoMinus(30));
  const [histDateTo, setHistDateTo]     = useState(todayIso());
  const [history, setHistory]           = useState<PlanHistoryItem[]>([]);
  const [histLoading, setHistLoading]   = useState(false);

  const [forecastDate, setForecastDate] = useState(targetDate);
  const [forecast, setForecast]         = useState<DemandForecast | null>(null);

  const [weights, setWeights] = useState<ObjWeights>({ alpha: 1.0, beta: 0.5, gamma: 2.0 });

  // ---------------------------------------------------------------------------
  // Load history
  // ---------------------------------------------------------------------------

  const loadHistory = useCallback(async () => {
    setHistLoading(true);
    try {
      const data = await apiFetch<PlanHistoryItem[]>(
        `/api/admin/transport/planner/history?date_from=${histDateFrom}&date_to=${histDateTo}`,
      );
      setHistory(data);
    } catch {
      setHistory([]);
    } finally { setHistLoading(false); }
  }, [histDateFrom, histDateTo]);

  // ---------------------------------------------------------------------------
  // Load forecast
  // ---------------------------------------------------------------------------

  const loadForecast = useCallback(async () => {
    try {
      const data = await apiFetch<DemandForecast>(
        `/api/admin/transport/planner/demand-forecast?target_date=${forecastDate}&lookback_weeks=8`,
      );
      setForecast(data);
    } catch { setForecast(null); }
  }, [forecastDate]);

  useEffect(() => { loadHistory(); }, [loadHistory]);
  useEffect(() => { loadForecast(); }, [loadForecast]);

  // ---------------------------------------------------------------------------
  // Derived stats
  // ---------------------------------------------------------------------------

  const appliedHistory = history.filter(h => h.applied);
  const scoreValues    = appliedHistory.map(h => Math.max(0, h.score));
  const utilValues     = appliedHistory.map(h => h.fleet_utilization_pct);

  const bestScore      = appliedHistory.length ? Math.max(...appliedHistory.map(h => h.score)) : null;
  const avgUtil30      = utilValues.length ? utilValues.reduce((a, b) => a + b, 0) / utilValues.length : null;

  // Weighted score preview
  const previewScore = (item: PlanHistoryItem) =>
    (weights.alpha * item.fleet_utilization_pct / 100 -
     weights.beta  * item.total_km / 1000 -
     weights.gamma * item.tw_violations).toFixed(2);

  return (
    <div className="analytics-shell">
      {/* ── History ────────────────────────────────────────────── */}
      <section className="analytics-section">
        <div className="analytics-section-title">История планов</div>
        <div className="analytics-filters">
          <label>
            От&nbsp;
            <input type="date" value={histDateFrom} onChange={e => setHistDateFrom(e.target.value)}
              className="analytics-date-input" />
          </label>
          <label>
            До&nbsp;
            <input type="date" value={histDateTo} onChange={e => setHistDateTo(e.target.value)}
              className="analytics-date-input" />
          </label>
          <button className="analytics-load-btn" onClick={loadHistory} disabled={histLoading}>
            {histLoading ? "..." : "⟳"}
          </button>
        </div>

        {/* Summary cards */}
        {appliedHistory.length > 0 && (
          <div className="analytics-summary-row">
            <div className="analytics-card">
              <div className="analytics-card-val">{appliedHistory.length}</div>
              <div className="analytics-card-lbl">Планов применено</div>
            </div>
            <div className="analytics-card">
              <div className="analytics-card-val">{avgUtil30 != null ? avgUtil30.toFixed(1) + "%" : "—"}</div>
              <div className="analytics-card-lbl">Ср. утилизация</div>
            </div>
            <div className="analytics-card">
              <div className="analytics-card-val">{bestScore != null ? bestScore.toFixed(1) : "—"}</div>
              <div className="analytics-card-lbl">Лучший Score</div>
            </div>
          </div>
        )}

        {/* Score sparkline */}
        {scoreValues.length > 1 && (
          <div className="analytics-spark-block">
            <div className="analytics-spark-label">Score по дням</div>
            <Sparkline values={scoreValues} color="#2563eb" />
            <div className="analytics-spark-label">Утилизация (%)</div>
            <Sparkline values={utilValues} color="#16a34a" />
          </div>
        )}

        {/* History table */}
        {history.length > 0 ? (
          <div className="analytics-table-wrap">
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Дата</th>
                  <th>Рейсов</th>
                  <th>Утил %</th>
                  <th>Пробег км</th>
                  <th>Наруш.</th>
                  <th>Score</th>
                  <th>Решатель</th>
                  <th>Применён</th>
                </tr>
              </thead>
              <tbody>
                {history.map(h => (
                  <tr key={h.plan_id} className={h.applied ? "" : "analytics-row-draft"}>
                    <td>{h.plan_date}</td>
                    <td>{h.routes}</td>
                    <td>{h.fleet_utilization_pct.toFixed(1)}</td>
                    <td>{h.total_km.toFixed(0)}</td>
                    <td>{h.tw_violations > 0 ? <span style={{ color: "#ef4444" }}>{h.tw_violations}</span> : 0}</td>
                    <td><b>{h.score.toFixed(1)}</b></td>
                    <td><span className="analytics-solver-badge">{h.solver}</span></td>
                    <td>{h.applied ? "✅" : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : !histLoading && (
          <div className="analytics-empty">Нет данных за выбранный период</div>
        )}
      </section>

      {/* ── Objective function weights ──────────────────────────── */}
      <section className="analytics-section">
        <div className="analytics-section-title">Настройки целевой функции</div>
        <div className="analytics-weights-hint">
          Score = α · Утилизация − β · Пробег/1000 − γ · Нарушений окон
        </div>
        <div className="analytics-sliders">
          <WeightSlider label="α — утилизация" value={weights.alpha} min={0} max={3} step={0.1}
            onChange={v => setWeights(w => ({ ...w, alpha: v }))} />
          <WeightSlider label="β — пробег" value={weights.beta} min={0} max={3} step={0.1}
            onChange={v => setWeights(w => ({ ...w, beta: v }))} />
          <WeightSlider label="γ — нарушения" value={weights.gamma} min={0} max={10} step={0.5}
            onChange={v => setWeights(w => ({ ...w, gamma: v }))} />
        </div>
        {appliedHistory.length > 0 && (
          <div className="analytics-weights-preview">
            <div className="analytics-section-title" style={{ fontSize: 11, marginBottom: 4 }}>
              Пересчёт Score с новыми весами
            </div>
            {appliedHistory.slice(-5).map(h => (
              <div key={h.plan_id} className="analytics-preview-row">
                <span>{h.plan_date}</span>
                <span>{previewScore(h)}</span>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* ── Demand forecast ─────────────────────────────────────── */}
      <section className="analytics-section">
        <div className="analytics-section-title">Прогноз спроса</div>
        <div className="analytics-filters">
          <label>
            Дата&nbsp;
            <input type="date" value={forecastDate} onChange={e => setForecastDate(e.target.value)}
              className="analytics-date-input" />
          </label>
          <button className="analytics-load-btn" onClick={loadForecast}>⟳</button>
        </div>

        {forecast && (
          <div className="analytics-forecast-card">
            <div className="analytics-forecast-val">{forecast.forecast_sts}</div>
            <div className="analytics-forecast-lbl">
              СТ ожидается ({DAY_NAMES[forecast.day_of_week]})
            </div>
            <div className="analytics-forecast-conf"
              style={{ color: CONFIDENCE_COLOR[forecast.confidence] }}>
              Уверенность: {forecast.confidence === "high" ? "высокая" :
                forecast.confidence === "medium" ? "средняя" :
                forecast.confidence === "low" ? "низкая" : "нет данных"}
            </div>
            {forecast.samples > 0 && (
              <div className="analytics-forecast-detail">
                {forecast.samples} наблюдений · σ = {forecast.stddev}
              </div>
            )}
            {forecast.sample_counts.length > 0 && (
              <div style={{ marginTop: 8 }}>
                <Sparkline values={forecast.sample_counts} color="#2563eb" />
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

// ---------------------------------------------------------------------------
// WeightSlider
// ---------------------------------------------------------------------------

function WeightSlider({ label, value, min, max, step, onChange }: {
  label: string; value: number; min: number; max: number; step: number;
  onChange: (v: number) => void;
}) {
  return (
    <label className="analytics-slider-row">
      <span>{label}</span>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(Number(e.target.value))} />
      <b>{value.toFixed(1)}</b>
    </label>
  );
}
