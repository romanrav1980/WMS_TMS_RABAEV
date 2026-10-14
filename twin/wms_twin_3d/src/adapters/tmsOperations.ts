import type { OpLine, OpLocation, OpPhase, TwinExecutor, TwinOperation } from "../contracts/twin";

// Сопоставление складских заданий WMS с операциями двойника (warehouse-twin-operation/1).
// Основание: wiki/requirements/warehouse_operations_digital_twin.md §5, §6, §10–§13.
// Форматы сверены с живым API 14.10.2026:
//   GET /api/warehouse-tasks?limit=500          (открытые статусы идут первыми — task_queue_read.py)
//   GET /api/warehouse-tasks/{id}, /progress, /sync
//   GET /api/case-pick/tasks?scope=all&limit=500, /api/case-pick/tasks/{id}
//   GET /api/resources, /api/resources/equipment, /api/resources/sessions
// Правила: исходный статус не переименовывается; неизвестное остаётся неизвестным; количества — строки.

export type WmsWarehouseTask = {
  task_id: number;
  task_type: string | null;
  task_source: string | null;
  source_doc_type: string | null;
  source_doc_id: number | null;
  uid_pallet: string | null;
  sscc: string | null;
  from_ware_id: number | null;
  from_cell: string | null;
  to_ware_id: number | null;
  to_cell: string | null;
  qty_exact: string | null;
  fact_qty_exact: string | null;
  unit_code: string | null;
  qty_mode: string | null;
  parent_task_id: number | null;
  priority: number | null;
  status: string | null;
  assigned_to: string | null;
  resource_id: number | null;
  resource_session_id: number | null;
  equipment_id: number | null;
  hu_content_version: number | string | null;
  wait_st_number: string | null;
  wait_target_tt_id: number | null;
  created_at: string | null;
  started_at: string | null;
  finished_at: string | null;
  cancelled_at: string | null;
  last_error: string | null;
};

export type WmsCaseLine = {
  case_pick_line_id: number;
  articul: string | null;
  product_name: string | null;
  cell_code: string | null;
  planned_qty: string | null;
  picked_qty: string | null;
  status: string | null;
};

export type WmsCaseTask = {
  case_pick_task_id: number;
  pick_wave_id: number | null;
  wave_code: string | null;
  customer_order_id: number | null;
  order_no: string | null;
  customer_name: string | null;
  sscc: string | null;
  pallet_type_name: string | null;
  status: string | null;
  assigned_resource_id: number | null;
  resource_session_id: number | null;
  equipment_id: number | null;
  assigned_to: string | null;
  resource_name?: string | null;
  ware_id: number | null;
  total_lines: number | null;
  picked_lines: number | null;
  planned_qty: string | null;
  picked_qty: string | null;
  blocking_reason?: string | null;
  blocking_cell_code?: string | null;
  problem?: string | null;
  current_cell?: string | null;
  content_version?: number | null;
  last_event_at?: string | null;
  created_at: string | null;
  started_at: string | null;
  closed_at: string | null;
  lines?: WmsCaseLine[];
};

export type WmsResource = {
  resource_id: number;
  resource_code: string | null;
  resource_name: string | null;
  resource_class: string | null;
  resource_type: string | null;
  equipment_code: string | null;
  ware_id: number | null;
  status: string | null;
  active_session_id: number | null;
  active_heartbeat_at: string | null;
  active_task_id: number | null;
  active_session_status: string | null;
  last_cell: string | null;
  last_position_at: string | null;
};

export type WmsEquipment = { equipment_id: number; equipment_code: string | null; equipment_type: string | null; equipment_name: string | null; ware_id: number | null; service_status: string | null };

export type WmsSession = { session_id: number; resource_id: number; equipment_id: number | null; status: string | null; current_task_id: number | null; last_heartbeat_at: string | null; logout_at: string | null };

const str = (v: unknown) => (v === null || v === undefined || v === "" ? undefined : String(v));

function location(cell: string | null, ware: number | null, cells: Set<string>): OpLocation | undefined {
  if (!cell && ware === null) return undefined;
  return { cell: cell ?? undefined, wareId: str(ware), bound: !!cell && cells.has(cell) };
}

// RRL_WAREHOUSE_TASK: PLANNED → ASSIGNED → IN_PROGRESS → DONE; CANCELLED, ERROR (§5).
export function phaseOfWarehouseTask(t: Pick<WmsWarehouseTask, "status" | "fact_qty_exact" | "qty_exact" | "last_error">): OpPhase {
  switch ((t.status ?? "").toUpperCase()) {
    case "PLANNED":
      return "PLANNED";
    case "ASSIGNED":
      return "ASSIGNED";
    case "IN_PROGRESS":
      return t.fact_qty_exact && t.fact_qty_exact !== "0" && t.fact_qty_exact !== t.qty_exact ? "PARTIAL" : "STARTED";
    case "DONE":
      return "COMPLETED";
    case "CANCELLED":
      return "CANCELLED";
    case "ERROR":
      return "FAILED";
    default:
      return "UNKNOWN";
  }
}

