import { useCallback, useEffect, useRef, useState } from "react";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const AXIS_START = 360;   // 06:00 in minutes from midnight
const AXIS_END   = 1320;  // 22:00
const PX_MIN     = 1.5;   // pixels per minute
const ROW_H      = 52;    // vehicle row height px
const HEADER_H   = 44;    // time axis header height px
const LEFT_W     = 210;   // vehicle info column width px
const CHART_W    = (AXIS_END - AXIS_START) * PX_MIN; // 1440px

// ---------------------------------------------------------------------------
// Operation colour groups (§10.6.3)
// ---------------------------------------------------------------------------
const OP_COLOR: Record<string, string> = {
  DOCK_ASSIGN: "#4A90D9", WAIT_LOAD: "#4A90D9", LOADING: "#4A90D9",
  CLOSE_GATE: "#4A90D9",  DOCUMENTS: "#4A90D9", DEPART: "#4A90D9",
  DRIVE: "#52C41A",       DRIVE_BACK: "#52C41A",
  UNLOAD: "#FAAD14",
  LOAD_RETURNS: "#9254DE", RETURN_HANDOVER: "#9254DE", CLEAN_RETURNS: "#9254DE",
  REST: "#BFBFBF",
  DRIVER_CHANGE: "#FF4D4F",
};

const OP_LABEL: Record<string, string> = {
  DOCK_ASSIGN: "Ворота", WAIT_LOAD: "Ожидание", LOADING: "Погрузка",
  CLOSE_GATE: "Закрытие", DOCUMENTS: "Документы", DEPART: "Выезд",
  DRIVE: "Переезд", DRIVE_BACK: "Возврат",
  UNLOAD: "Разгрузка",
  LOAD_RETURNS: "Возвраты", RETURN_HANDOVER: "Сдача", CLEAN_RETURNS: "Уборка",
  REST: "Перерыв", DRIVER_CHANGE: "Смена",
};

const LEGEND_GROUPS = [
  { label: "Склад",      color: "#4A90D9" },
  { label: "Переезд",    color: "#52C41A" },
  { label: "Разгрузка",  color: "#FAAD14" },
  { label: "Возвраты",   color: "#9254DE" },
  { label: "Перерыв",    color: "#BFBFBF" },
  { label: "Смена",      color: "#FF4D4F" },
];

// ---------------------------------------------------------------------------
// Status from current active operation
// ---------------------------------------------------------------------------
const OP_STATUS: Record<string, string> = {
  DOCK_ASSIGN: "Погрузка", WAIT_LOAD: "Погрузка", LOADING: "Погрузка",
  CLOSE_GATE: "Погрузка",  DOCUMENTS: "Погрузка",
  DEPART: "В рейсе",       DRIVE: "В рейсе",      UNLOAD: "В рейсе",
  DRIVE_BACK: "Возвраты",  LOAD_RETURNS: "Возвраты", RETURN_HANDOVER: "Возвраты",
  CLEAN_RETURNS: "Возвраты",
  REST: "Отдых",
};

const STATUS_COLOR: Record<string, string> = {
  "Погрузка": "#d97706", "В рейсе": "#16a34a",
  "Возвраты": "#7c3aed", "Отдых": "#6b7280", "На базе": "#2563eb",
};

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
type Operation = {
  op_id: number;
  tt_id: number;
  operation_code: string;
  ord: number;
  duration_min: number;
  plan_start: string | null;
  plan_end: string | null;
  fact_start: string | null;
  fact_end: string | null;
  delta_min: number | null;
  note: string | null;
};

type VehicleGantt = {
  vehicle_id: number;
  vehicle_num: string;
  vehicle_type: string;
  operations: Operation[];
};

type Tooltip = {
  x: number; y: number;
  op: Operation;
};

