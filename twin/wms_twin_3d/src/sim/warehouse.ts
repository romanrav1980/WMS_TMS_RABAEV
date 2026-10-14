import type { Cell, Resource, St, TwinState, WTask } from "../contracts/twin";
import { SKUS } from "./catalog";
import { cellById, gateById, logEvent, nextId, tripById } from "./journal";
import {
  CHARGER,
  LEVEL_H,
  advance,
  floorRoute,
  makeMover,
  receivingPoint,
  sampleMover,
  servicePoint,
  stagingPoint,
  trailerPoint
} from "./layout";
import type { Rng } from "./rng";

const SPEED = { picker: 0.32, reachtruck: 0.42, forklift: 0.5 } as const;
const REPL_THRESHOLD = 6;
const REPL_SLA_SEC = 15 * 60;

// ── Создание заданий (что должно произойти) ─────────────────────────

function hasOpenTask(w: TwinState, kind: WTask["kind"], key: (t: WTask) => boolean) {
  return w.tasks.some((t) => t.kind === kind && t.status !== "done" && key(t));
}

function addTask(w: TwinState, task: Omit<WTask, "id" | "status" | "createdAt">) {
  const t: WTask = { id: nextId(w, task.kind === "REPL" ? "REPL-" : task.kind === "PUTAWAY" ? "PUT-" : task.kind === "LOAD" ? "LD-" : "UL-"), status: "created", createdAt: w.simTime, ...task };
  w.tasks.push(t);
  return t;
}

function reserveSource(w: TwinState, face: Cell): Cell | undefined {
  const sameSlot = w.cells.filter((c) => c.role === "reserve" && c.aisle === face.aisle && c.slot === face.slot && c.qty > 0);
  if (sameSlot.length) return sameSlot.sort((a, b) => a.level - b.level)[0];
  return w.cells.find((c) => c.role === "reserve" && c.sku === face.sku && c.qty > 0);
}

export function ensureReplenishment(w: TwinState, face: Cell, urgent: boolean) {
  if (hasOpenTask(w, "REPL", (t) => t.toCell === face.id)) {
    if (urgent) w.tasks.forEach((t) => { if (t.kind === "REPL" && t.toCell === face.id) t.urgent = true; });
    return;
  }
  const source = reserveSource(w, face);
  if (!source) return;
  addTask(w, { kind: "REPL", urgent, sku: face.sku, fromCell: source.id, toCell: face.id });
  logEvent(w, "Создано пополнение", face.id, urgent ? "warn" : "info", { why: urgent ? "ячейка отбора пуста" : `остаток ${face.qty} ≤ ${REPL_THRESHOLD}` });
}

export function planTasks(w: TwinState) {
  for (const face of w.cells) {
    if (face.role === "pick" && face.qty <= REPL_THRESHOLD) ensureReplenishment(w, face, face.qty === 0);
  }
  for (const trip of w.trips) {
    if (trip.phase !== "docked") continue;
    if (trip.direction === "in") {
      while (trip.unloadTasksCreated < trip.pallets) {
        trip.unloadTasksCreated += 1;
        addTask(w, { kind: "UNLOAD", urgent: false, gateId: trip.gateId, tripId: trip.id });
      }
      continue;
    }
    for (const id of trip.stIds) {
      const st = w.sts[id];
      if (st.stage !== "staged" && st.stage !== "loading") continue;
      while (st.loadTasksCreated < st.pallets) {
        st.loadTasksCreated += 1;
        addTask(w, { kind: "LOAD", urgent: false, gateId: trip.gateId, tripId: trip.id, stId: st.id });
      }
    }
  }
  w.tasks = w.tasks.filter((t) => t.status !== "done" || w.simTime - t.createdAt < 1800);
}

// ── Общие операции ресурса ──────────────────────────────────────────