// CASE: NEW, ASSIGNED, IN_PROGRESS, PARTIAL, PICKED, WAIT_CONTROL, READY_TO_SHIP, SHIPPED, CANCELLED, FAILED, SYNC_CONFLICT (§6).
// Фаза описывает именно операцию сборки: собранный CASE — COMPLETED, но не «проверен» и не «отгружен» (это видно по rawStatus).
export function phaseOfCaseTask(t: Pick<WmsCaseTask, "status" | "blocking_reason">): OpPhase {
  if (t.blocking_reason) return "BLOCKED";
  switch ((t.status ?? "").toUpperCase()) {
    case "NEW":
      return "PLANNED";
    case "ASSIGNED":
      return "ASSIGNED";
    case "IN_PROGRESS":
      return "STARTED";
    case "PARTIAL":
      return "PARTIAL";
    case "PICKED":
    case "WAIT_CONTROL":
    case "READY_TO_SHIP":
    case "SHIPPED":
      return "COMPLETED";
    case "CANCELLED":
      return "CANCELLED";
    case "FAILED":
      return "FAILED";
    case "SYNC_CONFLICT":
      return "BLOCKED";
    default:
      return "UNKNOWN";
  }
}

export function operationFromWarehouseTask(t: WmsWarehouseTask, cells: Set<string>, observedAt: string): TwinOperation {
  return {
    key: `WH_TASK:${t.task_id}`,
    schemaVersion: "warehouse-twin-operation/1",
    source: { entity: "RRL_WAREHOUSE_TASK", id: String(t.task_id), rawStatus: t.status ?? "", mode: "LIVE", observedAt },
    warehouseId: str(t.to_ware_id ?? t.from_ware_id),
    kind: "MOVE",
    subtype: t.task_type ?? "—",
    phase: phaseOfWarehouseTask(t),
    context: {
      stNumber: str(t.wait_st_number),
      tripId: str(t.wait_target_tt_id),
      sourceDoc: t.source_doc_type ? `${t.source_doc_type}:${t.source_doc_id ?? "—"}` : str(t.task_source)
    },
    executor: { resourceId: str(t.resource_id), equipmentId: str(t.equipment_id), sessionId: str(t.resource_session_id), assignedTo: str(t.assigned_to) },
    loadUnit: { kind: t.uid_pallet || t.sscc ? "STOCK" : "UNKNOWN", uid: str(t.uid_pallet), sscc: str(t.sscc), contentVersion: str(t.hu_content_version) },
    from: location(t.from_cell, t.from_ware_id, cells),
    to: location(t.to_cell, t.to_ware_id, cells),
    quantity: { planned: str(t.qty_exact), confirmed: str(t.fact_qty_exact), unit: str(t.unit_code), mode: str(t.qty_mode), basis: "TASK_ROW" },
    blockedReason: undefined,
    lastError: str(t.last_error),
    times: { created: str(t.created_at), started: str(t.started_at), finished: str(t.finished_at), cancelled: str(t.cancelled_at) },
    priority: t.priority ?? undefined,
    routeBasis: "UNKNOWN"
  };
}

function caseLines(lines: WmsCaseLine[] | undefined, cells: Set<string>): OpLine[] | undefined {
  return lines?.map((l) => ({
    id: String(l.case_pick_line_id),
    cell: str(l.cell_code),
    sku: str(l.product_name) ?? str(l.articul),
    planned: str(l.planned_qty),
    picked: str(l.picked_qty),
    status: l.status ?? "",
    bound: !!l.cell_code && cells.has(l.cell_code)
  }));
}

export function operationFromCaseTask(t: WmsCaseTask, cells: Set<string>, observedAt: string): TwinOperation {
  const cell = t.current_cell ?? t.blocking_cell_code ?? null;
  const blocked = t.blocking_reason ?? (t.status === "SYNC_CONFLICT" ? "Конфликт синхронизации (SYNC_CONFLICT)" : undefined);
  return {
    key: `CASE_TASK:${t.case_pick_task_id}`,
    schemaVersion: "warehouse-twin-operation/1",
    source: { entity: "RRL_CASE_PICK_TASK", id: String(t.case_pick_task_id), rawStatus: t.status ?? "", mode: "LIVE", observedAt },
    warehouseId: str(t.ware_id),
    kind: "PICK",
    subtype: "CASE_PICK",
    phase: phaseOfCaseTask(t),
    context: { waveId: str(t.pick_wave_id), waveCode: str(t.wave_code), orderId: str(t.customer_order_id), orderNo: str(t.order_no), customer: str(t.customer_name) },
    executor: { resourceId: str(t.assigned_resource_id), equipmentId: str(t.equipment_id), sessionId: str(t.resource_session_id), assignedTo: str(t.assigned_to), label: str(t.resource_name) },
    loadUnit: { kind: "CASE", sscc: str(t.sscc), palletType: str(t.pallet_type_name), contentVersion: str(t.content_version) },
    to: cell ? { cell, wareId: str(t.ware_id), bound: cells.has(cell) } : undefined,
    quantity: { planned: str(t.planned_qty), confirmed: str(t.picked_qty), basis: "CASE_ROW" },
    progress: t.total_lines ? { done: t.picked_lines ?? 0, total: t.total_lines, label: "строк" } : undefined,
    lines: caseLines(t.lines, cells),
    blockedReason: blocked ?? undefined,
    lastError: str(t.problem),
    times: { created: str(t.created_at), started: str(t.started_at), finished: str(t.closed_at), lastEvent: str(t.last_event_at) },
    routeBasis: "UNKNOWN"
  };
}

