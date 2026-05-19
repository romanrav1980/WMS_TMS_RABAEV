import { useMemo, useState } from "react";
import type { Collision, DetailSelection, MinuteMetrics, ReplenishmentTask, ResourceState, SimulationReport, WarehouseEvent } from "../types";
import { collisionTitle } from "../replay/reducer";

export function KpiRow({ unitsDone, totalUnits, activePickers, collisions, overdue, avgSpeed }: {
  unitsDone: number;
  totalUnits: number;
  activePickers: number;
  collisions: Collision[];
  overdue: number;
  avgSpeed: number;
}) {
  const productivity = totalUnits ? Math.min(160, Math.round((unitsDone / Math.max(1, totalUnits * .25)) * 100)) : 100;
  return (
    <section className="twin-kpis">
      <article><span>Производительность</span><b>{productivity}%</b><em>к плану</em><i className="spark green" /></article>
      <article><span>Обработано единиц</span><b>{format(unitsDone)} / {format(totalUnits)}</b><em>план смены</em><i className="bar blue" /></article>
      <article><span>Активные комплектовщики</span><b>{activePickers} / 10</b><em>в работе</em><i className="ring blue" /></article>
      <article><span>SLA пополнения</span><b>100%</b><em>цель 95%</em><i className="ring amber" /></article>
      <article><span>Просроченные задачи</span><b>{overdue}</b><em>RTP очередь</em><i className="spark red" /></article>
      <article><span>Коллизии</span><b>{collisions.length}</b><em>критические</em><i className="warn-symbol">!</i></article>
      <article><span>Средняя скорость</span><b>{avgSpeed.toFixed(2).replace(".", ",")} м/с</b><em>комплектовщики</em><i className="spark green" /></article>
    </section>
  );
}

export function LeftPanel({ tasks, trucks, onSelect }: { tasks: ReplenishmentTask[]; trucks: ResourceState[]; onSelect: (selection: DetailSelection) => void }) {
  const overdue = tasks.filter((task) => task.overdueMinutes > 0 && task.status !== "DONE");
  const visible = overdue.length ? overdue : tasks.slice(0, 8);
  const busiest = trucks.sort((a, b) => b.queue - a.queue)[0] || trucks[0];
  return (
    <aside className="twin-panel twin-left-panel">
      <header>
        <div><h2>Задачи пополнения (RTP)</h2><p>Очередь, причины просрочки и влияние на отбор</p></div>
        <button className="chevron-button" type="button">›</button>
      </header>
      <div className="tabs"><button className="active">Просроченные <span>{overdue.length}</span></button><button>Все <span>{tasks.length}</span></button></div>
      <div className="rtp-task-list">
        {visible.length ? visible.map((task) => (
          <button key={task.id} className={`rtp-task-card ${task.overdueMinutes > 20 ? "critical" : task.overdueMinutes > 0 ? "warning" : ""}`} onClick={() => onSelect({ type: "task", task })}>
            <div className="task-top"><span className="delay-pill">{task.overdueMinutes || task.ageMinutes} мин</span><b>{task.targetCell}</b></div>
            <div className="task-body"><div><b>{task.reason}</b><span>{task.sku} · {task.stockText}</span><div className="stock-mini"><i style={{ width: `${task.stockPercent}%` }} /></div><span>{task.zone}{task.mode === "CASE_REPLENISHMENT" ? " · 5 задач/час" : ""}</span></div><div className="pallet-icon" /></div>
          </button>
        )) : <div className="rtp-task-card"><b>Нет открытых RTP задач</b><span>Очередь пополнения не блокирует волну.</span></div>}
      </div>
      {busiest && <div className="rtp-driver-card"><b>{busiest.id} · {busiest.driver}</b><span>Загрузка: {busiest.utilization}%</span><span>Очередь: {busiest.queue} задач</span></div>}
    </aside>
  );
}

export function RightPanel({ collisions, onSelect }: { collisions: Collision[]; onSelect: (selection: DetailSelection) => void }) {
  return (
    <aside className="twin-panel twin-right-panel">
      <header><div><h2>Коллизии и причины</h2><p>Root cause, потери и затронутые маршруты</p></div><select><option>Все</option></select></header>
      <div className="collision-feed">
        {collisions.length ? collisions.slice().reverse().map((collision) => (
          <button key={collision.id} className={`collision-card ${collision.severity}`} onClick={() => onSelect({ type: "collision", collision })}>
            <span className="collision-icon">!</span>
            <span className="collision-meta">
              <span className="collision-top"><b>{collisionTitle(collision.type)}</b><span>{collision.clock}</span></span>
              <span>{collision.locationLabel}</span>
              <span>{collision.rootCause}</span>
              <span>Влияет: {collision.affectedResources.join(", ") || collision.waveId} · потеря ~{collision.productivityLoss}/час</span>
            </span>
          </button>
        )) : <div className="collision-card"><span className="collision-icon">✓</span><span className="collision-meta"><b>Нет активных коллизий</b><span>Склад работает без критических блокеров.</span></span></div>}
      </div>
    </aside>
  );
}

