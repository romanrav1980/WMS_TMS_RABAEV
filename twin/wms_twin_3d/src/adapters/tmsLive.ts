import type { TwinOperation, TwinState } from "../contracts/twin";
import { detectCollisions } from "../sim/collisions";
import { createRng } from "../sim/rng";
import { createWorld } from "../sim/seed";
import type { TwinSource } from "./source";
import {
  type TmsSnapshot,
  type TmsSt,
  type TmsTask,
  type TmsTopologyMap,
  type TmsTopologySummary,
  applyTmsSnapshot,
  layoutFromTopology,
  pickTopology,
  pickWarehouse
} from "./tmsMapping";
import {
  type WmsCaseTask,
  type WmsEquipment,
  type WmsResource,
  type WmsSession,
  type WmsWarehouseTask,
  isOpenPhase,
  operationFromCaseTask,
  operationsSnapshot
} from "./tmsOperations";

// Live-адаптер к API WMS/TMS: только GET-запросы, двойник ничего не пишет.
// Авторизация — HTTP Basic, как в admin frontend: VITE_ADMIN_BASIC_AUTH в twin/wms_twin_3d/.env (см. .env.example).
// База API — VITE_API_BASE; по умолчанию относительный /api через прокси vite (порт 8088).
const API_BASE = import.meta.env.VITE_API_BASE ?? "";
const BASIC_AUTH = import.meta.env.VITE_ADMIN_BASIC_AUTH as string | undefined;
const TRIPS_REFRESH_MS = 60_000;
const OPS_REFRESH_MS = 15_000;
const STALE_AFTER_MS = OPS_REFRESH_MS * 3;
const LIST_LIMIT = 500;
const STS_CONCURRENCY = 4;
const MAX_TRIPS_WITH_STS = 80;

export const TMS_ENDPOINTS = {
  topologies: "/api/admin/warehouse-topologies",
  topologyMap: (id: number) => `/api/admin/warehouse-topologies/${id}/map`,
  tasks: (from: string, to: string) => `/api/admin/transport/tasks?include_readiness=true&date_from=${from}&date_to=${to}`,
  taskSts: (id: number) => `/api/admin/transport/tasks/${id}/sts`,
  freeSts: "/api/admin/transport/available-sts?page_size=300",
  warehouseTasks: `/api/warehouse-tasks?limit=${LIST_LIMIT}`,
  warehouseTask: (id: string) => `/api/warehouse-tasks/${id}`,
  warehouseTaskProgress: (id: string) => `/api/warehouse-tasks/${id}/progress`,
  warehouseTaskSync: (id: string) => `/api/warehouse-tasks/${id}/sync`,
  caseTasks: `/api/case-pick/tasks?scope=all&limit=${LIST_LIMIT}`,
  caseTask: (id: string) => `/api/case-pick/tasks/${id}`,
  resources: "/api/resources",
  equipment: "/api/resources/equipment",
  sessions: "/api/resources/sessions"
} as const;

class TmsHttpError extends Error {
  constructor(public readonly status: number, path: string) {
    super(`${status} ${path}`);
  }
}

export async function tmsGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { headers: BASIC_AUTH ? { Authorization: `Basic ${btoa(BASIC_AUTH)}` } : {} });
  if (!res.ok) throw new TmsHttpError(res.status, path);
  return (await res.json()) as T;
}

async function mapLimited<T, R>(items: T[], limit: number, fn: (item: T) => Promise<R>): Promise<R[]> {
  const out: R[] = new Array(items.length);
  let next = 0;
  const worker = async () => {
    while (next < items.length) {
      const i = next++;
      out[i] = await fn(items[i]);
    }
  };
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));
  return out;
}

const isoDate = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

function dateRange(params: URLSearchParams, now: Date) {
  const shift = (days: number) => isoDate(new Date(now.getFullYear(), now.getMonth(), now.getDate() + days));
  return { from: params.get("from") ?? shift(-2), to: params.get("to") ?? shift(30) };
}

function emptyWorld(): TwinState {
  const w = createWorld(0, createRng(0));
  w.mode = "live";
  w.cells = [];
  w.cellIndex = {};
  w.gates = [];
  w.resources = [];
  w.connection = { state: "LOADING" };
  w.layout = { ...w.layout, siteId: "WMS", siteName: "Загрузка структуры склада…", address: "Live-источник WMS/TMS", aisles: [] };
  return w;
}

const nowSeconds = (now: Date) => now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();

function errorText(err: unknown) {
  const code = err instanceof TmsHttpError ? err.status : 0;
  return code === 401 ? "нужен вход (401)" : code === 403 ? "нет прав (403)" : code ? `ошибка ${code}` : `недоступен: ${(err as Error).message}`;
}

