import type { Gate, St, Trip, TwinState } from "../contracts/twin";
import { CARRIERS, DRIVERS, STORES, SUPPLIERS, VEHICLES, plateLetters } from "./catalog";
import { gateById, logEvent, nextId } from "./journal";
import {
  SPAWN,
  advance,
  approachRoute,
  departRoute,
  makeMover,
  queuePoint,
  reverseRoute,
  sampleMover
} from "./layout";
import type { Rng } from "./rng";

const TRUCK_SPEED = 1.5;
const REVERSE_SPEED = 0.55;
const MAX_ACTIVE_OUTBOUND = 7;

function plate(rng: Rng) {
  const l = () => plateLetters[rng.int(0, plateLetters.length - 1)];
  return `${l()}${rng.int(100, 999)}${l()}${l()} ${rng.pick(["77", "50", "99", "190", "750"])}`;
}

// Ворота бронируются при планировании рейса (окно дока), занимаются физически при постановке.
function planGate(w: TwinState, kind: Gate["kind"]): Gate {
  const load = (g: Gate) => w.trips.filter((t) => t.gateId === g.id && t.phase !== "done" && t.phase !== "transit").length;
  return w.gates.filter((g) => g.kind === kind).sort((a, b) => load(a) - load(b) || a.index - b.index)[0];
}

function pickLines(w: TwinState, rng: Rng) {
  const count = rng.int(6, 12);
  const faces = w.cells.filter((c) => c.role === "pick");
  const lines = Array.from({ length: count }, () => {
    const cell = rng.pick(faces);
    return { cellId: cell.id, sku: cell.sku ?? "", qty: rng.int(3, 9), picked: false };
  });
  return lines.sort((a, b) => a.cellId.localeCompare(b.cellId));
}

function createOutboundTrip(w: TwinState, rng: Rng) {
  const vehicle = rng.pick(VEHICLES.filter((v) => v.pallets <= 8 || rng.next() < 0.4));
  const gate = planGate(w, "outbound");
  const tripId = nextId(w, "TT-58");
  const waveId = `WAVE-${String(w.counters.waveNo).padStart(3, "0")}`;
  const stores = Array.from({ length: rng.int(2, 3) }, () => rng.pick(STORES));
  const arriveAt = w.simTime + rng.int(22, 34) * 60;
  const stIds: string[] = [];
  for (const store of stores) {
    const lines = pickLines(w, rng);
    const st: St = {
      id: nextId(w, "СТ-104"),
      store,
      tripId,
      gateId: gate.id,
      waveId,
      stage: "created",
      stageAt: { created: w.simTime },
      lines,
      pallets: Math.max(1, Math.ceil(lines.length / 4)),
      palletsLoaded: 0,
      loadTasksCreated: 0,
      qcLeft: 0
    };
    w.sts[st.id] = st;
    stIds.push(st.id);
  }
  const trip = baseTrip(w, rng, tripId, "out", vehicle, gate, arriveAt);
  trip.stIds = stIds;
  trip.route = stores.map((s) => s.split(" · ")[0]).join(" → ");
  trip.pallets = stIds.reduce((sum, id) => sum + w.sts[id].pallets, 0);
  w.trips.push(trip);
  w.counters.waveNo += 1;
  logEvent(w, "Рейс запланирован", trip.id, "info", { where: gate.id, why: `${stIds.length} СТ · окно ${clock(trip.window.from)}–${clock(trip.window.to)}` });
}

function createInboundTrip(w: TwinState, rng: Rng) {
  const vehicle = rng.pick(VEHICLES.filter((v) => v.pallets >= 8));
  const gate = planGate(w, "inbound");
  const trip = baseTrip(w, rng, nextId(w, "IN-77"), "in", vehicle, gate, w.simTime + rng.int(4, 12) * 60);
  trip.route = `${rng.pick(SUPPLIERS)} → ${w.layout.siteName}`;
  trip.pallets = rng.int(Math.ceil(vehicle.pallets / 2), vehicle.pallets);
  w.trips.push(trip);
  logEvent(w, "Поставка ожидается", trip.id, "info", { where: gate.id, why: `${trip.pallets} паллет · ${trip.route}` });
}

