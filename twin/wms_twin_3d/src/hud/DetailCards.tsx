import type { ReactNode } from "react";
import type { Cell, Collision, Gate, Resource, St, Trip, TwinState } from "../contracts/twin";
import { skuName } from "../sim/catalog";
import { COLLISION_LABEL } from "../sim/collisions";
import { tripById } from "../sim/journal";
import { useTwin } from "../store/twinStore";
import { STAGE_LABEL, clock, minutesAgo, resourceStatus, riskBadge, shipmentLabel, stProgress, tripStatus } from "../ui/format";

export function Row({ k, v }: { k: string; v: ReactNode }) {
  return (
    <div className="row">
      <span>{k}</span>
      <b>{v}</b>
    </div>
  );
}

export function Chip({ tone, children }: { tone: string; children: ReactNode }) {
  return <span className={`chip tone-${tone}`}>{children}</span>;
}

function Bar({ value, max, tone = "info" }: { value: number; max: number; tone?: string }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <span className="bar">
      <span className={`bar-fill tone-${tone}`} style={{ width: `${pct}%` }} />
    </span>
  );
}

function Link({ onClick, children }: { onClick: () => void; children: ReactNode }) {
  return <button type="button" className="link" onClick={onClick}>{children}</button>;
}

export function TripCard({ trip, w }: { trip: Trip; w: TwinState }) {
  const select = useTwin((s) => s.select);
  const st = tripStatus(trip);
  const risk = riskBadge(trip);
  return (
    <>
      <div className="card-chips">
        <Chip tone={st.tone}>{st.label}</Chip>
        {risk && <Chip tone={risk.tone}>{risk.label}</Chip>}
      </div>
      {trip.waitReason && <p className="reason">{trip.waitReason}</p>}
      <div className="progress-line">
        <span>{trip.direction === "out" ? "Погружено" : "Выгружено"} {trip.palletsDone}/{trip.pallets} палл.</span>
        <Bar value={trip.palletsDone} max={trip.pallets} tone="ok" />
      </div>
      <Row k="Маршрут" v={trip.route} />
      <Row k="Ворота" v={trip.gateId ? <Link onClick={() => select({ kind: "gate", id: trip.gateId })}>{trip.gateId}</Link> : "не назначены"} />
      {trip.shipmentDate !== undefined && <Row k="Отгрузка (ТМС)" v={shipmentLabel(trip.shipmentDate)} />}
      {trip.readyPerc !== undefined && <Row k="Готовность СТ" v={`${trip.readyPerc}% · СТ ${trip.stCount ?? trip.stIds.length}`} />}
      <Row k="Окно дока" v={`${clock(trip.window.from)}–${clock(trip.window.to)}${trip.conditionRaw !== undefined ? " (условное)" : ""}`} />
      <Row k="Постановка" v={trip.dockedAt ? `${clock(trip.dockedAt)}${trip.onTime ? "" : " · опоздание"}` : "—"} />
      <Row k="ТС" v={`${trip.vehicle.name} · ${trip.plate}`} />
      <Row k="Перевозчик" v={trip.carrier} />
      <Row k="Водитель" v={trip.driver} />
      {trip.deliverAt && trip.phase === "transit" && <Row k="ETA магазины" v={clock(trip.deliverAt)} />}
      {trip.stIds.length > 0 && (
        <div className="sublist">
          <small>Сборочные задания</small>
          {trip.stIds.map((id) => {
            const s = w.sts[id];
            if (!s) return null;
            return (
              <button type="button" key={id} className="subrow" onClick={() => select({ kind: "st", id })}>
                <b>{id}</b>
                <span>{s.store.split(" · ")[0]}</span>
                <Chip tone={s.stage === "loaded" || s.stage === "shipped" || s.stage === "delivered" ? "ok" : s.stage === "created" ? "idle" : "info"}>{STAGE_LABEL[s.stage]}</Chip>
              </button>
            );
          })}
        </div>
      )}
    </>
  );
}

