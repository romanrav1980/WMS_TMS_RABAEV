import type { Aisle, Cell, Gate, Layout, St, StStage, Trip, TwinState } from "../contracts/twin";
import { LEVEL_H } from "../sim/layout";

// Сопоставление ответов API ТМС с TwinState. Только чтение, без сетевых вызовов — проверяется на сохранённых ответах.
// Форматы сверены с живым API 14.10.2026:
//   GET /api/admin/warehouse-topologies/{id}/map  (warehouse_topology_service.get_topology_map)
//   GET /api/admin/transport/tasks?include_readiness=true  (transport_service.list_tasks)
//   GET /api/admin/transport/tasks/{id}/sts  (transport_service.get_task_sts)
//   GET /api/admin/transport/available-sts  (transport_service.list_available_sts)

// ── Форматы ответов ТМС (только используемые поля) ───────────────────

export type TmsTopologySummary = {
  topology_id: number;
  ware_id: number;
  topology_code: string;
  topology_name: string | null;
  status: string;
  cell_count?: number | null;
  aisle_count?: number | null;
};

export type TmsTopologyMap = {
  topology: { topology_id: number; ware_id: number; ware_name: string | null; topology_code: string; topology_name: string | null; status: string };
  aisles: { aisle_code: string; x1: number; y1: number; x2: number; y2: number; active: number }[];
  gates: { gate_code: string; gate_kind: string; x: number; y: number; active: number }[];
  cells: {
    cell_code: string;
    legacy_cell_code?: string | null;
    aisle_code: string | null;
    bay_no: number | null;
    level_no: number | null;
    side_code: string | null;
    cell_kind: string | null;
    x: number;
    y: number;
    z: number | null;
    width: number | null;
    depth: number | null;
    active: number;
  }[];
};

export type TmsTask = {
  ID: number;
  TRANSPORT: string | null;
  TRANSTYPE: string | null;
  CONDITION: string | null;
  SHIPMENT_DATE: string | null;
  SHIPMENT_TIME: string | null;
  VODITEL_NAME: string | null;
  TK_NAME: string | null;
  IS_OWN_DRIVER: number | null;
  DOCK: string | null;
  REGIONS: string | null;
  DELETED: number | null;
  PALLET_COUNT: number | null;
  ST_COUNT: number | null;
  READY_PERC?: number | null;
};

export type TmsSt = {
  ST_NUMBER: string;
  ADDR: string | null;
  REGION: string | null;
  PALLETS_COUNT: number | null;
  WEIGHT_KG: number | null;
  WARE_ID: number | null;
  VERIFY_PERC: number | null;
  TRANSTASK_ID?: number | null;
};

export type TmsSnapshot = {
  topology: TmsTopologyMap;
  tasks: TmsTask[];
  taskSts: Record<number, TmsSt[]>;
  freeSts: TmsSt[];
  now: Date;
};

// ── Топология → layout, ячейки, ворота ───────────────────────────────

// BOTH — ворота и приёмки, и отгрузки; в модели двойника показываются как отгрузочные (рейсы), без замечания.
const GATE_KIND: Record<string, Gate["kind"]> = { SHIPPING: "outbound", OUTBOUND: "outbound", BOTH: "outbound", RECEIVING: "inbound", INBOUND: "inbound" };

// Топология склада — по тому же правилу, что WMS (master_data/topology_coverage.py):
// последняя опубликованная (max TOPOLOGY_ID при STATUS='PUBLISHED') для WARE_ID.
// Явный ?topology= допускается для просмотра, но непубликованная топология помечается замечанием.
export function publishedTopologyOf(list: TmsTopologySummary[], wareId: number): TmsTopologySummary | undefined {
  return list.filter((t) => t.ware_id === wareId && t.status === "PUBLISHED").sort((a, b) => b.topology_id - a.topology_id)[0];
}

export function pickTopology(list: TmsTopologySummary[], opts: { topology?: number; ware?: number } = {}): TmsTopologySummary | undefined {
  if (opts.topology) return list.find((t) => t.topology_id === opts.topology);
  if (opts.ware !== undefined) return publishedTopologyOf(list, opts.ware);
  return undefined;
}

// Склад по умолчанию: тот, где больше всего открытых операций и есть опубликованная топология.
export function pickWarehouse(list: TmsTopologySummary[], openOpsByWare: Map<number, number>): number | undefined {
  const published = new Set(list.filter((t) => t.status === "PUBLISHED").map((t) => t.ware_id));
  return [...openOpsByWare.entries()].filter(([w]) => published.has(w)).sort((a, b) => b[1] - a[1] || a[0] - b[0])[0]?.[0];
}

