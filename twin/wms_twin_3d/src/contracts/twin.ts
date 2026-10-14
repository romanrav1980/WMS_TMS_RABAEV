// Единый контракт состояния цифрового двойника (Twin State).
// Сцена, панели и адаптеры источников зависят только от этих типов.
// Идентификаторы совпадают с WMS/TMS: ячейка A01-S023-L1, СТ, рейс TT-…, ворота G01.

export type Vec2 = { x: number; z: number };

export type SourceMode = "sim" | "live";

// ── Топология склада ────────────────────────────────────────────────

export type Aisle = { id: string; index: number; x: number };

export type CellRole = "pick" | "reserve";

export type Cell = {
  id: string;
  index: number;
  aisle: number;
  slot: number;
  level: number;
  side: -1 | 1;
  x: number;
  y: number;
  z: number;
  role: CellRole;
  sku?: string;
  qty: number;
  capacity: number;
  // Размер ячейки в плане (м); по умолчанию — размеры демо-стеллажа.
  sizeX?: number;
  sizeZ?: number;
  // false — остаток неизвестен источнику (топология без складских данных).
  stockKnown?: boolean;
};

export type GateKind = "outbound" | "inbound";

export type Gate = {
  id: string;
  index: number;
  x: number;
  kind: GateKind;
  occupiedBy?: string;
  received: number;
};

export type Layout = {
  siteId: string;
  siteName: string;
  address: string;
  width: number;
  // depth — координата z фасада с воротами; stagingZ — линия выставки паллет перед воротами.
  depth: number;
  stagingZ: number;
  aisles: Aisle[];
  topologyId?: number;
  topologyCode?: string;
  wareId?: number;
};

// ── Движение ────────────────────────────────────────────────────────

export type Mover = {
  path: Vec2[];
  dist: number;
  len: number;
  speed: number;
  backwards: boolean;
};

// ── Ресурсы склада ──────────────────────────────────────────────────

export type ResourceKind = "picker" | "reachtruck" | "forklift";

export type ResourceStatus = "idle" | "moving" | "working" | "waiting" | "charging";

export type ResourceLeg = "none" | "toLine" | "toStaging" | "toSource" | "toTarget" | "toCharger" | "toPark";

export type Resource = {
  id: string;
  kind: ResourceKind;
  name: string;
  pos: Vec2;
  heading: number;
  mover?: Mover;
  leg: ResourceLeg;
  status: ResourceStatus;
  workLeft: number;
  fork: number;
  carrying: boolean;
  battery: number;
  done: number;
  taskId?: string;
  stId?: string;
  lineIdx: number;
  waitReason?: string;
  waitSince?: number;
  park: Vec2;
};

// ── Складские задания ───────────────────────────────────────────────

export type TaskKind = "REPL" | "PUTAWAY" | "LOAD" | "UNLOAD";

export type TaskStatus = "created" | "assigned" | "done";

export type WTask = {
  id: string;
  kind: TaskKind;
  status: TaskStatus;
  createdAt: number;
  urgent: boolean;
  sku?: string;
  fromCell?: string;
  toCell?: string;
  gateId?: string;
  stId?: string;
  tripId?: string;
  resourceId?: string;
};

// ── Сборочные задания (СТ) ──────────────────────────────────────────

export type StStage = "created" | "picking" | "picked" | "qc" | "staged" | "loading" | "loaded" | "shipped" | "delivered";

export const ST_STAGES: StStage[] = ["created", "picking", "picked", "qc", "staged", "loading", "loaded", "shipped", "delivered"];

export type StLine = { cellId: string; sku: string; qty: number; picked: boolean };

export type St = {
  id: string;
  store: string;
  tripId: string;
  gateId: string;
  waveId: string;
  stage: StStage;
  stageAt: Partial<Record<StStage, number>>;
  lines: StLine[];
  pallets: number;
  palletsLoaded: number;
  loadTasksCreated: number;
  qcLeft: number;
  pickerId?: string;
  wareId?: number;
  verifyPerc?: number;
  weightKg?: number;
};

// ── Транспорт ───────────────────────────────────────────────────────

export type TripDirection = "out" | "in";

export type TruckPhase = "planned" | "arriving" | "queued" | "reversing" | "docked" | "departing" | "transit" | "done";

export type TripRisk = "ok" | "risk" | "late";

export type VehicleType = { name: string; length: number; pallets: number; reefer: boolean };

export type Trip = {
  id: string;
  direction: TripDirection;
  plate: string;
  carrier: string;
  driver: string;
  vehicle: VehicleType;
  route: string;
  gateId: string;
  phase: TruckPhase;
  mover?: Mover;
  pos: Vec2;
  heading: number;
  stIds: string[];
  pallets: number;
  palletsDone: number;
  unloadTasksCreated: number;
  arriveAt: number;
  window: { from: number; to: number };
  dockedAt?: number;
  departedAt?: number;
  deliverAt?: number;
  paperworkLeft: number;
  queueSlot: number;
  risk: TripRisk;
  onTime?: boolean;
  waitReason?: string;
  // Поля live-источника ТМС (RRL_TRANSPORT_TASK).
  conditionRaw?: string;
  readyPerc?: number;
  shipmentDate?: string;
  stCount?: number;
};

// ── Коллизии и события ──────────────────────────────────────────────

