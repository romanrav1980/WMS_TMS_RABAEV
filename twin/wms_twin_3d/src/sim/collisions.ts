import type { Collision, CollisionType, Severity, TwinState, Vec2 } from "../contracts/twin";
import { cellById, gateById, logEvent } from "./journal";
import { X0, Z_FRONT, aisleX, queuePoint } from "./layout";

type Finding = { key: string; type: CollisionType; severity: Severity; where: string; pos: Vec2; affected: string[]; rootCause: string; weight: number; bound?: boolean };

const ROOT_CAUSE: Record<CollisionType, string> = {
  PICK_FACE_EMPTY: "Ячейка отбора опустела раньше, чем ричтрак выполнил пополнение",
  AISLE_CONGESTION: "В одном проходе одновременно работают 3+ комплектовщика",
  REACH_QUEUE: "Очередь заданий пополнения/размещения выше пропускной способности ричтраков",
  DOCK_QUEUE: "Забронированные ворота заняты предыдущим рейсом",
  TRIP_LATE: "Рейс не поставлен под погрузку / не отгружен до конца окна дока",
  LOW_BATTERY: "Заряд техники ниже порога — техника уходит на зарядку",
  WAITING_ST: "Машина стоит у ворот, но СТ ещё не прошли отбор и контроль",
  OP_BLOCKED: "Складское задание заблокировано: причина из WMS"
};

export const COLLISION_LABEL: Record<CollisionType, string> = {
  PICK_FACE_EMPTY: "Пустая ячейка отбора",
  AISLE_CONGESTION: "Затор в проходе",
  REACH_QUEUE: "Очередь ричтраков",
  DOCK_QUEUE: "Очередь к воротам",
  TRIP_LATE: "Опоздание рейса",
  LOW_BATTERY: "Низкий заряд",
  WAITING_ST: "Машина ждёт СТ",
  OP_BLOCKED: "Задание заблокировано"
};

function findings(w: TwinState): Finding[] {
  const out: Finding[] = [];
  const byFace = new Map<string, string[]>();
  for (const r of w.resources) {
    if (r.kind === "picker" && r.status === "waiting" && r.waitReason) {
      const cellId = r.waitReason.split(" ").pop()!;
      byFace.set(cellId, [...(byFace.get(cellId) ?? []), r.id]);
    }
    if (r.kind !== "picker" && r.battery < 15 && r.status !== "charging") {
      out.push({ key: `LB:${r.id}`, type: "LOW_BATTERY", severity: "warning", where: r.id, pos: r.pos, affected: [r.id], rootCause: ROOT_CAUSE.LOW_BATTERY, weight: 0 });
    }
  }
  for (const [cellId, pickers] of byFace) {
    const cell = cellById(w, cellId);
    if (!cell) continue;
    const since = Math.min(...pickers.map((id) => w.resources.find((r) => r.id === id)?.waitSince ?? w.simTime));
    out.push({ key: `PFE:${cellId}`, type: "PICK_FACE_EMPTY", severity: w.simTime - since > 180 ? "critical" : "warning", where: cellId, pos: { x: cell.x, z: cell.z }, affected: pickers, rootCause: ROOT_CAUSE.PICK_FACE_EMPTY, weight: pickers.length });
  }
  const perAisle = new Map<number, string[]>();
  for (const r of w.resources) {
    if (r.kind !== "picker" || r.pos.z > Z_FRONT - 0.5 || r.pos.x < X0 - 2) continue;
    const aisle = Math.round((r.pos.x - X0) / 4.4);
    perAisle.set(aisle, [...(perAisle.get(aisle) ?? []), r.id]);
  }
  for (const [aisle, ids] of perAisle) {
    if (ids.length < 3) continue;
    out.push({ key: `AC:${aisle}`, type: "AISLE_CONGESTION", severity: "warning", where: `Проход A${String(aisle + 1).padStart(2, "0")}`, pos: { x: aisleX(aisle), z: Z_FRONT - 12 }, affected: ids, rootCause: ROOT_CAUSE.AISLE_CONGESTION, weight: 0.3 * ids.length });
  }
  const openReach = w.tasks.filter((t) => (t.kind === "REPL" || t.kind === "PUTAWAY") && t.status === "created").length;
  if (openReach >= 5) {
    out.push({ key: "RQ", type: "REACH_QUEUE", severity: openReach >= 9 ? "critical" : "warning", where: `${openReach} заданий в очереди`, pos: { x: w.layout.width - 6, z: Z_FRONT + 1.5 }, affected: w.resources.filter((r) => r.kind === "reachtruck").map((r) => r.id), rootCause: ROOT_CAUSE.REACH_QUEUE, weight: 0 });
  }
  for (const trip of w.trips) {
    if (trip.phase === "queued") {
      out.push({ key: `DQ:${trip.id}`, type: "DOCK_QUEUE", severity: "warning", where: `${trip.id} → ${trip.gateId}`, pos: queuePoint(trip.queueSlot), affected: [trip.id], rootCause: ROOT_CAUSE.DOCK_QUEUE, weight: 1 });
    }
    const onMap = trip.phase === "arriving" || trip.phase === "queued" || trip.phase === "reversing";
    if ((trip.phase === "planned" || onMap) && w.simTime > trip.window.to) {
      const gate = gateById(w, trip.gateId);
      // Рейс без ворот: метка на площадке перед фасадом, место — по хэшу id, чтобы метки не накладывались.
      const spread = [...trip.id].reduce((h, ch) => (h * 31 + ch.charCodeAt(0)) % 997, 7) / 997;
      const atGate = gate ? { x: gate.x, z: w.layout.depth + 6 } : { x: w.layout.width * (0.12 + 0.76 * spread), z: w.layout.depth + 10 + (spread * 7) % 8 };
      out.push({ key: `TL:${trip.id}`, type: "TRIP_LATE", severity: "critical", where: `${trip.id} · окно до ${hhmm(trip.window.to)}`, pos: onMap ? trip.pos : atGate, affected: [trip.id, ...trip.stIds], rootCause: ROOT_CAUSE.TRIP_LATE, weight: 0 });
    }
    if (trip.phase === "docked" && trip.waitReason?.startsWith("Ждёт")) {
      const gate = gateById(w, trip.gateId);
      out.push({ key: `WS:${trip.id}`, type: "WAITING_ST", severity: w.simTime - (trip.dockedAt ?? w.simTime) > 900 ? "critical" : "warning", where: `${trip.id} у ${trip.gateId}`, pos: { x: gate?.x ?? 0, z: w.layout.depth + 4 }, affected: [trip.id], rootCause: `${ROOT_CAUSE.WAITING_ST}. ${trip.waitReason}`, weight: 1 });
    }
  }
  if (w.mode === "live") out.push(...blockedOperations(w));
  return out;
}

