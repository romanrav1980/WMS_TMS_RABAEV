import type { TwinState } from "../contracts/twin";
import { skuName } from "../sim/catalog";
import { cellById, gateById, tripById } from "../sim/journal";
import { useTwin } from "../store/twinStore";
import { computeKpi } from "../ui/kpi";
import { CellCard, Chip, CollisionCard, GateCard, ResourceCard, Row, StCard, TripCard } from "./DetailCards";
import { ExecutorCard, OperationCard } from "./OperationCard";
import { kindLabel } from "../ui/opsFormat";

// Правая панель: карточка выбранного объекта или площадки — читает тот же TwinState, что и 3D.
export function DetailPanel() {
  const world = useTwin((s) => s.world);
  useTwin((s) => s.hudVersion);
  const selected = useTwin((s) => s.selected);
  const select = useTwin((s) => s.select);
  const { kicker, title, body } = resolve(world, selected?.kind, selected?.id);
  return (
    <section className="panel detail-panel">
      <header>
        <div>
          <small className="kicker">{kicker}</small>
          <b className="title">{title}</b>
        </div>
        {selected && <button type="button" className="icon-btn" onClick={() => select(undefined, false)} title="Закрыть">×</button>}
      </header>
      <div className="detail-body">{body}</div>
    </section>
  );
}

function resolve(w: TwinState, kind?: string, id?: string) {
  if (kind === "trip") {
    const trip = tripById(w, id);
    if (trip) return { kicker: trip.direction === "out" ? "РЕЙС · ОТГРУЗКА" : "ПОСТАВКА · ПРИЁМКА", title: trip.id, body: <TripCard trip={trip} w={w} /> };
  }
  if (kind === "st" && id && w.sts[id]) return { kicker: "СБОРОЧНОЕ ЗАДАНИЕ", title: id, body: <StCard st={w.sts[id]} w={w} /> };
  if (kind === "resource") {
    const r = w.resources.find((x) => x.id === id);
    if (r) return { kicker: { picker: "КОМПЛЕКТОВЩИК", reachtruck: "РИЧТРАК", forklift: "ПОГРУЗЧИК" }[r.kind], title: `${r.id} · ${r.name}`, body: <ResourceCard r={r} w={w} /> };
  }
  if (kind === "gate") {
    const gate = gateById(w, id);
    if (gate) return { kicker: "ВОРОТА", title: gate.id, body: <GateCard gate={gate} w={w} /> };
  }
  if (kind === "cell") {
    const cell = cellById(w, id);
    if (cell) return { kicker: "ЯЧЕЙКА", title: cell.id, body: <CellCard cell={cell} w={w} /> };
  }
  if (kind === "operation") {
    const op = w.operations.find((o) => o.key === id);
    if (op) return { kicker: `ОПЕРАЦИЯ · ${kindLabel(op.subtype).toUpperCase()}`, title: op.key, body: <OperationCard op={op} w={w} /> };
  }
  if (kind === "executor") {
    const ex = w.executors.find((e) => e.id === id);
    if (ex) return { kicker: "ИСПОЛНИТЕЛЬ", title: `${ex.code} · ${ex.name}`, body: <ExecutorCard ex={ex} w={w} /> };
  }
  if (kind === "collision") {
    const c = w.collisions.find((x) => x.key === id);
    if (c) return { kicker: "КОЛЛИЗИЯ", title: c.where, body: <CollisionCard c={c} w={w} /> };
  }
  return { kicker: `СКЛАД · ${w.layout.siteId}`, title: w.layout.siteName, body: <SiteCard w={w} /> };
}

function SiteCard({ w }: { w: TwinState }) {
  const k = computeKpi(w);
  const select = useTwin((s) => s.select);
  if (w.mode === "live") return <LiveSiteCard w={w} />;
  const lowFaces = w.cells
    .filter((c) => c.role === "pick" && c.stockKnown !== false && c.qty <= 10)
    .sort((a, b) => a.qty - b.qty)
    .slice(0, 5);
  return (
    <>
      <p className="muted">{w.layout.address}</p>
      <div className="card-chips">
        <Chip tone={k.collisionsCritical ? "crit" : k.collisionsActive ? "warn" : "ok"}>{k.collisionsCritical ? "Есть критичные коллизии" : "Работа в норме"}</Chip>
      </div>
      <div className="tiles">
        <Tile label="Резерв занят" value={`${(k.reserveFill * 100).toFixed(0)}%`} />
        <Tile label="Ворота заняты" value={`${k.gatesBusy}/${k.gatesTotal}`} />
        <Tile label="Отгружено палл." value={String(k.palletsShipped)} />
        <Tile label="Размещено палл." value={String(k.palletsReceived)} />
      </div>
      <Row k="Ячеек отбора пусто / мало" v={`${k.facesEmpty} / ${k.facesLow}`} />
      <Row k="Очередь ричтраков" v={k.replQueue} />
      <Row k="СТ отгружено" v={k.stShipped} />
      <div className="sublist">
        <small>Низкий остаток в отборе</small>
        {lowFaces.map((c) => (
          <button type="button" key={c.id} className="subrow" onClick={() => select({ kind: "cell", id: c.id })}>
            <b>{c.id}</b>
            <span>{skuName(c.sku)}</span>
            <Chip tone={c.qty === 0 ? "crit" : "warn"}>{c.qty}</Chip>
          </button>
        ))}
      </div>
    </>
  );
}

function LiveSiteCard({ w }: { w: TwinState }) {
  const k = computeKpi(w);
  const sts = Object.values(w.sts);
  const planned = w.trips.filter((t) => t.phase === "planned");
  return (
    <>
      <p className="muted">{w.layout.address}</p>
      <div className="card-chips">
        <Chip tone={k.collisionsCritical ? "crit" : "ok"}>{k.collisionsCritical ? `${k.collisionsCritical} рейсов просрочено` : "Просрочек нет"}</Chip>
        <Chip tone="idle">только чтение</Chip>
      </div>
      {w.dataNotes.length > 0 && (
        <div className="notes">
          <small>Качество данных источника</small>
          {w.dataNotes.map((n) => <p key={n}>{n}</p>)}
        </div>
      )}
      <div className="tiles">
        <Tile label="Рейсы спланированы" value={String(planned.length)} />
        <Tile label="Рейсы отгружены" value={String(w.trips.filter((t) => t.phase === "done").length)} />
        <Tile label="СТ в рейсах" value={String(sts.filter((s) => s.tripId).length)} />
        <Tile label="СТ свободные" value={String(sts.filter((s) => !s.tripId).length)} />
      </div>
      <Row k="Ячеек в топологии" v={w.cells.length} />
      <Row k="Проходов / ворот" v={`${w.layout.aisles.length} / ${w.gates.length}`} />
      <Row k="Ворота с бронью рейсов" v={w.gates.filter((g) => planned.some((t) => t.gateId === g.id)).length} />
      <Row k="Операций склада в снимке" v={w.operations.length} />
      <Row k="Открытых без привязки к схеме" v={w.opsStats.unbound} />
      <Row k="Исполнителей / с наблюдённой позицией" v={`${w.executors.length} / ${w.executors.filter((e) => e.positionBasis === "OBSERVED_CELL").length}`} />
    </>
  );
}

function Tile({ label, value }: { label: string; value: string }) {
  return (
    <div className="tile">
      <small>{label}</small>
      <b>{value}</b>
    </div>
  );
}