export function DetailCard({ selection, collisions, tasks }: { selection: DetailSelection; collisions: Collision[]; tasks: ReplenishmentTask[] }) {
  if (!selection) return null;
  if (selection.type === "resource") {
    const resource = selection.resource;
    const issue = resourceIssue(resource, collisions, tasks);
    return (
      <div className="detail-card">
        <b>{resource.id}</b>
        <span>Статус: {resource.status} · скорость {resource.speedRatio}%</span>
        <span>Волна: {resource.waveId || "нет"} · клиент: {resource.clientId || "нет"}</span>
        <span>SKU: {resource.sku || "нет"} · задача: {resource.taskId || "нет"}</span>
        <span>Причина: {issue.reason}</span>
        <span>Влияющий ресурс: {issue.neighbor || "-"}</span>
        <span>Потери/риск: {issue.loss}</span>
      </div>
    );
  }
  if (selection.type === "task") {
    const task = selection.task;
    return <div className="detail-card"><b>RTP задача {task.id}</b><span>Статус: {task.status}</span><span>Назначение: {task.targetCell}</span><span>SKU: {task.sku}</span><span>Режим: {task.mode === "CASE_REPLENISHMENT" ? "коробочное пополнение" : "паллетное пополнение"}</span><span>Просрочка: {task.overdueMinutes} мин</span><span>Причина: {task.reason}</span></div>;
  }
  if (selection.type === "pickFace") {
    const ratio = Math.round((selection.fill?.ratio || 0) * 100);
    return <div className="detail-card"><b>{selection.cellId}</b><span>Заполнение: {ratio}%</span><span>Остаток: {Math.round(selection.fill?.qty || 0)} / {Math.round(selection.fill?.capacity || 0)} коробок</span></div>;
  }
  const collision = selection.collision;
  return (
    <div className="detail-card">
      <b>Коллизия: {collisionTitle(collision.type)}</b>
      <span>Адрес: {collision.locationLabel}</span>
      <span>Root cause: {collision.rootCause}</span>
      <span>Ресурсы: {collision.affectedResources.join(", ") || "-"}</span>
      <span>Волна/клиент: {collision.waveId || "-"} / {collision.clientId || "-"}</span>
      <span>SKU: {collision.sku || "-"}</span>
      <span>Потери: {collision.lostMinutes} мин · ~{collision.productivityLoss}/час</span>
    </div>
  );
}

function resourceIssue(resource: ResourceState, collisions: Collision[], tasks: ReplenishmentTask[]): { reason: string; neighbor: string; loss: string } {
  const directCollision = collisions.slice().reverse().find((collision) =>
    collision.affectedResources.includes(resource.id) || collision.raw.resource_id === resource.id
  );
  if (directCollision) {
    const neighbors = directCollision.affectedResources.filter((id) => id !== resource.id);
    return {
      reason: `${collisionTitle(directCollision.type)}: ${directCollision.rootCause}`,
      neighbor: neighbors.join(", ") || String(directCollision.raw.resource_id || ""),
      loss: `${directCollision.lostMinutes} мин · ${directCollision.locationLabel}`,
    };
  }
  if (resource.kind === "reachtruck") {
    const overdue = tasks.find((task) => task.status !== "DONE" && task.overdueMinutes > 0);
    if (overdue) {
      return {
        reason: `Очередь RTP: не выполнено пополнение ${overdue.id}`,
        neighbor: overdue.targetCell,
        loss: `${overdue.overdueMinutes} мин ожидания · ${overdue.reason}`,
      };
    }
  }
  if (resource.statusColor === "amber") {
    return { reason: "Замедление на маршруте: возможная плотность движения в соседнем сегменте", neighbor: "см. ближайшие коллизии", loss: "операционный риск" };
  }
  if (resource.statusColor === "gray") {
    return { reason: "Ожидание следующего задания или освобождения зоны", neighbor: "-", loss: "без активной коллизии" };
  }
  return { reason: "Активной причины замедления не найдено", neighbor: "-", loss: "нет" };
}