// Live: заблокированные складские операции с причиной из WMS (§15). Позиция — только привязанная ячейка.
function blockedOperations(w: TwinState): Finding[] {
  const out: Finding[] = [];
  for (const op of w.operations) {
    if (op.phase !== "BLOCKED" && op.phase !== "FAILED") continue;
    const cellId = [op.to, op.from].find((l) => l?.bound)?.cell ?? op.lines?.find((l) => l.bound)?.cell;
    const cell = cellById(w, cellId);
    out.push({
      key: `OB:${op.key}`,
      type: "OP_BLOCKED",
      severity: op.phase === "FAILED" ? "critical" : "warning",
      where: `${op.key} · ${op.source.rawStatus}`,
      pos: cell ? { x: cell.x, z: cell.z } : { x: w.layout.width / 2, z: w.layout.depth / 2 },
      affected: [op.key],
      rootCause: op.blockedReason ?? op.lastError ?? `Исходный статус ${op.source.rawStatus}`,
      weight: 0,
      bound: !!cell
    });
  }
  return out;
}

function hhmm(sec: number) {
  const m = Math.floor(sec / 60);
  return `${String(Math.floor(m / 60) % 24).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
}

export function detectCollisions(w: TwinState, dt: number) {
  const current = new Map(findings(w).map((f) => [f.key, f]));
  for (const c of w.collisions) {
    if (!c.active) continue;
    const f = current.get(c.key);
    if (!f) {
      c.active = false;
      c.endedAt = w.simTime;
      continue;
    }
    c.severity = f.severity;
    c.affected = f.affected;
    c.pos = f.pos;
    c.where = f.where;
    c.rootCause = f.rootCause;
    c.bound = f.bound;
    c.lostMinutes += (dt / 60) * f.weight;
    current.delete(c.key);
  }
  for (const f of current.values()) {
    const c: Collision = { key: f.key, type: f.type, severity: f.severity, startedAt: w.simTime, active: true, where: f.where, pos: f.pos, affected: f.affected, rootCause: f.rootCause, lostMinutes: 0, bound: f.bound };
    w.collisions.unshift(c);
    logEvent(w, COLLISION_LABEL[f.type], f.where, f.severity === "critical" ? "crit" : "warn", { why: f.rootCause, who: f.affected.join(", ") });
  }
  const ended = w.collisions.filter((c) => !c.active);
  if (ended.length > 40) {
    const drop = new Set(ended.slice(40).map((c) => c.key + c.startedAt));
    w.collisions = w.collisions.filter((c) => c.active || !drop.has(c.key + c.startedAt));
  }
}
