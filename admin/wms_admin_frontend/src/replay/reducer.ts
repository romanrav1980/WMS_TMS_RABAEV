import { clock, inferWaveByMinute, SHIFT_MINUTES } from "../demoData";
import type { Collision, CollisionType, MinuteMetrics, PickFaceFill, ReplenishmentTask, ResourceState, StockSnapshot, WarehouseCell, WarehouseEvent, WarehouseLayout } from "../types";

const rootCauseByType: Record<string, string> = {
  PICK_FACE_EMPTY: "Комплектовщик пришел к ячейке отбора, но доступного остатка уже не хватило",
  PICK_FACE_QUEUE: "Несколько комплектовщиков пришли к одной ячейке отбора одновременно",
  AISLE_CONGESTION: "Перегруз 10-метрового сегмента аллеи",
  REACHTRUCK_BLOCK: "Ричтрак выполняет опускание паллеты в зоне отбора",
  REACHTRUCK_CROSSING: "Два ричтрака одновременно проходят один сегмент аллеи",
  REACHTRUCK_PICKER_PASS: "Ричтрак проходит рядом с комплектовщиком в узкой аллее",
  DYNAMIC_CELL_SHORTAGE: "Нет свободной динамической ячейки под пополнение SKU",
  MINIMAX_WAIT: "Пополнение ожидает снижения остатка до Minimax-порога",
  REACH_RESOURCE_SHORTAGE: "Очередь пополнений выше пропускной способности RTP",
  PICKER_RESOURCE_SHORTAGE: "Активных клиентских паллет больше доступной емкости комплектовщиков",
  ROUTE_COMPLETION_DELAY: "Маршрут комплектации не закрыт в плановое окно",
  PALLET_TO_DOCK_DELAY: "Собранные паллеты не успевают выставить к воротам",
  DOCK_QUEUE: "Ворота и скорость отгрузки ограничивают выпуск клиентов",
  SHIPMENT_RATE_LIMIT: "Ограничение 15 паллет в час задерживает рейс"
};

export function visibleEvents(events: WarehouseEvent[], minute: number, waveId?: string): WarehouseEvent[] {
  return events.filter((event) => event.minute <= minute && (!waveId || event.wave_id === waveId));
}

export function currentMetrics(metrics: MinuteMetrics[], minute: number): MinuteMetrics | undefined {
  let best = metrics[0];
  for (const row of metrics) {
    if (Number(row.minute) <= minute) best = row;
  }
  return best;
}

export function resourceStateAt(layout: WarehouseLayout, events: WarehouseEvent[], minute: number, waveId?: string): ResourceState[] {
  const resources = new Map<string, ResourceState>();
  for (const event of visibleEvents(events, minute, waveId)) {
    if (!event.resource_id) continue;
    const previous = resources.get(event.resource_id) || makeResource(event.resource_id);
    const loc = eventLocation(layout, event) || { x: previous.x, y: previous.y, cell: previous.cell };
    const kind = event.resource_id.startsWith("RT") ? "reachtruck" : "picker";
    const speedRatio = kind === "picker" ? speedRatioForPicker(event.resource_id, minute) : 100;
    const status = statusLabel(kind, event, speedRatio);
    resources.set(event.resource_id, {
      ...previous,
      id: event.resource_id,
      kind,
      x: loc.x,
      y: loc.y,
      cell: loc.cell,
      waveId: event.wave_id || previous.waveId,
      clientId: event.client_id || previous.clientId,
      palletId: event.pallet_id || previous.palletId,
      sku: event.sku_id || previous.sku,
      taskId: event.task_id || previous.taskId,
      status,
      statusColor: statusColorName(status, speedRatio),
      speedRatio,
      queue: 0,
      utilization: clamp(Math.round((minute / SHIFT_MINUTES) * 100), 0, 100),
      driver: event.resource_id.startsWith("RT") ? `RTD${event.resource_id.slice(2)}` : "",
      trail: previous.trail.concat([{ x: loc.x, y: loc.y, minute: event.minute }]).slice(-18)
    });
  }
  for (let index = 1; index <= 10; index += 1) {
    const id = `P${String(index).padStart(2, "0")}`;
    if (!resources.has(id)) resources.set(id, makeResource(id));
  }
  for (let index = 1; index <= 5; index += 1) {
    const id = `RT${String(index).padStart(2, "0")}`;
    if (!resources.has(id)) resources.set(id, makeResource(id));
  }
  const tasks = replenishmentTasksAt(events, minute);
  return Array.from(resources.values()).map((resource) => resource.kind === "reachtruck"
    ? { ...resource, queue: tasks.filter((task) => task.status !== "DONE").length }
    : resource);
}

export function activeCollisions(events: WarehouseEvent[], minute: number, windowMinutes = 120, waveId?: string): Collision[] {
  return events
    .filter((event) => event.event_type === "COLLISION" && event.minute >= Math.max(0, minute - windowMinutes) && event.minute <= minute)
    .map((event, index) => normalizeCollision(event, index))
    .filter((collision) => !waveId || collision.waveId === waveId);
}