export function CapacityPanel({ report }: { report: SimulationReport }) {
  const capacity = report.capacity_analysis;
  const bottlenecks = report.bottleneck_summary || [];
  if (!capacity && !bottlenecks.length) return null;
  const pickerRatio = Number(capacity?.picker_demand_to_capacity_ratio || 0);
  const reachRatio = Number(capacity?.replenishment_demand_to_nominal_capacity_ratio || 0);
  return (
    <div className="capacity-card">
      <header><b>Мощность смены</b><span>{pickerRatio > 1 || reachRatio > 1 ? "дефицит" : "норма"}</span></header>
      <div className="capacity-lines">
        <CapacityLine
          label="Комплектовка"
          done={Number(capacity?.done_pick_boxes || 0)}
          demand={Number(capacity?.total_pick_boxes || 0)}
          capacity={Number(capacity?.picker_box_capacity_per_shift || 0)}
          ratio={pickerRatio}
        />
        <CapacityLine
          label="RTP"
          done={Number(report.totals?.done_replenishment_tasks || 0)}
          demand={Number(capacity?.replenishment_tasks || 0)}
          capacity={Number(capacity?.reachtruck_nominal_capacity_per_shift || 0)}
          ratio={reachRatio}
        />
      </div>
      <div className="bottleneck-chips">
        {bottlenecks.slice(0, 3).map((item) => (
          <span key={item.code} className={item.severity}>{bottleneckLabel(item.code)}{item.ratio ? ` x${item.ratio}` : ""}</span>
        ))}
      </div>
    </div>
  );
}