type TaskCard = {
  tt_id: number;
  vehicle_num: string;
  operations: Operation[];
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function fmtDate(iso: string) {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" });
}

function addDays(iso: string, n: number) {
  const d = new Date(iso + "T00:00:00");
  d.setDate(d.getDate() + n);
  return d.toISOString().slice(0, 10);
}

function parseMinFromStr(s: string | null): number | null {
  if (!s) return null;
  const parts = s.split(" ");
  const timePart = parts.length > 1 ? parts[1] : parts[0];
  const [h, m] = timePart.split(":").map(Number);
  if (isNaN(h) || isNaN(m)) return null;
  return h * 60 + m;
}

function fmtHHMM(min: number) {
  const h = Math.floor(min / 60) % 24;
  const m = min % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

function minToPx(min: number) {
  return (min - AXIS_START) * PX_MIN;
}

function getVehicleStatus(ops: Operation[], nowMin: number): string {
  for (const op of ops) {
    const s = parseMinFromStr(op.plan_start);
    const e = parseMinFromStr(op.plan_end);
    if (s !== null && e !== null && nowMin >= s && nowMin <= e) {
      return OP_STATUS[op.operation_code] || "В рейсе";
    }
  }
  return "На базе";
}

function vehicleInitials(num: string): string {
  return num.slice(0, 2).toUpperCase();
}

// ---------------------------------------------------------------------------
// SVG sub-components
// ---------------------------------------------------------------------------

function TimeAxisRow() {
  const ticks: React.ReactNode[] = [];
  for (let min = AXIS_START; min <= AXIS_END; min += 30) {
    const x = minToPx(min);
    const isHour = min % 60 === 0;
    ticks.push(
      <g key={min}>
        <line x1={x} y1={isHour ? HEADER_H - 22 : HEADER_H - 10} x2={x} y2={HEADER_H} stroke="#cbd5e1" strokeWidth={isHour ? 1.5 : 1} />
        {isHour && (
          <text x={x} y={HEADER_H - 26} textAnchor="middle" fontSize={11} fill="#64748b" fontFamily="inherit">
            {fmtHHMM(min)}
          </text>
        )}
      </g>
    );
  }
  return <>{ticks}</>;
}

function GridLines({ rowCount }: { rowCount: number }) {
  const lines: React.ReactNode[] = [];
  for (let min = AXIS_START; min <= AXIS_END; min += 60) {
    const x = minToPx(min);
    lines.push(
      <line key={min} x1={x} y1={0} x2={x} y2={HEADER_H + rowCount * ROW_H}
        stroke="#e2e8f0" strokeWidth={1} strokeDasharray={min % 120 === 0 ? "none" : "2,3"} />
    );
  }
  for (let i = 0; i <= rowCount; i++) {
    const y = HEADER_H + i * ROW_H;
    lines.push(
      <line key={`h${i}`} x1={0} y1={y} x2={CHART_W} y2={y} stroke="#f1f5f9" strokeWidth={1} />
    );
  }
  return <>{lines}</>;
}

function OpBlock({
  op, rowY, onHover, onLeave, onClick,
}: {
  op: Operation; rowY: number;
  onHover: (e: React.MouseEvent<SVGRectElement>, op: Operation) => void;
  onLeave: () => void;
  onClick: (op: Operation) => void;
}) {
  const startMin = parseMinFromStr(op.plan_start);
  const endMin   = parseMinFromStr(op.plan_end);
  if (startMin === null || endMin === null) return null;

  const clampedStart = Math.max(startMin, AXIS_START);
  const clampedEnd   = Math.min(endMin,   AXIS_END);
  if (clampedEnd <= clampedStart) return null;

  const x = minToPx(clampedStart);
  const w = Math.max((clampedEnd - clampedStart) * PX_MIN, 2);
  const y = rowY + 6;
  const h = ROW_H - 12;
  const color = OP_COLOR[op.operation_code] || "#94a3b8";
  const label = OP_LABEL[op.operation_code] || op.operation_code;
  const hasFact = op.fact_start !== null;

  return (
    <g>
      <rect
        x={x} y={y} width={w} height={h} rx={3}
        fill={color} opacity={hasFact ? 1 : 0.75}
        stroke={hasFact ? "rgba(0,0,0,.25)" : "none"} strokeWidth={1}
        style={{ cursor: "pointer" }}
        onMouseEnter={(e) => onHover(e, op)}
        onMouseLeave={onLeave}
        onClick={() => onClick(op)}
      />
      {w > 32 && (
        <text
          x={x + w / 2} y={y + h / 2 + 4}
          textAnchor="middle" fontSize={10} fill="#fff"
          fontWeight="600" fontFamily="inherit"
          style={{ pointerEvents: "none", userSelect: "none" }}
        >
          {label}
        </text>
      )}
    </g>
  );
}

// ---------------------------------------------------------------------------
// Main page component
// ---------------------------------------------------------------------------
export function TransportGanttPage({ onBack }: { onBack: () => void }) {
  const [ganttDate, setGanttDate]         = useState(todayIso());
  const [vehicles, setVehicles]           = useState<VehicleGantt[]>([]);
  const [loading, setLoading]             = useState(false);
  const [error, setError]                 = useState<string | null>(null);
  const [nowMin, setNowMin]               = useState(() => {
    const n = new Date(); return n.getHours() * 60 + n.getMinutes();
  });
  const [tooltip, setTooltip]             = useState<Tooltip | null>(null);
  const [taskCard, setTaskCard]           = useState<TaskCard | null>(null);
  const [vehicleFilter, setVehicleFilter] = useState("");
  const scrollRef                         = useRef<HTMLDivElement>(null);

  // Tick current-time line every minute
  useEffect(() => {
    const id = setInterval(() => {
      const n = new Date(); setNowMin(n.getHours() * 60 + n.getMinutes());
    }, 60_000);
    return () => clearInterval(id);
  }, []);

  // Fetch gantt data
  const fetchGantt = useCallback(async (date: string) => {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(
        `/api/admin/transport/vehicles/gantt?gantt_date=${date}`,
        { headers: { Authorization: "Basic " + btoa("admin:admin123") } }
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setVehicles(await r.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchGantt(ganttDate); }, [ganttDate, fetchGantt]);

  // Filtered vehicle list
  const filtered = vehicles.filter(
    (v) => !vehicleFilter || v.vehicle_num.toLowerCase().includes(vehicleFilter.toLowerCase())
  );

  // Summary counts
  const summary = filtered.reduce(
    (acc, v) => {
      const st = getVehicleStatus(v.operations, nowMin);
      acc.total++;
      acc[st] = (acc[st] || 0) + 1;
      return acc;
    },
    { total: 0 } as Record<string, number>
  );

  // Tooltip handlers
  const handleOpHover = useCallback((e: React.MouseEvent<SVGRectElement>, op: Operation) => {
    const rect = (e.currentTarget as SVGRectElement).getBoundingClientRect();
    setTooltip({ x: rect.left + rect.width / 2, y: rect.top - 8, op });
  }, []);
  const handleOpLeave = useCallback(() => setTooltip(null), []);

  const handleOpClick = useCallback((op: Operation) => {
    // Find which vehicle this op belongs to
    const v = filtered.find(vv => vv.operations.some(o => o.op_id === op.op_id));
    if (!v) return;
    setTaskCard({ tt_id: op.tt_id, vehicle_num: v.vehicle_num, operations: v.operations });
  }, [filtered]);

  // SVG height
  const svgH = HEADER_H + filtered.length * ROW_H + 2;
  const nowX = minToPx(nowMin);
  const showNowLine = nowMin >= AXIS_START && nowMin <= AXIS_END;

  // Upcoming trips (next 3 operations that haven't started yet)
  const upcoming: Array<{ vehicle_num: string; op: Operation }> = [];
  for (const v of filtered) {
    for (const op of v.operations) {
      const s = parseMinFromStr(op.plan_start);
      if (s !== null && s > nowMin && upcoming.length < 5) {
        upcoming.push({ vehicle_num: v.vehicle_num, op });
      }
    }
  }
  upcoming.sort((a, b) => {
    const sa = parseMinFromStr(a.op.plan_start) ?? 0;
    const sb = parseMinFromStr(b.op.plan_start) ?? 0;
    return sa - sb;
  });

  // Actual deviations (operations with delta)
  const deviations: Array<{ vehicle_num: string; op: Operation }> = [];
  for (const v of filtered) {
    for (const op of v.operations) {
      if (op.delta_min !== null && Math.abs(op.delta_min) > 0) {
        deviations.push({ vehicle_num: v.vehicle_num, op });
      }
    }
  }
  deviations.sort((a, b) => Math.abs(b.op.delta_min ?? 0) - Math.abs(a.op.delta_min ?? 0));

  return (
    <div className="gantt-page">
      {/* ---- Topbar ---- */}
      <header className="gantt-topbar">
        <button className="gantt-back-btn" onClick={onBack}>← Назад</button>
        <h2 className="gantt-title">Диаграмма Ганта</h2>

        {/* Date navigation */}
        <div className="gantt-date-nav">
          <button className="gantt-nav-btn" onClick={() => setGanttDate(d => addDays(d, -1))}>◄</button>
          <input
            type="date" className="gantt-date-input" value={ganttDate}
            onChange={e => setGanttDate(e.target.value)}
          />
          <button className="gantt-nav-btn" onClick={() => setGanttDate(d => addDays(d, 1))}>►</button>
          <button className="gantt-today-btn" onClick={() => setGanttDate(todayIso())}>Сегодня</button>
        </div>

        <span className="gantt-date-label">{fmtDate(ganttDate)}</span>

        {/* Vehicle filter */}
        <input
          className="gantt-veh-filter"
          placeholder="Фильтр по машине…"
          value={vehicleFilter}
          onChange={e => setVehicleFilter(e.target.value)}
        />

        <button
          className="gantt-refresh-btn"
          onClick={() => fetchGantt(ganttDate)}
          disabled={loading}
        >
          {loading ? "…" : "⟳"}
        </button>
      </header>

      {error && <div className="gantt-error">{error}</div>}

      {/* ---- Main body ---- */}
      <div className="gantt-body">
        {/* Left: vehicle info column */}
        <div className="gantt-left-col">
          {/* Header placeholder */}
          <div className="gantt-left-header" style={{ height: HEADER_H }}>Машина / Водитель</div>

          {filtered.length === 0 && !loading && (
            <div className="gantt-empty">Нет рейсов на {ganttDate}</div>
          )}
          {loading && <div className="gantt-loading">Загрузка…</div>}

          {filtered.map((v) => {
            const status = getVehicleStatus(v.operations, nowMin);
            const statusColor = STATUS_COLOR[status] || "#64748b";
            return (
              <div key={v.vehicle_id || v.vehicle_num} className="gantt-veh-row" style={{ height: ROW_H }}>
                <div className="gantt-veh-avatar">{vehicleInitials(v.vehicle_num)}</div>
                <div className="gantt-veh-info">
                  <span className="gantt-veh-num">{v.vehicle_num}</span>
                  <span className="gantt-veh-type">{v.vehicle_type || "—"}</span>
                </div>
                <span className="gantt-status-badge" style={{ background: statusColor }}>{status}</span>
              </div>
            );
          })}
        </div>

        {/* Right: scrollable SVG chart */}
        <div className="gantt-chart-wrap" ref={scrollRef}>
          <svg
            width={CHART_W}
            height={svgH}
            style={{ display: "block", fontFamily: "inherit" }}
          >
            {/* Background grid */}
            <GridLines rowCount={filtered.length} />

            {/* Time axis */}
            <rect x={0} y={0} width={CHART_W} height={HEADER_H} fill="#f8fafc" />
            <TimeAxisRow />

            {/* Operation blocks */}
            {filtered.map((v, vi) => {
              const rowY = HEADER_H + vi * ROW_H;
              return (
                <g key={v.vehicle_id || v.vehicle_num}>
                  {v.operations.map((op) => (
                    <OpBlock
                      key={op.op_id}
                      op={op}
                      rowY={rowY}
                      onHover={handleOpHover}
                      onLeave={handleOpLeave}
                      onClick={handleOpClick}
                    />
                  ))}
                </g>
              );
            })}

            {/* Current time line */}
            {showNowLine && (
              <g>
                <line
                  x1={nowX} y1={0} x2={nowX} y2={svgH}
                  stroke="#2563eb" strokeWidth={2} strokeDasharray="4,3"
                />
                <polygon
                  points={`${nowX - 5},0 ${nowX + 5},0 ${nowX},8`}
                  fill="#2563eb"
                />
              </g>
            )}
          </svg>
        </div>
      </div>

      {/* ---- Legend ---- */}
      <div className="gantt-legend">
        {LEGEND_GROUPS.map((g) => (
          <span key={g.label} className="gantt-legend-item">
            <span className="gantt-legend-swatch" style={{ background: g.color }} />
            {g.label}
          </span>
        ))}
      </div>

      {/* ---- Summary row ---- */}
      <div className="gantt-summary">
        <div className="gantt-sum-item">
          <span className="gantt-sum-count">{summary.total}</span>
          <span className="gantt-sum-label">Всего машин</span>
        </div>
        {(["В рейсе", "Погрузка", "Возвраты", "Отдых", "На базе"] as const).map((st) => {
          const cnt = summary[st] || 0;
          const pct = summary.total ? Math.round((cnt / summary.total) * 100) : 0;
          return (
            <div key={st} className="gantt-sum-item">
              <span className="gantt-sum-count" style={{ color: STATUS_COLOR[st] }}>{cnt}</span>
              <span className="gantt-sum-label">{st}</span>
              <span className="gantt-sum-pct">{pct}%</span>
            </div>
          );
        })}
      </div>

      {/* ---- Bottom panels ---- */}
      <div className="gantt-panels">
        {/* Upcoming */}
        <div className="gantt-panel">
          <div className="gantt-panel-title">Ближайшие операции</div>
          {upcoming.length === 0
            ? <div className="gantt-panel-empty">Нет предстоящих операций</div>
            : upcoming.slice(0, 5).map((u, i) => (
              <div key={i} className="gantt-panel-row">
                <span className="gantt-panel-veh">{u.vehicle_num}</span>
                <span className="gantt-panel-time">{u.op.plan_start?.slice(-5)}</span>
                <span
                  className="gantt-panel-op"
                  style={{ color: OP_COLOR[u.op.operation_code] || "#64748b" }}
                >
                  {OP_LABEL[u.op.operation_code] || u.op.operation_code}
                </span>
              </div>
            ))}
        </div>

        {/* Deviations */}
        <div className="gantt-panel">
          <div className="gantt-panel-title">Фактические отклонения</div>
          {deviations.length === 0
            ? <div className="gantt-panel-empty">Нет зафиксированных отклонений</div>
            : deviations.slice(0, 5).map((d, i) => {
              const delta = d.op.delta_min ?? 0;
              const color = Math.abs(delta) <= 15 ? "#16a34a" : Math.abs(delta) <= 60 ? "#d97706" : "#dc2626";
              return (
                <div key={i} className="gantt-panel-row">
                  <span className="gantt-panel-veh">{d.vehicle_num}</span>
                  <span className="gantt-panel-op">{OP_LABEL[d.op.operation_code] || d.op.operation_code}</span>
                  <span className="gantt-panel-delta" style={{ color }}>
                    {delta > 0 ? "+" : ""}{delta} мин
                  </span>
                </div>
              );
            })}
        </div>
      </div>

      {/* ---- Tooltip ---- */}
      {/* ---- Task card modal ---- */}
      {taskCard && (
        <div className="gantt-card-overlay" onClick={() => setTaskCard(null)}>
          <div className="gantt-card" onClick={e => e.stopPropagation()}>
            <div className="gantt-card-title">Рейс #{taskCard.tt_id} · {taskCard.vehicle_num}</div>
            <div className="gantt-card-ops">
              <div className="gantt-card-ops-title">Цепочка операций</div>
              {taskCard.operations.map(op => (
                <div key={op.op_id} className="gantt-card-op">
                  <span className="gantt-card-op-dot"
                    style={{ background: OP_COLOR[op.operation_code] || "#94a3b8" }} />
                  <span style={{ minWidth: 90, fontSize: 11 }}>{OP_LABEL[op.operation_code] || op.operation_code}</span>
                  <span style={{ color: "#64748b", fontSize: 11 }}>
                    {op.plan_start?.slice(-5)} – {op.plan_end?.slice(-5)}
                  </span>
                  {op.fact_start && (
                    <span style={{ color: "#16a34a", fontSize: 10, marginLeft: 4 }}>
                      ✓ {op.fact_start.slice(-5)}
                    </span>
                  )}
                  {op.delta_min !== null && (
                    <span style={{
                      fontSize: 10, marginLeft: 4,
                      color: Math.abs(op.delta_min) <= 15 ? "#16a34a" : Math.abs(op.delta_min) <= 60 ? "#d97706" : "#dc2626"
                    }}>
                      {op.delta_min > 0 ? "+" : ""}{op.delta_min}м
                    </span>
                  )}
                </div>
              ))}
            </div>
            <div className="gantt-card-actions">
              <button className="gantt-card-close-btn" onClick={() => setTaskCard(null)}>Закрыть</button>
            </div>
          </div>
        </div>
      )}

      {tooltip && (
        <div
          className="gantt-tooltip"
          style={{ left: tooltip.x, top: tooltip.y }}
        >
          <div className="gantt-tt-title">{OP_LABEL[tooltip.op.operation_code] || tooltip.op.operation_code}</div>
          <div className="gantt-tt-row">
            <span>План:</span>
            <span>{tooltip.op.plan_start?.slice(-5)} – {tooltip.op.plan_end?.slice(-5)}</span>
          </div>
          {tooltip.op.fact_start && (
            <div className="gantt-tt-row">
              <span>Факт:</span>
              <span>{tooltip.op.fact_start?.slice(-5)} – {tooltip.op.fact_end?.slice(-5) ?? "…"}</span>
            </div>
          )}
          {tooltip.op.delta_min !== null && (
            <div className="gantt-tt-row gantt-tt-delta"
              style={{ color: Math.abs(tooltip.op.delta_min) <= 15 ? "#16a34a" : Math.abs(tooltip.op.delta_min) <= 60 ? "#d97706" : "#dc2626" }}>
              <span>Δ:</span>
              <span>{tooltip.op.delta_min > 0 ? "+" : ""}{tooltip.op.delta_min} мин</span>
            </div>
          )}
          <div className="gantt-tt-row">
            <span>Длит.:</span>
            <span>{Math.round(tooltip.op.duration_min)} мин</span>
          </div>
        </div>
      )}
    </div>
  );
}