export function replenishmentTasksAt(events: WarehouseEvent[], minute: number): ReplenishmentTask[] {
  const tasks = new Map<string, ReplenishmentTask>();
  for (const event of events.filter((row) => row.minute <= minute)) {
    if (!["REPLENISHMENT_PLANNED", "REPLENISHMENT_RELEASED", "REACHTRUCK_TASK_STARTED", "REPLENISHMENT_DONE"].includes(event.event_type)) continue;
    const id = event.task_id || `${event.wave_id || "WAVE"}-${event.sku_id || "SKU"}-${event.target_cell || event.minute}`;
    const previous = tasks.get(id) || {
      id,
      waveId: event.wave_id,
      sku: event.sku_id || "SKU",
      targetCell: event.target_cell || event.cell || "A01-S001-L1",
      sourceCell: event.source_cell || "",
      createdMinute: event.minute,
      status: "PLANNED",
      mode: String(event.replenishment_mode || ""),
      reason: "Низкий остаток",
      stockPercent: 30,
      stockText: "12 / 96 шт",
      ageMinutes: 0,
      overdueMinutes: 0,
      zone: "Зона 1 · Стеллаж A01"
    };
    const status = event.event_type === "REPLENISHMENT_DONE" ? "DONE"
      : event.event_type === "REACHTRUCK_TASK_STARTED" ? "IN_PROGRESS"
      : event.event_type === "REPLENISHMENT_RELEASED" ? "RELEASED"
      : previous.status;
    const ageMinutes = Math.max(0, minute - previous.createdMinute);
    tasks.set(id, {
      ...previous,
      status,
      mode: String(event.replenishment_mode || previous.mode || ""),
      targetCell: event.target_cell || previous.targetCell,
      sourceCell: event.source_cell || previous.sourceCell,
      sku: event.sku_id || previous.sku,
      waveId: event.wave_id || previous.waveId,
      ageMinutes,
      overdueMinutes: status !== "DONE" ? Math.max(0, ageMinutes - 15) : 0,
      reason: event.replenishment_mode === "CASE_REPLENISHMENT" ? "Коробочное пополнение" : status === "PLANNED" ? "Minimax wait" : status === "RELEASED" ? "Низкий остаток" : "Ячейка отбора пуста",
      zone: `Зона ${parseAisle(event.target_cell || previous.targetCell) || 1} · Стеллаж ${aisleLabel(event.target_cell || previous.targetCell)}`
    });
  }
  return Array.from(tasks.values()).sort((a, b) => b.overdueMinutes - a.overdueMinutes || b.ageMinutes - a.ageMinutes);
}

export function pickFaceFillAt(stock: StockSnapshot | undefined, events: WarehouseEvent[], minute: number): Record<string, PickFaceFill> {
  const qtyByCell: Record<string, number> = { ...(stock?.pick_face_stock || {}) };
  const capacityByCell: Record<string, number> = { ...(stock?.pick_face_capacity || {}) };
  for (const event of events) {
    if (Number(event.minute) > minute) continue;
    if (event.event_type === "PICKER_TASK_STARTED" && event.cell) {
      qtyByCell[event.cell] = Math.max(0, Number(qtyByCell[event.cell] || 0) - Number(event.qty_boxes || 0));
    }
    if (event.event_type === "REPLENISHMENT_DONE" && event.target_cell) {
      const capacity = Number(capacityByCell[event.target_cell] || 600);
      capacityByCell[event.target_cell] = capacity;
      qtyByCell[event.target_cell] = Math.min(capacity, Number(qtyByCell[event.target_cell] || 0) + Number(event.qty_boxes || 0));
    }
  }
  return Object.fromEntries(Object.entries(capacityByCell).map(([cell, capacity]) => {
    const qty = Math.max(0, Number(qtyByCell[cell] || 0));
    return [cell, { qty, capacity, ratio: capacity > 0 ? Math.max(0, Math.min(1, qty / capacity)) : 0 }];
  }));
}

export function cellById(layout: WarehouseLayout, id?: string): WarehouseCell | undefined {
  if (!id) return undefined;
  return layout.cells.find((cell) => cell.cell_id === id);
}

export function parseAisle(value?: string): number {
  const match = /A(\d+)/.exec(String(value || ""));
  return match ? Number(match[1]) : 0;
}

export function parseSlot(value?: string): number {
  const match = /S(\d+)/.exec(String(value || ""));
  return match ? Number(match[1]) : 1;
}

export function aisleLabel(value?: string): string {
  const aisle = parseAisle(value);
  return aisle ? `A${String(aisle).padStart(2, "0")}` : "A01";
}

