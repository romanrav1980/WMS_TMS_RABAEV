import { useState } from "react";
import type { TwinState } from "../contracts/twin";
import { COLLISION_LABEL } from "../sim/collisions";
import { useTwin } from "../store/twinStore";
import { clock, minutesAgo, resourceStatus, riskBadge, tripStatus } from "../ui/format";
import { POSITION_LABEL } from "../ui/opsFormat";

type Tab = "trips" | "gates" | "machines" | "people" | "collisions";

export function FleetTable() {
  const world = useTwin((s) => s.world);
  useTwin((s) => s.hudVersion);
  const [tab, setTab] = useState<Tab>("trips");
  const trips = world.trips.filter((t) => t.phase !== "done");
  const counts: Record<Tab, string> = {
    trips: String(trips.length),
    gates: `${world.gates.filter((g) => g.occupiedBy).length}/${world.gates.length}`,
    machines: world.mode === "live" ? String(world.executors.filter((e) => !isPerson(e.kind)).length) : `${world.resources.filter((r) => r.kind !== "picker" && r.taskId).length}/${world.resources.filter((r) => r.kind !== "picker").length}`,
    people: world.mode === "live" ? String(world.executors.filter((e) => isPerson(e.kind)).length) : String(world.resources.filter((r) => r.kind === "picker").length),
    collisions: String(world.collisions.filter((c) => c.active).length)
  };
  const labels: Record<Tab, string> = { trips: "Рейсы", gates: "Ворота", machines: "Техника", people: "Люди", collisions: "Коллизии" };
  return (
    <section className="panel fleet-table">
      <nav className="tabs">
        {(Object.keys(labels) as Tab[]).map((t) => (
          <button type="button" key={t} className={tab === t ? "active" : ""} onClick={() => setTab(t)}>
            {labels[t]} <em>{counts[t]}</em>
          </button>
        ))}
      </nav>
      <div className="fleet-body">
        {tab === "trips" && <Trips w={world} />}
        {tab === "gates" && <Gates w={world} />}
        {tab === "machines" && (world.mode === "live" ? <Executors w={world} people={false} /> : <Resources w={world} kind="machines" />)}
        {tab === "people" && (world.mode === "live" ? <Executors w={world} people /> : <Resources w={world} kind="people" />)}
        {tab === "collisions" && <Collisions w={world} />}
      </div>
    </section>
  );
}

function Trips({ w }: { w: TwinState }) {
  const select = useTwin((s) => s.select);
  const order = { docked: 0, reversing: 1, queued: 2, arriving: 3, departing: 4, planned: 5, transit: 6, done: 7 };
  const trips = w.trips.filter((t) => t.phase !== "done").sort((a, b) => order[a.phase] - order[b.phase] || a.window.from - b.window.from);
  return (
    <>
      {trips.map((t) => {
        const st = tripStatus(t);
        const risk = riskBadge(t);
        return (
          <button type="button" key={t.id} className="fleet-row" onClick={() => select({ kind: "trip", id: t.id })}>
            <span className="fleet-id">
              <b>{t.id}</b>
              <small>{t.carrier}</small>
            </span>
            <span className="fleet-where">{t.gateId || "без ворот"} · {t.direction === "out" ? t.route : "приёмка"}</span>
            <span className={`chip tone-${risk?.tone ?? st.tone}`}>{risk ? `${st.label} · ${risk.label}` : st.label}</span>
            <span className="fleet-meta">{t.phase === "docked" ? `${t.palletsDone}/${t.pallets}` : t.phase === "planned" && t.readyPerc !== undefined ? `${t.readyPerc}%` : t.phase === "planned" ? clock(t.arriveAt) : t.phase === "transit" && t.deliverAt ? `ETA ${clock(t.deliverAt)}` : ""}</span>
          </button>
        );
      })}
    </>
  );
}