function baseTrip(_w: TwinState, rng: Rng, id: string, direction: Trip["direction"], vehicle: Trip["vehicle"], gate: Gate, arriveAt: number): Trip {
  return {
    id,
    direction,
    plate: plate(rng),
    carrier: rng.pick(CARRIERS),
    driver: rng.pick(DRIVERS),
    vehicle,
    route: "",
    gateId: gate.id,
    phase: "planned",
    pos: { ...SPAWN },
    heading: Math.PI / 2,
    stIds: [],
    pallets: 0,
    palletsDone: 0,
    unloadTasksCreated: 0,
    arriveAt,
    window: { from: arriveAt - 5 * 60, to: arriveAt + 20 * 60 },
    paperworkLeft: 0,
    queueSlot: -1,
    risk: "ok"
  };
}

export function clock(sec: number) {
  const m = Math.floor(sec / 60) % (24 * 60);
  return `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
}

export function spawnTrips(w: TwinState, rng: Rng) {
  const activeOut = w.trips.filter((t) => t.direction === "out" && t.phase !== "transit" && t.phase !== "done").length;
  if (w.simTime >= w.counters.nextOutboundAt && activeOut < MAX_ACTIVE_OUTBOUND) {
    createOutboundTrip(w, rng);
    w.counters.nextOutboundAt = w.simTime + rng.int(5, 9) * 60;
    w.entitiesVersion += 1;
  }
  if (w.simTime >= w.counters.nextInboundAt) {
    createInboundTrip(w, rng);
    w.counters.nextInboundAt = w.simTime + rng.int(25, 40) * 60;
    w.entitiesVersion += 1;
  }
}

function freeQueueSlot(w: TwinState) {
  const used = new Set(w.trips.filter((t) => t.phase === "queued" || (t.phase === "arriving" && t.queueSlot >= 0)).map((t) => t.queueSlot));
  let slot = 0;
  while (used.has(slot)) slot += 1;
  return slot;
}

function startApproach(w: TwinState, trip: Trip, gate: Gate) {
  gate.occupiedBy = trip.id;
  trip.queueSlot = -1;
  trip.phase = "arriving";
  trip.mover = makeMover(approachRoute(trip.pos, gate), TRUCK_SPEED);
  trip.waitReason = undefined;
  logEvent(w, "Назначены ворота", trip.id, "info", { where: gate.id, who: trip.driver });
}

function onPlannedTick(w: TwinState, trip: Trip) {
  if (w.simTime < trip.arriveAt) return;
  const gate = gateById(w, trip.gateId)!;
  w.gateLog.unshift({ at: w.simTime, dir: "in", tripId: trip.id, plate: trip.plate, carrier: trip.carrier, vehicle: trip.vehicle.name });
  w.entitiesVersion += 1;
  if (!gate.occupiedBy) {
    startApproach(w, trip, gate);
    return;
  }
  trip.queueSlot = freeQueueSlot(w);
  trip.phase = "arriving";
  trip.mover = makeMover([{ ...SPAWN }, queuePoint(trip.queueSlot)], TRUCK_SPEED);
  trip.waitReason = `Ворота ${gate.id} заняты рейсом ${gate.occupiedBy}`;
  logEvent(w, "Въезд на территорию · очередь", trip.id, "warn", { where: gate.id, why: trip.waitReason });
}

function onArrived(w: TwinState, trip: Trip) {
  const gate = gateById(w, trip.gateId)!;
  if (trip.queueSlot >= 0 && gate.occupiedBy !== trip.id) {
    trip.phase = "queued";
    trip.mover = undefined;
    return;
  }
  trip.phase = "reversing";
  trip.mover = makeMover(reverseRoute(gate, trip.vehicle.length), REVERSE_SPEED, true);
}

function onDocked(w: TwinState, trip: Trip) {
  trip.phase = "docked";
  trip.mover = undefined;
  trip.dockedAt = w.simTime;
  trip.onTime = w.simTime <= trip.window.to;
  logEvent(w, trip.direction === "out" ? "Постановка под погрузку" : "Постановка под выгрузку", trip.id, trip.onTime ? "info" : "warn", {
    where: trip.gateId,
    why: trip.onTime ? "в окне дока" : `опоздание к окну ${clock(trip.window.to)}`
  });
}

function dockedTick(w: TwinState, trip: Trip, dt: number) {
  const sts = trip.stIds.map((id) => w.sts[id]);
  const complete = trip.direction === "out" ? sts.every((s) => s.stage === "loaded") : trip.palletsDone >= trip.pallets;
  if (!complete) {
    const pending = sts.find((s) => s.stage !== "staged" && s.stage !== "loading" && s.stage !== "loaded");
    trip.waitReason = pending ? `Ждёт ${pending.id}: ${stageLabelShort(pending.stage)}` : undefined;
    return;
  }
  if (trip.paperworkLeft <= 0) trip.paperworkLeft = 90;
  trip.paperworkLeft -= dt;
  trip.waitReason = "Оформление документов";
  if (trip.paperworkLeft > 1) return;
  const gate = gateById(w, trip.gateId)!;
  trip.phase = "departing";
  trip.waitReason = undefined;
  trip.mover = makeMover(departRoute(gate, trip.vehicle.length), TRUCK_SPEED);
  for (const st of sts) {
    st.stage = "shipped";
    st.stageAt.shipped = w.simTime;
  }
  if (trip.direction === "out") w.counters.palletsShipped += trip.pallets;
  logEvent(w, trip.direction === "out" ? "Рейс отправлен" : "Машина выгружена", trip.id, "info", { where: gate.id, why: trip.route });
}

function stageLabelShort(stage: St["stage"]) {
  return { created: "ожидает отбора", picking: "в отборе", picked: "собрано", qc: "на контроле" }[stage as string] ?? stage;
}

function departingTick(w: TwinState, trip: Trip, arrived: boolean) {
  const gate = gateById(w, trip.gateId)!;
  if (gate.occupiedBy === trip.id && trip.mover && trip.mover.dist > trip.vehicle.length + 6) {
    gate.occupiedBy = undefined;
  }
  if (!arrived) return;
  trip.departedAt = w.simTime;
  trip.mover = undefined;
  w.gateLog.unshift({ at: w.simTime, dir: "out", tripId: trip.id, plate: trip.plate, carrier: trip.carrier, vehicle: trip.vehicle.name });
  trip.phase = trip.direction === "out" ? "transit" : "done";
  trip.deliverAt = w.simTime + (35 + (trip.stIds.length * 17) % 40) * 60;
  w.entitiesVersion += 1;
}

function riskOf(w: TwinState, trip: Trip): Trip["risk"] {
  if (trip.dockedAt !== undefined) return trip.onTime ? "ok" : "late";
  if (w.simTime > trip.window.to) return "late";
  if (trip.phase === "queued" || w.simTime > trip.window.from + 8 * 60) return "risk";
  return "ok";
}

export function stepTrips(w: TwinState, dt: number) {
  for (const trip of w.trips) {
    trip.risk = riskOf(w, trip);
    if (trip.phase === "planned") onPlannedTick(w, trip);
    else if (trip.phase === "queued") {
      const gate = gateById(w, trip.gateId)!;
      if (!gate.occupiedBy) startApproach(w, trip, gate);
    } else if (trip.phase === "docked") dockedTick(w, trip, dt);
    else if (trip.phase === "transit") {
      if (w.simTime >= (trip.deliverAt ?? 0)) {
        trip.phase = "done";
        for (const id of trip.stIds) {
          w.sts[id].stage = "delivered";
          w.sts[id].stageAt.delivered = w.simTime;
        }
        logEvent(w, "Доставлено в магазины", trip.id, "info", { why: trip.route });
      }
    }
    if (!trip.mover) continue;
    const arrived = advance(trip.mover, dt);
    const pose = sampleMover(trip.mover);
    trip.pos = pose.pos;
    trip.heading = pose.heading;
    if (trip.phase === "arriving" && arrived) onArrived(w, trip);
    else if (trip.phase === "reversing" && arrived) onDocked(w, trip);
    else if (trip.phase === "departing") departingTick(w, trip, arrived);
  }
  pruneTrips(w);
}

function pruneTrips(w: TwinState) {
  const keep = 14;
  const done = w.trips.filter((t) => t.phase === "done");
  if (done.length <= keep) return;
  const drop = new Set(done.slice(0, done.length - keep).map((t) => t.id));
  for (const t of w.trips) {
    if (!drop.has(t.id)) continue;
    for (const id of t.stIds) delete w.sts[id];
  }
  w.trips = w.trips.filter((t) => !drop.has(t.id));
  w.entitiesVersion += 1;
}
