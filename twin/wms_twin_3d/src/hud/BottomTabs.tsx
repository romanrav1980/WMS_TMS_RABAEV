import type { St, StStage, TwinState } from "../contracts/twin";
import { ST_STAGES } from "../contracts/twin";
import { tripById } from "../sim/journal";
import { type BottomTab, useTwin } from "../store/twinStore";
import { STAGE_LABEL, clock } from "../ui/format";
import { OperationsTab } from "./OperationsTab";

const TABS: { key: BottomTab; label: string }[] = [
  { key: "ops", label: "Операции склада" },
  { key: "journey", label: "Путь СТ" },
  { key: "docks", label: "График ворот" },
  { key: "gate", label: "Журнал КПП" },
  { key: "events", label: "События" }
];

export function BottomTabs() {
  const world = useTwin((s) => s.world);
  useTwin((s) => s.hudVersion);
  const tab = useTwin((s) => s.bottomTab);
  const setTab = useTwin((s) => s.setBottomTab);
  return (
    <section className="panel bottom-tabs">
      <nav className="tabs">
        {TABS.map((t) => (
          <button type="button" key={t.key} className={tab === t.key ? "active" : ""} onClick={() => setTab(t.key)}>{t.label}</button>
        ))}
      </nav>
      <div className="tab-body">
        {tab === "ops" && <OperationsTab w={world} />}
        {tab === "journey" && <Journey w={world} />}
        {tab === "docks" && <DockSchedule w={world} />}
        {tab === "gate" && <GateLog w={world} />}
        {tab === "events" && <Events w={world} />}
      </div>
    </section>
  );
}

// «Путь одной единицы» (как Journey of one parcel): СТ от создания до доставки в магазин.
function Journey({ w }: { w: TwinState }) {
  const selected = useTwin((s) => s.selected);
  const select = useTwin((s) => s.select);
  const setFollow = useTwin((s) => s.setFollow);
  const st = pickJourneySt(w, selected?.kind === "st" ? selected.id : undefined);
  if (!st) return <p className="muted">Нет активных СТ</p>;
  const current = ST_STAGES.indexOf(st.stage);
  const trip = tripById(w, st.tripId);
  return (
    <div className="journey">
      <div className="journey-head">
        <b>{st.id}</b>
        <span>{st.store} · {st.waveId} · рейс {st.tripId} · ворота {st.gateId}</span>
      </div>
      <ol className="stepper">
        {ST_STAGES.map((stage: StStage, i) => (
          <li key={stage} className={i < current ? "done" : i === current ? "current" : ""}>
            <span className="step-dot">{i < current ? "✓" : i + 1}</span>
            <b>{STAGE_LABEL[stage]}</b>
            <small>{st.stageAt[stage] !== undefined ? clock(st.stageAt[stage]!) : stage === "delivered" && trip?.deliverAt ? `ETA ${clock(trip.deliverAt)}` : ""}</small>
          </li>
        ))}
      </ol>
      <div className="journey-actions">
        <button type="button" className="primary" onClick={() => { select({ kind: "st", id: st.id }); setFollow(true); }}>Следить за СТ</button>
        {trip && <button type="button" onClick={() => select({ kind: "trip", id: trip.id })}>Открыть рейс</button>}
      </div>
    </div>
  );
}

function pickJourneySt(w: TwinState, id?: string): St | undefined {
  if (id && w.sts[id]) return w.sts[id];
  const all = Object.values(w.sts);
  return all.find((s) => s.stage === "picking") ?? all.find((s) => s.stage !== "delivered");
}

// График ворот: бронь окна (контур) и фактическое занятие (заливка) за ±2 часа.
function DockSchedule({ w }: { w: TwinState }) {
  const select = useTwin((s) => s.select);
  const from = w.simTime - 3600;
  const to = w.simTime + 3600;
  const pct = (t: number) => `${Math.max(0, Math.min(100, ((t - from) / (to - from)) * 100))}%`;
  const width = (a: number, b: number) => `${Math.max(0.6, ((Math.min(b, to) - Math.max(a, from)) / (to - from)) * 100)}%`;
  const ticks = [-60, -30, 0, 30, 60].map((m) => w.simTime + m * 60);
  return (
    <div className="gantt">
      <div className="gantt-scale">
        {ticks.map((t, i) => (
          <span key={t} style={{ left: pct(t) }} className={i === 2 ? "now" : ""}>{i === 2 ? "Сейчас" : clock(t)}</span>
        ))}
      </div>
      {w.gates.map((g) => (
        <div key={g.id} className="gantt-row">
          <button type="button" className="gantt-label" onClick={() => select({ kind: "gate", id: g.id })}>{g.id}</button>
          <div className="gantt-track">
            <span className="gantt-now" style={{ left: pct(w.simTime) }} />
            {w.trips
              .filter((t) => t.gateId === g.id && t.window.to > from && t.window.from < to)
              .map((t) => {
                const start = t.dockedAt ?? t.window.from;
                const end = t.departedAt ?? (t.dockedAt ? w.simTime : t.window.to);
                return (
                  <button type="button" key={t.id} className={`gantt-bar ${t.direction} ${t.dockedAt ? "actual" : "plan"} risk-${t.risk}`} style={{ left: pct(start), width: width(start, end) }} onClick={() => select({ kind: "trip", id: t.id })} title={`${t.id} · окно ${clock(t.window.from)}–${clock(t.window.to)}`}>
                    {t.id}
                  </button>
                );
              })}
          </div>
        </div>
      ))}
    </div>
  );
}

function GateLog({ w }: { w: TwinState }) {
  const select = useTwin((s) => s.select);
  const inCount = w.gateLog.filter((g) => g.dir === "in").length;
  const outCount = w.gateLog.length - inCount;
  return (
    <div className="table-wrap">
      <div className="mini-kpis">
        <span>Въезд/выезд <b>{inCount} · {outCount}</b></span>
        <span>На территории <b>{w.trips.filter((t) => ["arriving", "queued", "reversing", "docked", "departing"].includes(t.phase)).length}</b></span>
        <span>Очередь <b>{w.trips.filter((t) => t.phase === "queued").length}</b></span>
      </div>
      <table>
        <thead>
          <tr><th>Время</th><th>Напр.</th><th>Рейс · госномер</th><th>Перевозчик · ТС</th></tr>
        </thead>
        <tbody>
          {w.gateLog.slice(0, 30).map((g) => (
            <tr key={`${g.tripId}:${g.dir}:${g.at}`} onClick={() => select({ kind: "trip", id: g.tripId })}>
              <td>{clock(g.at)}</td>
              <td><span className={`chip tone-${g.dir === "in" ? "info" : "idle"}`}>{g.dir === "in" ? "Въезд" : "Выезд"}</span></td>
              <td><b>{g.tripId}</b> {g.plate}</td>
              <td>{g.carrier} · {g.vehicle}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Events({ w }: { w: TwinState }) {
  return (
    <div className="events">
      {w.events.slice(0, 60).map((e) => (
        <div key={e.id} className={`event lvl-${e.level}`}>
          <span className="event-time">{clock(e.at, true)}</span>
          <b>{e.what}</b>
          <span className="event-entity">{e.entity}{e.where ? ` · ${e.where}` : ""}</span>
          {e.why && <span className="event-why">{e.why}</span>}
          {e.who && <span className="event-who">{e.who}</span>}
        </div>
      ))}
    </div>
  );
}