export function layoutFromTopology(map: TmsTopologyMap) {
  const notes: string[] = [];
  if (map.topology.status !== "PUBLISHED") notes.push(`Топология ${map.topology.topology_code} не опубликована (${map.topology.status}); WMS использует только опубликованную.`);
  const withoutLegacy = map.cells.filter((c) => c.active === 1 && !c.legacy_cell_code).length;
  if (withoutLegacy) notes.push(`${withoutLegacy} ячеек топологии без LEGACY_CELL_CODE — не связаны со справочником ячеек WMS.`);
  const cellsRaw = map.cells.filter((c) => c.active === 1);
  const gatesRaw = map.gates.filter((g) => g.active === 1);
  const aisleCodes = [...new Set(cellsRaw.map((c) => c.aisle_code ?? ""))].sort();
  const aisleIndex = new Map(aisleCodes.map((code, i) => [code, i]));
  const aisleX = new Map(map.aisles.map((a) => [a.aisle_code, a.x1]));
  const cells: Cell[] = cellsRaw.map((c, index) => {
    const level = c.level_no ?? 1;
    const side: -1 | 1 = (c.side_code ?? "").toUpperCase().startsWith("R") ? 1 : -1;
    // Ключ ячейки двойника — код справочника WMS (RRL_CELLS.CELL = LEGACY_CELL_CODE), по нему ссылаются задания.
    return {
      id: c.legacy_cell_code || c.cell_code,
      index,
      aisle: aisleIndex.get(c.aisle_code ?? "") ?? 0,
      slot: c.bay_no ?? 0,
      level,
      side,
      x: c.x,
      y: c.z ?? (level - 1) * LEVEL_H,
      z: c.y,
      role: (c.cell_kind ?? "").toUpperCase() === "PICK_FACE" ? "pick" : "reserve",
      qty: 0,
      capacity: 1,
      sizeX: c.width ?? undefined,
      sizeZ: c.depth ?? undefined,
      stockKnown: false
    };
  });
  const cellIndex: Record<string, number> = {};
  for (const c of cells) cellIndex[c.id] = c.index;
  const gateYs = gatesRaw.map((g) => g.y);
  const maxCellZ = cells.reduce((m, c) => Math.max(m, c.z), 0);
  const maxX = Math.max(...cells.map((c) => c.x), ...gatesRaw.map((g) => g.x), 10);
  const wallZ = gateYs.length ? Math.max(...gateYs) : maxCellZ + 14;
  if (gateYs.length && new Set(gateYs).size > 1) notes.push("Ворота топологии стоят на разных фасадах; двойник показывает их на одном фасаде (z = max y).");
  const gates: Gate[] = gatesRaw
    .sort((a, b) => a.x - b.x)
    .map((g, index) => ({ id: g.gate_code, index, x: g.x, kind: GATE_KIND[(g.gate_kind ?? "").toUpperCase()] ?? "outbound", received: 0 }));
  const unknownKinds = gatesRaw.filter((g) => !GATE_KIND[(g.gate_kind ?? "").toUpperCase()]).length;
  if (unknownKinds) notes.push(`Неизвестный GATE_KIND у ${unknownKinds} ворот — показаны как отгрузочные.`);
  if (!gatesRaw.length) notes.push("В топологии нет ворот — транспортный фасад не привязан.");
  if (!map.aisles.length) notes.push("В топологии нет проходов — маршруты по проходам не строятся.");
  notes.push("Остатки ячеек в топологии отсутствуют — ячейки показаны без заполненности.");
  const aisles: Aisle[] = aisleCodes.map((code, index) => ({ id: code, index, x: aisleX.get(code) ?? 0 }));
  const t = map.topology;
  const layout: Layout = {
    siteId: `WARE-${t.ware_id}`,
    siteName: t.topology_name || t.topology_code,
    address: `Топология ${t.topology_code} · ${t.status} · склад ${t.ware_name ?? t.ware_id}`,
    width: maxX + 8,
    depth: wallZ,
    stagingZ: Math.max(maxCellZ + 4, wallZ - 7),
    aisles,
    topologyId: t.topology_id,
    topologyCode: t.topology_code,
    wareId: t.ware_id
  };
  return { layout, cells, cellIndex, gates, notes };
}