// Исполнители: позиция только по подтверждённой last_cell ресурса (§10, §13); иначе — неизвестна.
export function executorsFromResources(resources: WmsResource[], equipment: WmsEquipment[], sessions: WmsSession[], cells: Set<string>): TwinExecutor[] {
  const out: TwinExecutor[] = resources.map((r) => {
    const session = sessions.find((s) => s.resource_id === r.resource_id && (s.status ?? "").toUpperCase() === "ACTIVE");
    return {
      id: `RES:${r.resource_id}`,
      kind: r.resource_type ?? r.resource_class ?? "—",
      code: r.resource_code ?? String(r.resource_id),
      name: r.resource_name ?? r.resource_code ?? String(r.resource_id),
      wareId: str(r.ware_id),
      status: r.status ?? "",
      sessionStatus: str(r.active_session_status ?? session?.status),
      heartbeatAt: str(r.active_heartbeat_at ?? session?.last_heartbeat_at),
      activeTaskId: str(r.active_task_id ?? session?.current_task_id),
      equipmentCode: str(r.equipment_code),
      lastCell: str(r.last_cell),
      lastPositionAt: str(r.last_position_at),
      positionBasis: r.last_cell ? (cells.has(r.last_cell) ? "OBSERVED_CELL" : "UNBOUND_CELL") : "UNKNOWN"
    };
  });
  const linked = new Set(resources.map((r) => r.equipment_code).filter(Boolean));
  for (const e of equipment) {
    if (e.equipment_code && linked.has(e.equipment_code)) continue;
    out.push({
      id: `EQ:${e.equipment_id}`,
      kind: e.equipment_type ?? "—",
      code: e.equipment_code ?? String(e.equipment_id),
      name: e.equipment_name ?? e.equipment_code ?? String(e.equipment_id),
      wareId: str(e.ware_id),
      status: e.service_status ?? "",
      positionBasis: "UNKNOWN"
    });
  }
  return out;
}

const OPEN_PHASES = new Set<OpPhase>(["PLANNED", "ASSIGNED", "STARTED", "SOURCE_CONFIRMED", "CARRYING", "TARGET_CONFIRMED", "PARTIAL", "BLOCKED", "UNKNOWN"]);
export const isOpenPhase = (p: OpPhase) => OPEN_PHASES.has(p);

export type OpsInput = {
  warehouseTasks: WmsWarehouseTask[];
  caseTasks: WmsCaseTask[];
  resources: WmsResource[];
  equipment: WmsEquipment[];
  sessions: WmsSession[];
  wareId?: string;
  cells: Set<string>;
  observedAt: string;
  limit: number;
};

// Снимок операций одного склада: чужие склады не смешиваются (§3), лимит выдачи не выдаётся за полный склад (§12).
export function operationsSnapshot(input: OpsInput) {
  const all = [
    ...input.warehouseTasks.map((t) => operationFromWarehouseTask(t, input.cells, input.observedAt)),
    ...input.caseTasks.map((t) => operationFromCaseTask(t, input.cells, input.observedAt))
  ];
  const sameWare = (o: TwinOperation) => {
    if (!input.wareId) return true;
    if (o.kind === "MOVE") return o.from?.wareId === input.wareId || o.to?.wareId === input.wareId;
    return o.warehouseId === input.wareId;
  };
  const operations = all.filter(sameWare);
  const executors = executorsFromResources(input.resources, input.equipment, input.sessions, input.cells).filter((e) => !input.wareId || e.wareId === input.wareId);
  const isBound = (o: TwinOperation) => !!(o.from?.bound || o.to?.bound || o.lines?.some((l) => l.bound));
  return {
    operations,
    executors,
    stats: {
      inSnapshot: all.length,
      otherWarehouses: all.length - operations.length,
      unbound: operations.filter((o) => isOpenPhase(o.phase) && !isBound(o)).length,
      limitReached: input.warehouseTasks.length >= input.limit || input.caseTasks.length >= input.limit
    }
  };
}