function go(r: Resource, to: { x: number; z: number }, leg: Resource["leg"]) {
  r.mover = makeMover(floorRoute(r.pos, to), SPEED[r.kind]);
  r.leg = leg;
  r.status = "moving";
}

function move(r: Resource, dt: number): boolean {
  if (!r.mover) return true;
  const arrived = advance(r.mover, dt);
  const pose = sampleMover(r.mover);
  r.pos = pose.pos;
  if (r.mover.len > 0.05) r.heading = pose.heading;
  if (arrived) r.mover = undefined;
  return arrived;
}

function idle(r: Resource) {
  r.leg = "none";
  r.status = "idle";
  r.taskId = undefined;
  r.waitReason = undefined;
  r.waitSince = undefined;
}

// ── Комплектовщик: СТ построчно → выставка у ворот рейса ────────────

function nextSt(w: TwinState): St | undefined {
  return Object.values(w.sts)
    .filter((s) => s.stage === "created")
    .sort((a, b) => (tripById(w, a.tripId)?.window.from ?? 0) - (tripById(w, b.tripId)?.window.from ?? 0))[0];
}

function stepPicker(w: TwinState, r: Resource, dt: number) {
  const st = r.stId ? w.sts[r.stId] : undefined;
  if (!st) {
    const candidate = nextSt(w);
    if (candidate) {
      candidate.stage = "picking";
      candidate.stageAt.picking = w.simTime;
      candidate.pickerId = r.id;
      r.stId = candidate.id;
      r.lineIdx = 0;
      go(r, servicePoint(cellById(w, candidate.lines[0].cellId)!), "toLine");
      logEvent(w, "Начат отбор", candidate.id, "info", { who: `${r.id} · ${r.name}`, why: `${candidate.lines.length} строк · ${candidate.store}` });
    } else if (r.leg !== "toPark" && Math.hypot(r.pos.x - r.park.x, r.pos.z - r.park.z) > 0.5) {
      go(r, r.park, "toPark");
    } else if (r.leg === "toPark" && move(r, dt)) idle(r);
    return;
  }
  const line = st.lines[r.lineIdx];
  const face = line ? cellById(w, line.cellId) : undefined;
  if (r.status === "moving" && !move(r, dt)) return;
  if (r.leg === "toStaging") {
    st.stage = "picked";
    st.stageAt.picked = w.simTime;
    st.qcLeft = 100 + (st.lines.length % 4) * 15;
    r.done += 1;
    r.stId = undefined;
    idle(r);
    logEvent(w, "СТ собрано и выставлено", st.id, "info", { where: st.gateId, who: r.id });
    return;
  }
  if (!line || !face) return;
  if (r.status === "moving" || r.status === "waiting") {
    if (face.qty < line.qty) {
      if (r.status !== "waiting") {
        r.status = "waiting";
        r.waitSince = w.simTime;
        r.waitReason = `Пустая ячейка отбора ${face.id}`;
        ensureReplenishment(w, face, true);
      }
      return;
    }
    r.status = "working";
    r.waitReason = undefined;
    r.waitSince = undefined;
    r.workLeft = 14 + line.qty * 2.5;
    return;
  }
  if (r.status !== "working") return;
  r.workLeft -= dt;
  if (r.workLeft > 0) return;
  face.qty -= line.qty;
  line.picked = true;
  w.stockVersion += 1;
  w.counters.linesPicked += 1;
  w.counters.pickTimes.push(w.simTime);
  r.lineIdx += 1;
  const next = st.lines[r.lineIdx];
  if (next) go(r, servicePoint(cellById(w, next.cellId)!), "toLine");
  else go(r, stagingPoint(gateById(w, st.gateId)!, (r.id.charCodeAt(2) % 3) - 1), "toStaging");
}

// ── Ричтрак: пополнение и размещение ────────────────────────────────

function sourcePoint(w: TwinState, t: WTask) {
  if (t.kind === "PUTAWAY") return receivingPoint(gateById(w, t.gateId)!);
  return servicePoint(cellById(w, t.fromCell)!);
}

