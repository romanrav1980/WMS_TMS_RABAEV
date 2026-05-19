export type WarehouseCell = {
  cell_id: string;
  aisle: number;
  slot: number;
  level: number;
  x_m: number;
  y_m: number;
  role: string;
};

export type WarehouseGate = {
  gate_id: string;
  aisle: number;
  x_m: number;
  y_m: number;
};

export type WarehouseLayout = {
  run_id?: string;
  cells: WarehouseCell[];
  gates: WarehouseGate[];
};

export type WarehouseEvent = {
  id?: string;
  minute: number;
  clock?: string;
  event_type: string;
  collision_type?: CollisionType;
  resource_id?: string;
  task_id?: string;
  wave_id?: string;
  client_id?: string;
  pallet_id?: string;
  sku_id?: string;
  cell?: string;
  source_cell?: string;
  target_cell?: string;
  segment?: string;
  gate_id?: string;
  resources?: string[];
  lost_minutes?: number;
  [key: string]: unknown;
};

export type MinuteMetrics = {
  minute: number;
  done_pick_lines?: number;
  total_pick_lines?: number;
  picker_busy?: number;
  reachtruck_busy?: number;
  queued_replenishment?: number;
  dock_queue?: number;
  lost_minutes?: number;
  collisions?: number;
  [key: string]: unknown;
};

export type SimulationReport = {
  run_id?: string;
  scenario?: Record<string, number | string>;
  totals?: Record<string, number | string>;
  capacity_analysis?: {
    total_pick_boxes?: number;
    done_pick_boxes?: number;
    picker_box_capacity_per_shift?: number;
    picker_demand_to_capacity_ratio?: number;
    replenishment_tasks?: number;
    case_replenishment_tasks?: number;
    pallet_replenishment_tasks?: number;
    reachtruck_nominal_capacity_per_shift?: number;
    case_replenishment_capacity_if_all_case?: number;
    replenishment_demand_to_nominal_capacity_ratio?: number;
  };
  bottleneck_summary?: Array<{
    code: string;
    severity: "warning" | "critical";
    message: string;
    demand?: number;
    capacity?: number;
    ratio?: number;
    count?: number;
    lost_minutes?: number;
  }>;
};

export type StockSnapshot = {
  pick_face_stock?: Record<string, number>;
  pick_face_capacity?: Record<string, number>;
};

export type PickFaceFill = {
  qty: number;
  capacity: number;
  ratio: number;
};

export type CollisionType =
  | "PICK_FACE_EMPTY"
  | "PICK_FACE_QUEUE"
  | "AISLE_CONGESTION"
  | "REACHTRUCK_BLOCK"
  | "REACHTRUCK_CROSSING"
  | "REACHTRUCK_PICKER_PASS"
  | "DYNAMIC_CELL_SHORTAGE"
  | "MINIMAX_WAIT"
  | "REACH_RESOURCE_SHORTAGE"
  | "PICKER_RESOURCE_SHORTAGE"
  | "ROUTE_COMPLETION_DELAY"
  | "PALLET_TO_DOCK_DELAY"
  | "DOCK_QUEUE"
  | "SHIPMENT_RATE_LIMIT";

export type Collision = {
  id: string;
  minute: number;
  clock: string;
  type: CollisionType;
  severity: "warning" | "critical";
  locationLabel: string;
  affectedResources: string[];
  waveId?: string;
  clientId?: string;
  sku?: string;
  rootCause: string;
  lostMinutes: number;
  productivityLoss: number;
  raw: WarehouseEvent;
};

export type ResourceState = {
  id: string;
  kind: "picker" | "reachtruck";
  x: number;
  y: number;
  cell?: string;
  waveId?: string;
  clientId?: string;
  palletId?: string;
  sku?: string;
  taskId?: string;
  status: string;
  statusColor: "green" | "blue" | "amber" | "red" | "gray";
  speedRatio: number;
  queue: number;
  utilization: number;
  driver?: string;
  trail: Array<{ x: number; y: number; minute: number }>;
};

export type ReplenishmentTask = {
  id: string;
  waveId?: string;
  sku: string;
  targetCell: string;
  sourceCell?: string;
  createdMinute: number;
  status: string;
  mode?: string;
  reason: string;
  stockPercent: number;
  stockText: string;
  ageMinutes: number;
  overdueMinutes: number;
  zone: string;
};

export type ReplayData = {
  layout: WarehouseLayout;
  events: WarehouseEvent[];
  metrics: MinuteMetrics[];
  report: SimulationReport;
  stock?: StockSnapshot;
};

export type DetailSelection =
  | { type: "resource"; resource: ResourceState }
  | { type: "collision"; collision: Collision }
  | { type: "task"; task: ReplenishmentTask }
  | null;
