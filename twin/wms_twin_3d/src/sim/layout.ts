import type { Cell, Gate, Mover, Vec2 } from "../contracts/twin";

// Геометрия площадки в метрах. Ось x — вдоль фасада, ось z — от задней стены к воротам и дороге.
export const AISLES = 12;
export const SLOTS_PER_SIDE = 24;
export const LEVELS = 5;
export const AISLE_PITCH = 4.4;
export const AISLE_HALF = 1.0;
export const RACK_DEPTH = 1.1;
export const SLOT_LEN = 1.35;
export const LEVEL_H = 1.45;
export const X0 = 7;
export const Z_RACK_START = 6;
export const Z_RACK_END = Z_RACK_START + SLOTS_PER_SIDE * SLOT_LEN;
export const Z_FRONT = Z_RACK_END + 1.8;
export const Z_STAGING = 47;
export const WALL_Z = 54;
export const WIDTH = X0 * 2 + (AISLES - 1) * AISLE_PITCH;
export const ROAD_Z = 86;
export const EXIT_Z = ROAD_Z + 3.6;
export const SHOULDER_Z = 80;
export const SPAWN: Vec2 = { x: -110, z: ROAD_Z };
export const EXIT: Vec2 = { x: -110, z: EXIT_Z };
export const GATE_COUNT = 8;
export const GATE_X0 = 8.5;
export const GATE_PITCH = 6.5;
export const CHARGER: Vec2 = { x: WIDTH - 3, z: Z_FRONT + 1.5 };

export const aisleX = (index: number) => X0 + index * AISLE_PITCH;

export const gateX = (index: number) => GATE_X0 + index * GATE_PITCH;

export function rackX(aisle: number, side: -1 | 1) {
  return aisleX(aisle) + side * (AISLE_HALF + RACK_DEPTH / 2);
}

export function slotZ(zIndex: number) {
  return Z_RACK_START + (zIndex + 0.5) * SLOT_LEN;
}

export function cellId(aisle: number, slot: number, level: number) {
  const a = String(aisle + 1).padStart(2, "0");
  const s = String(slot).padStart(3, "0");
  return `A${a}-S${s}-L${level}`;
}

// Точка, где оператор стоит у ячейки: середина прохода напротив слота.
export function servicePoint(cell: Cell): Vec2 {
  return { x: aisleX(cell.aisle) + cell.side * 0.45, z: cell.z };
}

export function stagingPoint(gate: Gate, offset = 0): Vec2 {
  return { x: gate.x + offset, z: Z_STAGING };
}

export function receivingPoint(gate: Gate): Vec2 {
  return { x: gate.x - 1.6, z: Z_STAGING + 2.4 };
}

export function trailerPoint(gate: Gate): Vec2 {
  return { x: gate.x, z: WALL_Z + 1.4 };
}

const inRacks = (p: Vec2) => p.z < Z_FRONT - 0.3 && p.x > X0 - 2.5 && p.x < WIDTH - X0 + 2.5;

// Маршрут по полу склада: из прохода — в поперечный проезд, затем в нужный проход.
export function floorRoute(from: Vec2, to: Vec2): Vec2[] {
  if (inRacks(from) && inRacks(to) && Math.abs(from.x - to.x) < 1.2) return [from, to];
  const pts: Vec2[] = [from];
  if (inRacks(from)) pts.push({ x: from.x, z: Z_FRONT });
  if (inRacks(to)) pts.push({ x: to.x, z: Z_FRONT });
  pts.push(to);
  return dedupe(pts);
}

function dedupe(pts: Vec2[]): Vec2[] {
  return pts.filter((p, i) => i === 0 || Math.hypot(p.x - pts[i - 1].x, p.z - pts[i - 1].z) > 0.05);
}

export function pathLength(path: Vec2[]): number {
  let len = 0;
  for (let i = 1; i < path.length; i += 1) len += Math.hypot(path[i].x - path[i - 1].x, path[i].z - path[i - 1].z);
  return len;
}

export function makeMover(path: Vec2[], speed: number, backwards = false): Mover {
  return { path, dist: 0, len: pathLength(path), speed, backwards };
}

// Положение и курс на пути. Курс — угол поворота модели, у которой «перёд» смотрит в +z.
export function sampleMover(m: Mover): { pos: Vec2; heading: number } {
  const { path } = m;
  if (path.length === 1) return { pos: { ...path[0] }, heading: 0 };
  let left = Math.min(m.dist, m.len);
  for (let i = 1; i < path.length; i += 1) {
    const a = path[i - 1];
    const b = path[i];
    const seg = Math.hypot(b.x - a.x, b.z - a.z);
    if (left <= seg || i === path.length - 1) {
      const k = seg > 0 ? Math.min(left / seg, 1) : 1;
      const heading = Math.atan2(b.x - a.x, b.z - a.z) + (m.backwards ? Math.PI : 0);
      return { pos: { x: a.x + (b.x - a.x) * k, z: a.z + (b.z - a.z) * k }, heading };
    }
    left -= seg;
  }
  return { pos: { ...path[path.length - 1] }, heading: 0 };
}

// Продвигает движение; возвращает true, когда цель достигнута.
export function advance(m: Mover, dt: number): boolean {
  m.dist = Math.min(m.len, m.dist + m.speed * dt);
  return m.dist >= m.len - 1e-6;
}

// ── Маршруты грузовиков ─────────────────────────────────────────────

export function dockPoint(gate: Gate, length: number): Vec2 {
  return { x: gate.x, z: WALL_Z + length / 2 + 0.35 };
}

export function queuePoint(slot: number): Vec2 {
  return { x: -22 - slot * 17, z: SHOULDER_Z };
}

export function approachRoute(from: Vec2, gate: Gate): Vec2[] {
  const pts = [from];
  if (Math.abs(from.z - ROAD_Z) > 0.5) pts.push({ x: from.x + 10, z: ROAD_Z });
  pts.push({ x: gate.x + 20, z: ROAD_Z });
  return pts;
}

export function reverseRoute(gate: Gate, length: number): Vec2[] {
  return [
    { x: gate.x + 20, z: ROAD_Z },
    { x: gate.x + 7, z: ROAD_Z - 7 },
    { x: gate.x, z: WALL_Z + length + 9 },
    dockPoint(gate, length)
  ];
}

export function departRoute(gate: Gate, length: number): Vec2[] {
  return [
    dockPoint(gate, length),
    { x: gate.x, z: WALL_Z + length + 7 },
    { x: gate.x - 9, z: EXIT_Z },
    EXIT
  ];
}