function takeTask(w: TwinState, r: Resource, kinds: WTask["kind"][]): WTask | undefined {
  const open = w.tasks.filter((t) => t.status === "created" && kinds.includes(t.kind));
  open.sort((a, b) => Number(b.urgent) - Number(a.urgent) || a.createdAt - b.createdAt);
  const t = open[0];
  if (!t) return undefined;
  t.status = "assigned";
  t.resourceId = r.id;
  r.taskId = t.id;
  return t;
}

function chargeOrPark(w: TwinState, r: Resource, dt: number, kinds: WTask["kind"][]) {
  if (r.status === "charging") {
    r.battery = Math.min(100, r.battery + dt * 0.06);
    if (r.battery >= 96) idle(r);
    return true;
  }
  if (r.leg === "toCharger") {
    if (move(r, dt)) {
      r.status = "charging";
      logEvent(w, "Зарядка", r.id, "info", { why: `заряд ${Math.round(r.battery)}%` });
    }
    return true;
  }
  if (r.battery < 15) {
    go(r, CHARGER, "toCharger");
    return true;
  }
  const task = takeTask(w, r, kinds);
  if (task) {
    go(r, task.kind === "LOAD" ? stagingPoint(gateById(w, task.gateId)!) : task.kind === "UNLOAD" ? trailerPoint(gateById(w, task.gateId)!) : sourcePoint(w, task), "toSource");
    return true;
  }
  if (r.leg !== "toPark" && Math.hypot(r.pos.x - r.park.x, r.pos.z - r.park.z) > 0.5) go(r, r.park, "toPark");
  else if (r.leg === "toPark" && move(r, dt)) idle(r);
  return true;
}

function finishReachTask(w: TwinState, r: Resource, t: WTask, rng: Rng) {
  if (t.kind === "REPL") {
    const face = cellById(w, t.toCell)!;
    face.qty = face.capacity;
    w.counters.replDone += 1;
    if (w.simTime - t.createdAt <= REPL_SLA_SEC) w.counters.replOnTime += 1;
    logEvent(w, "Пополнение выполнено", face.id, "info", { who: r.id, why: `из ${t.fromCell}` });
  } else {
    const target = cellById(w, t.toCell)!;
    target.qty = target.capacity;
    target.sku = t.sku;
    w.counters.palletsReceived += 1;
    logEvent(w, "Паллета размещена", target.id, "info", { who: r.id });
  }
  w.stockVersion += 1;
  t.status = "done";
  r.battery = Math.max(0, r.battery - (2 + rng.next() * 2));
  r.done += 1;
  r.carrying = false;
  idle(r);
}

function workAt(r: Resource, dt: number, next: () => void) {
  r.workLeft -= dt;
  if (r.workLeft <= 0) next();
}

function stepReach(w: TwinState, r: Resource, dt: number, rng: Rng) {
  const t = w.tasks.find((x) => x.id === r.taskId);
  if (!t) {
    r.fork = 0;
    chargeOrPark(w, r, dt, ["REPL", "PUTAWAY"]);
    return;
  }
  if (r.status === "moving") {
    if (!move(r, dt)) return;
    const cell = cellById(w, r.leg === "toSource" ? t.fromCell : t.toCell);
    r.fork = cell ? (cell.y + 0.2) / (LEVEL_H * 4 + 0.2) : 0.05;
    r.status = "working";
    r.workLeft = 22;
    return;
  }
  workAt(r, dt, () => {
    if (r.leg === "toSource") {
      if (t.kind === "REPL") {
        const src = cellById(w, t.fromCell)!;
        src.qty = 0;
        src.sku = undefined;
      } else {
        const gate = gateById(w, t.gateId)!;
        gate.received = Math.max(0, gate.received - 1);
        t.toCell = putawayTarget(w, t.sku)?.id;
        if (!t.toCell) {
          t.status = "created";
          idle(r);
          return;
        }
      }
      w.stockVersion += 1;
      r.carrying = true;
      r.fork = 0.08;
      go(r, servicePoint(cellById(w, t.toCell)!), "toTarget");
    } else finishReachTask(w, r, t, rng);
  });
}