export function StCard({ st, w }: { st: St; w: TwinState }) {
  const select = useTwin((s) => s.select);
  const p = stProgress(st);
  const trip = tripById(w, st.tripId);
  return (
    <>
      <div className="card-chips">
        <Chip tone="info">{STAGE_LABEL[st.stage]}</Chip>
        <Chip tone="idle">{st.waveId}</Chip>
      </div>
      {p.total > 0 ? (
        <div className="progress-line">
          <span>Строки {p.picked}/{p.total}</span>
          <Bar value={p.picked} max={p.total} tone="ok" />
        </div>
      ) : (
        st.verifyPerc !== undefined && (
          <div className="progress-line">
            <span>Проверено {st.verifyPerc}% (VERIFY_PERC)</span>
            <Bar value={st.verifyPerc} max={100} tone="ok" />
          </div>
        )
      )}
      <Row k="Магазин" v={st.store} />
      <Row k="Рейс" v={trip ? <Link onClick={() => select({ kind: "trip", id: trip.id })}>{trip.id}</Link> : st.tripId || "не назначена"} />
      <Row k="Ворота" v={st.gateId || "—"} />
      {st.wareId !== undefined && <Row k="Склад (WARE_ID)" v={st.wareId} />}
      {st.weightKg !== undefined && <Row k="Вес" v={`${st.weightKg} кг`} />}
      <Row k="Паллет" v={`${st.palletsLoaded}/${st.pallets} погружено`} />
      {st.pickerId && <Row k="Комплектовщик" v={<Link onClick={() => select({ kind: "resource", id: st.pickerId! })}>{st.pickerId}</Link>} />}
      <div className="sublist">
        <small>Строки отбора</small>
        {st.lines.length === 0 && <span className="muted">Нет в данных источника</span>}
        {st.lines.map((l, i) => (
          <button type="button" key={`${l.cellId}:${i}`} className="subrow" onClick={() => select({ kind: "cell", id: l.cellId })}>
            <b>{l.cellId}</b>
            <span>{skuName(l.sku)} × {l.qty}</span>
            <Chip tone={l.picked ? "ok" : "idle"}>{l.picked ? "✓" : "…"}</Chip>
          </button>
        ))}
      </div>
    </>
  );
}

export function ResourceCard({ r, w }: { r: Resource; w: TwinState }) {
  const select = useTwin((s) => s.select);
  const setFollow = useTwin((s) => s.setFollow);
  const follow = useTwin((s) => s.follow);
  const status = resourceStatus(r, w);
  const task = w.tasks.find((t) => t.id === r.taskId);
  return (
    <>
      <div className="card-chips">
        <Chip tone={status.tone}>{status.label}</Chip>
        <button type="button" className={`chip-btn ${follow ? "active" : ""}`} onClick={() => setFollow(!follow)}>{follow ? "Следим камерой" : "Следить камерой"}</button>
      </div>
      {r.waitReason && <p className="reason">{r.waitReason}</p>}
      {r.kind !== "picker" && (
        <div className="progress-line">
          <span>Заряд {Math.round(r.battery)}%</span>
          <Bar value={r.battery} max={100} tone={r.battery < 20 ? "crit" : "ok"} />
        </div>
      )}
      <Row k="Тип" v={{ picker: "Комплектовщик", reachtruck: "Ричтрак", forklift: "Погрузчик" }[r.kind]} />
      <Row k="Имя" v={r.name} />
      {r.stId && <Row k="СТ" v={<Link onClick={() => select({ kind: "st", id: r.stId! })}>{r.stId}</Link>} />}
      {task && <Row k="Задание" v={`${task.id} · ${task.kind}`} />}
      {task?.fromCell && <Row k="Откуда" v={<Link onClick={() => select({ kind: "cell", id: task.fromCell! })}>{task.fromCell}</Link>} />}
      {task?.toCell && <Row k="Куда" v={<Link onClick={() => select({ kind: "cell", id: task.toCell! })}>{task.toCell}</Link>} />}
      {task?.gateId && <Row k="Ворота" v={task.gateId} />}
      <Row k={r.kind === "picker" ? "СТ собрано" : "Заданий выполнено"} v={r.done} />
    </>
  );
}