// ── Рейсы и СТ ───────────────────────────────────────────────────────

// Секунды от полуночи текущих суток (та же шкала, что simTime в live-режиме). Даты другого дня дают <0 или >86400.
export function secondsFromToday(iso: string | null | undefined, now: Date): number | undefined {
  if (!iso) return undefined;
  const t = new Date(iso);
  if (Number.isNaN(t.getTime())) return undefined;
  const midnight = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  return Math.round((t.getTime() - midnight.getTime()) / 1000);
}

// CONDITION легаси-рейса: на 14.10.2026 в данных встречаются «Спланирован» и «Отгружен».
// Состояний двора (въезд, постановка, погрузка) RRL_TRANSPORT_TASK не хранит, поэтому машин на сцене в live нет.
export function phaseFromCondition(condition: string | null): { phase: Trip["phase"]; known: boolean } {
  const c = (condition ?? "").trim().toLowerCase();
  if (c.startsWith("отгруж")) return { phase: "done", known: true };
  if (c.startsWith("спланир") || c.startsWith("сформир")) return { phase: "planned", known: true };
  return { phase: "planned", known: false };
}

// Стадия СТ по VERIFY_PERC (процент проверенных паллет) и состоянию рейса — приближение, пока нет событий отбора.
export function stageFromVerify(verifyPerc: number | null, tripShipped: boolean): StStage {
  if (tripShipped) return "shipped";
  const v = verifyPerc ?? 0;
  if (v >= 100) return "staged";
  if (v > 0) return "qc";
  return "created";
}

const WINDOW_SEC = 60 * 60;

function riskOf(phase: Trip["phase"], from: number | undefined, readyPerc: number | undefined, nowSec: number): Trip["risk"] {
  if (phase !== "planned" || from === undefined) return "ok";
  if (nowSec > from + WINDOW_SEC) return "late";
  if (nowSec > from - 30 * 60 && (readyPerc ?? 0) < 100) return "risk";
  return "ok";
}

// /tasks/{id}/sts группирует по СТ и точке маршрута (ORD) — одна СТ может прийти несколькими строками.
// Сворачиваем по ST_NUMBER: паллеты и вес суммируются, VERIFY_PERC взвешивается по паллетам.
export function mergeStRows(rows: TmsSt[]): TmsSt[] {
  const byId = new Map<string, TmsSt>();
  for (const row of rows) {
    const prev = byId.get(row.ST_NUMBER);
    if (!prev) {
      byId.set(row.ST_NUMBER, { ...row });
      continue;
    }
    const pa = prev.PALLETS_COUNT ?? 0;
    const pb = row.PALLETS_COUNT ?? 0;
    const total = pa + pb;
    prev.VERIFY_PERC = total ? Math.round(((prev.VERIFY_PERC ?? 0) * pa + (row.VERIFY_PERC ?? 0) * pb) / total) : prev.VERIFY_PERC;
    prev.PALLETS_COUNT = total;
    prev.WEIGHT_KG = (prev.WEIGHT_KG ?? 0) + (row.WEIGHT_KG ?? 0);
  }
  return [...byId.values()];
}

function stFromTms(row: TmsSt, tripId: string, gateId: string, shipped: boolean, nowSec: number): St {
  const stage = stageFromVerify(row.VERIFY_PERC, shipped);
  return {
    id: row.ST_NUMBER,
    store: row.ADDR || row.REGION || "—",
    tripId,
    gateId,
    waveId: "—",
    stage,
    stageAt: { [stage]: nowSec },
    lines: [],
    pallets: row.PALLETS_COUNT ?? 0,
    palletsLoaded: shipped ? row.PALLETS_COUNT ?? 0 : 0,
    loadTasksCreated: 0,
    qcLeft: 0,
    wareId: row.WARE_ID ?? undefined,
    verifyPerc: row.VERIFY_PERC ?? undefined,
    weightKg: row.WEIGHT_KG ?? undefined
  };
}