export function ResourcePerformancePanel({ metrics, events, report, minute }: {
  metrics: MinuteMetrics[];
  events: WarehouseEvent[];
  report: SimulationReport;
  minute: number;
}) {
  const [hoverMinute, setHoverMinute] = useState<number | null>(null);
  const [pinnedMinute, setPinnedMinute] = useState<number | null>(null);
  const points = buildPerformancePoints(metrics, events, report);
  const lossEventsByMinute = useMemo(() => buildLossEventsByMinute(events), [events]);
  if (!points.length) return null;
  const current = nearestPoint(points, minute);
  const hover = pinnedMinute !== null ? nearestPoint(points, pinnedMinute) : hoverMinute === null ? null : nearestPoint(points, hoverMinute);
  const hoverLossEvents = hover ? (lossEventsByMinute[hover.minute] || []) : [];
  const selectMinuteFromSvg = (event: React.MouseEvent<SVGSVGElement>, preferLoss: boolean) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width * 960;
    return nearestVisualPoint(points, x, preferLoss).minute;
  };
  const maxQueue = Math.max(1, ...points.map((point) => point.queue));
  const maxLost = Math.max(1, ...points.map((point) => point.lost));
  const collisionTotals = buildCollisionTotals(events);
  const topCollisions = Object.entries(collisionTotals).sort((a, b) => b[1] - a[1]).slice(0, 4);
  const capacity = report.capacity_analysis;
  return (
    <section className="performance-panel">
      <header>
        <div>
          <h2>Производительность ресурсов и коллизии</h2>
          <p>График показывает, где очередь RTP и потери минут начинают съедать сменную мощность.</p>
        </div>
        <div className="performance-kpis">
          <span><b>{Math.round(current.pickerLoad)}%</b> комплектовщики</span>
          <span><b>{Math.round(current.reachLoad)}%</b> RTP</span>
          <span><b>{current.queue}</b> очередь RTP</span>
          <span><b>{current.lost}</b> потеряно мин</span>
        </div>
      </header>
      <div className="performance-content">
        <div className="performance-chart" aria-label="График производительности ресурсов">
          <svg viewBox="0 0 960 230" role="img" onMouseLeave={() => setHoverMinute(null)} onContextMenu={(event) => {
            event.preventDefault();
            setPinnedMinute(selectMinuteFromSvg(event, true));
          }} onMouseMove={(event) => {
            if (pinnedMinute !== null) return;
            setHoverMinute(selectMinuteFromSvg(event, true));
          }}>
            <g className="chart-grid">
              {[0, 25, 50, 75, 100].map((tick) => <line key={tick} x1="44" x2="928" y1={yFor(100 - tick)} y2={yFor(100 - tick)} />)}
            </g>
            <path className="chart-area queue" d={areaPath(points, (point) => point.queue / maxQueue * 100)} />
            <path className="chart-line picker" d={linePath(points, (point) => point.pickerLoad)} />
            <path className="chart-line reach" d={linePath(points, (point) => point.reachLoad)} />
            <path className="chart-line lost" d={linePath(points, (point) => point.lost / maxLost * 100)} />
            {points.map((point) => point.lost > 0 ? (
              <g key={`loss-${point.minute}`} onMouseEnter={() => setHoverMinute(point.minute)} onContextMenu={(event) => { event.preventDefault(); setPinnedMinute(point.minute); }}>
                <circle className="loss-marker-hit" cx={xFor(point.minute)} cy={yFor(point.lost / maxLost * 100)} r="12" />
                <circle className="loss-marker" cx={xFor(point.minute)} cy={yFor(point.lost / maxLost * 100)} r="4.5" />
              </g>
            ) : (
              <g key={`zero-${point.minute}`} className="zero-marker" onMouseEnter={() => setHoverMinute(point.minute)} onContextMenu={(event) => { event.preventDefault(); setPinnedMinute(point.minute); }}>
                <circle className="zero-marker-hit" cx={xFor(point.minute)} cy={yFor(0)} r="9" />
                <line x1={xFor(point.minute) - 3} x2={xFor(point.minute) + 3} y1={yFor(0) - 3} y2={yFor(0) + 3} />
                <line x1={xFor(point.minute) - 3} x2={xFor(point.minute) + 3} y1={yFor(0) + 3} y2={yFor(0) - 3} />
              </g>
            ))}
            <line className="chart-now" x1={xFor(minute)} x2={xFor(minute)} y1="22" y2="196" />
            {hover && <line className="chart-hover" x1={xFor(hover.minute)} x2={xFor(hover.minute)} y1="22" y2="196" />}
            {[0, 180, 360, 540, 720].map((tick) => (
              <g key={tick}>
                <text x={xFor(tick)} y="220">{clockLabel(tick)}</text>
              </g>
            ))}
          </svg>
          {hover && (
            <div className="loss-tooltip" style={{ left: `${Math.min(76, Math.max(12, (xFor(hover.minute) / 960) * 100))}%` }}>
              <b>{clockLabel(hover.minute)} · потери {hover.lost} мин/мин{pinnedMinute !== null ? " · закреплено" : ""}</b>
              {hoverLossEvents.length ? hoverLossEvents.slice(0, 5).map((event, index) => (
                <span key={`${event.minute}-${event.collision_type}-${index}`}>
                  {collisionTitle(String(event.collision_type || "UNKNOWN"))}: {(Array.isArray(event.resources) ? event.resources.join(", ") : event.resource_id) || "-"} · {event.cell || event.segment || event.gate_id || event.target_cell || "-"} · {event.lost_minutes || 1} мин
                </span>
              )) : <span>В эту минуту нет событий потерь. Правый клик по красному кружку покажет причины пика.</span>}
              {pinnedMinute !== null && <button type="button" onClick={() => setPinnedMinute(null)}>Снять закрепление</button>}
            </div>
          )}
          <div className="performance-legend">
            <span><i className="blue" /> Комплектовщики</span>
            <span><i className="amber" /> RTP занятость</span>
            <span><i className="queue" /> Очередь RTP</span>
            <span><i className="red" /> Потери минут/мин</span>
          </div>
        </div>
        <div className="performance-diagnosis">
          <b>Диагноз смены</b>
          <span>Комплектовка: спрос x{Number(capacity?.picker_demand_to_capacity_ratio || 0).toFixed(2)}</span>
          <span>RTP: спрос x{Number(capacity?.replenishment_demand_to_nominal_capacity_ratio || 0).toFixed(2)}</span>
          <span>Выполнено отбора: {format(Number(capacity?.done_pick_boxes || 0))} / {format(Number(capacity?.total_pick_boxes || 0))} коробок</span>
          <span>Пополнения: {format(Number(report.totals?.done_replenishment_tasks || 0))} / {format(Number(capacity?.replenishment_tasks || 0))} задач</span>
          <div className="collision-breakdown">
            {topCollisions.map(([type, count]) => (
              <span key={type}><b>{collisionTitle(type)}</b><i>{count}</i></span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function CapacityLine({ label, done, demand, capacity, ratio }: { label: string; done: number; demand: number; capacity: number; ratio: number }) {
  const fill = Math.min(100, Math.round((done / Math.max(1, demand)) * 100));
  return (
    <div className="capacity-line">
      <span><b>{label}</b><em>{format(done)} / {format(demand)}</em></span>
      <span className="capacity-bar"><i className={ratio > 1.25 ? "red" : ratio > 1 ? "amber" : "green"} style={{ width: `${Math.max(4, fill)}%` }} /></span>
      <span className="capacity-note">мощность {format(capacity)} · спрос x{ratio.toFixed(2)}</span>
    </div>
  );
}

function bottleneckLabel(code: string): string {
  const labels: Record<string, string> = {
    PICKER_CAPACITY_SHORTAGE: "мало комплектовщиков",
    REACHTRUCK_CAPACITY_SHORTAGE: "мало RTP",
    REACH_RESOURCE_SHORTAGE: "очередь RTP",
    ROUTE_COMPLETION_DELAY: "хвост маршрутов",
    REACHTRUCK_PICKER_PASS: "пересечения",
    REACHTRUCK_CROSSING: "встречные RTP",
    PICK_FACE_EMPTY: "пустой отбор",
  };
  return labels[code] || code.replace(/_/g, " ").toLowerCase();
}

function format(value: number) {
  return new Intl.NumberFormat("ru-RU").format(Math.round(value));
}

type PerformancePoint = {
  minute: number;
  pickerLoad: number;
  reachLoad: number;
  queue: number;
  lost: number;
};

function buildPerformancePoints(metrics: MinuteMetrics[], events: WarehouseEvent[], report: SimulationReport): PerformancePoint[] {
  const source: MinuteMetrics[] = metrics.length ? metrics : Array.from({ length: 25 }, (_, index) => ({ minute: index * 30 }));
  const pickerCount = Number(report.scenario?.pickers || 24);
  const reachtruckCount = Number(report.scenario?.reachtrucks || 12);
  return source
    .filter((row, index) => index % 10 === 0 || Number(row.minute) % 30 === 0 || Number(row.minute) === 720)
    .map((row) => {
      const minute = Number(row.minute || 0);
      const sameMinuteLoss = events
        .filter((event) => event.event_type === "COLLISION" && Number(event.minute) === minute)
        .reduce((sum, event) => sum + Number(event.lost_minutes || 1), 0);
      const lost = Number(row.lost_minutes || sameMinuteLoss);
      return {
        minute,
        pickerLoad: clamp(Number(row.picker_busy || 0) / Math.max(1, pickerCount) * 100, 0, 100),
        reachLoad: clamp(Number(row.reachtruck_busy || 0) / Math.max(1, reachtruckCount) * 100, 0, 100),
        queue: Number(row.queued_replenishment || 0),
        lost
      };
    });
}

function nearestPoint(points: PerformancePoint[], minute: number): PerformancePoint {
  return points.reduce((best, point) => Math.abs(point.minute - minute) < Math.abs(best.minute - minute) ? point : best, points[0]);
}

function nearestVisualPoint(points: PerformancePoint[], x: number, preferLoss: boolean): PerformancePoint {
  const candidates = preferLoss && points.some((point) => point.lost > 0) ? points.filter((point) => point.lost > 0) : points;
  return candidates.reduce((best, point) => Math.abs(xFor(point.minute) - x) < Math.abs(xFor(best.minute) - x) ? point : best, candidates[0]);
}

function buildCollisionTotals(events: WarehouseEvent[]): Record<string, number> {
  return events.reduce<Record<string, number>>((totals, event) => {
    if (event.event_type !== "COLLISION") return totals;
    const type = String(event.collision_type || "UNKNOWN");
    totals[type] = (totals[type] || 0) + 1;
    return totals;
  }, {});
}

function buildLossEventsByMinute(events: WarehouseEvent[]): Record<number, WarehouseEvent[]> {
  return events.reduce<Record<number, WarehouseEvent[]>>((rows, event) => {
    if (event.event_type !== "COLLISION") return rows;
    const minute = Number(event.minute || 0);
    rows[minute] = rows[minute] || [];
    rows[minute].push(event);
    return rows;
  }, {});
}

function linePath(points: PerformancePoint[], getValue: (point: PerformancePoint) => number): string {
  return points.map((point, index) => `${index ? "L" : "M"}${xFor(point.minute).toFixed(1)} ${yFor(getValue(point)).toFixed(1)}`).join(" ");
}

function areaPath(points: PerformancePoint[], getValue: (point: PerformancePoint) => number): string {
  if (!points.length) return "";
  const top = linePath(points, getValue);
  const last = points[points.length - 1];
  const first = points[0];
  return `${top} L${xFor(last.minute).toFixed(1)} 196 L${xFor(first.minute).toFixed(1)} 196 Z`;
}

function xFor(minute: number): number {
  return 44 + clamp(minute, 0, 720) / 720 * 884;
}

function yFor(value: number): number {
  return 196 - clamp(value, 0, 100) / 100 * 174;
}

function clockLabel(minute: number): string {
  const total = 8 * 60 + minute;
  return `${String(Math.floor(total / 60)).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}