export function GateCard({ gate, w }: { gate: Gate; w: TwinState }) {
  const select = useTwin((s) => s.select);
  const trip = tripById(w, gate.occupiedBy);
  const planned = w.trips.filter((t) => t.gateId === gate.id && (t.phase === "planned" || t.phase === "queued" || t.phase === "arriving"));
  return (
    <>
      <div className="card-chips">
        <Chip tone={gate.occupiedBy ? "info" : "ok"}>{gate.occupiedBy ? "Занята" : "Свободна"}</Chip>
        <Chip tone="idle">{gate.kind === "inbound" ? "Приёмка" : "Отгрузка"}</Chip>
      </div>
      <Row k="Текущий рейс" v={trip ? <Link onClick={() => select({ kind: "trip", id: trip.id })}>{trip.id}</Link> : "—"} />
      {gate.kind === "inbound" && <Row k="Паллет в зоне приёмки" v={gate.received} />}
      <div className="sublist">
        <small>Забронировано</small>
        {planned.length === 0 && <span className="muted">Нет ожидаемых рейсов</span>}
        {planned.map((t) => (
          <button type="button" key={t.id} className="subrow" onClick={() => select({ kind: "trip", id: t.id })}>
            <b>{t.id}</b>
            <span>окно {clock(t.window.from)}–{clock(t.window.to)}</span>
            <Chip tone={t.risk === "ok" ? "idle" : t.risk === "risk" ? "warn" : "crit"}>{tripStatus(t).label}</Chip>
          </button>
        ))}
      </div>
    </>
  );
}

export function CellCard({ cell, w }: { cell: Cell; w: TwinState }) {
  const tasks = w.tasks.filter((t) => t.status !== "done" && (t.toCell === cell.id || t.fromCell === cell.id));
  const fill = cell.qty / cell.capacity;
  return (
    <>
      <div className="card-chips">
        <Chip tone={cell.role === "pick" ? "info" : "idle"}>{cell.role === "pick" ? "Ячейка отбора" : "Резерв"}</Chip>
        {cell.role === "pick" && cell.stockKnown !== false && <Chip tone={cell.qty === 0 ? "crit" : fill <= 0.21 ? "warn" : "ok"}>{cell.qty === 0 ? "Пусто" : fill <= 0.21 ? "Мало" : "Норма"}</Chip>}
      </div>
      {cell.stockKnown === false ? (
        <p className="muted">Остаток: нет данных (топология без складских остатков)</p>
      ) : (
        <div className="progress-line">
          <span>Остаток {cell.qty}/{cell.capacity} кор.</span>
          <Bar value={cell.qty} max={cell.capacity} tone={cell.qty === 0 ? "crit" : fill <= 0.21 ? "warn" : "ok"} />
        </div>
      )}
      <Row k="SKU" v={cell.sku ?? "—"} />
      <Row k="Товар" v={skuName(cell.sku)} />
      <Row k="Проход / уровень" v={`A${String(cell.aisle + 1).padStart(2, "0")} · L${cell.level}`} />
      {tasks.map((t) => (
        <Row key={t.id} k={t.kind === "REPL" ? "Пополнение" : "Размещение"} v={`${t.id} · ${t.status === "created" ? "в очереди" : `выполняет ${t.resourceId}`}`} />
      ))}
    </>
  );
}

export function CollisionCard({ c, w }: { c: Collision; w: TwinState }) {
  const select = useTwin((s) => s.select);
  return (
    <>
      <div className="card-chips">
        <Chip tone={c.severity === "critical" ? "crit" : "warn"}>{c.severity === "critical" ? "Критично" : "Риск"}</Chip>
        <Chip tone={c.active ? "info" : "idle"}>{c.active ? "Активна" : "Закрыта"}</Chip>
      </div>
      <p className="reason">{c.rootCause}</p>
      <Row k="Тип" v={COLLISION_LABEL[c.type]} />
      <Row k="Где" v={c.where} />
      <Row k="Начало" v={`${clock(c.startedAt)} · ${minutesAgo(w.simTime, c.startedAt)}`} />
      {c.endedAt && <Row k="Конец" v={clock(c.endedAt)} />}
      <Row k="Потери" v={`${c.lostMinutes.toFixed(1)} чел.-мин`} />
      <div className="sublist">
        <small>Затронуты</small>
        {c.affected.map((id) => {
          const kind = id.startsWith("TT") || id.startsWith("IN") ? "trip" : id.startsWith("СТ") ? "st" : "resource";
          return (
            <button type="button" key={id} className="subrow" onClick={() => select({ kind, id })}>
              <b>{id}</b>
            </button>
          );
        })}
      </div>
    </>
  );
}