// Открытые операции по складам — для выбора склада по умолчанию.
function openOpsByWare(wt: WmsWarehouseTask[], cp: WmsCaseTask[]) {
  const m = new Map<number, number>();
  const add = (w: number | null) => { if (w !== null && w !== undefined) m.set(w, (m.get(w) ?? 0) + 1); };
  for (const t of wt) if (t.status && !["DONE", "CANCELLED"].includes(t.status)) add(t.to_ware_id ?? t.from_ware_id);
  for (const t of cp) if (t.status && !["SHIPPED", "CANCELLED"].includes(t.status)) add(t.ware_id);
  return m;
}

export function createTmsLiveSource(): TwinSource {
  const params = new URLSearchParams(window.location.search);
  const world = emptyWorld();
  let message = BASIC_AUTH ? "Загрузка данных WMS/TMS…" : "Не задан VITE_ADMIN_BASIC_AUTH (twin/wms_twin_3d/.env)";
  let topology: TmsTopologyMap | undefined;
  let wareId: number | undefined = Number(params.get("ware")) || undefined;
  let lastOkAt = 0;
  let failed = false;
  let structureNotes: string[] = [];
  let busyOps = false;
  let busyTrips = false;

  const loadStructure = async (wt: WmsWarehouseTask[], cp: WmsCaseTask[]) => {
    const list = await tmsGet<TmsTopologySummary[]>(TMS_ENDPOINTS.topologies);
    const requestedTopology = Number(params.get("topology")) || undefined;
    if (!wareId && requestedTopology) wareId = list.find((t) => t.topology_id === requestedTopology)?.ware_id;
    if (!wareId) wareId = pickWarehouse(list, openOpsByWare(wt, cp));
    const chosen = pickTopology(list, { topology: requestedTopology, ware: wareId });
    structureNotes = [];
    if (!chosen) {
      structureNotes.push(wareId ? `Для склада ${wareId} нет опубликованной топологии — операции показываются без привязки к схеме.` : "Не найден склад с опубликованной топологией.");
      world.layout = { ...world.layout, siteId: `WARE-${wareId ?? "?"}`, siteName: `Склад ${wareId ?? "?"}`, address: "Нет опубликованной топологии", wareId };
      world.layoutVersion += 1;
      topology = { topology: { topology_id: 0, ware_id: wareId ?? 0, ware_name: null, topology_code: "—", topology_name: null, status: "NONE" }, aisles: [], gates: [], cells: [] };
      return;
    }
    topology = await tmsGet<TmsTopologyMap>(TMS_ENDPOINTS.topologyMap(chosen.topology_id));
    const topo = layoutFromTopology(topology);
    world.layout = topo.layout;
    world.cells = topo.cells;
    world.cellIndex = topo.cellIndex;
    world.gates = topo.gates;
    structureNotes = topo.notes;
    world.layoutVersion += 1;
    world.stockVersion += 1;
  };

  const refreshOps = async () => {
    if (busyOps || !BASIC_AUTH) return;
    busyOps = true;
    try {
      const [wt, cp, resources, equipment, sessions] = await Promise.all([
        tmsGet<WmsWarehouseTask[]>(TMS_ENDPOINTS.warehouseTasks),
        tmsGet<WmsCaseTask[]>(TMS_ENDPOINTS.caseTasks),
        tmsGet<WmsResource[]>(TMS_ENDPOINTS.resources).catch(() => [] as WmsResource[]),
        tmsGet<WmsEquipment[]>(TMS_ENDPOINTS.equipment).catch(() => [] as WmsEquipment[]),
        tmsGet<WmsSession[]>(TMS_ENDPOINTS.sessions).catch(() => [] as WmsSession[])
      ]);
      if (!topology) await loadStructure(wt, cp);
      const observedAt = new Date().toISOString();
      const snap = operationsSnapshot({
        warehouseTasks: wt,
        caseTasks: cp,
        resources,
        equipment,
        sessions,
        wareId: wareId !== undefined ? String(wareId) : undefined,
        cells: new Set(world.cells.map((c) => c.id)),
        observedAt,
        limit: LIST_LIMIT
      });
      world.operations = snap.operations;
      world.executors = snap.executors;
      world.opsStats = snap.stats;
      world.simTime = nowSeconds(new Date());
      detectCollisions(world, OPS_REFRESH_MS / 1000);
      world.entitiesVersion += 1;
      lastOkAt = Date.now();
      failed = false;
      const open = snap.operations.filter((o) => isOpenPhase(o.phase)).length;
      message = `Склад ${wareId ?? "?"}: ${open} открытых операций, ${snap.executors.length} исполнителей; рейсов ${world.trips.length}`;
    } catch (err) {
      failed = true;
      message = `API WMS ${errorText(err)}${lastOkAt ? " · показан последний снимок" : ""}`;
    } finally {
      busyOps = false;
      world.dataNotes = [...structureNotes, ...tripNotes];
    }
  };

  let tripNotes: string[] = [];
  const refreshTrips = async () => {
    if (busyTrips || !BASIC_AUTH || !topology) return;
    busyTrips = true;
    try {
      const now = new Date();
      const range = dateRange(params, now);
      const tasks = await tmsGet<TmsTask[]>(TMS_ENDPOINTS.tasks(range.from, range.to));
      const planned = tasks.filter((t) => !t.DELETED && (t.ST_COUNT ?? 0) > 0 && !(t.CONDITION ?? "").toLowerCase().startsWith("отгруж")).slice(0, MAX_TRIPS_WITH_STS);
      const stLists = await mapLimited(planned, STS_CONCURRENCY, (t) => tmsGet<TmsSt[]>(TMS_ENDPOINTS.taskSts(t.ID)).catch(() => [] as TmsSt[]));
      const taskSts: Record<number, TmsSt[]> = {};
      planned.forEach((t, i) => { taskSts[t.ID] = stLists[i]; });
      const freeSts = params.get("freeSts") === "0" ? [] : await tmsGet<TmsSt[]>(TMS_ENDPOINTS.freeSts).catch(() => [] as TmsSt[]);
      const snapshot: TmsSnapshot = { topology, tasks, taskSts, freeSts, now };
      applyTmsSnapshot(world, snapshot, false);
      tripNotes = world.dataNotes.filter((n) => !structureNotes.includes(n));
      world.dataNotes = [...structureNotes, ...tripNotes];
      world.simTime = nowSeconds(now);
      detectCollisions(world, TRIPS_REFRESH_MS / 1000);
    } catch (err) {
      tripNotes = [`Рейсы ТМС: ${errorText(err)}`];
    } finally {
      busyTrips = false;
    }
  };

  void refreshOps().then(refreshTrips);
  const opsTimer = window.setInterval(() => void refreshOps(), OPS_REFRESH_MS);
  const tripsTimer = window.setInterval(() => void refreshTrips(), TRIPS_REFRESH_MS);
  world.simTime = nowSeconds(new Date());
  return {
    mode: "live",
    world,
    // Live-время — часы компьютера; скорость проигрывания на него не влияет.
    advance: () => {
      world.simTime = nowSeconds(new Date());
      const age = lastOkAt ? Date.now() - lastOkAt : 0;
      world.connection = {
        state: !lastOkAt ? (failed ? "DISCONNECTED" : "LOADING") : failed ? "DISCONNECTED" : age > STALE_AFTER_MS ? "STALE" : "LIVE",
        snapshotAt: lastOkAt || undefined,
        message
      };
      world.version += 1;
    },
    status: () => ({ ok: world.connection.state === "LIVE", message }),
    dispose: () => {
      window.clearInterval(opsTimer);
      window.clearInterval(tripsTimer);
    }
  };
}

