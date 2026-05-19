import type { Collision, DetailSelection, ReplenishmentTask, ResourceState } from "../types";
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

export function DetailCard({ selection }: { selection: DetailSelection }) {
  if (!selection) return <div className="detail-card"><b>Склад</b><span>Нажмите ресурс, задачу или коллизию.</span></div>;
  if (selection.type === "resource") {
    const resource = selection.resource;
    return <div className="detail-card"><b>{resource.id}</b><span>Статус: {resource.status}</span><span>Волна: {resource.waveId || "нет"}</span><span>Клиент: {resource.clientId || "нет"}</span><span>SKU: {resource.sku || "нет"}</span><span>Скорость: {resource.speedRatio}%</span></div>;
  }
  if (selection.type === "task") {
    const task = selection.task;
    return <div className="detail-card"><b>RTP задача {task.id}</b><span>Статус: {task.status}</span><span>Назначение: {task.targetCell}</span><span>SKU: {task.sku}</span><span>Режим: {task.mode === "CASE_REPLENISHMENT" ? "коробочное пополнение" : "паллетное пополнение"}</span><span>Просрочка: {task.overdueMinutes} мин</span><span>Причина: {task.reason}</span></div>;
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

function format(value: number) {
  return new Intl.NumberFormat("ru-RU").format(Math.round(value));
}