export type CollisionType =
  | "PICK_FACE_EMPTY"
  | "AISLE_CONGESTION"
  | "REACH_QUEUE"
  | "DOCK_QUEUE"
  | "TRIP_LATE"
  | "LOW_BATTERY"
  | "WAITING_ST"
  | "OP_BLOCKED";

export type Severity = "warning" | "critical";

export type Collision = {
  key: string;
  type: CollisionType;
  severity: Severity;
  startedAt: number;
  endedAt?: number;
  active: boolean;
  where: string;
  pos: Vec2;
  affected: string[];
  rootCause: string;
  lostMinutes: number;
  // false — место на схеме неизвестно (объект не привязан к топологии), метка на сцене не рисуется.
  bound?: boolean;
};

export type EventLevel = "info" | "warn" | "crit";

// Событие в духе GS1 EPCIS: что, с чем, где, почему, кто, откуда пришло.
export type TwinEvent = {
  id: number;
  at: number;
  what: string;
  entity: string;
  where?: string;
  why?: string;
  who?: string;
  level: EventLevel;
  source: "sim" | "wms" | "tms" | "gps";
};

export type GateLogEntry = {
  at: number;
  dir: "in" | "out";
  tripId: string;
  plate: string;
  carrier: string;
  vehicle: string;
};

// ── Складские операции (контракт warehouse-twin-operation/1) ─────────
// Нормализованное представление заданий WMS по wiki/requirements/warehouse_operations_digital_twin.md §10–§11.
// Это ключи и фазы визуализации, а не новые статусы Oracle: исходный статус хранится в source.rawStatus.

export type OpPhase =
  | "PLANNED"
  | "ASSIGNED"
  | "STARTED"
  | "SOURCE_CONFIRMED"
  | "CARRYING"
  | "TARGET_CONFIRMED"
  | "PARTIAL"
  | "BLOCKED"
  | "COMPLETED"
  | "CANCELLED"
  | "FAILED"
  | "UNKNOWN";

export type OpKind = "MOVE" | "PICK";

export type OpLocation = { cell?: string; wareId?: string; bound: boolean };

export type OpLine = { id: string; cell?: string; sku?: string; planned?: string; picked?: string; status: string; bound: boolean };

export type TwinOperation = {
  key: string;
  schemaVersion: "warehouse-twin-operation/1";
  source: { entity: string; id: string; rawStatus: string; mode: "LIVE" | "SIM"; observedAt: string };
  warehouseId?: string;
  kind: OpKind;
  subtype: string;
  phase: OpPhase;
  context: { waveId?: string; waveCode?: string; orderId?: string; orderNo?: string; customer?: string; stNumber?: string; tripId?: string; sourceDoc?: string };
  executor: { resourceId?: string; equipmentId?: string; sessionId?: string; assignedTo?: string; label?: string };
  loadUnit: { kind: "STOCK" | "CASE" | "UNKNOWN"; uid?: string; sscc?: string; palletType?: string; contentVersion?: string };
  from?: OpLocation;
  to?: OpLocation;
  // Количества — точные десятичные строки из API, без округления (§4).
  quantity: { planned?: string; confirmed?: string; remaining?: string; unit?: string; mode?: string; basis: string };
  progress?: { done: number; total: number; label: string };
  lines?: OpLine[];
  blockedReason?: string;
  lastError?: string;
  times: { created?: string; started?: string; finished?: string; cancelled?: string; lastEvent?: string };
  priority?: number;
  routeBasis: "UNKNOWN" | "CALCULATED";
};

export type PositionBasis = "OBSERVED_CELL" | "UNBOUND_CELL" | "UNKNOWN" | "SIMULATED";

export type TwinExecutor = {
  id: string;
  kind: string;
  code: string;
  name: string;
  wareId?: string;
  status: string;
  sessionStatus?: string;
  heartbeatAt?: string;
  activeTaskId?: string;
  equipmentCode?: string;
  lastCell?: string;
  lastPositionAt?: string;
  positionBasis: PositionBasis;
};

export type ConnectionState = "SIM" | "LOADING" | "LIVE" | "STALE" | "DISCONNECTED";

// ── Корневое состояние ──────────────────────────────────────────────

export type TwinState = {
  mode: SourceMode;
  seed: number;
  simTime: number;
  shiftStart: number;
  version: number;
  layoutVersion: number;
  entitiesVersion: number;
  stockVersion: number;
  layout: Layout;
  cells: Cell[];
  cellIndex: Record<string, number>;
  gates: Gate[];
  resources: Resource[];
  tasks: WTask[];
  sts: Record<string, St>;
  trips: Trip[];
  collisions: Collision[];
  events: TwinEvent[];
  gateLog: GateLogEntry[];
  // Замечания к качеству данных источника (показываются в карточке площадки).
  dataNotes: string[];
  operations: TwinOperation[];
  executors: TwinExecutor[];
  connection: { state: ConnectionState; snapshotAt?: number; message?: string };
  opsStats: { inSnapshot: number; otherWarehouses: number; unbound: number; limitReached: boolean };
  counters: {
    seq: number;
    eventSeq: number;
    linesPicked: number;
    pickTimes: number[];
    palletsReceived: number;
    palletsShipped: number;
    replDone: number;
    replOnTime: number;
    nextOutboundAt: number;
    nextInboundAt: number;
    waveNo: number;
  };
};

export type SelectionKind = "trip" | "resource" | "gate" | "cell" | "st" | "collision" | "site" | "operation" | "executor";

export type Selection = { kind: SelectionKind; id: string };