function Gates({ w }: { w: TwinState }) {
  const select = useTwin((s) => s.select);
  return (
    <>
      {w.gates.map((g) => (
        <button type="button" key={g.id} className="fleet-row" onClick={() => select({ kind: "gate", id: g.id })}>
          <span className="fleet-id">
            <b>{g.id}</b>
            <small>{g.kind === "inbound" ? "приёмка" : "отгрузка"}</small>
          </span>
          <span className="fleet-where">{g.occupiedBy ?? "—"}</span>
          <span className={`chip tone-${g.occupiedBy ? "info" : "ok"}`}>{g.occupiedBy ? "Занята" : "Свободна"}</span>
          <span className="fleet-meta">{w.trips.filter((t) => t.gateId === g.id && t.phase === "planned").length} в плане</span>
        </button>
      ))}
    </>
  );
}

function Resources({ w, kind }: { w: TwinState; kind: "machines" | "people" }) {
  const select = useTwin((s) => s.select);
  const list = w.resources.filter((r) => (kind === "people" ? r.kind === "picker" : r.kind !== "picker"));
  return (
    <>
      {list.map((r) => {
        const st = resourceStatus(r, w);
        return (
          <button type="button" key={r.id} className="fleet-row" onClick={() => select({ kind: "resource", id: r.id })}>
            <span className="fleet-id">
              <b>{r.id}</b>
              <small>{r.name}</small>
            </span>
            <span className="fleet-where">{r.stId ?? r.taskId ?? "—"}</span>
            <span className={`chip tone-${st.tone}`}>{st.label}</span>
            <span className="fleet-meta">{r.kind === "picker" ? `${r.done} СТ` : `${Math.round(r.battery)}%`}</span>
          </button>
        );
      })}
    </>
  );
}

const isPerson = (kind: string) => !/(REACH|FORK|TRUCK|EQUIP|ТЕХ)/i.test(kind);

function Executors({ w, people }: { w: TwinState; people: boolean }) {
  const select = useTwin((s) => s.select);
  const list = w.executors.filter((e) => isPerson(e.kind) === people);
  if (!list.length) return <p className="muted pad">Нет исполнителей этого склада в данных WMS</p>;
  return (
    <>
      {list.map((e) => (
        <button type="button" key={e.id} className="fleet-row" onClick={() => select({ kind: "executor", id: e.id })}>
          <span className="fleet-id">
            <b>{e.code}</b>
            <small>{e.name}</small>
          </span>
          <span className="fleet-where">{e.kind}{e.lastCell ? ` · ${e.lastCell}` : ""}</span>
          <span className={`chip tone-${e.positionBasis === "OBSERVED_CELL" ? "ok" : "idle"}`}>{POSITION_LABEL[e.positionBasis]}</span>
          <span className="fleet-meta">{e.sessionStatus ?? e.status}</span>
        </button>
      ))}
    </>
  );
}

function Collisions({ w }: { w: TwinState }) {
  const select = useTwin((s) => s.select);
  if (!w.collisions.length) return <p className="muted pad">Коллизий нет</p>;
  return (
    <>
      {w.collisions.slice(0, 30).map((c) => (
        <button type="button" key={c.key + c.startedAt} className={`fleet-row ${c.active ? "" : "faded"}`} onClick={() => select({ kind: "collision", id: c.key })}>
          <span className="fleet-id">
            <b>{COLLISION_LABEL[c.type]}</b>
            <small>{minutesAgo(w.simTime, c.startedAt)}</small>
          </span>
          <span className="fleet-where">{c.where}</span>
          <span className={`chip tone-${!c.active ? "idle" : c.severity === "critical" ? "crit" : "warn"}`}>{c.active ? (c.severity === "critical" ? "Критично" : "Риск") : "Закрыта"}</span>
          <span className="fleet-meta">{c.lostMinutes.toFixed(1)} мин</span>
        </button>
      ))}
    </>
  );
}