export function collisionTitle(type: string): string {
  return {
    PICK_FACE_EMPTY: "Ячейка отбора пуста",
    PICK_FACE_QUEUE: "Очередь к ячейке отбора",
    AISLE_CONGESTION: "Затор в проходе",
    REACHTRUCK_BLOCK: "Блокировка маршрута",
    REACHTRUCK_CROSSING: "Пересечение RT",
    REACHTRUCK_PICKER_PASS: "RT рядом с комплектовщиком",
    DYNAMIC_CELL_SHORTAGE: "Нет dynamic ячейки",
    MINIMAX_WAIT: "Minimax wait",
    REACH_RESOURCE_SHORTAGE: "Очередь RTP",
    PICKER_RESOURCE_SHORTAGE: "Нехватка комплектовщиков",
    ROUTE_COMPLETION_DELAY: "Маршрут опаздывает",
    PALLET_TO_DOCK_DELAY: "Подача к воротам опаздывает",
    DOCK_QUEUE: "Очередь на ворота",
    SHIPMENT_RATE_LIMIT: "Ограничение отгрузки"
  }[type] || type;
}

function normalizeCollision(event: WarehouseEvent, index: number): Collision {
  const type = (event.collision_type || "PICK_FACE_QUEUE") as CollisionType;
  const lost = Number(event.lost_minutes || 1);
  return {
    id: event.id || `collision-${event.minute}-${index}`,
    minute: event.minute,
    clock: event.clock || clock(event.minute),
    type,
    severity: severityForType(type, lost),
    locationLabel: event.cell || event.segment || event.gate_id || event.target_cell || "A01-S023-L1",
    affectedResources: Array.isArray(event.resources) ? event.resources : [event.resource_id].filter(Boolean) as string[],
    waveId: event.wave_id || inferWaveByMinute(event.minute),
    clientId: event.client_id,
    sku: event.sku_id,
    rootCause: rootCauseByType[type] || "Операционная задержка склада",
    lostMinutes: lost,
    productivityLoss: Math.round(lost * 18),
    raw: event
  };
}

export function eventLocation(layout: WarehouseLayout, event: WarehouseEvent): { x: number; y: number; cell?: string } | null {
  const cellId = event.cell || event.target_cell || event.source_cell;
  const cell = cellById(layout, cellId);
  if (cell) return { x: Number(cell.x_m), y: Number(cell.y_m), cell: cell.cell_id };
  if (event.segment) {
    const parsed = /A(\d+)-SEG(\d+)/.exec(event.segment);
    if (parsed) return { x: Number(parsed[2]) * 10 + 5, y: (Number(parsed[1]) - 1) * 4, cell: event.segment };
  }
  return null;
}

function makeResource(id: string): ResourceState {
  const isRt = id.startsWith("RT");
  const n = Number(id.replace(/\D/g, "")) || 1;
  return {
    id,
    kind: isRt ? "reachtruck" : "picker",
    x: isRt ? -4 : 2 + n * 2,
    y: isRt ? (n - 1) * 14 + 3 : (n - 1) * 7 + 3,
    status: "ожид.",
    statusColor: "gray",
    speedRatio: 0,
    queue: 0,
    utilization: 0,
    driver: isRt ? `RTD${id.slice(2)}` : "",
    trail: []
  };
}

function speedRatioForPicker(id: string, minute: number): number {
  const base: Record<string, number> = { P01: 78, P02: 96, P03: 64, P04: 74, P05: 104, P06: 88, P07: 132, P08: 118, P09: 121, P10: 98 };
  return clamp((base[id] || 96) + ((minute + Number(id.replace(/\D/g, ""))) % 17) - 8, 45, 138);
}

function statusLabel(kind: ResourceState["kind"], event: WarehouseEvent, speedRatio: number): string {
  if (kind === "reachtruck") {
    if (event.event_type === "REACHTRUCK_TASK_STARTED") return "в пути";
    if (event.event_type === "REPLENISHMENT_DONE") return "готов";
    return "queue";
  }
  if (speedRatio < 60) return "стоп";
  if (speedRatio < 82) return "замедлен";
  if (event.event_type === "PICKER_TASK_DONE") return "готов";
  return "отбор";
}

function statusColorName(status: string, speedRatio: number): ResourceState["statusColor"] {
  if (status === "стоп") return "red";
  if (status === "замедлен") return "amber";
  if (status === "ожид.") return "gray";
  if (speedRatio >= 105) return "green";
  return "blue";
}

function severityForType(type: string, lost: number): Collision["severity"] {
  if (["PICK_FACE_EMPTY", "PICK_FACE_QUEUE", "REACHTRUCK_BLOCK", "REACHTRUCK_CROSSING", "ROUTE_COMPLETION_DELAY", "PALLET_TO_DOCK_DELAY", "DOCK_QUEUE", "REACH_RESOURCE_SHORTAGE"].includes(type) || lost >= 5) return "critical";
  return "warning";
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}
