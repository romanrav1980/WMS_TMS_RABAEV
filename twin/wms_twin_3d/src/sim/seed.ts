import type { Cell, Gate, Resource, ResourceKind, TwinState, Vec2 } from "../contracts/twin";
import { PICKER_NAMES, SKUS } from "./catalog";
import {
  AISLES,
  GATE_COUNT,
  LEVELS,
  LEVEL_H,
  SLOTS_PER_SIDE,
  WALL_Z,
  WIDTH,
  Z_FRONT,
  Z_STAGING,
  aisleX,
  cellId,
  gateX,
  rackX,
  slotZ
} from "./layout";
import type { Rng } from "./rng";

export const SHIFT_START = 8 * 3600;
const PICK_CAPACITY = 32;

function buildCells(rng: Rng): Cell[] {
  const cells: Cell[] = [];
  for (let aisle = 0; aisle < AISLES; aisle += 1) {
    for (let zi = 0; zi < SLOTS_PER_SIDE; zi += 1) {
      for (const side of [-1, 1] as const) {
        const slot = zi * 2 + (side === -1 ? 1 : 2);
        const sku = SKUS[(aisle * 7 + zi * 3 + (side === 1 ? 1 : 0)) % SKUS.length].code;
        for (let level = 1; level <= LEVELS; level += 1) {
          const pick = level === 1;
          const occupied = pick || rng.next() < 0.62;
          cells.push({
            id: cellId(aisle, slot, level),
            index: cells.length,
            aisle,
            slot,
            level,
            side,
            x: rackX(aisle, side),
            y: (level - 1) * LEVEL_H,
            z: slotZ(zi),
            role: pick ? "pick" : "reserve",
            sku: occupied ? sku : undefined,
            qty: pick ? rng.int(12, PICK_CAPACITY) : occupied ? PICK_CAPACITY : 0,
            capacity: PICK_CAPACITY
          });
        }
      }
    }
  }
  return cells;
}

function buildGates(): Gate[] {
  return Array.from({ length: GATE_COUNT }, (_, index) => ({
    id: `G${String(index + 1).padStart(2, "0")}`,
    index,
    x: gateX(index),
    kind: index >= GATE_COUNT - 2 ? "inbound" : "outbound",
    received: 0
  }));
}

function resource(kind: ResourceKind, id: string, name: string, park: Vec2, rng: Rng): Resource {
  return {
    id,
    kind,
    name,
    pos: { ...park },
    heading: Math.PI,
    leg: "none",
    status: "idle",
    workLeft: 0,
    fork: 0,
    carrying: false,
    battery: kind === "picker" ? 100 : rng.int(55, 98),
    done: 0,
    lineIdx: 0,
    park
  };
}

function buildResources(rng: Rng): Resource[] {
  const list: Resource[] = [];
  PICKER_NAMES.forEach((name, i) => {
    list.push(resource("picker", `P${String(i + 1).padStart(2, "0")}`, name, { x: aisleX(i + 2), z: Z_FRONT + 2.2 }, rng));
  });
  for (let i = 0; i < 4; i += 1) {
    list.push(resource("reachtruck", `RT${String(i + 1).padStart(2, "0")}`, `Ричтрак ${i + 1}`, { x: WIDTH - 11 + i * 2.2, z: Z_FRONT + 1.6 }, rng));
  }
  for (let i = 0; i < 3; i += 1) {
    list.push(resource("forklift", `FL${String(i + 1).padStart(2, "0")}`, `Погрузчик ${i + 1}`, { x: gateX(i * 3) + 3, z: Z_STAGING - 2.6 }, rng));
  }
  return list;
}

export function createWorld(seed: number, rng: Rng): TwinState {
  const cells = buildCells(rng);
  const cellIndex: Record<string, number> = {};
  for (const c of cells) cellIndex[c.id] = c.index;
  return {
    mode: "sim",
    seed,
    simTime: SHIFT_START + 5 * 60,
    shiftStart: SHIFT_START,
    version: 0,
    layoutVersion: 0,
    entitiesVersion: 0,
    stockVersion: 0,
    layout: {
      siteId: "WH-01",
      siteName: "РЦ «Северный»",
      address: "Демо-площадка · мок-данные по шагам процессов WMS/TMS",
      width: WIDTH,
      depth: WALL_Z,
      stagingZ: Z_STAGING,
      aisles: Array.from({ length: AISLES }, (_, i) => ({ id: `A${String(i + 1).padStart(2, "0")}`, index: i, x: aisleX(i) }))
    },
    cells,
    cellIndex,
    gates: buildGates(),
    resources: buildResources(rng),
    tasks: [],
    sts: {},
    trips: [],
    collisions: [],
    events: [],
    gateLog: [],
    dataNotes: [],
    operations: [],
    executors: [],
    connection: { state: "SIM" },
    opsStats: { inSnapshot: 0, otherWarehouses: 0, unbound: 0, limitReached: false },
    counters: {
      seq: 100,
      eventSeq: 1,
      linesPicked: 0,
      pickTimes: [],
      palletsReceived: 0,
      palletsShipped: 0,
      replDone: 0,
      replOnTime: 0,
      nextOutboundAt: 0,
      nextInboundAt: 0,
      waveNo: 1
    }
  };
}