function putawayTarget(w: TwinState, sku?: string): Cell | undefined {
  const empty = w.cells.filter((c) => c.role === "reserve" && c.qty === 0);
  const facesForSku = new Set(w.cells.filter((c) => c.role === "pick" && c.sku === sku).map((c) => `${c.aisle}:${c.slot}`));
  return empty.find((c) => facesForSku.has(`${c.aisle}:${c.slot}`)) ?? empty[0];
}

// ── Погрузчик у ворот: загрузка рейса и выгрузка поставки ───────────

function lowestStockSku(w: TwinState): string {
  const totals = new Map<string, number>(SKUS.map((s) => [s.code, 0]));
  for (const c of w.cells) if (c.sku) totals.set(c.sku, (totals.get(c.sku) ?? 0) + c.qty);
  return [...totals.entries()].sort((a, b) => a[1] - b[1])[0][0];
}

function stepForklift(w: TwinState, r: Resource, dt: number) {
  const t = w.tasks.find((x) => x.id === r.taskId);
  if (!t) {
    r.fork = 0;
    chargeOrPark(w, r, dt, ["LOAD", "UNLOAD"]);
    return;
  }
  const gate = gateById(w, t.gateId)!;
  const trip = tripById(w, t.tripId);
  if (r.status === "moving") {
    if (!move(r, dt)) return;
    r.status = "working";
    r.workLeft = r.leg === "toSource" ? 9 : 7;
    r.fork = r.leg === "toSource" ? 0.15 : 0.05;
    return;
  }
  workAt(r, dt, () => {
    if (r.leg === "toSource") {
      r.carrying = true;
      go(r, t.kind === "LOAD" ? trailerPoint(gate) : receivingPoint(gate), "toTarget");
      return;
    }
    r.carrying = false;
    t.status = "done";
    r.done += 1;
    r.battery = Math.max(0, r.battery - 1.2);
    if (trip) trip.palletsDone += 1;
    if (t.kind === "LOAD" && t.stId) {
      const st = w.sts[t.stId];
      st.palletsLoaded += 1;
      if (st.stage === "staged") {
        st.stage = "loading";
        st.stageAt.loading = w.simTime;
      }
      if (st.palletsLoaded >= st.pallets) {
        st.stage = "loaded";
        st.stageAt.loaded = w.simTime;
      }
    } else if (t.kind === "UNLOAD") {
      gate.received += 1;
      addTask(w, { kind: "PUTAWAY", urgent: false, gateId: gate.id, tripId: t.tripId, sku: lowestStockSku(w) });
    }
    idle(r);
  });
}

// ── Контроль качества СТ ────────────────────────────────────────────

function stepQc(w: TwinState, dt: number) {
  for (const st of Object.values(w.sts)) {
    if (st.stage === "picked") {
      st.stage = "qc";
      st.stageAt.qc = w.simTime;
    } else if (st.stage === "qc") {
      st.qcLeft -= dt;
      if (st.qcLeft <= 0) {
        st.stage = "staged";
        st.stageAt.staged = w.simTime;
        logEvent(w, "Контроль пройден", st.id, "info", { where: st.gateId, why: `${st.pallets} палл. к воротам` });
      }
    }
  }
}

export function stepWarehouse(w: TwinState, dt: number, rng: Rng) {
  stepQc(w, dt);
  for (const r of w.resources) {
    if (r.kind === "picker") stepPicker(w, r, dt);
    else if (r.kind === "reachtruck") stepReach(w, r, dt, rng);
    else stepForklift(w, r, dt);
  }
}