// Ленивые подробности выбранной операции (§5, §6): карточка, прогресс семейства, доменная синхронизация, строки CASE.
export type OperationDetail = { raw?: Record<string, unknown>; progress?: Record<string, unknown>; sync?: Record<string, unknown>; caseOp?: TwinOperation; error?: string };

export async function fetchOperationDetail(op: TwinOperation, cellKeys: Set<string>): Promise<OperationDetail> {
  try {
    if (op.source.entity === "RRL_WAREHOUSE_TASK") {
      const [raw, progress, sync] = await Promise.all([
        tmsGet<Record<string, unknown>>(TMS_ENDPOINTS.warehouseTask(op.source.id)),
        tmsGet<Record<string, unknown>>(TMS_ENDPOINTS.warehouseTaskProgress(op.source.id)).catch(() => undefined),
        tmsGet<Record<string, unknown>>(TMS_ENDPOINTS.warehouseTaskSync(op.source.id)).catch(() => undefined)
      ]);
      return { raw, progress, sync };
    }
    if (op.source.entity === "RRL_CASE_PICK_TASK") {
      const raw = await tmsGet<WmsCaseTask & Record<string, unknown>>(TMS_ENDPOINTS.caseTask(op.source.id));
      return { raw, caseOp: operationFromCaseTask(raw, cellKeys, new Date().toISOString()) };
    }
    return {};
  } catch (err) {
    return { error: errorText(err) };
  }
}