export function tripsFromTasks(snapshot: TmsSnapshot, gates: Gate[], topologyWareId?: number) {
  const notes: string[] = [];
  const nowSec = secondsFromToday(snapshot.now.toISOString(), snapshot.now) ?? 0;
  const gateCodes = new Map(gates.map((g) => [g.id.toUpperCase(), g.id]));
  const trips: Trip[] = [];
  const sts: Record<string, St> = {};
  let unknownCondition = 0;
  let dockMismatch = 0;
  for (const task of snapshot.tasks) {
    if (task.DELETED) continue;
    const { phase, known } = phaseFromCondition(task.CONDITION);
    if (!known) unknownCondition += 1;
    const gateId = task.DOCK ? gateCodes.get(task.DOCK.trim().toUpperCase()) ?? "" : "";
    if (task.DOCK && !gateId) dockMismatch += 1;
    const from = secondsFromToday(task.SHIPMENT_TIME ?? task.SHIPMENT_DATE, snapshot.now);
    const readyPerc = task.READY_PERC ?? undefined;
    const id = String(task.ID);
    const shipped = phase === "done";
    const rows = mergeStRows(snapshot.taskSts[task.ID] ?? []);
    for (const row of rows) sts[row.ST_NUMBER] = stFromTms(row, id, gateId, shipped, nowSec);
    const pallets = task.PALLET_COUNT ?? 0;
    trips.push({
      id,
      direction: "out",
      plate: task.TRANSPORT ?? "—",
      carrier: task.TK_NAME ?? (task.IS_OWN_DRIVER ? "Собственный парк" : "—"),
      driver: task.VODITEL_NAME ?? "—",
      vehicle: { name: task.TRANSTYPE ? `Тип ТС ${task.TRANSTYPE}` : "—", length: 8.6, pallets: Math.max(pallets, 1), reefer: false },
      route: (task.REGIONS ?? "").replace(/[\s;]+/g, " ").trim() || "—",
      gateId,
      phase,
      pos: { x: 0, z: 0 },
      heading: 0,
      stIds: rows.map((r) => r.ST_NUMBER),
      pallets,
      palletsDone: shipped ? pallets : 0,
      unloadTasksCreated: 0,
      arriveAt: from ?? nowSec,
      window: { from: from ?? nowSec, to: (from ?? nowSec) + WINDOW_SEC },
      paperworkLeft: 0,
      queueSlot: -1,
      risk: riskOf(phase, from, readyPerc, nowSec),
      conditionRaw: task.CONDITION ?? "",
      readyPerc,
      shipmentDate: task.SHIPMENT_TIME ?? task.SHIPMENT_DATE ?? undefined,
      stCount: task.ST_COUNT ?? rows.length,
      waitReason: phase === "planned" && readyPerc !== undefined && readyPerc < 100 ? `Готовность СТ ${readyPerc}%` : undefined
    });
  }
  for (const row of mergeStRows(snapshot.freeSts)) {
    if (!sts[row.ST_NUMBER]) sts[row.ST_NUMBER] = stFromTms(row, "", "", false, nowSec);
  }
  if (unknownCondition) notes.push(`Нераспознанный CONDITION у ${unknownCondition} рейсов — показаны как «Спланирован».`);
  if (dockMismatch) notes.push(`DOCK не совпадает с воротами топологии у ${dockMismatch} рейсов — ворота не назначены.`);
  if (topologyWareId !== undefined) {
    const foreign = Object.values(sts).filter((s) => s.wareId !== undefined && s.wareId !== topologyWareId).length;
    if (foreign) notes.push(`${foreign} СТ относятся к другим складам (WARE_ID ≠ ${topologyWareId}); у рейса склад не указан.`);
  }
  notes.push("Окно дока условное: SHIPMENT_TIME … +60 мин; стадия СТ — по VERIFY_PERC.");
  return { trips, sts, notes };
}

// ── Применение снимка к состоянию двойника (на месте, с сигналами версий) ──

export function applyTmsSnapshot(world: TwinState, snapshot: TmsSnapshot, layoutChanged: boolean): void {
  if (layoutChanged) {
    const topo = layoutFromTopology(snapshot.topology);
    world.layout = topo.layout;
    world.cells = topo.cells;
    world.cellIndex = topo.cellIndex;
    world.gates = topo.gates;
    world.dataNotes = topo.notes;
    world.layoutVersion += 1;
    world.stockVersion += 1;
  }
  const { trips, sts, notes } = tripsFromTasks(snapshot, world.gates, world.layout.wareId);
  world.trips = trips;
  world.sts = sts;
  world.resources = [];
  world.tasks = [];
  world.dataNotes = [...world.dataNotes.filter((n) => n.startsWith("Ворота") || n.startsWith("Неизвестный GATE") || n.startsWith("Остатки")), ...notes];
  world.entitiesVersion += 1;
  world.version += 1;
}
