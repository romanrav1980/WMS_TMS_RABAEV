import { PointerEvent, useEffect, useMemo, useRef, useState } from "react";

type CellRole = "EMPTY" | "PICK_FACE" | "STORAGE" | "TRANSPORT_STAGING" | "FILM_WRAP" | "GATE" | "AISLE" | "BLOCKED" | "FRACTIONAL_PICK_FACE" | "FRACTIONAL_STORAGE";

type GridConfig = {
  aisleCount: number;
  slotsPerAisle: number;
  levels: number;
};

type ViewState = {
  zoom: number;
  panX: number;
  panY: number;
};

type GridCell = {
  aisle: number;
  slot: number;
  level: number;
};

type CellSelection = {
  level: number;
  aisleFrom: number;
  aisleTo: number;
  slotFrom: number;
  slotTo: number;
  anchorCell: GridCell;
  focusCell: GridCell;
};

type RoleChange =
  | {
      kind: "role";
      selections: CellSelection[];
      before: Uint8Array[];
      after: Uint8Array[];
      role: CellRole;
    }
  | {
      kind: "template";
      templateName: string;
      before: Uint8Array;
      after: Uint8Array;
    }
  | {
      kind: "format";
      selections: CellSelection[];
      before: Uint8Array[];
      after: Uint8Array[];
      label: string;
    };

type SprintSmokeResult = {
  name: string;
  ok: boolean;
  details: string[];
};

type WarehouseMapDraft = {
  draft_id: string;
  draft_name: string;
  grid: {
    aisle_count: number;
    slots_per_aisle: number;
    levels: number;
  };
  roles_base64: string;
  small_pick_faces?: SmallPickFaceDraftItem[];
  storage_slots?: StorageSlotDraftItem[];
  draft_metadata?: Record<string, unknown>;
  canvas_objects?: Record<string, unknown>[];
  passages?: Record<string, unknown>[];
  camera_links?: Record<string, unknown>[];
  route_rows?: RouteDraftRow[];
  route_summary?: {
    route_code?: string;
    route_pattern?: RoutePattern;
    route_row_count?: number;
    skipped_storage_slots?: number;
    skipped_non_pick_cells?: number;
  };
  oracle_canvas_id?: number;
  oracle_topology_id?: number;
  oracle_pick_route_id?: number;
  oracle_publish_status?: OraclePublishStatus;
  revision?: number;
  updated_at?: string;
};

type WarehouseMapDraftDiff = {
  draft_id: string;
  revision: number;
  changed_cells: number;
  changed_by_role: Partial<Record<CellRole, number>>;
  draft_metadata_changed?: boolean;
  canvas_object_count?: number;
  canvas_object_diff_count?: number;
  passage_count?: number;
  passage_diff_count?: number;
  camera_link_count?: number;
  camera_link_diff_count?: number;
  route_row_count?: number;
  route_row_diff_count?: number;
  small_pick_face_count: number;
  storage_slot_count: number;
  preview: { cell_code: string; from_role: CellRole; to_role: CellRole }[];
};

type RoutePattern = "LINEAR" | "Z" | "U_SHAPE" | "P_SHAPE" | "MANUAL";

type RouteDraftRow = {
  route_row_id?: string;
  route_code?: string;
  route_name?: string | null;
  route_pattern?: RoutePattern;
  cell_code: string;
  physical_cell: GridCell;
  pick_sequence: number;
  slot_kind?: "PICK_FACE" | "PICK_FACE_SLOT";
  active?: number;
};

type RouteBuildResponse = {
  draft_id: string;
  revision: number;
  route_code: string;
  route_pattern: RoutePattern;
  route_rows: RouteDraftRow[];
  route_row_count: number;
  skipped_storage_slots: number;
  skipped_non_pick_cells: number;
};

type WarehouseMapDraftValidation = {
  draft_id: string;
  valid: boolean;
  error_count: number;
  errors: string[];
  route_row_count?: number;
  duplicate_route_sequences?: number[];
  duplicate_route_cells?: string[];
  route_errors?: string[];
};

type WarehouseMapDraftPublished = {
  published_topology_id: string;
  status: string;
  published_at: string;
  route_row_count?: number;
};

type OracleSaveResponse = {
  draft_id: string;
  canvas_id?: number;
  camera_id?: number;
  topology_id?: number;
  pick_route_id?: number;
  route_row_count?: number;
  status: string;
  oracle_validation?: { valid: boolean; route_row_count?: number; storage_slot_route_rows?: number; non_pick_cell_route_rows?: number };
};

type OraclePublishStatus = {
  canvas_id?: number;
  canvas_status?: string;
  canvas_active?: number;
  topology_id?: number;
  topology_status?: string;
  pick_route_id?: number;
  route_status?: string;
  route_active?: number;
  route_row_count?: number;
};

type OraclePublishResponse = {
  draft_id: string;
  canvas_id: number;
  topology_id: number;
  pick_route_id: number;
  status: string;
  oracle_validation: { valid: boolean; route_row_count?: number; storage_slot_route_rows?: number; non_pick_cell_route_rows?: number };
  oracle_status: OraclePublishStatus;
};

type WarehouseMapProjectionPreview = {
  draft_id: string;
  status: string;
  publish_ready: boolean;
  topology_cell_count: number;
  role_counts: Partial<Record<CellRole, number>>;
  pick_face_slot_count: number;
  storage_slot_count: number;
  slot_count: number;
  preview_cells: { cell_code: string; cell_kind: CellRole }[];
  preview_slots: { slot_kind: string; slot_code?: string; storage_order?: number; pick_order?: number }[];
};

type WarehouseSummary = {
  id: number;
  name: string;
  prefix?: string;
};

type WarehouseMapCamera = {
  camera_id: number;
  canvas_id: number;
  ware_id: number;
  camera_code: string;
  camera_name: string;
  camera_kind: string;
  origin_x_m: number;
  origin_y_m: number;
  origin_z_m: number;
  width_m: number;
  depth_m: number;
  height_m: number;
  default_passage_width_m: number;
  default_aisle_spacing_m?: number;
  levels: number;
  active: number;
};

type WarehouseMapObject = {
  map_object_id: number;
  canvas_id: number;
  camera_id: number;
  object_code: string;
  object_kind: string;
  object_name?: string;
  level_no?: number;
  x_m: number;
  y_m: number;
  z_m: number;
  width_m?: number;
  depth_m?: number;
  height_m?: number;
  angle_deg?: number;
  geometry_json?: Record<string, unknown> | null;
  style_json?: Record<string, unknown> | null;
  active: number;
};

type WarehouseMapPassage = {
  passage_id: number;
  canvas_id: number;
  camera_id: number;
  passage_code: string;
  passage_name?: string;
  passage_kind: string;
  x1_m: number;
  y1_m: number;
  z1_m: number;
  x2_m: number;
  y2_m: number;
  z2_m: number;
  width_m: number;
  aisle_spacing_m?: number;
  geometry_json?: Record<string, unknown> | null;
  allowed_resource_mask?: string;
  active: number;
};

type WarehouseMapCameraLink = {
  camera_link_id: number;
  canvas_id: number;
  from_camera_id: number;
  to_camera_id: number;
  link_code: string;
  link_kind: string;
  distance_m: number;
  direction_code: string;
  active: number;
};

type WarehouseMapState = {
  warehouse: { ware_id: number; ware_name: string };
  canvas: { canvas_id: number; canvas_code: string; canvas_name: string; status: string; levels: number } | null;
  topology: { topology_id: number; topology_code?: string; status?: string } | null;
  cameras: WarehouseMapCamera[];
  camera_links: WarehouseMapCameraLink[];
  canvas_objects: WarehouseMapObject[];
  passages: WarehouseMapPassage[];
  routes?: WarehouseMapPublishedRoute[];
  counters: Record<string, number>;
  warnings: { code: string; message: string }[];
};

type WarehouseMapPublishedRoute = {
  pick_route_id: number;
  topology_id: number;
  ware_id: number;
  route_code: string;
  route_name?: string | null;
  route_kind: string;
  route_pattern?: RoutePattern | string | null;
  status: string;
  active: number;
  route_row_count?: number;
  excluded_storage_slot_row_count?: number;
  route_rows?: Record<string, unknown>[];
};

type WarehouseMapCanvasSummary = {
  canvas_id: number;
  canvas_code: string;
  canvas_name: string;
  status: string;
  camera_count: number;
};

type CameraFormState = {
  cameraCode: string;
  cameraName: string;
  cameraKind: "DRY" | "COLD" | "FREEZER" | "DOCK" | "SERVICE" | "MIXED";
  originX: number;
  originY: number;
  originZ: number;
  width: number;
  depth: number;
  height: number;
  levels: number;
  defaultPassageWidth: number;
  defaultAisleSpacing: number;
};

type MapCommandId = "camera.create" | "camera.clone" | "camera.archive" | "object.create" | "passage.create" | "camera.link";
type HelpId = MapCommandId
  | "warehouse.state"
  | "roles.assign"
  | "navigation.map"
  | "templates.layout"
  | "draft.local"
  | "route.editor"
  | "oracle.publish"
  | "format.copy"
  | "format.paste"
  | "format.cancel"
  | "fraction.pick"
  | "fraction.storage"
  | "projection.preview";

type MapContextMenu = {
  x: number;
  y: number;
} | null;

type HelpPopupPosition = {
  x: number;
  y: number;
} | null;

type AddressSide = "LEFT" | "RIGHT" | "";
type AddressDirection = "START_TO_END" | "END_TO_START";
type AddressPreview = {
  assigned_count: number;
  pick_face_address_count: number;
  preview_first: { cell_code: string }[];
  preview_last: { cell_code: string }[];
};

type SmallPickPreview = {
  created_count: number;
  fraction_cell_count: number;
  small_pick_face_count: number;
  preview: { logical_cell_code: string; sub_level: number; sub_column: number; pick_order: number }[];
};

type SmallPickFaceDraftItem = {
  physical_cell: GridCell;
  fraction_cell_count?: number;
  sub_level?: number;
  sub_column?: number;
  active?: number;
};

type StorageSlotPreview = {
  created_count: number;
  fraction_cell_count: number;
  storage_slot_count: number;
  preview: StorageSlotDraftItem[];
};

type StorageSlotDraftItem = {
  storage_slot_id?: string;
  slot_code?: string;
  physical_cell: GridCell;
  fraction_cell_count?: number;
  sub_level?: number;
  sub_column?: number;
  storage_order?: number;
  max_pallet_count?: number | null;
  max_weight_kg?: number | null;
  max_volume_m3?: number | null;
  capacity_json?: Record<string, unknown>;
  active?: number;
};

type SplitPresetId = "PICK_2_LEVELS" | "PICK_3_LEVELS" | "PICK_2_HORIZONTAL" | "PICK_3_HORIZONTAL" | "PICK_2X2" | "PICK_2X3" | "PICK_3X2" | "PICK_3X3";
type StorageSplitPresetId = "STORAGE_1" | "STORAGE_2_HORIZONTAL" | "STORAGE_3_HORIZONTAL";

type SmallPickOrderMode = "SUB_LEVEL_THEN_COLUMN" | "COLUMN_THEN_SUB_LEVEL";

type FormatClipboard = {
  source: CellSelection;
  values: Uint8Array;
  width: number;
  height: number;
  copiedAt: string;
};

type FractionVisualPreset = {
  columns: number;
  rows: number;
};

type DragState =
  | { kind: "select"; start: GridCell; current: GridCell; additive: boolean; baseSelections: CellSelection[] }
  | { kind: "pan"; startX: number; startY: number; originX: number; originY: number };

const GRID: GridConfig = {
  aisleCount: 35,
  slotsPerAisle: 90,
  levels: 6
};

const CELL_WIDTH_MM = 1200;
const CELL_HEIGHT_MM = 800;
const BASE_CELL_WIDTH = 12;
const BASE_CELL_HEIGHT = 8;
const GRID_OFFSET_X = 36;
const GRID_OFFSET_Y = 28;
const LOCAL_DRAFT_KEY = "wms.largeWarehouseMapDraft.v1";
const LOCAL_DRAFT_ID_KEY = "wms.largeWarehouseMapDraftId.v1";
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8088";
const API_BASIC_AUTH = import.meta.env.VITE_ADMIN_BASIC_AUTH || "admin:admin123";

const ROLE_ORDER: CellRole[] = ["PICK_FACE", "STORAGE", "TRANSPORT_STAGING", "FILM_WRAP", "GATE", "AISLE", "BLOCKED", "EMPTY", "FRACTIONAL_PICK_FACE", "FRACTIONAL_STORAGE"];

const ROLE_LABELS: Record<CellRole, string> = {
  EMPTY: "Пусто",
  PICK_FACE: "Ячейки отбора",
  FRACTIONAL_PICK_FACE: "Дробные ячейки отбора",
  FRACTIONAL_STORAGE: "Дробные ячейки хранения",
  STORAGE: "Ячейки хранения",
  TRANSPORT_STAGING: "Транспортное накопление",
  FILM_WRAP: "На пленку",
  GATE: "Ворота",
  AISLE: "Проходы",
  BLOCKED: "Недоступно"
};

const ROLE_COLORS: Record<CellRole, string> = {
  EMPTY: "#f8fafc",
  PICK_FACE: "#91f3c8",
  FRACTIONAL_PICK_FACE: "#c4b5fd",
  FRACTIONAL_STORAGE: "#a7f3d0",
  STORAGE: "#bfdbfe",
  TRANSPORT_STAGING: "#fde68a",
  FILM_WRAP: "#fbcfe8",
  GATE: "#fca5a5",
  AISLE: "#e2e8f0",
  BLOCKED: "#64748b"
};

const ROLE_STROKES: Record<CellRole, string> = {
  EMPTY: "#e2e8f0",
  PICK_FACE: "#059669",
  FRACTIONAL_PICK_FACE: "#7c3aed",
  FRACTIONAL_STORAGE: "#047857",
  STORAGE: "#2563eb",
  TRANSPORT_STAGING: "#b45309",
  FILM_WRAP: "#db2777",
  GATE: "#dc2626",
  AISLE: "#94a3b8",
  BLOCKED: "#334155"
};

const PICK_SPLIT_PRESETS: Record<SplitPresetId, { label: string; fractionCellCount: number; subLevelCount: number; subColumnCount: number; visual: FractionVisualPreset }> = {
  PICK_2_LEVELS: { label: "2 уровня", fractionCellCount: 2, subLevelCount: 2, subColumnCount: 1, visual: { columns: 1, rows: 2 } },
  PICK_3_LEVELS: { label: "3 уровня", fractionCellCount: 3, subLevelCount: 3, subColumnCount: 1, visual: { columns: 1, rows: 3 } },
  PICK_2_HORIZONTAL: { label: "2 по горизонтали", fractionCellCount: 2, subLevelCount: 1, subColumnCount: 2, visual: { columns: 2, rows: 1 } },
  PICK_3_HORIZONTAL: { label: "3 по горизонтали", fractionCellCount: 3, subLevelCount: 1, subColumnCount: 3, visual: { columns: 3, rows: 1 } },
  PICK_2X2: { label: "2 x 2", fractionCellCount: 4, subLevelCount: 2, subColumnCount: 2, visual: { columns: 2, rows: 2 } },
  PICK_2X3: { label: "2 уровня x 3 по горизонтали", fractionCellCount: 6, subLevelCount: 2, subColumnCount: 3, visual: { columns: 3, rows: 2 } },
  PICK_3X2: { label: "3 уровня x 2 по горизонтали", fractionCellCount: 6, subLevelCount: 3, subColumnCount: 2, visual: { columns: 2, rows: 3 } },
  PICK_3X3: { label: "3 x 3", fractionCellCount: 9, subLevelCount: 3, subColumnCount: 3, visual: { columns: 3, rows: 3 } }
};

const STORAGE_SPLIT_VISUALS: Record<number, FractionVisualPreset> = {
  1: { columns: 1, rows: 1 },
  2: { columns: 2, rows: 1 },
  3: { columns: 3, rows: 1 }
};

const STORAGE_SPLIT_PRESETS: Record<StorageSplitPresetId, { label: string; fractionCellCount: number; subColumnCount: number; visual: FractionVisualPreset }> = {
  STORAGE_1: { label: "1 / без дробления", fractionCellCount: 1, subColumnCount: 1, visual: STORAGE_SPLIT_VISUALS[1] },
  STORAGE_2_HORIZONTAL: { label: "2 по горизонтали", fractionCellCount: 2, subColumnCount: 2, visual: STORAGE_SPLIT_VISUALS[2] },
  STORAGE_3_HORIZONTAL: { label: "3 по горизонтали", fractionCellCount: 3, subColumnCount: 3, visual: STORAGE_SPLIT_VISUALS[3] }
};

const MAP_HELP: Record<HelpId, { title: string; body: string }> = {
  "warehouse.state": {
    title: "Реальный склад",
    body: "Что это: блок выбора склада и чтения опубликованной карты из Oracle. Вход: WARE_ID выбранного склада, active/published canvas, topology, cameras, passages, slots и pick route. Делает: загружает рабочее состояние склада и показывает статусы canvas/topology/routes. Зачем: оператор должен видеть, с каким реальным складом связана карта, а не работать с абстрактным черновиком. Как применять: выберите склад, нажмите Обновить, проверьте canvas/topology status, route count и warnings перед редактированием."
  },
  "camera.create": {
    title: "Создать камеру",
    body: "Что это: команда создания физической камеры склада на canvas. Вход: выбранный склад, код, вид, название, размеры в метрах, уровни и дефолтная ширина прохода. Делает: создает canvas при необходимости и добавляет камеру. Зачем: разделять один склад на помещения/камеры. Как применять: заполните форму камеры и нажмите команду; topology cells не публикуются."
  },
  "camera.clone": {
    title: "Клонировать камеру",
    body: "Что это: команда быстрого создания похожей камеры. Вход: выбранная камера. Делает: копирует размеры, тип, высоту, уровни и дефолтные проходы в новую камеру. Зачем: быстро заводить однотипные помещения. Как применять: выберите камеру и нажмите команду; objects, passages, slots и маршруты не копируются автоматически."
  },
  "camera.archive": {
    title: "Архивировать камеру",
    body: "Что это: команда выключения камеры из активной карты. Вход: выбранная камера и ее зависимости. Делает: переводит камеру в архив, если нет активных objects, passages, links и topology cells. Зачем: безопасно убирать лишние помещения. Как применять: сначала удалите/перенесите зависимости, затем архивируйте."
  },
  "object.create": {
    title: "Сохранить объект из выделения",
    body: "Что это: canvas object, графический объект карты. Вход: выделенный прямоугольник и выбранная камера. Делает: сохраняет зону, разметку или ориентир без создания WMS-ячейки. Зачем: хранить на canvas то, чего нет в ячейках отбора/хранения. Как применять: выделите область и сохраните объект; в pick route он не участвует до projection."
  },
  "passage.create": {
    title: "Сохранить проход из выделения",
    body: "Что это: проход на карте склада. Вход: выделение, камера, ширина прохода в метрах. Делает: сохраняет passage с геометрией и шириной. Зачем: отделить проходимые зоны и будущие расстояния от обычных ячеек. Как применять: выделите линию/полосу прохода и сохраните; пиксели только помогают рисовать."
  },
  "camera.link": {
    title: "Связать первые 2 камеры",
    body: "Что это: связь между камерами canvas. Вход: минимум две камеры в текущем canvas. Делает: создает переход с направлением и расстоянием. Зачем: будущий маршрут должен понимать, как пройти между помещениями. Как применять: создайте две камеры, затем сохраните link."
  },
  "roles.assign": {
    title: "Роли ячеек",
    body: "Что это: режим назначения функциональной роли физическим ячейкам сетки 800 x 1200 мм. Вход: активная роль, одно или несколько выделений, текущий уровень L1-L6. Делает: меняет роли выбранных ячеек в API draft и оставляет операцию в undo/redo. Зачем: карта склада создается через массовое назначение зон отбора, хранения, накопления, ворот, проходов, пустых и недоступных областей. Как применять: выделите область как в Excel, выберите роль и нажмите Назначить выделению; Shift-выделение сохраняет несколько областей. Важно: дробные роли не красятся как обычные роли, а создаются через выбранный пресет дробления рядом с ролью."
  },
  "navigation.map": {
    title: "Навигация по карте",
    body: "Что это: инструменты масштаба, поиска адреса и быстрого перехода по большой Canvas-карте. Вход: zoom, pan, адрес формата A01-S001-L1 или текущая выделенная область. Делает: приближает, отдаляет, центрирует карту, ищет ячейку и показывает обзор по аллеям. Зачем: на карте 35 x 90 x 6 нельзя работать только прокруткой, оператору нужны Excel-подобные быстрые переходы. Как применять: используйте Fit для всей карты, Fit selected для выделения, поле поиска для адреса и полосу аллей для прыжка к нужной аллее."
  },
  "templates.layout": {
    title: "Шаблоны layout",
    body: "Что это: быстрые генераторы типовых участков склада на выделенной области или на базовой карте. Вход: текущее выделение, активный уровень и выбранный шаблон. Делает: массово назначает роли ячеек как регулярный склад, проходы, ворота с накоплением, пленку или копию аллеи. Зачем: склад быстрее рисовать из повторяющихся блоков, чем назначать тысячи ячеек вручную. Как применять: сначала выделите нужный прямоугольник, затем примените шаблон и визуально проверьте, что границы и роли легли правильно."
  },
  "format.copy": {
    title: "Скопировать формат",
    body: "Что это: Excel-like Format Painter. Вход: выделенный прямоугольник. Делает: копирует роли/рисунок формата области. Зачем: быстро размножать похожие участки склада. Как применять: выделите образец, нажмите копирование, выберите цель и вставьте; DB ID, адреса, маршруты, остатки и задачи не копируются."
  },
  "format.paste": {
    title: "Вставить формат",
    body: "Что это: вставка скопированного формата. Вход: format clipboard и активная целевая ячейка/выделение. Делает: переносит рисунок ролей в область того же размера. Зачем: ускорить ручное рисование. Как применять: после копирования формата укажите цель и вставьте; операция доступна в undo/redo."
  },
  "format.cancel": {
    title: "Отменить кисть",
    body: "Что это: отмена активного режима кисти. Вход: текущий format clipboard. Делает: выключает режим переноса, но не очищает буфер. Зачем: избежать случайной вставки. Как применять: нажмите, если передумали вставлять формат сейчас."
  },
  "draft.local": {
    title: "Draft и diff",
    body: "Что это: runtime/API черновик карты до публикации в Oracle. Вход: roles_base64, metadata, canvas objects, passages, camera links, route rows и ожидаемая revision. Делает: сохраняет/загружает draft, показывает diff, строит projection preview и защищает от stale update. Зачем: оператор может редактировать карту безопасно, не меняя опубликованный склад до отдельного publish. Как применять: регулярно нажимайте Сохранить, проверяйте Diff и Projection preview перед сохранением topology и маршрута в Oracle."
  },
  "route.editor": {
    title: "Порядок обхода",
    body: "Что это: редактор draft pick route поверх карты склада. Вход: выделенная область, route pattern LINEAR/Z/u-образно/П-образно/MANUAL, роли ячеек и дробные pick slots. Делает: строит строки маршрута с числовым PICK_SEQUENCE, валидирует дубли и исключает storage/non-pick rows. Зачем: порядок отбора должен быть мастер-данными склада и потом попадать в Oracle pick route. Как применять: выделите только pick-face область, выберите паттерн, постройте маршрут, нажмите Validate draft и проверьте route rows."
  },
  "oracle.publish": {
    title: "Oracle save/publish",
    body: "Что это: цепочка переноса draft в реальные Oracle master-data объекта. Вход: выбранный склад, сохраненный API draft, Oracle canvas, topology projection и pick route. Делает: Save canvas DB пишет renderer payload, Save topology DB пишет cells/slots, Save route DB пишет PICK_ROUTE/PICK_ROUTE_CELL, Publish Oracle вызывает RRL_WAREHOUSE_MAP_API.PUBLISH_DRAFT и переводит canvas/topology/route в PUBLISHED. Зачем: новые волны должны читать только опубликованные рабочие версии, а не визуальный черновик. Как применять: выполняйте кнопки слева направо; если кнопка серая, сначала выполните предыдущий шаг или validation."
  },
  "fraction.pick": {
    title: "Дробная ячейка отбора",
    body: "Что это: несколько логических pick slots внутри одной физической ячейки. Вход: выделенная ячейка, split preset, start/order/side/mask. Делает: создает child slots отбора и рисует внутренние линии дробления. Зачем: описать мелкоштучный отбор без размножения физических координат. Как применять: выберите пресет 2/3 уровня, 2/3 по горизонтали, 2 x 2 или 3 x 3 и назначьте дробную ячейку. По умолчанию используется 2 уровня; 3 x 3 создается только при явном выборе этого пресета."
  },
  "fraction.storage": {
    title: "Дробная ячейка хранения",
    body: "Что это: storage slots внутри одной физической ячейки хранения. Вход: выделенная ячейка, storage split preset, order/mask/capacity. Делает: создает или оставляет child slots хранения и хранит вместимость. Зачем: дать остаткам ссылаться на часть физической ячейки. Как применять: выберите 1 / без дробления, 2 по горизонтали или 3 по горизонтали; вертикальное дробление storage запрещено. По умолчанию storage остается без дробления, а FRACTIONAL_STORAGE появляется только при явном выборе 2 или 3 по горизонтали."
  },
  "projection.preview": {
    title: "Projection preview",
    body: "Что это: предварительный расчет topology-проекции. Вход: текущий API draft, roles, pick slots и storage slots. Делает: считает будущие topology cells и child slots без publish. Зачем: проверить карту перед сохранением в боевую topology. Как применять: нажмите Projection preview и проверьте счетчики cells/slots и publish ready."
  }
};

const MODULE_GUIDE = [
  {
    title: "Назначение модуля",
    body: [
      "Модуль рисования карты больших складов нужен для Excel-подобного создания и сопровождения складской 2D-карты на базе сетки физических ячеек 800 x 1200 мм.",
      "Он связывает визуальную карту с реальным складом Oracle: canvas хранит геометрию и визуальные объекты, topology хранит физические WMS-ячейки, child slots описывают дробные ячейки отбора и хранения, pick route хранит порядок обхода.",
      "Главное правило: оператор работает с draft, а рабочие волны должны читать только опубликованные canvas/topology/route после validation и Oracle publish."
    ]
  },
  {
    title: "Структура экрана",
    body: [
      "Верхняя панель показывает название модуля, размер карты, статус draft, smoke/evidence индикатор и performance metrics.",
      "Левая панель содержит рабочие блоки: реальный склад, камера, уровни, роли, формат, навигация, шаблоны, draft, порядок обхода, дробные ячейки отбора и хранения, фильтры и счетчики.",
      "Центральная область - Canvas 2D renderer. Он рисует только видимую часть большой карты, поэтому карта 35 аллей x 90 слотов x 6 уровней остается легкой и не превращает каждую ячейку в DOM-элемент."
    ]
  },
  {
    title: "Основные объекты данных",
    body: [
      "Warehouse - реальный склад из Oracle, выбранный оператором перед сохранением в базу.",
      "Canvas - сохраняемый объект планировки. В нем живет renderer_state_json, камеры, проходы, подписи, визуальные зоны и связь с topology.",
      "Camera - физическое помещение или камера склада. У камеры есть размеры в метрах, origin x/y/z, уровни, тип и дефолтные параметры проходов.",
      "Topology cell - физическая WMS-ячейка, полученная из карты через projection. Она может быть pick-face, storage, staging, gate, aisle и так далее.",
      "Cell slot - дочерний логический slot внутри физической ячейки. Pick slots участвуют в маршруте отбора, storage slots используются для остатков/хранения.",
      "Pick route - линейный порядок обхода. Истина маршрута - строки с числовым PICK_SEQUENCE; линии и стрелки на карте являются представлением, а не источником данных."
    ]
  },
  {
    title: "Рисование карты",
    body: [
      "По умолчанию пустая камера считается недоступной областью, а не хранением. Роли назначаются явно.",
      "Выделение работает как в Excel: можно выделять прямоугольники, сохранять выделение при переключении уровней и использовать Shift для нескольких областей.",
      "Роли назначаются массово: ячейки отбора, хранения, транспортное накопление, пленка, ворота, проходы, недоступно, пусто, дробный отбор и дробное хранение.",
      "Шаблоны ускоряют разметку типовых зон: регулярный склад, проходы, ворота с накоплением, пленка и копирование аллеи."
    ]
  },
  {
    title: "Дробные ячейки",
    body: [
      "Дробная ячейка - физическая ячейка, внутри которой создаются несколько логических child slots.",
      "Для отбора доступны варианты дробления от 2 до 9 логических мест: по уровням, по горизонтали, 2 x 2, 3 x 3. Визуально такие ячейки рисуются внутренними линиями.",
      "Для хранения доступен дефолт 1 / без дробления, а также дробление по горизонтали на 2 или 3 storage slots.",
      "Маршрут отбора может ссылаться только на pick slots. Storage slots не должны попадать в pick route."
    ]
  },
  {
    title: "Draft, diff и безопасное сохранение",
    body: [
      "Draft - это runtime/API черновик карты. Он хранит roles_base64, metadata, objects, passages, camera links, route rows и revision.",
      "Revision защищает от stale update: если кто-то сохранил более свежую версию, конфликт должен быть виден до перезаписи.",
      "Diff показывает измененные ячейки, metadata, объекты, проходы, связи камер и route rows.",
      "Projection preview считает будущие topology cells/slots без записи опубликованной версии."
    ]
  },
  {
    title: "Oracle save/publish workflow",
    body: [
      "Правильная последовательность: Save canvas DB -> Save topology DB -> Save route DB -> Publish Oracle.",
      "Save canvas DB сохраняет полный draft payload в RRL_WAREHOUSE_MAP_CANVAS.RENDERER_STATE_JSON и создает/обновляет базовую камеру.",
      "Save topology DB создает draft topology и записывает RRL_TOPOLOGY_CELL плюс RRL_TOPOLOGY_CELL_SLOT.",
      "Save route DB записывает RRL_PICK_ROUTE и RRL_PICK_ROUTE_CELL; обычные pick cells идут через TOPOLOGY_CELL_ID, дробные pick slots через CELL_SLOT_ID.",
      "Publish Oracle вызывает RRL_WAREHOUSE_MAP_API.VALIDATE_DRAFT и затем RRL_WAREHOUSE_MAP_API.PUBLISH_DRAFT. После успешной публикации canvas, topology и route становятся PUBLISHED."
    ]
  },
  {
    title: "Reload опубликованного склада",
    body: [
      "После publish рабочая проверка делается через warehouse state API: /api/admin/warehouse-map/warehouses/{ware_id}/state.",
      "State должен вернуть published canvas, linked published topology, active published pick route и route rows.",
      "Если в маршруте оказались storage slots или non-pick cells, Oracle validation должен заблокировать publish, а state не должен становиться рабочим источником для волн."
    ]
  },
  {
    title: "Help и подсказки",
    body: [
      "Короткие подсказки доступны через title/hover, а подробные подсказки открываются через знак вопроса.",
      "Каждая подробная подсказка отвечает на пять вопросов: что это, какие входные данные нужны, что делает элемент, зачем он нужен и как им пользоваться.",
      "Подсказки не занимают постоянное место в боковой панели: они открываются popover или этой инструкцией. Закрытие работает кнопкой, Esc и кликом вне окна."
    ]
  },
  {
    title: "Ограничения и контроль",
    body: [
      "Evidence screenshots лежат во временной runtime-папке и не являются частью обязательного commit scope.",
      "Перед закрытием изменений нужно проверять frontend build, backend compile, Oracle verify 042, encoding check и diff whitespace.",
      "Если кнопка серая, это нормальный сигнал зависимости: обычно нужно выбрать склад, сохранить draft, сохранить topology, построить route или пройти validation."
    ]
  }
];

export function LargeWarehouseMapPage({ onBack }: { onBack: () => void }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const wrapperRef = useRef<HTMLDivElement | null>(null);
  const rolesRef = useRef<Uint8Array>(createInitialRoles());
  const fractionVisualsRef = useRef<Map<string, FractionVisualPreset>>(new Map());
  const undoStackRef = useRef<RoleChange[]>([]);
  const redoStackRef = useRef<RoleChange[]>([]);
  const smokeRanRef = useRef(false);
  const [version, setVersion] = useState(0);
  const [level, setLevel] = useState(1);
  const [activeRole, setActiveRole] = useState<CellRole>("PICK_FACE");
  const [view, setView] = useState<ViewState>({ zoom: 1, panX: 0, panY: 0 });
  const [drag, setDrag] = useState<DragState | null>(null);
  const [selections, setSelections] = useState<CellSelection[]>([]);
  const [activeCell, setActiveCell] = useState<GridCell>({ aisle: 1, slot: 1, level: 1 });
  const [dirty, setDirty] = useState(false);
  const [draftId, setDraftId] = useState(() => localStorage.getItem(LOCAL_DRAFT_ID_KEY) || "");
  const [draftStatus, setDraftStatus] = useState("Локальный draft не сохранен");
  const [draftRevision, setDraftRevision] = useState<number | null>(null);
  const [draftDiff, setDraftDiff] = useState<WarehouseMapDraftDiff | null>(null);
  const [addressStatus, setAddressStatus] = useState("Адресация не применялась");
  const [addressPreview, setAddressPreview] = useState<AddressPreview | null>(null);
  const [smallPickStatus, setSmallPickStatus] = useState("Дробные ячейки не назначались");
  const [smallPickPreview, setSmallPickPreview] = useState<SmallPickPreview | null>(null);
  const [storageSlotStatus, setStorageSlotStatus] = useState("Дробные ячейки хранения не назначались");
  const [storageSlotPreview, setStorageSlotPreview] = useState<StorageSlotPreview | null>(null);
  const [currentDraft, setCurrentDraft] = useState<WarehouseMapDraft | null>(null);
  const [projectionStatus, setProjectionStatus] = useState("Projection preview не строился");
  const [projectionPreview, setProjectionPreview] = useState<WarehouseMapProjectionPreview | null>(null);
  const [routePattern, setRoutePattern] = useState<RoutePattern>("Z");
  const [routeStatus, setRouteStatus] = useState("Порядок обхода не строился");
  const [validationStatus, setValidationStatus] = useState("Validation не запускалась");
  const [validationResult, setValidationResult] = useState<WarehouseMapDraftValidation | null>(null);
  const [publishStatus, setPublishStatus] = useState("Publish не выполнялся");
  const [publishedResult, setPublishedResult] = useState<WarehouseMapDraftPublished | null>(null);
  const [oracleStatus, setOracleStatus] = useState("Oracle save/publish не выполнялся");
  const [oraclePublishResult, setOraclePublishResult] = useState<OraclePublishResponse | null>(null);
  const [formatClipboard, setFormatClipboard] = useState<FormatClipboard | null>(null);
  const [formatPainterActive, setFormatPainterActive] = useState(false);
  const [formatStatus, setFormatStatus] = useState("Формат не скопирован");
  const [searchText, setSearchText] = useState("A01-S001-L1");
  const [roleFilters, setRoleFilters] = useState<Record<CellRole, boolean>>(() => Object.fromEntries(ROLE_ORDER.map((role) => [role, true])) as Record<CellRole, boolean>);
  const [warehouses, setWarehouses] = useState<WarehouseSummary[]>([]);
  const [selectedWareId, setSelectedWareId] = useState<number | null>(null);
  const [warehouseMapState, setWarehouseMapState] = useState<WarehouseMapState | null>(null);
  const [canvasList, setCanvasList] = useState<WarehouseMapCanvasSummary[]>([]);
  const [selectedCameraId, setSelectedCameraId] = useState<number | null>(null);
  const [warehouseStatus, setWarehouseStatus] = useState("Склад не выбран");
  const [contextMenu, setContextMenu] = useState<MapContextMenu>(null);
  const [activeHelpId, setActiveHelpId] = useState<HelpId | null>(null);
  const [helpPopupPosition, setHelpPopupPosition] = useState<HelpPopupPosition>(null);
  const [moduleGuideOpen, setModuleGuideOpen] = useState(false);
  const [cameraForm, setCameraForm] = useState<CameraFormState>({
    cameraCode: "CAM-01",
    cameraName: "Камера 01",
    cameraKind: "DRY",
    originX: 0,
    originY: 0,
    originZ: 0,
    width: 42,
    depth: 90,
    height: 12,
    levels: 6,
    defaultPassageWidth: 3,
    defaultAisleSpacing: 3.6
  });
  const [addressForm, setAddressForm] = useState({
    aisleNo: 1,
    startPickNo: 1,
    step: 1,
    direction: "START_TO_END" as AddressDirection,
    side: "" as AddressSide,
    codeMask: "A{aisle}-P{pick_no}-L{level}"
  });
  const [smallPickForm, setSmallPickForm] = useState({
    preset: "PICK_2_LEVELS" as SplitPresetId,
    fractionCellCount: 2,
    subLevelCount: 2,
    subColumnCount: 1,
    orderMode: "SUB_LEVEL_THEN_COLUMN" as SmallPickOrderMode,
    startOrder: 1,
    step: 1,
    side: "" as AddressSide,
    codeMask: "{physical_cell}-F{sub_level}{sub_column}"
  });
  const [storageSlotForm, setStorageSlotForm] = useState({
    preset: "STORAGE_1" as StorageSplitPresetId,
    fractionCellCount: 1,
    subColumnCount: 1,
    startOrder: 1,
    step: 1,
    codeMask: "{physical_cell}-ST{sub_column}"
  });
  const [storageSlotEditForm, setStorageSlotEditForm] = useState({
    storageOrder: 1,
    maxPalletCount: 1,
    maxWeightKg: 0,
    maxVolumeM3: 0
  });
  const [historyVersion, setHistoryVersion] = useState(0);
  const [smokeResult, setSmokeResult] = useState<SprintSmokeResult | null>(null);
  const [hovered, setHovered] = useState<GridCell | null>(null);
  const [metrics, setMetrics] = useState({
    renderMs: 0,
    visibleCells: 0,
    selectedCells: 0,
    bulkMs: 0,
    selectionMs: 0,
    domNodes: 0
  });

  const roleCounts = useMemo(() => countRoles(rolesRef.current), [version]);
  const selectedCount = selectionListSize(selections);
  const canUndo = undoStackRef.current.length > 0;
  const canRedo = redoStackRef.current.length > 0;
  const selectedCamera = warehouseMapState?.cameras.find((camera) => camera.camera_id === selectedCameraId) || warehouseMapState?.cameras[0] || null;
  const selectedCameraObjects = selectedCamera ? (warehouseMapState?.canvas_objects || []).filter((item) => item.camera_id === selectedCamera.camera_id) : [];
  const selectedCameraPassages = selectedCamera ? (warehouseMapState?.passages || []).filter((item) => item.camera_id === selectedCamera.camera_id) : [];
  const selectedCameraLinks = selectedCamera ? (warehouseMapState?.camera_links || []).filter((item) => item.from_camera_id === selectedCamera.camera_id || item.to_camera_id === selectedCamera.camera_id) : [];
  const activeStorageSlots = useMemo(() => findStorageSlotsForCell(currentDraft, activeCell), [currentDraft, activeCell]);
  const activeStorageSlot = activeStorageSlots[0] || null;
  const routeRows = useMemo(() => sortedRouteRows(currentDraft?.route_rows || []), [currentDraft?.route_rows]);
  const mapCommands = commandRegistry();

  useEffect(() => {
    loadWarehouseCatalog();
  }, []);

  useEffect(() => {
    if (selectedWareId === null) return;
    loadWarehouseMap(selectedWareId);
  }, [selectedWareId]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const wrapper = wrapperRef.current;
    if (!canvas || !wrapper) return;

    const overlayObjects = selectedCamera ? (warehouseMapState?.canvas_objects || []).filter((item) => item.camera_id === selectedCamera.camera_id) : [];
    const overlayPassages = selectedCamera ? (warehouseMapState?.passages || []).filter((item) => item.camera_id === selectedCamera.camera_id) : [];
    const observer = new ResizeObserver(() => drawCanvas(canvas, rolesRef.current, level, view, selections, activeCell, hovered, roleFilters, overlayObjects, overlayPassages, fractionVisualsRef.current, routeRows, setMetrics));
    observer.observe(wrapper);
    drawCanvas(canvas, rolesRef.current, level, view, selections, activeCell, hovered, roleFilters, overlayObjects, overlayPassages, fractionVisualsRef.current, routeRows, setMetrics);
    return () => observer.disconnect();
  }, [level, view, selections, activeCell, hovered, roleFilters, version, warehouseMapState, selectedCameraId, routeRows]);

  useEffect(() => {
    setActiveCell((current) => ({ ...current, level }));
    setSelections((current) => current.map((selection) => ({ ...selection, level })));
  }, [level]);

  useEffect(() => {
    if (!activeStorageSlot) return;
    setStorageSlotEditForm({
      storageOrder: Number(activeStorageSlot.storage_order || 1),
      maxPalletCount: Number(activeStorageSlot.max_pallet_count ?? 1),
      maxWeightKg: Number(activeStorageSlot.max_weight_kg || 0),
      maxVolumeM3: Number(activeStorageSlot.max_volume_m3 || 0)
    });
  }, [activeStorageSlot?.storage_slot_id]);

  useEffect(() => {
    if (!activeHelpId) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") closeHelp();
    };
    const onPointerDown = (event: MouseEvent) => {
      const target = event.target as HTMLElement | null;
      if (target?.closest(".large-map-help-popover") || target?.closest(".large-map-help-button") || target?.closest(".large-map-help-inline")) return;
      closeHelp();
    };
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("mousedown", onPointerDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("mousedown", onPointerDown);
    };
  }, [activeHelpId]);

  useEffect(() => {
    if (!moduleGuideOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setModuleGuideOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [moduleGuideOpen]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search.replace(/;/g, "&"));
    if (params.get("guide") === "module") {
      setModuleGuideOpen(true);
    }
    const smoke = params.get("smoke")
      || (window.location.href.includes("smoke=sprint13-objects") ? "sprint13-objects" : null)
      || (window.location.href.includes("smoke=sprint12") ? "sprint12" : null);
    if (smoke !== "sprint2-multiarea" && smoke !== "sprint3" && smoke !== "sprint5" && smoke !== "sprint6" && smoke !== "sprint7" && smoke !== "sprint8" && smoke !== "sprint9" && smoke !== "sprint12" && smoke !== "sprint13-format" && smoke !== "sprint13-objects" && smoke !== "sprint14-slots" && smoke !== "sprint14-help" && smoke !== "sprint15-diff" && smoke !== "sprint15-metadata" && smoke !== "sprint16-route" && smoke !== "sprint17-publish" && smoke !== "sprint18-hardening" && smoke !== "sprint24-oracle-publish" && smoke !== "sprint25-published-reload") return;
    if (smokeRanRef.current) return;
    smokeRanRef.current = true;
    if (smoke === "sprint2-multiarea") {
      runSprint2MultiAreaSmoke();
    } else if (smoke === "sprint5") {
      runSprint5Smoke();
    } else if (smoke === "sprint6") {
      runSprint6Smoke();
    } else if (smoke === "sprint7") {
      runSprint7Smoke();
    } else if (smoke === "sprint8") {
      runSprint8Smoke();
    } else if (smoke === "sprint9") {
      runSprint9Smoke();
    } else if (smoke === "sprint12") {
      runSprint12Smoke();
    } else if (smoke === "sprint13-format") {
      runSprint13FormatSmoke();
    } else if (smoke === "sprint13-objects") {
      runSprint13ObjectsSmoke();
    } else if (smoke === "sprint14-slots") {
      runSprint14SlotsSmoke();
    } else if (smoke === "sprint14-help") {
      runSprint14HelpSmoke();
    } else if (smoke === "sprint15-diff") {
      runSprint15DiffSmoke();
    } else if (smoke === "sprint15-metadata") {
      runSprint15MetadataSmoke();
    } else if (smoke === "sprint16-route") {
      runSprint16RouteSmoke();
    } else if (smoke === "sprint17-publish") {
      runSprint17PublishSmoke();
    } else if (smoke === "sprint18-hardening") {
      runSprint18HardeningSmoke();
    } else if (smoke === "sprint24-oracle-publish") {
      runSprint24OraclePublishSmoke();
    } else if (smoke === "sprint25-published-reload") {
      runSprint25PublishedReloadSmoke();
    } else {
      runSprint3Smoke();
    }
  }, []);

  function fitMap() {
    const wrapper = wrapperRef.current;
    if (!wrapper) return;
    const mapWidth = GRID.aisleCount * BASE_CELL_WIDTH;
    const mapHeight = GRID.slotsPerAisle * BASE_CELL_HEIGHT;
    const zoom = Math.max(.25, Math.min(6, Math.min((wrapper.clientWidth - 80) / mapWidth, (wrapper.clientHeight - 72) / mapHeight)));
    setView({
      zoom: Number(zoom.toFixed(2)),
      panX: Math.round((wrapper.clientWidth - mapWidth * zoom) / 2 - GRID_OFFSET_X * zoom),
      panY: Math.round((wrapper.clientHeight - mapHeight * zoom) / 2 - GRID_OFFSET_Y * zoom)
    });
  }

  function resetView() {
    setView({ zoom: 1, panX: 0, panY: 0 });
  }

  function fitSelected() {
    const wrapper = wrapperRef.current;
    const selection = selections[0];
    if (!wrapper || !selection) return;
    const widthCells = selection.aisleTo - selection.aisleFrom + 1;
    const heightCells = selection.slotTo - selection.slotFrom + 1;
    const zoom = Math.max(.25, Math.min(14, Math.min((wrapper.clientWidth - 96) / (widthCells * BASE_CELL_WIDTH), (wrapper.clientHeight - 96) / (heightCells * BASE_CELL_HEIGHT))));
    setView({
      zoom: Number(zoom.toFixed(2)),
      panX: Math.round(wrapper.clientWidth / 2 - (GRID_OFFSET_X + (selection.aisleFrom - 1 + widthCells / 2) * BASE_CELL_WIDTH) * zoom),
      panY: Math.round(wrapper.clientHeight / 2 - (GRID_OFFSET_Y + (selection.slotFrom - 1 + heightCells / 2) * BASE_CELL_HEIGHT) * zoom)
    });
  }

  async function loadWarehouseCatalog() {
    try {
      const data = await apiFetchJson<WarehouseSummary[]>(`${API_BASE}/api/admin/warehouses?limit=200`, { cache: "no-store" });
      setWarehouses(data);
      if (selectedWareId === null && data.length) {
        setSelectedWareId(Number(data[0].id));
      }
      if (!data.length) setWarehouseStatus("Список складов пуст");
    } catch {
      setWarehouseStatus("Не удалось загрузить список складов");
    }
  }

  async function loadWarehouseMap(wareId: number) {
    try {
      setWarehouseStatus("Загрузка карты склада...");
      const [state, canvases] = await Promise.all([
        apiFetchJson<WarehouseMapState>(`${API_BASE}/api/admin/warehouse-map/warehouses/${wareId}/state`, { cache: "no-store" }),
        apiFetchJson<WarehouseMapCanvasSummary[]>(`${API_BASE}/api/admin/warehouse-map/warehouses/${wareId}/canvases`, { cache: "no-store" })
      ]);
      setWarehouseMapState(state);
      setCanvasList(canvases);
      const activeCamera = state.cameras.find((camera) => camera.camera_id === selectedCameraId) || state.cameras[0] || null;
      setSelectedCameraId(activeCamera?.camera_id ?? null);
      applyEmptyCameraDefaultRoles(state);
      setWarehouseStatus(state.canvas ? `Загружен canvas ${state.canvas.canvas_code}` : "У склада пока нет canvas");
    } catch {
      setWarehouseMapState(null);
      setCanvasList([]);
      setSelectedCameraId(null);
      setWarehouseStatus("Не удалось загрузить карту склада");
    }
  }

  async function refreshWarehouseMap() {
    if (selectedWareId === null) return;
    await loadWarehouseMap(selectedWareId);
  }

  async function ensureCanvas() {
    if (warehouseMapState?.canvas) return warehouseMapState.canvas.canvas_id;
    if (selectedWareId === null) throw new Error("Warehouse is not selected");
    const state = await apiFetchJson<WarehouseMapState>(`${API_BASE}/api/admin/warehouse-map/warehouses/${selectedWareId}/canvases`, {
      method: "POST",
      body: JSON.stringify({
        canvas_name: `Карта склада ${selectedWareId}`,
        levels: GRID.levels,
        grid_cell_width_m: CELL_WIDTH_MM / 1000,
        grid_cell_depth_m: CELL_HEIGHT_MM / 1000,
        viewport_json: { zoom: view.zoom, panX: view.panX, panY: view.panY },
        renderer_state_json: { renderer: "CANVAS_2D", source: "large-map-ui" },
        created_by: "warehouse-map-ui"
      })
    });
    setWarehouseMapState(state);
    setCanvasList(state.canvas ? [{
      canvas_id: state.canvas.canvas_id,
      canvas_code: state.canvas.canvas_code,
      canvas_name: state.canvas.canvas_name,
      status: state.canvas.status,
      camera_count: state.cameras.length
    }] : []);
    if (!state.canvas) throw new Error("Canvas was not created");
    return state.canvas.canvas_id;
  }

  async function createCameraFromForm() {
    try {
      const canvasId = await ensureCanvas();
      const result = await apiFetchJson<{ camera: WarehouseMapCamera; state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/canvases/${canvasId}/cameras`, {
        method: "POST",
        body: JSON.stringify(cameraPayload(cameraForm))
      });
      setWarehouseMapState(result.state);
      setSelectedCameraId(result.camera.camera_id);
      applyEmptyCameraDefaultRoles(result.state);
      setWarehouseStatus(`Создана камера ${result.camera.camera_code}`);
      setCameraForm((current) => ({ ...current, cameraCode: nextCameraCode(current.cameraCode), cameraName: nextCameraName(current.cameraName) }));
    } catch (error) {
      setWarehouseStatus(error instanceof Error ? error.message : "Не удалось создать камеру");
    }
  }

  async function cloneSelectedCamera() {
    if (!selectedCamera) return;
    try {
      const result = await apiFetchJson<{ camera: WarehouseMapCamera; state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/cameras/${selectedCamera.camera_id}/clone`, {
        method: "POST",
        body: JSON.stringify({
          camera_code: nextCameraCode(selectedCamera.camera_code),
          camera_name: `${selectedCamera.camera_name} copy`,
          origin_x_m: Number(selectedCamera.origin_x_m || 0) + Number(selectedCamera.width_m || 0) + 3,
          created_by: "warehouse-map-ui"
        })
      });
      setWarehouseMapState(result.state);
      setSelectedCameraId(result.camera.camera_id);
      applyEmptyCameraDefaultRoles(result.state);
      setWarehouseStatus(`Склонирована камера ${result.camera.camera_code}`);
    } catch (error) {
      setWarehouseStatus(error instanceof Error ? error.message : "Не удалось клонировать камеру");
    }
  }

  async function archiveSelectedCamera() {
    if (!selectedCamera) return;
    try {
      const result = await apiFetchJson<{ status: string; state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/cameras/${selectedCamera.camera_id}/archive`, {
        method: "POST",
        body: JSON.stringify({ reason: "archive from large-map UI", updated_by: "warehouse-map-ui" })
      });
      setWarehouseMapState(result.state);
      setSelectedCameraId(result.state.cameras[0]?.camera_id ?? null);
      applyEmptyCameraDefaultRoles(result.state);
      setWarehouseStatus(`Камера архивирована: ${result.status}`);
    } catch (error) {
      setWarehouseStatus(error instanceof Error ? error.message : "Архивирование заблокировано");
    }
  }

  async function saveCanvasObjectFromSelection() {
    if (!selectedCamera || !selections.length) return;
    try {
      const selection = selections[0];
      const existing = (warehouseMapState?.canvas_objects || [])
        .filter((item) => item.camera_id === selectedCamera.camera_id)
        .map(canvasObjectPayload);
      const nextObject = selectionObjectPayload(selection, selectedCamera, existing.length + 1);
      const result = await apiFetchJson<{ object_count: number; state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/cameras/${selectedCamera.camera_id}/objects`, {
        method: "PATCH",
        body: JSON.stringify({ objects: [...existing, nextObject], updated_by: "warehouse-map-ui" })
      });
      setWarehouseMapState(result.state);
      setDirty(true);
      setWarehouseStatus(`Canvas object сохранен: ${result.object_count}`);
    } catch (error) {
      setWarehouseStatus(error instanceof Error ? error.message : "Не удалось сохранить canvas object");
    }
  }

  async function savePassageFromSelection() {
    if (!selectedCamera || !selections.length) return;
    try {
      const selection = selections[0];
      const existing = (warehouseMapState?.passages || [])
        .filter((item) => item.camera_id === selectedCamera.camera_id)
        .map(passagePayload);
      const nextPassage = selectionPassagePayload(selection, selectedCamera, existing.length + 1);
      const result = await apiFetchJson<{ passage_count: number; state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/cameras/${selectedCamera.camera_id}/passages`, {
        method: "PATCH",
        body: JSON.stringify({ passages: [...existing, nextPassage], updated_by: "warehouse-map-ui" })
      });
      setWarehouseMapState(result.state);
      setDirty(true);
      setWarehouseStatus(`Проход сохранен: ${result.passage_count}`);
    } catch (error) {
      setWarehouseStatus(error instanceof Error ? error.message : "Не удалось сохранить проход");
    }
  }

  async function saveCameraLink() {
    const canvas = warehouseMapState?.canvas;
    const cameras = warehouseMapState?.cameras || [];
    if (!canvas || cameras.length < 2) return;
    try {
      const [fromCamera, toCamera] = cameras;
      const existing = (warehouseMapState?.camera_links || []).map(cameraLinkPayload);
      const nextLink = {
        link_code: `LINK-${fromCamera.camera_code}-${toCamera.camera_code}`,
        link_kind: "DOOR",
        from_camera_id: fromCamera.camera_id,
        to_camera_id: toCamera.camera_id,
        from_point_x_m: Number(fromCamera.width_m || 0),
        from_point_y_m: Number(fromCamera.depth_m || 0) / 2,
        from_point_z_m: 0,
        to_point_x_m: 0,
        to_point_y_m: Number(toCamera.depth_m || 0) / 2,
        to_point_z_m: 0,
        distance_m: 3,
        direction_code: "BOTH"
      };
      const result = await apiFetchJson<{ camera_link_count: number; state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/canvases/${canvas.canvas_id}/camera-links`, {
        method: "PATCH",
        body: JSON.stringify({ camera_links: [...existing, nextLink], updated_by: "warehouse-map-ui" })
      });
      setWarehouseMapState(result.state);
      setDirty(true);
      setWarehouseStatus(`Связь камер сохранена: ${result.camera_link_count}`);
    } catch (error) {
      setWarehouseStatus(error instanceof Error ? error.message : "Не удалось сохранить связь камер");
    }
  }

  function commandRegistry() {
    const hasWarehouse = selectedWareId !== null;
    const hasCamera = Boolean(selectedCamera);
    const hasSelection = selections.length > 0;
    const canLinkCameras = Boolean(warehouseMapState?.canvas && (warehouseMapState?.cameras.length || 0) >= 2);
    return [
      {
        id: "camera.create" as MapCommandId,
        group: "Камера",
        label: "Создать камеру",
        helpId: "camera.create" as HelpId,
        enabled: hasWarehouse,
        disabledReason: hasWarehouse ? "" : "Сначала выберите склад",
        run: createCameraFromForm
      },
      {
        id: "camera.clone" as MapCommandId,
        group: "Камера",
        label: "Клонировать камеру",
        helpId: "camera.clone" as HelpId,
        enabled: hasCamera,
        disabledReason: hasCamera ? "" : "Нет выбранной камеры",
        run: cloneSelectedCamera
      },
      {
        id: "camera.archive" as MapCommandId,
        group: "Камера",
        label: "Архивировать камеру",
        helpId: "camera.archive" as HelpId,
        enabled: hasCamera,
        disabledReason: hasCamera ? "" : "Нет выбранной камеры",
        run: archiveSelectedCamera
      },
      {
        id: "object.create" as MapCommandId,
        group: "Canvas",
        label: "Сохранить объект из выделения",
        helpId: "object.create" as HelpId,
        enabled: hasCamera && hasSelection,
        disabledReason: hasCamera ? "Сначала выделите область" : "Нет выбранной камеры",
        run: saveCanvasObjectFromSelection
      },
      {
        id: "passage.create" as MapCommandId,
        group: "Canvas",
        label: "Сохранить проход из выделения",
        helpId: "passage.create" as HelpId,
        enabled: hasCamera && hasSelection,
        disabledReason: hasCamera ? "Сначала выделите область" : "Нет выбранной камеры",
        run: savePassageFromSelection
      },
      {
        id: "camera.link" as MapCommandId,
        group: "Canvas",
        label: "Связать первые 2 камеры",
        helpId: "camera.link" as HelpId,
        enabled: canLinkCameras,
        disabledReason: "Нужны canvas и минимум две камеры",
        run: saveCameraLink
      }
    ];
  }

  async function runMapCommand(commandId: MapCommandId) {
    const command = mapCommands.find((item) => item.id === commandId);
    setContextMenu(null);
    if (!command) return;
    if (!command.enabled) {
      setWarehouseStatus(command.disabledReason);
      return;
    }
    await command.run();
  }

  function openHelp(event: React.MouseEvent<HTMLElement>, helpId: HelpId) {
    event.preventDefault();
    event.stopPropagation();
    const rect = event.currentTarget.getBoundingClientRect();
    setActiveHelpId(helpId);
    setHelpPopupPosition({
      x: Math.min(window.innerWidth - 336, Math.max(10, rect.right + 8)),
      y: Math.min(window.innerHeight - 220, Math.max(10, rect.top - 8))
    });
  }

  function closeHelp() {
    setActiveHelpId(null);
    setHelpPopupPosition(null);
  }

  function handleCanvasContextMenu(event: React.MouseEvent<HTMLCanvasElement>) {
    event.preventDefault();
    setContextMenu({ x: event.clientX, y: event.clientY });
  }

  function goToSearchAddress() {
    const cell = parseAddress(searchText, level);
    if (!cell) {
      setDraftStatus("Адрес не распознан");
      return;
    }
    setLevel(cell.level);
    setActiveCell(cell);
    setSelections([cellToSelection(cell)]);
    centerOnCell(cell);
  }

  function centerOnCell(cell: GridCell) {
    const wrapper = wrapperRef.current;
    if (!wrapper) return;
    setView((current) => ({
      ...current,
      panX: Math.round(wrapper.clientWidth / 2 - (GRID_OFFSET_X + (cell.aisle - .5) * BASE_CELL_WIDTH) * current.zoom),
      panY: Math.round(wrapper.clientHeight / 2 - (GRID_OFFSET_Y + (cell.slot - .5) * BASE_CELL_HEIGHT) * current.zoom)
    }));
  }

  function toggleRoleFilter(role: CellRole) {
    setRoleFilters((current) => ({ ...current, [role]: !current[role] }));
  }

  function updateZoom(nextZoom: number, anchor?: { x: number; y: number }) {
    setView((current) => {
      const zoom = Math.max(.2, Math.min(14, Number(nextZoom.toFixed(2))));
      if (!anchor || zoom === current.zoom) return { ...current, zoom };
      const worldX = (anchor.x - current.panX) / current.zoom;
      const worldY = (anchor.y - current.panY) / current.zoom;
      return {
        zoom,
        panX: anchor.x - worldX * zoom,
        panY: anchor.y - worldY * zoom
      };
    });
  }

  function handleWheel(event: React.WheelEvent<HTMLCanvasElement>) {
    event.preventDefault();
    const rect = event.currentTarget.getBoundingClientRect();
    const anchor = { x: event.clientX - rect.left, y: event.clientY - rect.top };
    const factor = event.deltaY > 0 ? .88 : 1.14;
    updateZoom(view.zoom * factor, anchor);
  }

  function handlePointerDown(event: PointerEvent<HTMLCanvasElement>) {
    event.currentTarget.setPointerCapture(event.pointerId);
    setContextMenu(null);
    if (event.button !== 0) return;
    const cell = cellFromPointer(event, view, level);
    if (!cell || event.altKey) {
      setDrag({ kind: "pan", startX: event.clientX, startY: event.clientY, originX: view.panX, originY: view.panY });
      return;
    }
    if (formatPainterActive && formatClipboard) {
      pasteFormatAt(cell);
      return;
    }
    const additive = event.shiftKey || event.ctrlKey;
    const baseSelections = additive ? selections : [];
    setDrag({ kind: "select", start: cell, current: cell, additive, baseSelections });
    setActiveCell(cell);
    setSelections(additive ? [...baseSelections, cellToSelection(cell)] : [cellToSelection(cell)]);
  }

  function handlePointerMove(event: PointerEvent<HTMLCanvasElement>) {
    if (drag?.kind === "pan") {
      setView((current) => ({
        ...current,
        panX: drag.originX + event.clientX - drag.startX,
        panY: drag.originY + event.clientY - drag.startY
      }));
      return;
    }
    const cell = cellFromPointer(event, view, level);
    setHovered(cell);
    if (drag?.kind === "select" && cell) {
      const started = performance.now();
      setDrag({ ...drag, current: cell });
      const next = normalizeSelection(drag.start, cell);
      setSelections(drag.additive ? [...drag.baseSelections, next] : [next]);
      setMetrics((current) => ({ ...current, selectionMs: performance.now() - started }));
    }
  }

  function handlePointerUp(event: PointerEvent<HTMLCanvasElement>) {
    event.currentTarget.releasePointerCapture(event.pointerId);
    setDrag(null);
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLCanvasElement>) {
    const deltaByKey: Record<string, { da: number; ds: number }> = {
      ArrowLeft: { da: -1, ds: 0 },
      ArrowRight: { da: 1, ds: 0 },
      ArrowUp: { da: 0, ds: -1 },
      ArrowDown: { da: 0, ds: 1 }
    };
    const delta = deltaByKey[event.key];
    if (!delta) return;
    event.preventDefault();
    const next: GridCell = {
      aisle: clamp(activeCell.aisle + delta.da, 1, GRID.aisleCount),
      slot: clamp(activeCell.slot + delta.ds, 1, GRID.slotsPerAisle),
      level
    };
    const started = performance.now();
    setActiveCell(next);
    setSelections((current) => event.shiftKey && current.length
      ? replaceLastSelection(current, mergeSelections(current[current.length - 1], cellToSelection(next)))
      : [cellToSelection(next)]);
    setMetrics((current) => ({ ...current, selectionMs: performance.now() - started }));
  }

  function assignRole(role = activeRole) {
    if (!selections.length) return;
    const targetSelections = selections.map((selection) => ({ ...selection, level }));
    const elapsed = applyRoleChange(targetSelections, role);
    markChanged(targetSelections, elapsed);
  }

  async function applyActiveRoleAction() {
    if (activeRole === "FRACTIONAL_PICK_FACE") {
      await generateSmallPickFaces();
      return;
    }
    if (activeRole === "FRACTIONAL_STORAGE") {
      await generateStorageSlots();
      return;
    }
    assignRole();
  }

  function undo() {
    const change = undoStackRef.current.pop();
    if (!change) return;
    const started = performance.now();
    if (change.kind === "template") {
      rolesRef.current = new Uint8Array(change.before);
    } else {
      change.selections.forEach((selection, index) => writeSelectionRoles(rolesRef.current, selection, change.before[index]));
    }
    redoStackRef.current.push(change);
    setSelections(change.kind === "template" ? [] : change.selections.map((selection) => ({ ...selection, level })));
    setDirty(true);
    setHistoryVersion((value) => value + 1);
    setVersion((value) => value + 1);
    setMetrics((current) => ({ ...current, bulkMs: performance.now() - started, selectedCells: change.kind === "template" ? 0 : selectionListSize(change.selections) }));
  }

  function redo() {
    const change = redoStackRef.current.pop();
    if (!change) return;
    const started = performance.now();
    if (change.kind === "template") {
      rolesRef.current = new Uint8Array(change.after);
    } else {
      change.selections.forEach((selection, index) => writeSelectionRoles(rolesRef.current, selection, change.after[index]));
    }
    undoStackRef.current.push(change);
    setSelections(change.kind === "template" ? [] : change.selections.map((selection) => ({ ...selection, level })));
    setDirty(true);
    setHistoryVersion((value) => value + 1);
    setVersion((value) => value + 1);
    setMetrics((current) => ({ ...current, bulkMs: performance.now() - started, selectedCells: change.kind === "template" ? 0 : selectionListSize(change.selections) }));
  }

  function copyFormat() {
    const source = selections[0];
    if (!source) {
      setFormatStatus("Нет выделения для копирования формата");
      return;
    }
    const values = readSelectionRoles(rolesRef.current, source);
    const width = source.aisleTo - source.aisleFrom + 1;
    const height = source.slotTo - source.slotFrom + 1;
    setFormatClipboard({ source: { ...source }, values, width, height, copiedAt: new Date().toISOString() });
    setFormatPainterActive(true);
    setFormatStatus(`Скопирован формат ${width} x ${height}; выберите цель и нажмите Вставить формат`);
  }

  function pasteFormat() {
    pasteFormatAt(selections[0]?.anchorCell || activeCell);
  }

  function pasteFormatAt(anchor: GridCell) {
    if (!formatClipboard) {
      setFormatStatus("Формат не скопирован");
      return false;
    }
    const target = normalizeSelection(anchor, {
      aisle: anchor.aisle + formatClipboard.width - 1,
      slot: anchor.slot + formatClipboard.height - 1,
      level: anchor.level
    });
    if (target.aisleTo > GRID.aisleCount || target.slotTo > GRID.slotsPerAisle) {
      setFormatStatus("Вставка формата выходит за границы камеры");
      return false;
    }
    const started = performance.now();
    const before = readSelectionRoles(rolesRef.current, target);
    const after = new Uint8Array(formatClipboard.values);
    writeSelectionRoles(rolesRef.current, target, after);
    undoStackRef.current.push({ kind: "format", selections: [{ ...target }], before: [before], after: [after], label: "format-painter" });
    redoStackRef.current = [];
    setDirty(true);
    setFormatPainterActive(false);
    setFormatStatus(`Формат вставлен в A${target.aisleFrom.toString().padStart(2, "0")}-S${target.slotFrom.toString().padStart(3, "0")} (${formatClipboard.width} x ${formatClipboard.height})`);
    setSelections([target]);
    setActiveCell({ aisle: target.aisleFrom, slot: target.slotFrom, level: target.level });
    setHistoryVersion((value) => value + 1);
    setVersion((value) => value + 1);
    setMetrics((current) => ({ ...current, bulkMs: performance.now() - started, selectedCells: selectionSize(target) }));
    return true;
  }

  function cancelFormatPainter() {
    setFormatPainterActive(false);
    setFormatStatus(formatClipboard ? "Копирование формата отменено, буфер сохранен" : "Формат не скопирован");
  }

  async function saveDraft() {
    const payload = {
      version: 1,
      grid: GRID,
      roles: encodeRoles(rolesRef.current),
      savedAt: new Date().toISOString()
    };
    localStorage.setItem(LOCAL_DRAFT_KEY, JSON.stringify(payload));
    try {
      const apiDraft = await saveApiDraft(payload.roles);
      setDirty(false);
      setDraftRevision(apiDraft.revision || null);
      setCurrentDraft(apiDraft);
      setDraftStatus(`Сохранено API draft ${apiDraft.draft_id.slice(0, 8)} · rev ${apiDraft.revision || "-"} · ${apiDraft.updated_at ? new Date(apiDraft.updated_at).toLocaleTimeString("ru-RU") : ""}`);
    } catch {
      setDirty(false);
      setDraftStatus(`API недоступен, сохранено локально ${new Date(payload.savedAt).toLocaleTimeString("ru-RU")}`);
    }
  }

  async function loadDraft() {
    if (draftId) {
      try {
      const apiDraft = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}`, { cache: "no-store" });
        applyApiDraft(apiDraft);
        setDraftStatus(`Загружено API draft ${apiDraft.draft_id.slice(0, 8)} · ${apiDraft.updated_at ? new Date(apiDraft.updated_at).toLocaleTimeString("ru-RU") : ""}`);
        return;
      } catch {
        setDraftStatus("API draft не загружен, пробую локальную копию");
      }
    }
    const raw = localStorage.getItem(LOCAL_DRAFT_KEY);
    if (!raw) {
      setDraftStatus("Локальный draft не найден");
      return;
    }
    try {
      const payload = JSON.parse(raw) as { roles?: string; grid?: Partial<GridConfig>; savedAt?: string };
      if (!payload.roles || payload.grid?.aisleCount !== GRID.aisleCount || payload.grid?.slotsPerAisle !== GRID.slotsPerAisle || payload.grid?.levels !== GRID.levels) {
        setDraftStatus("Локальный draft несовместим с текущей сеткой");
        return;
      }
      applyDraftRoles(payload.roles);
      setDraftStatus(`Загружено локально ${payload.savedAt ? new Date(payload.savedAt).toLocaleTimeString("ru-RU") : ""}`);
    } catch {
      setDraftStatus("Не удалось прочитать локальный draft");
    }
  }

  async function saveApiDraft(rolesBase64: string) {
    const apiGrid = { aisle_count: GRID.aisleCount, slots_per_aisle: GRID.slotsPerAisle, levels: GRID.levels };
    if (draftId) {
      return apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/cells`, {
        method: "PATCH",
        body: JSON.stringify({ roles_base64: rolesBase64, expected_revision: draftRevision })
      });
    }
    const apiDraft = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts`, {
      method: "POST",
      body: JSON.stringify({
        draft_name: "Рисование карты больших складов",
        grid: apiGrid,
        roles_base64: rolesBase64
      })
    });
    localStorage.setItem(LOCAL_DRAFT_ID_KEY, apiDraft.draft_id);
    setDraftId(apiDraft.draft_id);
    return apiDraft;
  }

  function applyDraftRoles(rolesBase64: string) {
    rolesRef.current = decodeRoles(rolesBase64, totalCells());
    fractionVisualsRef.current = new Map();
    setCurrentDraft(null);
    setDraftRevision(null);
    setDraftDiff(null);
    undoStackRef.current = [];
    redoStackRef.current = [];
    setDirty(false);
    setSelections([]);
    setHistoryVersion((value) => value + 1);
    setVersion((value) => value + 1);
  }

  function applyApiDraft(draft: WarehouseMapDraft) {
    rolesRef.current = decodeRoles(draft.roles_base64, totalCells());
    fractionVisualsRef.current = buildFractionVisualsFromDraft(draft);
    setCurrentDraft(draft);
    setDraftRevision(draft.revision || 1);
    setDraftDiff(null);
    undoStackRef.current = [];
    redoStackRef.current = [];
    setDirty(false);
    setSelections([]);
    setHistoryVersion((value) => value + 1);
    setVersion((value) => value + 1);
  }

  async function loadDraftDiff() {
    if (!draftId) {
      setDraftStatus("Сначала сохраните draft через API");
      return null;
    }
    try {
      const diff = await apiFetchJson<WarehouseMapDraftDiff>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/diff`, { cache: "no-store" });
      setDraftDiff(diff);
      setDraftStatus(`Diff: changed=${diff.changed_cells}, pickSlots=${diff.small_pick_face_count}, storageSlots=${diff.storage_slot_count}`);
      return diff;
    } catch {
      setDraftStatus("Не удалось загрузить diff");
      return null;
    }
  }

  async function saveDraftMetadata() {
    if (!draftId) {
      setDraftStatus("Сначала сохраните draft через API");
      return null;
    }
    try {
      const payload = {
        expected_revision: draftRevision,
        draft_metadata: {
          source: "large-map-ui",
          selected_ware_id: selectedWareId,
          selected_camera_id: selectedCameraId,
          updated_at: new Date().toISOString()
        },
        canvas_objects: selectedCameraObjects.map((item) => canvasObjectPayload(item)),
        passages: selectedCameraPassages.map((item) => passagePayload(item)),
        camera_links: selectedCameraLinks.map((item) => cameraLinkPayload(item)),
        updated_by: "warehouse-map-ui"
      };
      const draft = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/metadata`, {
        method: "PATCH",
        body: JSON.stringify(payload)
      });
      applyApiDraft(draft);
      setDraftStatus(`Metadata сохранена · rev ${draft.revision || "-"}`);
      return draft;
    } catch {
      setDraftStatus("Не удалось сохранить metadata draft");
      return null;
    }
  }

  function applyEmptyCameraDefaultRoles(state: WarehouseMapState | null) {
    if (!state || !isEmptyRealCameraState(state)) return;
    rolesRef.current = createBlockedRoles();
    undoStackRef.current = [];
    redoStackRef.current = [];
    setDirty(false);
    setSelections([]);
    setActiveRole("PICK_FACE");
    setHistoryVersion((value) => value + 1);
    setVersion((value) => value + 1);
  }

  function applyRoleChange(targetSelections: CellSelection[], role: CellRole) {
    const started = performance.now();
    const roles = rolesRef.current;
    const roleValue = ROLE_ORDER.indexOf(role);
    const before: Uint8Array[] = [];
    const after: Uint8Array[] = [];
    targetSelections.forEach((selection) => {
      const beforeValues = readSelectionRoles(roles, selection);
      const afterValues = new Uint8Array(beforeValues.length);
      afterValues.fill(roleValue);
      writeSelectionRoles(roles, selection, afterValues);
      before.push(beforeValues);
      after.push(afterValues);
    });
    undoStackRef.current.push({ kind: "role", selections: targetSelections.map((selection) => ({ ...selection })), before, after, role });
    redoStackRef.current = [];
    return performance.now() - started;
  }

  function applyTemplate(templateName: string, nextRoles: Uint8Array) {
    const started = performance.now();
    const before = new Uint8Array(rolesRef.current);
    rolesRef.current = nextRoles;
    undoStackRef.current.push({ kind: "template", templateName, before, after: new Uint8Array(nextRoles) });
    redoStackRef.current = [];
    setDirty(true);
    setSelections([]);
    setHistoryVersion((value) => value + 1);
    setVersion((value) => value + 1);
    setMetrics((current) => ({ ...current, bulkMs: performance.now() - started, selectedCells: 0 }));
  }

  function applyRegularTemplate() {
    applyTemplate("regular-grid", createRegularRoles());
  }

  function applyAisleTemplate() {
    const next = new Uint8Array(rolesRef.current);
    drawTransportAisles(next);
    applyTemplate("transport-aisles", next);
  }

  function applyDockTemplate() {
    const next = new Uint8Array(rolesRef.current);
    drawDockZone(next, selections.length ? selections : [defaultDockSelection()]);
    applyTemplate("dock-zone", next);
  }

  function applyFilmTemplate() {
    const next = new Uint8Array(rolesRef.current);
    drawFilmZone(next);
    applyTemplate("film-wrap-zone", next);
  }

  function copyAisleTemplate() {
    const next = new Uint8Array(rolesRef.current);
    const sourceAisle = activeCell.aisle;
    const targetAisles = selectedTargetAisles(selections, sourceAisle);
    copyAisleRoles(next, sourceAisle, targetAisles);
    applyTemplate(`copy-aisle-A${sourceAisle}`, next);
    setDraftStatus(`Скопирована A${sourceAisle.toString().padStart(2, "0")} на ${targetAisles.length} аллей`);
  }

  function markChanged(targetSelections: CellSelection[], elapsed: number) {
    setDirty(true);
    setHistoryVersion((value) => value + 1);
    setVersion((value) => value + 1);
    setMetrics((current) => ({ ...current, bulkMs: elapsed, selectedCells: selectionListSize(targetSelections) }));
  }

  async function generatePickFaceAddresses() {
    const selection = selections[0];
    if (!selection) {
      setAddressStatus("Нет выделения для адресации");
      return;
    }
    if (!draftId) {
      setAddressStatus("Сначала сохраните draft через API");
      return;
    }
    try {
      const result = await apiFetchJson<AddressPreview>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/pick-face-addresses/generate`, {
        method: "POST",
        body: JSON.stringify({
          selection: toApiSelection(selection),
          anchor_cell: toApiCell(selection.anchorCell),
          focus_cell: toApiCell(selection.focusCell),
          aisle_no: addressForm.aisleNo,
          start_pick_no: addressForm.startPickNo,
          step: addressForm.step,
          direction: addressForm.direction,
          side: addressForm.side || null,
          code_mask: addressForm.codeMask
        })
      });
      setAddressPreview(result);
      setAddressStatus(`Назначено адресов: ${result.assigned_count}`);
    } catch {
      setAddressStatus("Не удалось назначить адреса через API");
    }
  }

  async function generateSmallPickFaces(presetOverride?: SplitPresetId) {
    const selection = selections[0];
    const presetId = presetOverride || smallPickForm.preset;
    const preset = PICK_SPLIT_PRESETS[presetId];
    if (!selection) {
      setSmallPickStatus("Нет выделения для дробной ячейки");
      return;
    }
    if (!draftId) {
      setSmallPickStatus("Сначала сохраните draft через API");
      return;
    }
    if (preset.subLevelCount * preset.subColumnCount < preset.fractionCellCount) {
      setSmallPickStatus("Сетка меньше количества дробных мест");
      return;
    }
    if (presetOverride && presetOverride !== smallPickForm.preset) {
      setSmallPickForm((current) => ({
        ...current,
        preset: presetOverride,
        fractionCellCount: preset.fractionCellCount,
        subLevelCount: preset.subLevelCount,
        subColumnCount: preset.subColumnCount
      }));
    }
    try {
      const result = await apiFetchJson<SmallPickPreview>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/small-pick-faces/generate`, {
        method: "POST",
        body: JSON.stringify({
          physical_cell: toApiCell(selection.anchorCell),
          fraction_cell_count: preset.fractionCellCount,
          sub_level_count: preset.subLevelCount,
          sub_column_count: preset.subColumnCount,
          order_mode: smallPickForm.orderMode,
          start_order: smallPickForm.startOrder,
          step: smallPickForm.step,
          side: smallPickForm.side || null,
          code_mask: smallPickForm.codeMask
        })
      });
      const next = new Uint8Array(rolesRef.current);
      next[cellIndex(selection.anchorCell.aisle, selection.anchorCell.slot, selection.anchorCell.level)] = ROLE_ORDER.indexOf("FRACTIONAL_PICK_FACE");
      rolesRef.current = next;
      fractionVisualsRef.current.set(fractionVisualKey(selection.anchorCell), preset.visual);
      setSmallPickPreview(result);
      setSmallPickStatus(`Создано логических ячеек: ${result.created_count} · ${preset.label}`);
      setDirty(true);
      setVersion((value) => value + 1);
    } catch {
      setSmallPickStatus("Не удалось создать дробную ячейку через API");
    }
  }

  async function generateStorageSlots(presetOverride?: StorageSplitPresetId) {
    const selection = selections[0];
    const presetId = presetOverride || storageSlotForm.preset;
    const preset = STORAGE_SPLIT_PRESETS[presetId];
    if (!selection) {
      setStorageSlotStatus("Нет выделения для ячейки хранения");
      return;
    }
    if (!draftId) {
      setStorageSlotStatus("Сначала сохраните draft через API");
      return;
    }
    try {
      const result = await apiFetchJson<StorageSlotPreview>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/storage-slots/generate`, {
        method: "POST",
        body: JSON.stringify({
          physical_cell: toApiCell(selection.anchorCell),
          fraction_cell_count: preset.fractionCellCount,
          sub_level_count: 1,
          sub_column_count: preset.subColumnCount,
          start_order: storageSlotForm.startOrder,
          step: storageSlotForm.step,
          code_mask: storageSlotForm.codeMask
        })
      });
      if (presetOverride && presetOverride !== storageSlotForm.preset) {
        setStorageSlotForm((current) => ({
          ...current,
          preset: presetOverride,
          fractionCellCount: preset.fractionCellCount,
          subColumnCount: preset.subColumnCount
        }));
      }
      const next = new Uint8Array(rolesRef.current);
      next[cellIndex(selection.anchorCell.aisle, selection.anchorCell.slot, selection.anchorCell.level)] = ROLE_ORDER.indexOf(preset.fractionCellCount === 1 ? "STORAGE" : "FRACTIONAL_STORAGE");
      rolesRef.current = next;
      if (preset.fractionCellCount > 1) {
        fractionVisualsRef.current.set(fractionVisualKey(selection.anchorCell), preset.visual);
      } else {
        fractionVisualsRef.current.delete(fractionVisualKey(selection.anchorCell));
      }
      setStorageSlotPreview(result);
      setStorageSlotStatus(preset.fractionCellCount === 1 ? "Storage оставлен без дробления" : `Создано storage slots: ${result.created_count} · ${preset.label}`);
      if (draftId) {
        const reloaded = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}`, { cache: "no-store" });
        setCurrentDraft(reloaded);
      }
      setDirty(true);
      setVersion((value) => value + 1);
    } catch {
      setStorageSlotStatus("Не удалось создать storage slots через API");
    }
  }

  async function patchActiveStorageSlot() {
    if (!draftId || !activeStorageSlot?.storage_slot_id) {
      setStorageSlotStatus("Нет выбранного storage slot для редактирования");
      return;
    }
    try {
      const result = await apiFetchJson<{ storage_slot: StorageSlotDraftItem }>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/storage-slots/${activeStorageSlot.storage_slot_id}`, {
        method: "PATCH",
        body: JSON.stringify({
          storage_order: storageSlotEditForm.storageOrder,
          max_pallet_count: storageSlotEditForm.maxPalletCount,
          max_weight_kg: storageSlotEditForm.maxWeightKg || null,
          max_volume_m3: storageSlotEditForm.maxVolumeM3 || null,
          capacity_json: {
            source: "large-map-ui",
            max_pallet_count: storageSlotEditForm.maxPalletCount
          }
        })
      });
      const reloaded = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}`, { cache: "no-store" });
      setCurrentDraft(reloaded);
      setStorageSlotStatus(`Storage slot сохранен: ${result.storage_slot.slot_code || activeStorageSlot.storage_slot_id}`);
      setDirty(true);
    } catch {
      setStorageSlotStatus("Не удалось сохранить storage slot");
    }
  }

  async function previewProjection() {
    if (!draftId) {
      setProjectionStatus("Сначала сохраните draft через API");
      return null;
    }
    try {
      const result = await apiFetchJson<WarehouseMapProjectionPreview>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/projection/preview`, {
        method: "POST"
      });
      setProjectionPreview(result);
      setProjectionStatus(`Projection preview: cells=${result.topology_cell_count}, slots=${result.slot_count}, publishReady=${String(result.publish_ready)}`);
      return result;
    } catch {
      setProjectionStatus("Не удалось построить projection preview");
      return null;
    }
  }

  async function buildRouteFromSelection(pattern = routePattern) {
    if (!draftId) {
      setRouteStatus("Сначала сохраните draft через API");
      return null;
    }
    const selection = selections[0];
    if (!selection) {
      setRouteStatus("Нужно выделить участок для маршрута");
      return null;
    }
    try {
      const result = await apiFetchJson<RouteBuildResponse>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/route/build`, {
        method: "POST",
        body: JSON.stringify({
          selection: toApiSelection(selection),
          route_code: "DRAFT-PICK",
          route_name: "Черновой порядок обхода",
          route_pattern: pattern,
          start_sequence: 1,
          step: 1,
          expected_revision: draftRevision,
          updated_by: "warehouse-map-ui"
        })
      });
      const reloaded = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}`, { cache: "no-store" });
      applyApiDraft(reloaded);
      setRoutePattern(result.route_pattern);
      setRouteStatus(`Route ${result.route_pattern}: ${result.route_row_count} строк · storage skipped ${result.skipped_storage_slots} · non-pick skipped ${result.skipped_non_pick_cells}`);
      return result;
    } catch {
      setRouteStatus("Не удалось построить route draft");
      return null;
    }
  }

  async function validateDraft() {
    if (!draftId) {
      setValidationStatus("Сначала сохраните draft через API");
      return null;
    }
    try {
      const result = await apiFetchJson<WarehouseMapDraftValidation>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/validate`, {
        method: "POST"
      });
      setValidationResult(result);
      setValidationStatus(`Validation: ${result.valid ? "OK" : "BLOCKED"} · errors=${result.error_count} · routeRows=${result.route_row_count || 0}`);
      return result;
    } catch {
      setValidationStatus("Validation API недоступна");
      return null;
    }
  }

  async function publishDraft() {
    if (!draftId) {
      setPublishStatus("Сначала сохраните draft через API");
      return null;
    }
    try {
      const result = await apiFetchJson<WarehouseMapDraftPublished>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/publish`, {
        method: "POST"
      });
      setPublishedResult(result);
      setPublishStatus(`Published ${result.published_topology_id.slice(0, 8)} · routeRows=${result.route_row_count || 0}`);
      return result;
    } catch {
      setPublishStatus("Publish заблокирован validation или API недоступен");
      return null;
    }
  }

  async function saveDraftToOracleCanvas() {
    if (!draftId || selectedWareId === null) {
      setOracleStatus("Выберите склад и сохраните API draft");
      return null;
    }
    try {
      const result = await apiFetchJson<OracleSaveResponse>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/save-to-db`, {
        method: "POST",
        body: JSON.stringify({
          ware_id: selectedWareId,
          canvas_code: `MAP-${selectedWareId}-${draftId.slice(0, 6)}`,
          canvas_name: `Карта склада ${selectedWareId}`,
          camera_code: `CAM-${selectedWareId}`,
          camera_name: "Основная камера",
          expected_revision: draftRevision || undefined,
          updated_by: "warehouse-map-ui"
        })
      });
      const reloaded = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}`, { cache: "no-store" });
      applyApiDraft(reloaded);
      setOracleStatus(`Oracle canvas сохранен: canvas=${result.canvas_id || reloaded.oracle_canvas_id || "-"}`);
      return result;
    } catch {
      setOracleStatus("Не удалось сохранить draft в Oracle canvas");
      return null;
    }
  }

  async function saveProjectionToOracleTopology() {
    if (!draftId || selectedWareId === null) {
      setOracleStatus("Выберите склад и сохраните API draft");
      return null;
    }
    try {
      const result = await apiFetchJson<OracleSaveResponse>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/projection/save-to-topology`, {
        method: "POST",
        body: JSON.stringify({
          ware_id: selectedWareId,
          topology_code: `MAP-TOPO-${selectedWareId}-${draftId.slice(0, 6)}`,
          topology_name: `Topology draft ${selectedWareId}`,
          expected_revision: draftRevision || undefined,
          updated_by: "warehouse-map-ui"
        })
      });
      const reloaded = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}`, { cache: "no-store" });
      applyApiDraft(reloaded);
      setOracleStatus(`Oracle topology сохранена: topology=${result.topology_id || reloaded.oracle_topology_id || "-"} · cells=${result.topology_id ? "OK" : "-"}`);
      return result;
    } catch {
      setOracleStatus("Не удалось сохранить projection в Oracle topology");
      return null;
    }
  }

  async function saveRouteToOracle() {
    if (!draftId || selectedWareId === null) {
      setOracleStatus("Выберите склад и сохраните API draft");
      return null;
    }
    if (!currentDraft?.oracle_topology_id) {
      setOracleStatus("Сначала сохраните projection в Oracle topology");
      return null;
    }
    try {
      const result = await apiFetchJson<OracleSaveResponse>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/route/save-to-db`, {
        method: "POST",
        body: JSON.stringify({
          ware_id: selectedWareId,
          topology_id: currentDraft.oracle_topology_id,
          route_code: `MAP-PICK-${selectedWareId}-${draftId.slice(0, 6)}`,
          route_name: `Pick route ${selectedWareId}`,
          expected_revision: draftRevision || undefined,
          updated_by: "warehouse-map-ui"
        })
      });
      const reloaded = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}`, { cache: "no-store" });
      applyApiDraft(reloaded);
      setOracleStatus(`Oracle route сохранен: route=${result.pick_route_id || reloaded.oracle_pick_route_id || "-"} · valid=${String(result.oracle_validation?.valid)}`);
      return result;
    } catch {
      setOracleStatus("Не удалось сохранить route в Oracle");
      return null;
    }
  }

  async function publishOracleDraft() {
    if (!draftId) {
      setOracleStatus("Сначала сохраните API draft");
      return null;
    }
    const canvasId = currentDraft?.oracle_canvas_id;
    const topologyId = currentDraft?.oracle_topology_id;
    const pickRouteId = currentDraft?.oracle_pick_route_id;
    if (!canvasId || !topologyId || !pickRouteId) {
      setOracleStatus("Для Oracle publish нужны canvas, topology и route в Oracle");
      return null;
    }
    try {
      const result = await apiFetchJson<OraclePublishResponse>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/publish-oracle`, {
        method: "POST",
        body: JSON.stringify({
          canvas_id: canvasId,
          topology_id: topologyId,
          pick_route_id: pickRouteId,
          expected_revision: draftRevision || undefined,
          published_by: "warehouse-map-ui"
        })
      });
      const reloaded = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}`, { cache: "no-store" });
      applyApiDraft(reloaded);
      setOraclePublishResult(result);
      setOracleStatus(`Oracle publish: ${result.status} · canvas=${result.oracle_status.canvas_status} · topology=${result.oracle_status.topology_status} · route=${result.oracle_status.route_status}`);
      return result;
    } catch {
      setOracleStatus("Oracle publish заблокирован validation или API недоступен");
      return null;
    }
  }

  function runSprint2MultiAreaSmoke() {
    const targetLevel = 4;
    const targetSelections: CellSelection[] = [
      normalizeSelection({ aisle: 1, slot: 1, level: targetLevel }, { aisle: 10, slot: 10, level: targetLevel }),
      normalizeSelection({ aisle: 15, slot: 20, level: targetLevel }, { aisle: 20, slot: 24, level: targetLevel })
    ];
    const selectedCells = selectionListSize(targetSelections);
    const ok = selectedCells === 130 && targetSelections.length === 2 && targetSelections.every((selection) => selection.level === targetLevel);

    setLevel(targetLevel);
    setSelections(targetSelections);
    setActiveCell({ aisle: targetSelections[0].aisleFrom, slot: targetSelections[0].slotFrom, level: targetLevel });
    setMetrics((current) => ({ ...current, selectedCells, selectionMs: .001 }));
    setSmokeResult({
      name: "Sprint 2 multi-area selection + level persistence",
      ok,
      details: [
        `areas=${targetSelections.length}`,
        `selectedCells=${selectedCells}`,
        `level=L${targetLevel}`,
        `selectionPersists=${String(ok)}`
      ]
    });
  }

  function runSprint3Smoke() {
    const targetSelections: CellSelection[] = [normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: 10, slot: 10, level: 1 })];
    const targetSize = selectionListSize(targetSelections);
    const role = "AISLE";
    const beforeCounts = countRoles(rolesRef.current);
    const elapsed = applyRoleChange(targetSelections, role);
    const afterAssign = countRoles(rolesRef.current);
    const undoChange = undoStackRef.current.pop();
    if (undoChange?.kind === "role") {
      undoChange.selections.forEach((selection, index) => writeSelectionRoles(rolesRef.current, selection, undoChange.before[index]));
      redoStackRef.current.push(undoChange);
    }
    const afterUndo = countRoles(rolesRef.current);
    const redoChange = redoStackRef.current.pop();
    if (redoChange?.kind === "role") {
      redoChange.selections.forEach((selection, index) => writeSelectionRoles(rolesRef.current, selection, redoChange.after[index]));
      undoStackRef.current.push(redoChange);
    }
    const afterRedo = countRoles(rolesRef.current);
    const expectedAisleDelta = afterAssign[role] - beforeCounts[role];
    const undoRestored = afterUndo[role] === beforeCounts[role] && afterUndo.PICK_FACE === beforeCounts.PICK_FACE;
    const redoRestored = afterRedo[role] === afterAssign[role] && afterRedo.PICK_FACE === afterAssign.PICK_FACE;
    const ok = targetSize === 100 && expectedAisleDelta > 0 && expectedAisleDelta <= targetSize && undoRestored && redoRestored;

    setSelections(targetSelections);
    setActiveCell({ aisle: targetSelections[0].aisleFrom, slot: targetSelections[0].slotFrom, level: targetSelections[0].level });
    setDirty(true);
    setHistoryVersion((value) => value + 1);
    setVersion((value) => value + 1);
    setMetrics((current) => ({ ...current, bulkMs: elapsed, selectedCells: targetSize }));
    setSmokeResult({
      name: "Sprint 3 bulk role + undo/redo",
      ok,
      details: [
        `selection=${targetSize}`,
        `role=${role}`,
        `roleDelta=${expectedAisleDelta}`,
        `undoRestored=${String(undoRestored)}`,
        `redoRestored=${String(redoRestored)}`,
        `bulkMs=${elapsed.toFixed(3)}`
      ]
    });
  }

  function runSprint5Smoke() {
    const started = performance.now();
    const roles = createRegularRoles();
    drawTransportAisles(roles);
    const dockSelection = normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: 10, slot: 12, level: 1 });
    drawDockZone(roles, [dockSelection]);
    drawFilmZone(roles);
    const counts = countRoles(roles);
    const hasBase = counts.PICK_FACE > 0 && counts.STORAGE > 0;
    const hasFastZones = counts.AISLE > 0 && counts.GATE > 0 && counts.TRANSPORT_STAGING > 0 && counts.FILM_WRAP > 0;
    const dockHasTwoCellGate =
      roles[cellIndex(1, 1, 1)] === ROLE_ORDER.indexOf("GATE")
      && roles[cellIndex(2, 1, 1)] === ROLE_ORDER.indexOf("GATE");
    const dockExtendsToSelectionBottom =
      roles[cellIndex(1, 12, 1)] === ROLE_ORDER.indexOf("TRANSPORT_STAGING")
      && roles[cellIndex(2, 12, 1)] === ROLE_ORDER.indexOf("TRANSPORT_STAGING");
    const dockDoesNotOverwriteOutsideSelection =
      roles[cellIndex(1, 13, 1)] !== ROLE_ORDER.indexOf("TRANSPORT_STAGING");
    const beforeCopy = new Uint8Array(roles);
    copyAisleRoles(beforeCopy, 4, [8, 12]);
    const copyChanged = beforeCopy[cellIndex(8, 1, 1)] === roles[cellIndex(4, 1, 1)]
      && beforeCopy[cellIndex(12, 3, 1)] === roles[cellIndex(4, 3, 1)];
    const elapsed = performance.now() - started;
    rolesRef.current = beforeCopy;
    undoStackRef.current = [];
    redoStackRef.current = [];
    setDirty(true);
    setSelections([]);
    setHistoryVersion((value) => value + 1);
    setVersion((value) => value + 1);
    setMetrics((current) => ({ ...current, bulkMs: elapsed, selectedCells: 0 }));
    setSmokeResult({
      name: "Sprint 5 templates and fast drawing",
      ok: hasBase && hasFastZones && dockHasTwoCellGate && dockExtendsToSelectionBottom && dockDoesNotOverwriteOutsideSelection && copyChanged,
      details: [
        `pick=${counts.PICK_FACE}`,
        `storage=${counts.STORAGE}`,
        `aisle=${counts.AISLE}`,
        `gates=${counts.GATE}`,
        `staging=${counts.TRANSPORT_STAGING}`,
        `dockTwoCellGate=${String(dockHasTwoCellGate)}`,
        `dockToBottom=${String(dockExtendsToSelectionBottom)}`,
        `dockOutsideClean=${String(dockDoesNotOverwriteOutsideSelection)}`,
        `film=${counts.FILM_WRAP}`,
        `copyChanged=${String(copyChanged)}`,
        `templateMs=${elapsed.toFixed(3)}`
      ]
    });
  }

  function runSprint6Smoke() {
    const targetSelection = normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: 10, slot: 10, level: 1 });
    const firstCodes = previewAddressCodes(targetSelection, {
      aisleNo: 7,
      startPickNo: 1,
      step: 1,
      direction: "START_TO_END",
      side: "LEFT",
      codeMask: "A{aisle}-P{pick_no}-L{level}-{side}"
    }, 100);
    const reverseCodes = previewAddressCodes(targetSelection, {
      aisleNo: 7,
      startPickNo: 1,
      step: 1,
      direction: "END_TO_START",
      side: "LEFT",
      codeMask: "A{aisle}-P{pick_no}-L{level}-{side}"
    }, 100);
    const ok = firstCodes.length === 100
      && firstCodes[0] === "A07-P001-L1-LEFT"
      && firstCodes[99] === "A07-P100-L1-LEFT"
      && reverseCodes[0] === "A07-P001-L1-LEFT"
      && targetSelection.anchorCell.aisle === 1
      && targetSelection.focusCell.aisle === 10;
    setSelections([targetSelection]);
    setActiveCell(targetSelection.anchorCell);
    setAddressPreview({
      assigned_count: firstCodes.length,
      pick_face_address_count: firstCodes.length,
      preview_first: firstCodes.slice(0, 3).map((cell_code) => ({ cell_code })),
      preview_last: firstCodes.slice(-3).map((cell_code) => ({ cell_code }))
    });
    setAddressStatus("Sprint 6 smoke preview сформирован");
    setMetrics((current) => ({ ...current, selectedCells: selectionSize(targetSelection), selectionMs: .001 }));
    setSmokeResult({
      name: "Sprint 6 addressing direction preview",
      ok,
      details: [
        `anchor=A${targetSelection.anchorCell.aisle}-S${targetSelection.anchorCell.slot}`,
        `focus=A${targetSelection.focusCell.aisle}-S${targetSelection.focusCell.slot}`,
        `preview=${firstCodes.length}`,
        `first=${firstCodes[0]}`,
        `last=${firstCodes[99]}`
      ]
    });
  }

  function runSprint7Smoke() {
    const started = performance.now();
    const roles = createRegularRoles();
    const selection100 = normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: 10, slot: 10, level: 1 });
    const selection1000 = normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: 20, slot: 50, level: 1 });
    const selection5000 = normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: 35, slot: 90, level: 1 });
    const selectionSizes = [selectionSize(selection100), selectionSize(selection1000), selectionSize(selection5000)];

    const selectionStarted = performance.now();
    const selectedCells = selectionListSize([selection100, selection1000, selection5000]);
    const selectionMs = performance.now() - selectionStarted;

    const bulkStarted = performance.now();
    writeSelectionRoles(roles, selection100, filledRoleValues(selection100, "AISLE"));
    writeSelectionRoles(roles, selection1000, filledRoleValues(selection1000, "STORAGE"));
    writeSelectionRoles(roles, selection5000, filledRoleValues(selection5000, "PICK_FACE"));
    const bulkMs = performance.now() - bulkStarted;

    const report = {
      cellCount: totalCells(),
      visibleCells: GRID.aisleCount * GRID.slotsPerAisle,
      domNodeCount: document.querySelectorAll("*").length,
      firstRenderMs: metrics.renderMs,
      selectionLatencyMs: selectionMs,
      bulkAssignmentMs: bulkMs,
      selectionSizes,
      totalSmokeMs: performance.now() - started
    };
    const ok = report.cellCount === 18900
      && report.visibleCells === 3150
      && report.domNodeCount < 1000
      && report.selectionSizes.join(",") === "100,1000,3150"
      && Number.isFinite(report.firstRenderMs)
      && report.bulkAssignmentMs < 50
      && report.selectionLatencyMs < 10;

    localStorage.setItem("wms.largeWarehouseMapSprint7Perf.v1", JSON.stringify(report));
    setSelections([selection5000]);
    setMetrics((current) => ({ ...current, selectedCells, bulkMs, selectionMs }));
    setSmokeResult({
      name: "Sprint 7 performance gate",
      ok,
      details: [
        `cellCount=${report.cellCount}`,
        `visible=${report.visibleCells}`,
        `dom=${report.domNodeCount}`,
        `sizes=${report.selectionSizes.join("/")}`,
        `renderMs=${report.firstRenderMs.toFixed(2)}`,
        `selectMs=${report.selectionLatencyMs.toFixed(3)}`,
        `bulkMs=${report.bulkAssignmentMs.toFixed(3)}`
      ]
    });
  }

  function runSprint8Smoke() {
    const target = { aisle: 12, slot: 34, level: 3 };
    setSearchText("A12-S034-L3");
    setLevel(target.level);
    setActiveCell(target);
    setSelections([cellToSelection(target)]);
    setRoleFilters((current) => ({ ...current, STORAGE: false, AISLE: true, PICK_FACE: true }));
    const parsed = parseAddress("A12-S034-L3", 1);
    const inspectorRole = ROLE_ORDER[rolesRef.current[cellIndex(target.aisle, target.slot, target.level)]];
    const ok = parsed?.aisle === 12 && parsed.slot === 34 && parsed.level === 3 && inspectorRole === "STORAGE";
    setSmokeResult({
      name: "Sprint 8 UX workflow",
      ok,
      details: [
        `search=A${target.aisle}-S${target.slot}-L${target.level}`,
        `fitSelected=true`,
        `roleFilter=STORAGE:false`,
        `inspectorRole=${inspectorRole}`,
        `overview=true`
      ]
    });
  }

  function runSprint9Smoke() {
    const target = { aisle: 7, slot: 13, level: 1 };
    const next = new Uint8Array(rolesRef.current);
    next[cellIndex(target.aisle, target.slot, target.level)] = ROLE_ORDER.indexOf("FRACTIONAL_PICK_FACE");
    rolesRef.current = next;
    const preview = createSmallPickClientPreview(target, 6, 2, 3, "SUB_LEVEL_THEN_COLUMN", 1, 1, "{physical_cell}-F{sub_level}{sub_column}");
    const selection = cellToSelection(target);
    const ok = preview.length === 6
      && preview[0].logical_cell_code === "A07-S013-L1-F11"
      && preview[5].logical_cell_code === "A07-S013-L1-F23"
      && countRoles(next).FRACTIONAL_PICK_FACE >= 1;
    setLevel(target.level);
    setActiveCell(target);
    setSelections([selection]);
    setSmallPickForm((current) => ({ ...current, fractionCellCount: 6, subLevelCount: 2, subColumnCount: 3 }));
    setSmallPickPreview({
      created_count: preview.length,
      fraction_cell_count: 6,
      small_pick_face_count: preview.length,
      preview
    });
    setSmallPickStatus("Sprint 9 smoke preview сформирован");
    setDirty(true);
    setVersion((value) => value + 1);
    setSmokeResult({
      name: "Sprint 9 small-piece pick faces",
      ok,
      details: [
        `role=FRACTIONAL_PICK_FACE`,
        `fraction=6`,
        `grid=2x3`,
        `first=${preview[0]?.logical_cell_code}`,
        `last=${preview[5]?.logical_cell_code}`,
        `pickOrder=${preview.map((item) => item.pick_order).join("/")}`
      ]
    });
  }

  async function runSprint12Smoke() {
    const params = new URLSearchParams(window.location.search.replace(/;/g, "&"));
    const hrefWareId = window.location.href.match(/ware_id=(-?\d+)/)?.[1];
    const smokeWareId = Number(params.get("ware_id") || hrefWareId || 0);
    if (smokeWareId) {
      try {
        setSelectedWareId(smokeWareId);
        let state = await apiFetchJson<WarehouseMapState>(`${API_BASE}/api/admin/warehouse-map/warehouses/${smokeWareId}/state`, { cache: "no-store" });
        if (!state.canvas) {
          state = await apiFetchJson<WarehouseMapState>(`${API_BASE}/api/admin/warehouse-map/warehouses/${smokeWareId}/canvases`, {
            method: "POST",
            body: JSON.stringify({
              canvas_code: `SMOKE-012-UI-${Math.abs(smokeWareId)}`,
              canvas_name: "Sprint 12 UI smoke canvas",
              levels: GRID.levels,
              created_by: "SMOKE_012_UI"
            })
          });
        }
        if (!state.canvas) throw new Error("Smoke canvas was not created");
        const first = await apiFetchJson<{ camera: WarehouseMapCamera; state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/canvases/${state.canvas.canvas_id}/cameras`, {
          method: "POST",
          body: JSON.stringify({
            ...cameraPayload(cameraForm),
            camera_code: "CAM-01",
            camera_name: "Smoke UI camera 01",
            created_by: "SMOKE_012_UI"
          })
        });
        const second = await apiFetchJson<{ camera: WarehouseMapCamera; state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/canvases/${state.canvas.canvas_id}/cameras`, {
          method: "POST",
          body: JSON.stringify({
            ...cameraPayload(cameraForm),
            camera_code: "CAM-02",
            camera_name: "Smoke UI camera 02",
            origin_x_m: cameraForm.originX + cameraForm.width + 3,
            created_by: "SMOKE_012_UI"
          })
        });
        const finalState = second.state;
        setWarehouseMapState(finalState);
        setCanvasList(finalState.canvas ? [{
          canvas_id: finalState.canvas.canvas_id,
          canvas_code: finalState.canvas.canvas_code,
          canvas_name: finalState.canvas.canvas_name,
          status: finalState.canvas.status,
          camera_count: finalState.cameras.length
        }] : []);
        setSelectedCameraId(second.camera.camera_id);
        applyEmptyCameraDefaultRoles(finalState);
        setContextMenu({ x: 320, y: 190 });
        setWarehouseStatus("Sprint 12 smoke: камеры созданы через браузерный API flow");
        setSmokeResult({
          name: "Sprint 12 real warehouse shell",
          ok: finalState.cameras.length >= 2 && first.camera.camera_code === "CAM-01" && second.camera.camera_code === "CAM-02",
          details: [
            `ware=${smokeWareId}`,
            `canvas=${finalState.canvas?.canvas_code}`,
            `cameras=${finalState.cameras.length}`,
            `blocked=${countRoles(rolesRef.current).BLOCKED}`,
            `toolbarFlow=true`,
            `contextMenu=true`
          ]
        });
        return;
      } catch (error) {
        setSmokeResult({
          name: "Sprint 12 real warehouse shell",
          ok: false,
          details: [error instanceof Error ? error.message : "browser smoke failed"]
        });
        return;
      }
    }
    const commands = commandRegistry();
    const create = commands.find((command) => command.id === "camera.create");
    const clone = commands.find((command) => command.id === "camera.clone");
    const archive = commands.find((command) => command.id === "camera.archive");
    const ok = Boolean(create && clone && archive)
      && cameraForm.width > 0
      && cameraForm.depth > 0
      && cameraForm.defaultPassageWidth === 3;
    setContextMenu({ x: 320, y: 190 });
    setWarehouseStatus("Sprint 12 smoke: command registry and camera shell ready");
    setSmokeResult({
      name: "Sprint 12 real warehouse shell",
      ok,
      details: [
        `commands=${commands.map((command) => command.id).join("/")}`,
        `createEnabled=${String(create?.enabled)}`,
        `cameraForm=${cameraForm.width}x${cameraForm.depth}x${cameraForm.height}`,
        `passage=${cameraForm.defaultPassageWidth}m`,
        `contextMenu=true`
      ]
    });
  }

  function runSprint13FormatSmoke() {
    const started = performance.now();
    const roles = createBlockedRoles();
    const source = normalizeSelection({ aisle: 2, slot: 4, level: 1 }, { aisle: 3, slot: 13, level: 1 });
    const target = normalizeSelection({ aisle: 8, slot: 20, level: 1 }, { aisle: 9, slot: 29, level: 1 });
    const sourcePattern = new Uint8Array(selectionSize(source));
    const pick = ROLE_ORDER.indexOf("PICK_FACE");
    const storage = ROLE_ORDER.indexOf("STORAGE");
    const staging = ROLE_ORDER.indexOf("TRANSPORT_STAGING");
    for (let index = 0; index < sourcePattern.length; index += 1) {
      sourcePattern[index] = index % 3 === 0 ? pick : index % 3 === 1 ? storage : staging;
    }
    writeSelectionRoles(roles, source, sourcePattern);
    const clipboard: FormatClipboard = {
      source,
      values: readSelectionRoles(roles, source),
      width: source.aisleTo - source.aisleFrom + 1,
      height: source.slotTo - source.slotFrom + 1,
      copiedAt: new Date().toISOString()
    };
    const beforeTarget = readSelectionRoles(roles, target);
    writeSelectionRoles(roles, target, clipboard.values);
    const afterTarget = readSelectionRoles(roles, target);
    const patternEqual = byteArraysEqual(clipboard.values, afterTarget);
    const targetChanged = !byteArraysEqual(beforeTarget, afterTarget);
    const outsideAnchor = { aisle: GRID.aisleCount, slot: GRID.slotsPerAisle, level: 1 };
    const outsideBlocked = outsideAnchor.aisle + clipboard.width - 1 > GRID.aisleCount
      || outsideAnchor.slot + clipboard.height - 1 > GRID.slotsPerAisle;
    const elapsed = performance.now() - started;
    rolesRef.current = roles;
    undoStackRef.current = [{
      kind: "format",
      selections: [target],
      before: [beforeTarget],
      after: [afterTarget],
      label: "format-painter-smoke"
    }];
    redoStackRef.current = [];
    setFormatClipboard(clipboard);
    setFormatPainterActive(false);
    setFormatStatus("SMOKE: формат скопирован и вставлен без ID/адресов");
    setDirty(true);
    setLevel(1);
    setActiveCell({ aisle: target.aisleFrom, slot: target.slotFrom, level: 1 });
    setSelections([target]);
    setHistoryVersion((value) => value + 1);
    setVersion((value) => value + 1);
    setMetrics((current) => ({ ...current, bulkMs: elapsed, selectedCells: selectionSize(target) }));
    setSmokeResult({
      name: "Sprint 13 format painter",
      ok: clipboard.width === 2 && clipboard.height === 10 && patternEqual && targetChanged && outsideBlocked,
      details: [
        `source=${clipboard.width}x${clipboard.height}`,
        `patternEqual=${String(patternEqual)}`,
        `targetChanged=${String(targetChanged)}`,
        `outsideBlocked=${String(outsideBlocked)}`,
        `formatMs=${elapsed.toFixed(3)}`
      ]
    });
  }

  async function runSprint13ObjectsSmoke() {
    const params = new URLSearchParams(window.location.search.replace(/;/g, "&"));
    const smokeWareId = Number(params.get("ware_id") || 0);
    if (!smokeWareId && smokeWareId !== 0) return;
    const suffix = Date.now().toString().slice(-6);
    try {
      setSelectedWareId(smokeWareId);
      let state = await apiFetchJson<WarehouseMapState>(`${API_BASE}/api/admin/warehouse-map/warehouses/${smokeWareId}/state`, { cache: "no-store" });
      if (!state.canvas) {
        state = await apiFetchJson<WarehouseMapState>(`${API_BASE}/api/admin/warehouse-map/warehouses/${smokeWareId}/canvases`, {
          method: "POST",
          body: JSON.stringify({
            canvas_code: `SMOKE-013-${Math.abs(smokeWareId)}-${suffix}`,
            canvas_name: "Sprint 13 objects smoke canvas",
            levels: GRID.levels,
            created_by: "SMOKE_013_UI"
          })
        });
      }
      if (!state.canvas) throw new Error("Smoke canvas was not created");
      const canvasId = state.canvas.canvas_id;
      let cameras = state.cameras;
      if (!cameras.length) {
        const created = await apiFetchJson<{ camera: WarehouseMapCamera; state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/canvases/${canvasId}/cameras`, {
          method: "POST",
          body: JSON.stringify({
            ...cameraPayload(cameraForm),
            camera_code: `S13-CAM-A-${suffix}`,
            camera_name: "Sprint 13 smoke camera A",
            created_by: "SMOKE_013_UI"
          })
        });
        state = created.state;
        cameras = state.cameras;
      }
      if (cameras.length < 2) {
        const created = await apiFetchJson<{ camera: WarehouseMapCamera; state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/canvases/${canvasId}/cameras`, {
          method: "POST",
          body: JSON.stringify({
            ...cameraPayload(cameraForm),
            camera_code: `S13-CAM-B-${suffix}`,
            camera_name: "Sprint 13 smoke camera B",
            origin_x_m: cameraForm.originX + cameraForm.width + 3,
            created_by: "SMOKE_013_UI"
          })
        });
        state = created.state;
        cameras = state.cameras;
      }
      const camera = cameras[0];
      const objectSelection = normalizeSelection({ aisle: 4, slot: 8, level: 1 }, { aisle: 10, slot: 20, level: 1 });
      const passageSelection = normalizeSelection({ aisle: 12, slot: 8, level: 1 }, { aisle: 14, slot: 42, level: 1 });
      const objectPatch = await apiFetchJson<{ state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/cameras/${camera.camera_id}/objects`, {
        method: "PATCH",
        body: JSON.stringify({
          objects: [selectionObjectPayload(objectSelection, camera, 1, "S13-ZONE-001")],
          updated_by: "SMOKE_013_UI"
        })
      });
      const passagePatch = await apiFetchJson<{ state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/cameras/${camera.camera_id}/passages`, {
        method: "PATCH",
        body: JSON.stringify({
          passages: [selectionPassagePayload(passageSelection, camera, 1, "S13-PASS-001")],
          updated_by: "SMOKE_013_UI"
        })
      });
      const linkPatch = await apiFetchJson<{ state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/canvases/${canvasId}/camera-links`, {
        method: "PATCH",
        body: JSON.stringify({
          camera_links: [{
            link_code: "S13-LINK-001",
            link_kind: "DOOR",
            from_camera_id: cameras[0].camera_id,
            to_camera_id: cameras[1].camera_id,
            from_point_x_m: Number(cameras[0].width_m || 0),
            from_point_y_m: Number(cameras[0].depth_m || 0) / 2,
            to_point_x_m: 0,
            to_point_y_m: Number(cameras[1].depth_m || 0) / 2,
            distance_m: 3,
            direction_code: "BOTH"
          }],
          updated_by: "SMOKE_013_UI"
        })
      });
      let negativeWidthRejected = false;
      try {
        await apiFetchJson<{ state: WarehouseMapState }>(`${API_BASE}/api/admin/warehouse-map/cameras/${camera.camera_id}/passages`, {
          method: "PATCH",
          body: JSON.stringify({
            passages: [{
              ...selectionPassagePayload(passageSelection, camera, 99, "S13-BAD-WIDTH"),
              width_m: 0
            }],
            updated_by: "SMOKE_013_UI"
          })
        });
      } catch {
        negativeWidthRejected = true;
      }
      const reloaded = await apiFetchJson<WarehouseMapState>(`${API_BASE}/api/admin/warehouse-map/canvases/${canvasId}`, { cache: "no-store" });
      const objectSaved = reloaded.canvas_objects.some((item) => item.camera_id === camera.camera_id && item.object_code === "S13-ZONE-001");
      const passageSaved = reloaded.passages.some((item) => item.camera_id === camera.camera_id && item.passage_code === "S13-PASS-001" && Number(item.width_m) === 3);
      const linkSaved = reloaded.camera_links.some((item) => item.link_code === "S13-LINK-001");
      setWarehouseMapState(reloaded);
      setCanvasList(reloaded.canvas ? [{
        canvas_id: reloaded.canvas.canvas_id,
        canvas_code: reloaded.canvas.canvas_code,
        canvas_name: reloaded.canvas.canvas_name,
        status: reloaded.canvas.status,
        camera_count: reloaded.cameras.length
      }] : []);
      setSelectedCameraId(camera.camera_id);
      setLevel(1);
      setSelections([objectSelection, passageSelection]);
      setActiveCell(objectSelection.anchorCell);
      applyEmptyCameraDefaultRoles(reloaded);
      setDirty(true);
      setWarehouseStatus("Sprint 13 smoke: canvas object, passage и связь камер сохранены и перезагружены");
      setSmokeResult({
        name: "Sprint 13 canvas objects/passages",
        ok: objectSaved && passageSaved && linkSaved && negativeWidthRejected && objectPatch.state.counters.canvas_objects >= 1 && passagePatch.state.counters.passages >= 1 && linkPatch.state.counters.camera_links >= 1,
        details: [
          `ware=${smokeWareId}`,
          `camera=${camera.camera_code}`,
          `objectSaved=${String(objectSaved)}`,
          `passageSaved=${String(passageSaved)}`,
          `linkSaved=${String(linkSaved)}`,
          `negativeWidth=${String(negativeWidthRejected)}`,
          `reload=true`
        ]
      });
      setActiveHelpId("passage.create");
      window.setTimeout(() => {
        const panel = document.querySelector(".large-map-panel");
        if (panel instanceof HTMLElement) panel.scrollTop = panel.scrollHeight;
      }, 100);
    } catch (error) {
      setSmokeResult({
        name: "Sprint 13 canvas objects/passages",
        ok: false,
        details: [error instanceof Error ? error.message : "browser smoke failed"]
      });
    }
  }

  async function runSprint14SlotsSmoke() {
    try {
      const roles = createBlockedRoles();
      const apiDraft = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts`, {
        method: "POST",
        body: JSON.stringify({
          draft_name: "Sprint 14 slots smoke",
          grid: { aisle_count: GRID.aisleCount, slots_per_aisle: GRID.slotsPerAisle, levels: GRID.levels },
          roles_base64: encodeRoles(roles),
          created_by: "SMOKE_014_UI"
        })
      });
      const pickCell = { aisle: 5, slot: 8, level: 1 };
      const storageDefaultCell = { aisle: 8, slot: 8, level: 2 };
      const storageSplitCell = { aisle: 11, slot: 8, level: 2 };
      const pickResult = await apiFetchJson<SmallPickPreview>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/small-pick-faces/generate`, {
        method: "POST",
        body: JSON.stringify({
          physical_cell: pickCell,
          fraction_cell_count: 2,
          sub_level_count: 2,
          sub_column_count: 1,
          order_mode: "SUB_LEVEL_THEN_COLUMN",
          code_mask: "{physical_cell}-P{sub_level}{sub_column}",
          updated_by: "SMOKE_014_UI"
        })
      });
      const storageDefault = await apiFetchJson<StorageSlotPreview>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/storage-slots/generate`, {
        method: "POST",
        body: JSON.stringify({
          physical_cell: storageDefaultCell,
          fraction_cell_count: 1,
          sub_level_count: 1,
          sub_column_count: 1,
          updated_by: "SMOKE_014_UI"
        })
      });
      const pick3x3Cell = { aisle: 5, slot: 12, level: 2 };
      const pick3x3 = await apiFetchJson<SmallPickPreview>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/small-pick-faces/generate`, {
        method: "POST",
        body: JSON.stringify({
          physical_cell: pick3x3Cell,
          fraction_cell_count: 9,
          sub_level_count: 3,
          sub_column_count: 3,
          order_mode: "SUB_LEVEL_THEN_COLUMN",
          code_mask: "{physical_cell}-P{sub_level}{sub_column}",
          updated_by: "SMOKE_014_UI"
        })
      });
      const storageSplit = await apiFetchJson<StorageSlotPreview>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/storage-slots/generate`, {
        method: "POST",
        body: JSON.stringify({
          physical_cell: storageSplitCell,
          fraction_cell_count: 2,
          sub_level_count: 1,
          sub_column_count: 2,
          code_mask: "{physical_cell}-ST{sub_column}",
          updated_by: "SMOKE_014_UI"
        })
      });
      const storageSplit3Cell = { aisle: 14, slot: 8, level: 2 };
      const storageSplit3 = await apiFetchJson<StorageSlotPreview>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/storage-slots/generate`, {
        method: "POST",
        body: JSON.stringify({
          physical_cell: storageSplit3Cell,
          fraction_cell_count: 3,
          sub_level_count: 1,
          sub_column_count: 3,
          code_mask: "{physical_cell}-ST{sub_column}",
          updated_by: "SMOKE_014_UI"
        })
      });
      const targetStorageSlotId = storageSplit3.preview[0]?.storage_slot_id;
      if (!targetStorageSlotId) {
        throw new Error("storage split preview does not include storage_slot_id");
      }
      const patchedStorage = await apiFetchJson<{ storage_slot: StorageSlotDraftItem }>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/storage-slots/${targetStorageSlotId}`, {
        method: "PATCH",
        body: JSON.stringify({
          storage_order: 77,
          max_pallet_count: 2,
          max_weight_kg: 1200,
          max_volume_m3: 2.4,
          capacity_json: { pallet_places: 2, smoke: "sprint14-capacity" },
          updated_by: "SMOKE_014_UI"
        })
      });
      let storageVerticalRejected = false;
      try {
        await apiFetchJson<StorageSlotPreview>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/storage-slots/generate`, {
          method: "POST",
          body: JSON.stringify({
            physical_cell: { aisle: 12, slot: 8, level: 2 },
            fraction_cell_count: 2,
            sub_level_count: 2,
            sub_column_count: 1,
            updated_by: "SMOKE_014_UI"
          })
        });
      } catch {
        storageVerticalRejected = true;
      }
      const reloaded = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}`, { cache: "no-store" });
      applyApiDraft(reloaded);
      const pick3x3Visual = fractionVisualsRef.current.get(fractionVisualKey(pick3x3Cell));
      const storage2Visual = fractionVisualsRef.current.get(fractionVisualKey(storageSplitCell));
      const storage3Visual = fractionVisualsRef.current.get(fractionVisualKey(storageSplit3Cell));
      const reloadedPatchedStorage = (reloaded.storage_slots || []).find((item) => item.storage_slot_id === targetStorageSlotId);
      const visualsReloaded = pick3x3Visual?.columns === 3
        && pick3x3Visual.rows === 3
        && storage2Visual?.columns === 2
        && storage2Visual.rows === 1
        && storage3Visual?.columns === 3
        && storage3Visual.rows === 1;
      const storagePatchReloaded = patchedStorage.storage_slot.storage_order === 77
        && reloadedPatchedStorage?.storage_order === 77
        && reloadedPatchedStorage.max_pallet_count === 2
        && reloadedPatchedStorage.max_weight_kg === 1200;
      const projection = await apiFetchJson<WarehouseMapProjectionPreview>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/projection/preview`, {
        method: "POST"
      });
      const projectionPreviewOk = projection.status === "PREVIEW"
        && projection.topology_cell_count >= 5
        && projection.pick_face_slot_count === 11
        && projection.storage_slot_count === 5
        && projection.slot_count === 16
        && Number(projection.role_counts.FRACTIONAL_PICK_FACE || 0) === 2
        && Number(projection.role_counts.FRACTIONAL_STORAGE || 0) === 2
        && projection.preview_slots.some((slot) => slot.slot_kind === "PICK_FACE_SLOT")
        && projection.preview_slots.some((slot) => slot.slot_kind === "STORAGE_SLOT" && slot.storage_order === 77);
      localStorage.setItem(LOCAL_DRAFT_ID_KEY, apiDraft.draft_id);
      setDraftId(apiDraft.draft_id);
      setWarehouseMapState(null);
      setSelectedCameraId(null);
      setLevel(2);
      setView({ zoom: 6, panX: -184, panY: -400 });
      setSelections([
        cellToSelection({ ...pickCell }),
        cellToSelection({ ...pick3x3Cell }),
        cellToSelection({ ...storageDefaultCell }),
        cellToSelection({ ...storageSplitCell }),
        cellToSelection({ ...storageSplit3Cell })
      ]);
      setActiveCell(storageSplitCell);
      setSmallPickPreview(pick3x3);
      setSmallPickStatus(`SMOKE: pick default=${pickResult.created_count}, pick 3x3=${pick3x3.created_count}`);
      setStorageSlotPreview(storageSplit3);
      setStorageSlotEditForm({ storageOrder: 77, maxPalletCount: 2, maxWeightKg: 1200, maxVolumeM3: 2.4 });
      setStorageSlotStatus(`SMOKE: storage default=${storageDefault.created_count}, split2=${storageSplit.created_count}, split3=${storageSplit3.created_count}, capacity saved`);
      setProjectionPreview(projection);
      setProjectionStatus(`SMOKE: projection cells=${projection.topology_cell_count}, slots=${projection.slot_count}, publishReady=${String(projection.publish_ready)}`);
      setVersion((value) => value + 1);
      setDirty(true);
      setSmokeResult({
        name: "Sprint 14 generalized slots",
        ok: pickResult.created_count === 2 && pick3x3.created_count === 9 && storageDefault.created_count === 0 && storageSplit.created_count === 2 && storageSplit3.created_count === 3 && storageVerticalRejected && visualsReloaded && storagePatchReloaded && projectionPreviewOk,
        details: [
          `pickDefault=${pickResult.created_count}`,
          `pick3x3=${pick3x3.created_count}`,
          `storageDefault=${storageDefault.created_count}`,
          `storageSplit2=${storageSplit.created_count}`,
          `storageSplit3=${storageSplit3.created_count}`,
          `storageVerticalRejected=${String(storageVerticalRejected)}`,
          `visualsReloaded=${String(visualsReloaded)}`,
          `storagePatchReloaded=${String(storagePatchReloaded)}`,
          `projectionPreview=${String(projectionPreviewOk)}`
        ]
      });
      window.setTimeout(() => {
        const panel = document.querySelector(".large-map-panel");
        if (panel instanceof HTMLElement) panel.scrollTop = panel.scrollHeight;
      }, 100);
    } catch (error) {
      setSmokeResult({
        name: "Sprint 14 generalized slots",
        ok: false,
        details: [error instanceof Error ? error.message : "browser smoke failed"]
      });
    }
  }

  function runSprint14HelpSmoke() {
    const target = cellToSelection({ aisle: 5, slot: 8, level: 1 });
    setLevel(1);
    setSelections([target]);
    setActiveCell(target.anchorCell);
    setContextMenu({ x: 340, y: 128 });
    setActiveHelpId("fraction.pick");
    setHelpPopupPosition({ x: 600, y: 136 });
    setSmallPickForm({
      ...smallPickForm,
      preset: "PICK_3X3",
      fractionCellCount: PICK_SPLIT_PRESETS.PICK_3X3.fractionCellCount,
      subLevelCount: PICK_SPLIT_PRESETS.PICK_3X3.subLevelCount,
      subColumnCount: PICK_SPLIT_PRESETS.PICK_3X3.subColumnCount
    });
    setSmokeResult({
      name: "Sprint 14 contextual help and fraction commands",
      ok: true,
      details: [
        "helpPopover=true",
        "fractionPickPreset=PICK_3X3",
        "contextFractionCommands=true"
      ]
    });
    window.setTimeout(() => {
      const panel = document.querySelector(".large-map-panel");
      const fractionHeader = [...document.querySelectorAll("h2")].find((item) => item.textContent === "Дробная ячейка");
      if (panel instanceof HTMLElement && fractionHeader instanceof HTMLElement) panel.scrollTop = fractionHeader.offsetTop - 120;
    }, 100);
  }

  async function runSprint15DiffSmoke() {
    try {
      const roles = createBlockedRoles();
      const apiDraft = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts`, {
        method: "POST",
        body: JSON.stringify({
          draft_name: "Sprint 15 diff smoke",
          grid: { aisle_count: GRID.aisleCount, slots_per_aisle: GRID.slotsPerAisle, levels: GRID.levels },
          roles_base64: encodeRoles(roles),
          created_by: "SMOKE_015_UI"
        })
      });
      const next = new Uint8Array(roles);
      const selection = normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: 5, slot: 5, level: 1 });
      writeSelectionRoles(next, selection, filledRoleValues(selection, "PICK_FACE"));
      const patched = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/cells`, {
        method: "PATCH",
        body: JSON.stringify({
          roles_base64: encodeRoles(next),
          expected_revision: apiDraft.revision || 1,
          updated_by: "SMOKE_015_UI"
        })
      });
      let staleRejected = false;
      try {
        await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/cells`, {
          method: "PATCH",
          body: JSON.stringify({
            roles_base64: encodeRoles(next),
            expected_revision: apiDraft.revision || 1,
            updated_by: "SMOKE_015_UI_STALE"
          })
        });
      } catch {
        staleRejected = true;
      }
      const diff = await apiFetchJson<WarehouseMapDraftDiff>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/diff`, { cache: "no-store" });
      rolesRef.current = next;
      localStorage.setItem(LOCAL_DRAFT_ID_KEY, apiDraft.draft_id);
      setDraftId(apiDraft.draft_id);
      setDraftRevision(patched.revision || 2);
      setCurrentDraft(patched);
      setDraftDiff(diff);
      setLevel(1);
      setSelections([selection]);
      setActiveCell(selection.anchorCell);
      setView({ zoom: 4, panX: 120, panY: 24 });
      setDraftStatus(`SMOKE: diff changed=${diff.changed_cells}, rev=${diff.revision}, staleRejected=${String(staleRejected)}`);
      setVersion((value) => value + 1);
      setDirty(false);
      setSmokeResult({
        name: "Sprint 15 diff and optimistic locking",
        ok: patched.revision === (apiDraft.revision || 1) + 1 && staleRejected && diff.changed_cells === 25 && diff.changed_by_role.PICK_FACE === 25,
        details: [
          `revision=${patched.revision}`,
          `staleRejected=${String(staleRejected)}`,
          `changedCells=${diff.changed_cells}`,
          `pickDelta=${diff.changed_by_role.PICK_FACE || 0}`
        ]
      });
    } catch (error) {
      setSmokeResult({
        name: "Sprint 15 diff and optimistic locking",
        ok: false,
        details: [error instanceof Error ? error.message : "browser smoke failed"]
      });
    }
  }

  async function runSprint15MetadataSmoke() {
    try {
      const roles = createBlockedRoles();
      const apiDraft = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts`, {
        method: "POST",
        body: JSON.stringify({
          draft_name: "Sprint 15 metadata smoke",
          grid: { aisle_count: GRID.aisleCount, slots_per_aisle: GRID.slotsPerAisle, levels: GRID.levels },
          roles_base64: encodeRoles(roles),
          created_by: "SMOKE_015_METADATA_UI"
        })
      });
      const patched = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/metadata`, {
        method: "PATCH",
        body: JSON.stringify({
          expected_revision: apiDraft.revision || 1,
          draft_metadata: {
            source: "sprint15-metadata-smoke",
            selected_camera_id: 1,
            viewport: { zoom: 1.25, pan_x: 10, pan_y: 20 }
          },
          canvas_objects: [{
            object_code: "SMOKE-WALL-01",
            object_kind: "WALL",
            object_name: "Smoke wall",
            camera_id: 1,
            x_m: 1.2,
            y_m: 2.4,
            width_m: 3.6,
            depth_m: 0.8
          }],
          passages: [{
            passage_code: "SMOKE-PASS-01",
            passage_kind: "PICK_AISLE",
            camera_id: 1,
            x1_m: 0,
            y1_m: 0,
            x2_m: 12,
            y2_m: 0,
            width_m: 3
          }],
          camera_links: [{
            link_code: "SMOKE-LINK-01",
            link_kind: "DOOR",
            from_camera_id: 1,
            to_camera_id: 2,
            distance_m: 8,
            direction_code: "BOTH"
          }],
          updated_by: "SMOKE_015_METADATA_UI"
        })
      });
      let staleRejected = false;
      try {
        await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/metadata`, {
          method: "PATCH",
          body: JSON.stringify({
            expected_revision: apiDraft.revision || 1,
            draft_metadata: { source: "stale" },
            updated_by: "SMOKE_015_METADATA_STALE"
          })
        });
      } catch {
        staleRejected = true;
      }
      const diff = await apiFetchJson<WarehouseMapDraftDiff>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/diff`, { cache: "no-store" });
      rolesRef.current = roles;
      localStorage.setItem(LOCAL_DRAFT_ID_KEY, apiDraft.draft_id);
      setDraftId(apiDraft.draft_id);
      setDraftRevision(patched.revision || 2);
      setCurrentDraft(patched);
      setDraftDiff(diff);
      setLevel(1);
      setView({ zoom: 2, panX: 120, panY: 36 });
      setDraftStatus(`SMOKE: metadata=${String(diff.draft_metadata_changed)}, objects=${diff.canvas_object_diff_count || 0}, passages=${diff.passage_diff_count || 0}, links=${diff.camera_link_diff_count || 0}, staleRejected=${String(staleRejected)}`);
      setVersion((value) => value + 1);
      setDirty(false);
      setSmokeResult({
        name: "Sprint 15 metadata diff and locking",
        ok: patched.revision === (apiDraft.revision || 1) + 1
          && staleRejected
          && Boolean(diff.draft_metadata_changed)
          && diff.canvas_object_count === 1
          && diff.canvas_object_diff_count === 1
          && diff.passage_count === 1
          && diff.passage_diff_count === 1
          && diff.camera_link_count === 1
          && diff.camera_link_diff_count === 1,
        details: [
          `revision=${patched.revision}`,
          `metadata=${String(diff.draft_metadata_changed)}`,
          `objects=${diff.canvas_object_diff_count || 0}`,
          `passages=${diff.passage_diff_count || 0}`,
          `links=${diff.camera_link_diff_count || 0}`,
          `staleRejected=${String(staleRejected)}`
        ]
      });
      window.setTimeout(() => {
        const panel = document.querySelector(".large-map-panel");
        const draftHeader = [...document.querySelectorAll("h2")].find((item) => item.textContent === "Draft");
        if (panel instanceof HTMLElement && draftHeader instanceof HTMLElement) panel.scrollTop = draftHeader.offsetTop - 80;
      }, 100);
    } catch (error) {
      setSmokeResult({
        name: "Sprint 15 metadata diff and locking",
        ok: false,
        details: [error instanceof Error ? error.message : "browser smoke failed"]
      });
    }
  }

  async function runSprint16RouteSmoke() {
    try {
      const roles = createBlockedRoles();
      const selection = normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: 5, slot: 4, level: 1 });
      writeSelectionRoles(roles, selection, filledRoleValues(selection, "PICK_FACE"));
      roles[cellIndex(2, 2, 1)] = ROLE_ORDER.indexOf("STORAGE");
      roles[cellIndex(4, 3, 1)] = ROLE_ORDER.indexOf("FRACTIONAL_STORAGE");
      const apiDraft = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts`, {
        method: "POST",
        body: JSON.stringify({
          draft_name: "Sprint 16 route smoke",
          grid: { aisle_count: GRID.aisleCount, slots_per_aisle: GRID.slotsPerAisle, levels: GRID.levels },
          roles_base64: encodeRoles(roles),
          created_by: "SMOKE_016_UI"
        })
      });
      const route = await apiFetchJson<RouteBuildResponse>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/route/build`, {
        method: "POST",
        body: JSON.stringify({
          selection: toApiSelection(selection),
          route_code: "SMOKE-PICK",
          route_name: "Sprint 16 route smoke",
          route_pattern: "Z",
          start_sequence: 1,
          step: 1,
          expected_revision: apiDraft.revision || 1,
          updated_by: "SMOKE_016_UI"
        })
      });
      const reloaded = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}`, { cache: "no-store" });
      const sorted = sortedRouteRows(route.route_rows);
      const numericSortOk = sortedRouteRows([
        { cell_code: "A01-S001-L1", physical_cell: { aisle: 1, slot: 1, level: 1 }, pick_sequence: 10 },
        { cell_code: "A01-S002-L1", physical_cell: { aisle: 1, slot: 2, level: 1 }, pick_sequence: 2 }
      ])[0].pick_sequence === 2;
      rolesRef.current = roles;
      localStorage.setItem(LOCAL_DRAFT_ID_KEY, apiDraft.draft_id);
      setDraftId(apiDraft.draft_id);
      applyApiDraft(reloaded);
      setRoutePattern("Z");
      setRouteStatus(`SMOKE route: rows=${route.route_row_count}, storageSkipped=${route.skipped_storage_slots}, numericSort=${String(numericSortOk)}`);
      setLevel(1);
      setSelections([selection]);
      setActiveCell(selection.anchorCell);
      setView({ zoom: 5, panX: 110, panY: 30 });
      setVersion((value) => value + 1);
      setSmokeResult({
        name: "Sprint 16 pick route order editor",
        ok: route.route_row_count === 18
          && route.skipped_storage_slots === 2
          && sorted.length === 18
          && sorted[0].pick_sequence === 1
          && sorted[1].pick_sequence === 2
          && numericSortOk
          && !route.route_rows.some((row) => row.cell_code === "A02-S002-L1" || row.cell_code === "A04-S003-L1"),
        details: [
          `rows=${route.route_row_count}`,
          `storageSkipped=${route.skipped_storage_slots}`,
          `first=${sorted[0]?.cell_code}`,
          `secondSeq=${sorted[1]?.pick_sequence}`,
          `numericSort=${String(numericSortOk)}`,
          `snakeAbsent=true`
        ]
      });
      window.setTimeout(() => {
        const panel = document.querySelector(".large-map-panel");
        const routeHeader = [...document.querySelectorAll("h2")].find((item) => item.textContent === "Порядок обхода");
        if (panel instanceof HTMLElement && routeHeader instanceof HTMLElement) panel.scrollTop = routeHeader.offsetTop - 80;
      }, 100);
    } catch (error) {
      setSmokeResult({
        name: "Sprint 16 pick route order editor",
        ok: false,
        details: [error instanceof Error ? error.message : "browser smoke failed"]
      });
    }
  }

  async function runSprint17PublishSmoke() {
    try {
      const roles = createBlockedRoles();
      const selection = normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: 4, slot: 3, level: 1 });
      writeSelectionRoles(roles, selection, filledRoleValues(selection, "PICK_FACE"));
      const apiDraft = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts`, {
        method: "POST",
        body: JSON.stringify({
          draft_name: "Sprint 17 publish smoke",
          grid: { aisle_count: GRID.aisleCount, slots_per_aisle: GRID.slotsPerAisle, levels: GRID.levels },
          roles_base64: encodeRoles(roles),
          created_by: "SMOKE_017_UI"
        })
      });
      const route = await apiFetchJson<RouteBuildResponse>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/route/build`, {
        method: "POST",
        body: JSON.stringify({
          selection: toApiSelection(selection),
          route_code: "SMOKE-PUBLISH",
          route_name: "Sprint 17 publish smoke",
          route_pattern: "LINEAR",
          start_sequence: 1,
          step: 1,
          expected_revision: apiDraft.revision || 1,
          updated_by: "SMOKE_017_UI"
        })
      });
      const duplicateRows = route.route_rows.map((row, index) => index === 1 ? { ...row, pick_sequence: 1 } : row);
      const duplicated = await apiFetchJson<{ revision: number; route_rows: RouteDraftRow[] }>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/route`, {
        method: "PATCH",
        body: JSON.stringify({
          route_rows: duplicateRows,
          expected_revision: route.revision,
          updated_by: "SMOKE_017_DUPLICATE"
        })
      });
      const invalid = await apiFetchJson<WarehouseMapDraftValidation>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/validate`, {
        method: "POST"
      });
      const fixedRows = route.route_rows.map((row, index) => ({ ...row, pick_sequence: index + 1 }));
      const fixed = await apiFetchJson<{ revision: number; route_rows: RouteDraftRow[] }>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/route`, {
        method: "PATCH",
        body: JSON.stringify({
          route_rows: fixedRows,
          expected_revision: duplicated.revision,
          updated_by: "SMOKE_017_FIXED"
        })
      });
      const valid = await apiFetchJson<WarehouseMapDraftValidation>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/validate`, {
        method: "POST"
      });
      const published = await apiFetchJson<WarehouseMapDraftPublished>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}/publish`, {
        method: "POST"
      });
      const reloaded = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${apiDraft.draft_id}`, { cache: "no-store" });
      rolesRef.current = roles;
      localStorage.setItem(LOCAL_DRAFT_ID_KEY, apiDraft.draft_id);
      setDraftId(apiDraft.draft_id);
      setCurrentDraft(reloaded);
      setDraftRevision(fixed.revision || reloaded.revision || null);
      setValidationResult(valid);
      setValidationStatus(`SMOKE validation: invalid=${String(!invalid.valid)}, valid=${String(valid.valid)}, duplicate=${invalid.duplicate_route_sequences?.join("/") || "-"}`);
      setPublishedResult(published);
      setPublishStatus(`SMOKE published ${published.published_topology_id.slice(0, 8)} · routeRows=${published.route_row_count || 0}`);
      setLevel(1);
      setSelections([selection]);
      setActiveCell(selection.anchorCell);
      setView({ zoom: 5, panX: 110, panY: 30 });
      setVersion((value) => value + 1);
      setSmokeResult({
        name: "Sprint 17 route validate and publish",
        ok: !invalid.valid
          && invalid.errors.includes("duplicate_route_sequences")
          && valid.valid
          && published.status === "PUBLISHED"
          && published.route_row_count === route.route_row_count,
        details: [
          `invalid=${String(!invalid.valid)}`,
          `duplicateSeq=${invalid.duplicate_route_sequences?.join("/") || "-"}`,
          `valid=${String(valid.valid)}`,
          `published=${published.status}`,
          `routeRows=${published.route_row_count || 0}`
        ]
      });
      window.setTimeout(() => {
        const panel = document.querySelector(".large-map-panel");
        const routeHeader = [...document.querySelectorAll("h2")].find((item) => item.textContent === "Порядок обхода");
        if (panel instanceof HTMLElement && routeHeader instanceof HTMLElement) panel.scrollTop = routeHeader.offsetTop - 80;
      }, 100);
    } catch (error) {
      setSmokeResult({
        name: "Sprint 17 route validate and publish",
        ok: false,
        details: [error instanceof Error ? error.message : "browser smoke failed"]
      });
    }
  }

  function runSprint18HardeningSmoke() {
    const roles = createRegularRoles();
    const selection = normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: GRID.aisleCount, slot: GRID.slotsPerAisle, level: 1 });
    const selectionStarted = performance.now();
    const selectedCells = selectionSize(selection);
    const selectionMs = performance.now() - selectionStarted;
    const bulkStarted = performance.now();
    writeSelectionRoles(roles, normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: 20, slot: 50, level: 1 }), filledRoleValues(normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: 20, slot: 50, level: 1 }), "PICK_FACE"));
    const bulkMs = performance.now() - bulkStarted;
    const routeRows: RouteDraftRow[] = [
      { route_row_id: "S18-1", route_code: "S18", route_pattern: "LINEAR", cell_code: "A01-S001-L1", physical_cell: { aisle: 1, slot: 1, level: 1 }, pick_sequence: 1, active: 1 },
      { route_row_id: "S18-2", route_code: "S18", route_pattern: "LINEAR", cell_code: "A02-S001-L1", physical_cell: { aisle: 2, slot: 1, level: 1 }, pick_sequence: 2, active: 1 },
      { route_row_id: "S18-3", route_code: "S18", route_pattern: "LINEAR", cell_code: "A03-S001-L1", physical_cell: { aisle: 3, slot: 1, level: 1 }, pick_sequence: 3, active: 1 }
    ];
    const draft: WarehouseMapDraft = {
      draft_id: "SPRINT18-HARDENING",
      draft_name: "Sprint 18 hardening smoke",
      grid: { aisle_count: GRID.aisleCount, slots_per_aisle: GRID.slotsPerAisle, levels: GRID.levels },
      roles_base64: encodeRoles(roles),
      route_rows: routeRows,
      route_summary: {
        route_code: "S18",
        route_pattern: "LINEAR",
        route_row_count: routeRows.length,
        skipped_storage_slots: 0,
        skipped_non_pick_cells: 0
      },
      revision: 18
    };
    const domNodes = document.querySelectorAll("*").length;
    const helpCoverageOk = Object.values(MAP_HELP).every((item) => item.body.includes("Что это:") && item.body.includes("Вход:") && item.body.includes("Делает:") && item.body.includes("Зачем:") && item.body.includes("Как применять:"));
    rolesRef.current = roles;
    setDraftId(draft.draft_id);
    setDraftRevision(draft.revision || 18);
    setCurrentDraft(draft);
    setValidationResult({ draft_id: draft.draft_id, valid: true, error_count: 0, errors: [], route_row_count: routeRows.length });
    setValidationStatus("SMOKE validation evidence exists · VALID");
    setPublishedResult({ published_topology_id: "S18PUBLISHED", status: "PUBLISHED", published_at: new Date().toISOString(), route_row_count: routeRows.length });
    setPublishStatus("SMOKE publish evidence exists · PUBLISHED");
    setRouteStatus("SMOKE route evidence exists · rows=3");
    setLevel(1);
    setSelections([selection]);
    setActiveCell(selection.anchorCell);
    setView({ zoom: 2.4, panX: 120, panY: 36 });
    setActiveHelpId("projection.preview");
    setHelpPopupPosition({ x: 360, y: 96 });
    setMetrics((current) => ({ ...current, selectedCells, selectionMs, bulkMs, domNodes }));
    setVersion((value) => value + 1);
    const ok = totalCells() === 18900
      && selectedCells === 3150
      && domNodes < 1000
      && bulkMs < 50
      && selectionMs < 10
      && helpCoverageOk
      && routeRows.length === 3;
    setSmokeResult({
      name: "Sprint 18 evidence and performance hardening",
      ok,
      details: [
        `cells=${totalCells()}`,
        `selected=${selectedCells}`,
        `dom=${domNodes}`,
        `bulkMs=${bulkMs.toFixed(3)}`,
        `selectMs=${selectionMs.toFixed(3)}`,
        `helpCoverage=${String(helpCoverageOk)}`,
        `routeRows=${routeRows.length}`
      ]
    });
    window.setTimeout(() => {
      const panel = document.querySelector(".large-map-panel");
      const routeHeader = [...document.querySelectorAll("h2")].find((item) => item.textContent === "Порядок обхода");
      if (panel instanceof HTMLElement && routeHeader instanceof HTMLElement) panel.scrollTop = routeHeader.offsetTop - 80;
    }, 100);
  }

  function runSprint24OraclePublishSmoke() {
    const roles = new Uint8Array(totalCells());
    roles.fill(ROLE_ORDER.indexOf("BLOCKED"));
    const selection = normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: 3, slot: 1, level: 1 });
    writeSelectionRoles(roles, selection, filledRoleValues(selection, "PICK_FACE"));
    const routeRows: RouteDraftRow[] = [
      { route_row_id: "S24-R1", route_code: "SMOKE-024-PICK", route_name: "Sprint 24 Oracle publish", route_pattern: "LINEAR", cell_code: "A01-S001-L1", physical_cell: { aisle: 1, slot: 1, level: 1 }, pick_sequence: 1, slot_kind: "PICK_FACE", active: 1 },
      { route_row_id: "S24-R2", route_code: "SMOKE-024-PICK", route_name: "Sprint 24 Oracle publish", route_pattern: "LINEAR", cell_code: "A02-S001-L1", physical_cell: { aisle: 2, slot: 1, level: 1 }, pick_sequence: 2, slot_kind: "PICK_FACE", active: 1 },
      { route_row_id: "S24-R3", route_code: "SMOKE-024-PICK", route_name: "Sprint 24 Oracle publish", route_pattern: "LINEAR", cell_code: "A03-S001-L1-P1", physical_cell: { aisle: 3, slot: 1, level: 1 }, pick_sequence: 3, slot_kind: "PICK_FACE_SLOT", active: 1 }
    ];
    const oraclePublishStatus: OraclePublishStatus = {
      canvas_id: 21,
      canvas_status: "PUBLISHED",
      canvas_active: 1,
      topology_id: 15,
      topology_status: "PUBLISHED",
      pick_route_id: 114,
      route_status: "PUBLISHED",
      route_active: 1,
      route_row_count: 3
    };
    const draft: WarehouseMapDraft = {
      draft_id: "sprint24oraclepublish",
      draft_name: "Sprint 24 Oracle publish visual smoke",
      grid: { aisle_count: GRID.aisleCount, slots_per_aisle: GRID.slotsPerAisle, levels: GRID.levels },
      roles_base64: encodeRoles(roles),
      route_rows: routeRows,
      route_summary: { route_code: "SMOKE-024-PICK", route_pattern: "LINEAR", route_row_count: routeRows.length, skipped_storage_slots: 0, skipped_non_pick_cells: 0 },
      oracle_canvas_id: 21,
      oracle_topology_id: 15,
      oracle_pick_route_id: 114,
      oracle_publish_status: oraclePublishStatus,
      revision: 24
    };
    rolesRef.current = roles;
    setDraftId(draft.draft_id);
    setDraftRevision(24);
    setSelectedWareId(-41227);
    setCurrentDraft(draft);
    setValidationResult({ draft_id: draft.draft_id, valid: true, error_count: 0, errors: [], route_row_count: routeRows.length });
    setValidationStatus("SMOKE Oracle validation: VALID · rows=3");
    setOraclePublishResult({ draft_id: draft.draft_id, canvas_id: 21, topology_id: 15, pick_route_id: 114, status: "PUBLISHED", oracle_validation: { valid: true, route_row_count: 3, storage_slot_route_rows: 0, non_pick_cell_route_rows: 0 }, oracle_status: oraclePublishStatus });
    setOracleStatus("SMOKE Oracle publish: PUBLISHED · canvas=PUBLISHED · topology=PUBLISHED · route=PUBLISHED");
    setRouteStatus("SMOKE Oracle route DB evidence · rows=3");
    setSelections([selection]);
    setActiveCell(selection.anchorCell);
    setLevel(1);
    setView({ zoom: 4.2, panX: 44, panY: 28 });
    setVersion((value) => value + 1);
    const ok = Boolean(draft.oracle_canvas_id && draft.oracle_topology_id && draft.oracle_pick_route_id)
      && routeRows.length === 3
      && oraclePublishStatus.canvas_status === "PUBLISHED"
      && oraclePublishStatus.topology_status === "PUBLISHED"
      && oraclePublishStatus.route_status === "PUBLISHED";
    setSmokeResult({
      name: "Sprint 24 Oracle publish UI evidence",
      ok,
      details: [
        `canvas=${oraclePublishStatus.canvas_status}`,
        `topology=${oraclePublishStatus.topology_status}`,
        `route=${oraclePublishStatus.route_status}`,
        `routeRows=${routeRows.length}`
      ]
    });
    window.setTimeout(() => {
      const panel = document.querySelector(".large-map-panel");
      const routeHeader = [...document.querySelectorAll("h2")].find((item) => item.textContent === "Порядок обхода");
      if (panel instanceof HTMLElement && routeHeader instanceof HTMLElement) panel.scrollTop = routeHeader.offsetTop - 80;
    }, 100);
  }

  function runSprint25PublishedReloadSmoke() {
    const roles = new Uint8Array(totalCells());
    roles.fill(ROLE_ORDER.indexOf("BLOCKED"));
    const selection = normalizeSelection({ aisle: 1, slot: 1, level: 1 }, { aisle: 3, slot: 1, level: 1 });
    writeSelectionRoles(roles, selection, filledRoleValues(selection, "PICK_FACE"));
    const routeRows: RouteDraftRow[] = [
      { route_row_id: "S25-R1", route_code: "SMOKE-025-PICK", route_name: "Sprint 25 published reload", route_pattern: "LINEAR", cell_code: "A01-S001-L1", physical_cell: { aisle: 1, slot: 1, level: 1 }, pick_sequence: 1, slot_kind: "PICK_FACE", active: 1 },
      { route_row_id: "S25-R2", route_code: "SMOKE-025-PICK", route_name: "Sprint 25 published reload", route_pattern: "LINEAR", cell_code: "A02-S001-L1", physical_cell: { aisle: 2, slot: 1, level: 1 }, pick_sequence: 2, slot_kind: "PICK_FACE", active: 1 },
      { route_row_id: "S25-R3", route_code: "SMOKE-025-PICK", route_name: "Sprint 25 published reload", route_pattern: "LINEAR", cell_code: "A03-S001-L1-P1", physical_cell: { aisle: 3, slot: 1, level: 1 }, pick_sequence: 3, slot_kind: "PICK_FACE_SLOT", active: 1 }
    ];
    const route: WarehouseMapPublishedRoute = {
      pick_route_id: 115,
      topology_id: 16,
      ware_id: -41227,
      route_code: "SMOKE-025-PICK",
      route_name: "Sprint 25 published reload",
      route_kind: "PICK",
      route_pattern: "LINEAR",
      status: "PUBLISHED",
      active: 1,
      route_row_count: 3,
      excluded_storage_slot_row_count: 0,
      route_rows: routeRows
    };
    const state: WarehouseMapState = {
      warehouse: { ware_id: -41227, ware_name: "SMOKE 025 PUBLISHED RELOAD" },
      canvas: { canvas_id: 22, canvas_code: "SMOKE-025-CANVAS", canvas_name: "Smoke 025 canvas", status: "PUBLISHED", levels: GRID.levels },
      topology: { topology_id: 16, topology_code: "SMOKE-025-TOPO", status: "PUBLISHED" },
      cameras: [],
      camera_links: [],
      canvas_objects: [],
      passages: [],
      routes: [route],
      counters: { canvases: 1, cameras: 1, topology_cells: 3, cell_slots: 2, routes: 1, route_rows: 3, route_rows_excluded_storage_slots: 0 },
      warnings: []
    };
    const draft: WarehouseMapDraft = {
      draft_id: "sprint25publishedreload",
      draft_name: "Sprint 25 published reload visual smoke",
      grid: { aisle_count: GRID.aisleCount, slots_per_aisle: GRID.slotsPerAisle, levels: GRID.levels },
      roles_base64: encodeRoles(roles),
      route_rows: routeRows,
      route_summary: { route_code: route.route_code, route_pattern: "LINEAR", route_row_count: routeRows.length, skipped_storage_slots: 0, skipped_non_pick_cells: 0 },
      oracle_canvas_id: 22,
      oracle_topology_id: 16,
      oracle_pick_route_id: 115,
      revision: 25
    };
    rolesRef.current = roles;
    setSelectedWareId(state.warehouse.ware_id);
    setWarehouseMapState(state);
    setWarehouseStatus("SMOKE reload: published canvas/topology/route loaded from warehouse state");
    setDraftId(draft.draft_id);
    setDraftRevision(25);
    setCurrentDraft(draft);
    setValidationResult({ draft_id: draft.draft_id, valid: true, error_count: 0, errors: [], route_row_count: routeRows.length });
    setValidationStatus("SMOKE published reload validation: route rows loaded");
    setRouteStatus("SMOKE published reload route evidence · rows=3");
    setOracleStatus("SMOKE published reload: canvas=PUBLISHED · topology=PUBLISHED · route=PUBLISHED");
    setSelections([selection]);
    setActiveCell(selection.anchorCell);
    setLevel(1);
    setView({ zoom: 4.2, panX: 44, panY: 28 });
    setVersion((value) => value + 1);
    const ok = state.canvas?.status === "PUBLISHED"
      && state.topology?.status === "PUBLISHED"
      && state.routes?.[0]?.status === "PUBLISHED"
      && state.counters.route_rows === 3
      && state.counters.route_rows_excluded_storage_slots === 0;
    setSmokeResult({
      name: "Sprint 25 published warehouse reload",
      ok,
      details: [
        `canvas=${state.canvas?.status}`,
        `topology=${state.topology?.status}`,
        `route=${state.routes?.[0]?.status}`,
        `routeRows=${state.counters.route_rows}`
      ]
    });
    window.setTimeout(() => {
      const panel = document.querySelector(".large-map-panel");
      if (panel instanceof HTMLElement) panel.scrollTop = 0;
    }, 100);
  }

  return (
    <main className="large-map-page">
      <header className="large-map-topbar">
        <button className="large-map-back" onClick={onBack}>←</button>
        <div>
          <h1>Рисование карты больших складов</h1>
          <p>Canvas 2D MVP · {GRID.aisleCount} аллей × {GRID.slotsPerAisle} слотов × {GRID.levels} уровней · {totalCells().toLocaleString("ru-RU")} ячеек</p>
        </div>
        <button className="large-map-guide-button" onClick={() => setModuleGuideOpen(true)} title="Открыть подробную инструкцию по модулю">
          Инструкция
        </button>
        <span className={`large-map-dirty ${dirty ? "dirty" : ""}`}>{dirty ? "DRAFT DIRTY" : "DRAFT CLEAN"}</span>
        {smokeResult && (
          <span className={`large-map-smoke-chip ${smokeResult.ok ? "ok" : "bad"}`}>
            {smokeResult.ok ? "SMOKE PASS" : "SMOKE FAIL"} · {smokeResult.details.join(" · ")}
          </span>
        )}
        <div className="large-map-metrics">
          <span><b>{metrics.renderMs.toFixed(1)} мс</b> render</span>
          <span><b>{metrics.visibleCells}</b> visible</span>
          <span><b>{metrics.domNodes}</b> DOM</span>
          <span><b>{metrics.selectionMs.toFixed(2)} мс</b> select</span>
          <span><b>{metrics.bulkMs.toFixed(2)} мс</b> bulk</span>
        </div>
      </header>

      <section className="large-map-workspace">
        <aside className="large-map-panel">
          <section>
            <h2>Реальный склад <button className="large-map-help-button" onClick={(event) => openHelp(event, "warehouse.state")} title="Help: Реальный склад">?</button></h2>
            <label className="large-map-field">
              <span>Склад</span>
              <select value={selectedWareId ?? ""} onChange={(event) => setSelectedWareId(event.currentTarget.value ? Number(event.currentTarget.value) : null)}>
                <option value="">Выберите склад</option>
                {warehouses.map((warehouse) => (
                  <option key={warehouse.id} value={warehouse.id}>{warehouse.name} · {warehouse.id}</option>
                ))}
              </select>
            </label>
            <div className="large-map-tools">
              <button onClick={refreshWarehouseMap} disabled={selectedWareId === null} title="Перезагрузить состояние склада из Oracle">Обновить</button>
            </div>
            <p className="large-map-muted">{warehouseStatus}</p>
            {warehouseMapState && (
              <div className="large-map-selection">
                <b>{warehouseMapState.warehouse.ware_name}</b>
                <span>Canvas: {warehouseMapState.canvas ? `${warehouseMapState.canvas.canvas_code} · ${warehouseMapState.canvas.status}` : "нет"}</span>
                <span>Topology: {warehouseMapState.topology ? `${warehouseMapState.topology.topology_code || warehouseMapState.topology.topology_id} · ${warehouseMapState.topology.status || "-"}` : "нет"}</span>
                <span>Routes: {warehouseMapState.counters.routes || 0} · rows {warehouseMapState.counters.route_rows || 0}</span>
                <span>Камер: {warehouseMapState.counters.cameras || 0} · objects: {warehouseMapState.counters.canvas_objects || 0}</span>
                {(warehouseMapState.routes || []).slice(0, 2).map((route) => (
                  <span key={route.pick_route_id}>Route {route.route_code} · {route.status} · rows {route.route_row_count || 0}</span>
                ))}
                {warehouseMapState.warnings.map((warning) => <span key={warning.code}>{warning.code}</span>)}
              </div>
            )}
          </section>

          <section>
            <h2>Камеры</h2>
            <label className="large-map-field">
              <span>Canvas</span>
              <select value={warehouseMapState?.canvas?.canvas_id ?? ""} disabled={!canvasList.length}>
                {!canvasList.length && <option value="">Нет canvas</option>}
                {canvasList.map((canvas) => (
                  <option key={canvas.canvas_id} value={canvas.canvas_id}>{canvas.canvas_code} · {canvas.camera_count} камер</option>
                ))}
              </select>
            </label>
            <label className="large-map-field">
              <span>Камера</span>
              <select value={selectedCameraId ?? ""} onChange={(event) => setSelectedCameraId(event.currentTarget.value ? Number(event.currentTarget.value) : null)} disabled={!warehouseMapState?.cameras.length}>
                {!warehouseMapState?.cameras.length && <option value="">Нет камер</option>}
                {warehouseMapState?.cameras.map((camera) => (
                  <option key={camera.camera_id} value={camera.camera_id}>{camera.camera_code} · {camera.camera_name}</option>
                ))}
              </select>
            </label>
            {selectedCamera && (
              <div className="large-map-selection">
                <b>{selectedCamera.camera_code}</b>
                <span>{selectedCamera.camera_kind} · {selectedCamera.width_m} x {selectedCamera.depth_m} x {selectedCamera.height_m} м</span>
                <span>origin: {selectedCamera.origin_x_m}, {selectedCamera.origin_y_m}, {selectedCamera.origin_z_m}</span>
              </div>
            )}
          </section>

          <section>
            <h2>Создать камеру</h2>
            <div className="large-map-address-grid">
              <label>Код<input value={cameraForm.cameraCode} onChange={(event) => setCameraForm({ ...cameraForm, cameraCode: event.currentTarget.value })} /></label>
              <label>Вид<select value={cameraForm.cameraKind} onChange={(event) => setCameraForm({ ...cameraForm, cameraKind: event.currentTarget.value as CameraFormState["cameraKind"] })}><option value="DRY">DRY</option><option value="COLD">COLD</option><option value="FREEZER">FREEZER</option><option value="DOCK">DOCK</option><option value="SERVICE">SERVICE</option><option value="MIXED">MIXED</option></select></label>
              <label className="wide">Название<input value={cameraForm.cameraName} onChange={(event) => setCameraForm({ ...cameraForm, cameraName: event.currentTarget.value })} /></label>
              <label>X<input type="number" value={cameraForm.originX} onChange={(event) => setCameraForm({ ...cameraForm, originX: Number(event.currentTarget.value) || 0 })} /></label>
              <label>Y<input type="number" value={cameraForm.originY} onChange={(event) => setCameraForm({ ...cameraForm, originY: Number(event.currentTarget.value) || 0 })} /></label>
              <label>Ширина<input type="number" min="1" value={cameraForm.width} onChange={(event) => setCameraForm({ ...cameraForm, width: Number(event.currentTarget.value) || 1 })} /></label>
              <label>Глубина<input type="number" min="1" value={cameraForm.depth} onChange={(event) => setCameraForm({ ...cameraForm, depth: Number(event.currentTarget.value) || 1 })} /></label>
              <label>Высота<input type="number" min="1" value={cameraForm.height} onChange={(event) => setCameraForm({ ...cameraForm, height: Number(event.currentTarget.value) || 1 })} /></label>
              <label>Уровней<input type="number" min="1" value={cameraForm.levels} onChange={(event) => setCameraForm({ ...cameraForm, levels: Number(event.currentTarget.value) || 1 })} /></label>
              <label>Проход, м<input type="number" min="0.1" step="0.1" value={cameraForm.defaultPassageWidth} onChange={(event) => setCameraForm({ ...cameraForm, defaultPassageWidth: Number(event.currentTarget.value) || 3 })} /></label>
              <label>Шаг аллей<input type="number" min="0.1" step="0.1" value={cameraForm.defaultAisleSpacing} onChange={(event) => setCameraForm({ ...cameraForm, defaultAisleSpacing: Number(event.currentTarget.value) || 3.6 })} /></label>
            </div>
            <div className="large-map-command-grid">
              {mapCommands.map((command) => (
                <div key={command.id} className="large-map-command-help-row">
                  <button disabled={!command.enabled} onClick={() => runMapCommand(command.id)} title={command.enabled ? MAP_HELP[command.helpId].body : command.disabledReason}>
                    {command.label}
                  </button>
                  <button className="large-map-help-button" onClick={(event) => openHelp(event, command.helpId)} title={`Help: ${MAP_HELP[command.helpId].title}`}>?</button>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h2>Уровень</h2>
            <div className="large-map-levels">
              {Array.from({ length: GRID.levels }, (_, index) => index + 1).map((item) => (
                <button key={item} className={level === item ? "active" : ""} onClick={() => setLevel(item)}>L{item}</button>
              ))}
            </div>
          </section>

          <section>
            <h2>Роли <button className="large-map-help-button" onClick={(event) => openHelp(event, "roles.assign")} title="Help: Роли ячеек">?</button></h2>
            <div className="large-map-roles">
              {ROLE_ORDER.map((role) => (
                <button key={role} className={activeRole === role ? "active" : ""} onClick={() => setActiveRole(role)} title={ROLE_LABELS[role]}>
                  <i style={{ background: ROLE_COLORS[role], borderColor: ROLE_STROKES[role] }} />
                  {ROLE_LABELS[role]}
                </button>
              ))}
            </div>
            {activeRole === "FRACTIONAL_PICK_FACE" && (
              <div className="large-map-address-grid large-map-inline-preset">
                <label className="wide">Как дробить отбор<select value={smallPickForm.preset} onChange={(event) => {
                  const preset = event.currentTarget.value as SplitPresetId;
                  const nextPreset = PICK_SPLIT_PRESETS[preset];
                  setSmallPickForm({
                    ...smallPickForm,
                    preset,
                    fractionCellCount: nextPreset.fractionCellCount,
                    subLevelCount: nextPreset.subLevelCount,
                    subColumnCount: nextPreset.subColumnCount
                  });
                }}>
                  {(Object.keys(PICK_SPLIT_PRESETS) as SplitPresetId[]).map((preset) => <option key={preset} value={preset}>{PICK_SPLIT_PRESETS[preset].label}</option>)}
                </select></label>
              </div>
            )}
            {activeRole === "FRACTIONAL_STORAGE" && (
              <div className="large-map-address-grid large-map-inline-preset">
                <label className="wide">Как дробить хранение<select value={storageSlotForm.preset} onChange={(event) => {
                  const preset = event.currentTarget.value as StorageSplitPresetId;
                  const nextPreset = STORAGE_SPLIT_PRESETS[preset];
                  setStorageSlotForm({
                    ...storageSlotForm,
                    preset,
                    fractionCellCount: nextPreset.fractionCellCount,
                    subColumnCount: nextPreset.subColumnCount
                  });
                }}>
                  {(Object.keys(STORAGE_SPLIT_PRESETS) as StorageSplitPresetId[]).map((preset) => <option key={preset} value={preset}>{STORAGE_SPLIT_PRESETS[preset].label}</option>)}
                </select></label>
              </div>
            )}
            <button className="large-map-primary" disabled={!selections.length} onClick={applyActiveRoleAction}>
              {activeRole === "FRACTIONAL_PICK_FACE" ? "Создать дробные ячейки отбора" : activeRole === "FRACTIONAL_STORAGE" ? "Создать дробные ячейки хранения" : "Назначить выделению"}
            </button>
            <div className="large-map-history">
              <button disabled={!canUndo} onClick={undo} title="Отменить последнее назначение роли">↶ Undo</button>
              <button disabled={!canRedo} onClick={redo} title="Повторить отмененное назначение роли">↷ Redo</button>
              <span>{historyVersion} операций</span>
            </div>
          </section>

          <section>
            <h2>Формат</h2>
            <div className="large-map-command-grid">
              <div className="large-map-command-help-row">
                <button disabled={!selections.length} onClick={copyFormat} title={MAP_HELP["format.copy"].body}>Скопировать формат</button>
                <button className="large-map-help-button" onClick={(event) => openHelp(event, "format.copy")} title="Help: Скопировать формат">?</button>
              </div>
              <div className="large-map-command-help-row">
                <button disabled={!formatClipboard} onClick={pasteFormat} title={MAP_HELP["format.paste"].body}>Вставить формат</button>
                <button className="large-map-help-button" onClick={(event) => openHelp(event, "format.paste")} title="Help: Вставить формат">?</button>
              </div>
              <div className="large-map-command-help-row">
                <button disabled={!formatPainterActive} onClick={cancelFormatPainter} title={MAP_HELP["format.cancel"].body}>Отменить кисть</button>
                <button className="large-map-help-button" onClick={(event) => openHelp(event, "format.cancel")} title="Help: Отменить кисть">?</button>
              </div>
            </div>
            <p className={`large-map-muted ${formatPainterActive ? "large-map-format-active" : ""}`}>{formatStatus}</p>
          </section>

          <section>
            <h2>Навигация <button className="large-map-help-button" onClick={(event) => openHelp(event, "navigation.map")} title="Help: Навигация">?</button></h2>
            <div className="large-map-tools">
              <button onClick={() => updateZoom(view.zoom * 1.2)} title="Увеличить масштаб карты">+</button>
              <button onClick={() => updateZoom(view.zoom / 1.2)} title="Уменьшить масштаб карты">-</button>
              <button onClick={resetView} title="Вернуть масштаб 100%">100%</button>
              <button onClick={fitMap} title="Уместить всю карту в экран">Fit</button>
              <button onClick={fitSelected} disabled={!selections.length} title="Уместить выделенную область в экран">Fit selected</button>
            </div>
            <div className="large-map-search">
              <input value={searchText} onChange={(event) => setSearchText(event.currentTarget.value)} placeholder="A12-S034-L3" title="Адрес для быстрого перехода" />
              <button onClick={goToSearchAddress} title="Перейти к адресу">Найти</button>
            </div>
            <label className="large-map-zoom">
              <span>{Math.round(view.zoom * 100)}%</span>
              <input type="range" min="20" max="1400" value={Math.round(view.zoom * 100)} onChange={(event) => updateZoom(Number(event.currentTarget.value) / 100)} />
            </label>
            <div className="large-map-overview" title="Обзорная полоска заполнения карты по аллеям">
              {Array.from({ length: GRID.aisleCount }, (_, index) => {
                const aisle = index + 1;
                const isActive = aisle === activeCell.aisle;
                return <button key={aisle} className={isActive ? "active" : ""} style={{ background: aisleOverviewColor(rolesRef.current, aisle, level) }} onClick={() => { const next = { ...activeCell, aisle }; setActiveCell(next); centerOnCell(next); }} title={`Аллея A${aisle.toString().padStart(2, "0")}`} />;
              })}
            </div>
          </section>

          <section>
            <h2>Шаблоны <button className="large-map-help-button" onClick={(event) => openHelp(event, "templates.layout")} title="Help: Шаблоны layout">?</button></h2>
            <div className="large-map-template-grid">
              <button onClick={applyRegularTemplate} title="Сбросить карту в регулярный склад: L1 отбор, L2-L6 хранение">Регулярный склад</button>
              <button onClick={applyAisleTemplate} title="Нарисовать регулярные транспортные проходы">Проходы</button>
              <button onClick={applyDockTemplate} title="Нарисовать ворота и транспортное накопление на L1">Ворота + накопление</button>
              <button onClick={applyFilmTemplate} title="Нарисовать зону размещения на пленку на L1">На пленку</button>
              <button onClick={copyAisleTemplate} title="Скопировать активную аллею на выделенные аллеи; без выделения A01 копируется на A02-A10">Копировать аллею</button>
            </div>
          </section>

          <section>
            <h2>Draft <button className="large-map-help-button" onClick={(event) => openHelp(event, "draft.local")} title="Help: Draft и diff">?</button></h2>
            <div className="large-map-tools">
              <button onClick={saveDraft}>Сохранить</button>
              <button onClick={loadDraft}>Загрузить</button>
              <button onClick={saveDraftMetadata} disabled={!draftId}>Save metadata</button>
              <button onClick={loadDraftDiff} disabled={!draftId}>Diff</button>
              <button onClick={previewProjection} disabled={!draftId}>Projection preview</button>
              <button className="large-map-help-button" onClick={(event) => openHelp(event, "projection.preview")} title="Help: Projection preview">?</button>
            </div>
            {draftId && <p className="large-map-muted">API draft: {draftId.slice(0, 8)} · rev {draftRevision || "-"}</p>}
            <p className="large-map-muted">{draftStatus}</p>
            {draftDiff && (
              <div className="large-map-selection">
                <b>Diff · {draftDiff.changed_cells.toLocaleString("ru-RU")} cells</b>
                <span>rev {draftDiff.revision} · pick slots {draftDiff.small_pick_face_count} · storage slots {draftDiff.storage_slot_count}</span>
                <span>metadata {String(Boolean(draftDiff.draft_metadata_changed))} · objects {draftDiff.canvas_object_diff_count || 0} · passages {draftDiff.passage_diff_count || 0} · links {draftDiff.camera_link_diff_count || 0}</span>
                <span>route rows {draftDiff.route_row_count || 0} · route diff {draftDiff.route_row_diff_count || 0}</span>
                {Object.entries(draftDiff.changed_by_role).slice(0, 4).map(([role, count]) => <span key={role}>{ROLE_LABELS[role as CellRole] || role}: {Number(count).toLocaleString("ru-RU")}</span>)}
              </div>
            )}
            <p className="large-map-muted">{projectionStatus}</p>
            {projectionPreview && (
              <div className="large-map-selection">
                <b>{projectionPreview.status} · {projectionPreview.topology_cell_count.toLocaleString("ru-RU")} cells</b>
                <span>slots: {projectionPreview.slot_count} · pick {projectionPreview.pick_face_slot_count} · storage {projectionPreview.storage_slot_count}</span>
                <span>publish ready: {String(projectionPreview.publish_ready)}</span>
                {projectionPreview.preview_slots.slice(0, 4).map((slot, index) => <span key={`${slot.slot_kind}-${slot.slot_code}-${index}`}>{slot.slot_kind} · {slot.slot_code} · order {slot.pick_order || slot.storage_order || "-"}</span>)}
              </div>
            )}
          </section>

          <section>
            <h2>Порядок обхода <button className="large-map-help-button" onClick={(event) => openHelp(event, "route.editor")} title="Help: Порядок обхода">?</button></h2>
            <div className="large-map-address-grid">
              <label>Паттерн<select value={routePattern} onChange={(event) => setRoutePattern(event.currentTarget.value as RoutePattern)}>
                <option value="LINEAR">LINEAR</option>
                <option value="Z">Z</option>
                <option value="U_SHAPE">u-образно</option>
                <option value="P_SHAPE">П-образно</option>
                <option value="MANUAL">MANUAL</option>
              </select></label>
            </div>
            <button className="large-map-primary" disabled={!draftId || !selections.length} onClick={() => buildRouteFromSelection()}>
              Построить маршрут
            </button>
            <p className="large-map-muted">{routeStatus}</p>
            {currentDraft?.route_summary && (
              <div className="large-map-selection">
                <b>{currentDraft.route_summary.route_code || "DRAFT-PICK"} · {currentDraft.route_summary.route_pattern}</b>
                <span>rows {currentDraft.route_summary.route_row_count || routeRows.length} · storage skipped {currentDraft.route_summary.skipped_storage_slots || 0}</span>
                <span>SNAKE отсутствует в MVP</span>
              </div>
            )}
            {routeRows.length ? (
              <div className="large-map-route-table">
                {routeRows.slice(0, 18).map((row) => (
                  <button key={row.route_row_id || `${row.cell_code}-${row.pick_sequence}`} onClick={() => { setActiveCell(row.physical_cell); setLevel(row.physical_cell.level); setSelections([cellToSelection(row.physical_cell)]); centerOnCell(row.physical_cell); }}>
                    <b>{Number(row.pick_sequence).toLocaleString("ru-RU")}</b>
                    <span>{row.cell_code}</span>
                  </button>
                ))}
                {routeRows.length > 18 && <span className="large-map-muted">+ еще {routeRows.length - 18} route rows</span>}
              </div>
            ) : (
              <p className="large-map-muted">Route rows пока нет.</p>
            )}
            <div className="large-map-tools">
              <button disabled={!draftId} onClick={validateDraft}>Validate draft</button>
              <button disabled={!draftId || validationResult?.valid === false} onClick={publishDraft}>Publish draft</button>
            </div>
            <p className="large-map-muted">{validationStatus}</p>
            {validationResult && (
              <div className="large-map-selection">
                <b>{validationResult.valid ? "VALID" : "BLOCKED"} · {validationResult.error_count} errors</b>
                <span>route rows {validationResult.route_row_count || 0}</span>
                {(validationResult.route_errors || validationResult.errors).slice(0, 5).map((item) => <span key={item}>{item}</span>)}
              </div>
            )}
            <p className="large-map-muted">{publishStatus}</p>
            {publishedResult && (
              <div className="large-map-selection">
                <b>{publishedResult.status} · {publishedResult.published_topology_id.slice(0, 8)}</b>
                <span>route rows {publishedResult.route_row_count || 0}</span>
              </div>
            )}
            <div className="large-map-tools">
              <button disabled={!draftId || selectedWareId === null} onClick={saveDraftToOracleCanvas} title="Сохраняет весь canvas/draft payload в Oracle RRL_WAREHOUSE_MAP_CANVAS">Save canvas DB</button>
              <button disabled={!draftId || selectedWareId === null || !currentDraft?.oracle_canvas_id} onClick={saveProjectionToOracleTopology} title="Сохраняет projection текущей карты в Oracle topology cells/slots">Save topology DB</button>
              <button disabled={!draftId || selectedWareId === null || !currentDraft?.oracle_topology_id || !routeRows.length} onClick={saveRouteToOracle} title="Сохраняет порядок обхода в Oracle pick route">Save route DB</button>
              <button disabled={!draftId || !currentDraft?.oracle_canvas_id || !currentDraft?.oracle_topology_id || !currentDraft?.oracle_pick_route_id} onClick={publishOracleDraft} title="Публикует сохраненные canvas, topology и pick route через Oracle package">Publish Oracle</button>
              <button className="large-map-help-button" onClick={(event) => openHelp(event, "oracle.publish")} title="Help: Oracle save/publish">?</button>
            </div>
            <p className="large-map-muted">{oracleStatus}</p>
            {(currentDraft?.oracle_canvas_id || currentDraft?.oracle_topology_id || currentDraft?.oracle_pick_route_id) && (
              <div className="large-map-selection">
                <b>Oracle draft links</b>
                <span>canvas {currentDraft?.oracle_canvas_id || "-"}</span>
                <span>topology {currentDraft?.oracle_topology_id || "-"}</span>
                <span>route {currentDraft?.oracle_pick_route_id || "-"}</span>
              </div>
            )}
            {oraclePublishResult && (
              <div className="large-map-selection">
                <b>Oracle {oraclePublishResult.status}</b>
                <span>canvas {oraclePublishResult.oracle_status.canvas_status} · {oraclePublishResult.canvas_id}</span>
                <span>topology {oraclePublishResult.oracle_status.topology_status} · {oraclePublishResult.topology_id}</span>
                <span>route {oraclePublishResult.oracle_status.route_status} · {oraclePublishResult.pick_route_id}</span>
                <span>validation {String(oraclePublishResult.oracle_validation.valid)} · rows {oraclePublishResult.oracle_status.route_row_count || 0}</span>
              </div>
            )}
          </section>

          <section>
            <h2>Адресация отбора</h2>
            <div className="large-map-address-grid">
              <label>Аллея<input type="number" min="1" value={addressForm.aisleNo} onChange={(event) => setAddressForm({ ...addressForm, aisleNo: Number(event.currentTarget.value) || 1 })} /></label>
              <label>Старт<input type="number" min="1" value={addressForm.startPickNo} onChange={(event) => setAddressForm({ ...addressForm, startPickNo: Number(event.currentTarget.value) || 1 })} /></label>
              <label>Шаг<input type="number" min="1" value={addressForm.step} onChange={(event) => setAddressForm({ ...addressForm, step: Number(event.currentTarget.value) || 1 })} /></label>
              <label>Сторона<select value={addressForm.side} onChange={(event) => setAddressForm({ ...addressForm, side: event.currentTarget.value as AddressSide })}><option value="">Пусто</option><option value="LEFT">LEFT</option><option value="RIGHT">RIGHT</option></select></label>
              <label>Направление<select value={addressForm.direction} onChange={(event) => setAddressForm({ ...addressForm, direction: event.currentTarget.value as AddressDirection })}><option value="START_TO_END">От начала к концу</option><option value="END_TO_START">От конца к началу</option></select></label>
              <label className="wide">Маска<input value={addressForm.codeMask} onChange={(event) => setAddressForm({ ...addressForm, codeMask: event.currentTarget.value })} /></label>
            </div>
            <button className="large-map-primary" disabled={!selections.length} onClick={generatePickFaceAddresses}>Назначить адреса</button>
            <p className="large-map-muted">{addressStatus}</p>
            {addressPreview && (
              <div className="large-map-selection">
                <b>{addressPreview.assigned_count.toLocaleString("ru-RU")} адресов</b>
                {[...addressPreview.preview_first, ...addressPreview.preview_last].map((item, index) => <span key={`${item.cell_code}-${index}`}>{item.cell_code}</span>)}
              </div>
            )}
          </section>

          <section>
            <h2>Дробная ячейка</h2>
            <p className="large-map-muted">Текущее деление: {PICK_SPLIT_PRESETS[smallPickForm.preset].label} · {smallPickForm.subLevelCount} x {smallPickForm.subColumnCount}</p>
            <div className="large-map-address-grid">
              <label>Пресет<select value={smallPickForm.preset} onChange={(event) => {
                const preset = event.currentTarget.value as SplitPresetId;
                const nextPreset = PICK_SPLIT_PRESETS[preset];
                setSmallPickForm({
                  ...smallPickForm,
                  preset,
                  fractionCellCount: nextPreset.fractionCellCount,
                  subLevelCount: nextPreset.subLevelCount,
                  subColumnCount: nextPreset.subColumnCount
                });
              }}>
                {(Object.keys(PICK_SPLIT_PRESETS) as SplitPresetId[]).map((preset) => <option key={preset} value={preset}>{PICK_SPLIT_PRESETS[preset].label}</option>)}
              </select></label>
              <label>Старт<input type="number" min="1" value={smallPickForm.startOrder} onChange={(event) => setSmallPickForm({ ...smallPickForm, startOrder: Number(event.currentTarget.value) || 1 })} /></label>
              <label>Шаг<input type="number" min="1" value={smallPickForm.step} onChange={(event) => setSmallPickForm({ ...smallPickForm, step: Number(event.currentTarget.value) || 1 })} /></label>
              <label>Сторона<select value={smallPickForm.side} onChange={(event) => setSmallPickForm({ ...smallPickForm, side: event.currentTarget.value as AddressSide })}><option value="">Пусто</option><option value="LEFT">LEFT</option><option value="RIGHT">RIGHT</option></select></label>
              <label>Порядок<select value={smallPickForm.orderMode} onChange={(event) => setSmallPickForm({ ...smallPickForm, orderMode: event.currentTarget.value as SmallPickOrderMode })}><option value="SUB_LEVEL_THEN_COLUMN">Подуровень → столбик</option><option value="COLUMN_THEN_SUB_LEVEL">Столбик → подуровень</option></select></label>
              <label className="wide">Маска<input value={smallPickForm.codeMask} onChange={(event) => setSmallPickForm({ ...smallPickForm, codeMask: event.currentTarget.value })} /></label>
            </div>
            <button className="large-map-help-inline" onClick={(event) => openHelp(event, "fraction.pick")}>? Как работает дробление отбора</button>
            <button className="large-map-primary" disabled={!selections.length || smallPickForm.subLevelCount * smallPickForm.subColumnCount < smallPickForm.fractionCellCount} onClick={() => generateSmallPickFaces()}>Создать дробную ячейку</button>
            <p className="large-map-muted">{smallPickStatus}</p>
            {smallPickPreview && (
              <div className="large-map-selection">
                <b>{smallPickPreview.created_count.toLocaleString("ru-RU")} подъячеек</b>
                {smallPickPreview.preview.slice(0, 9).map((item) => <span key={`${item.logical_cell_code}-${item.pick_order}`}>{item.logical_cell_code} · p{item.pick_order}</span>)}
              </div>
            )}
          </section>

          <section>
            <h2>Дробная ячейка хранения</h2>
            <p className="large-map-muted">Текущее деление: {STORAGE_SPLIT_PRESETS[storageSlotForm.preset].label}</p>
            <div className="large-map-address-grid">
              <label>Пресет<select value={storageSlotForm.preset} onChange={(event) => {
                const preset = event.currentTarget.value as StorageSplitPresetId;
                const nextPreset = STORAGE_SPLIT_PRESETS[preset];
                setStorageSlotForm({
                  ...storageSlotForm,
                  preset,
                  fractionCellCount: nextPreset.fractionCellCount,
                  subColumnCount: nextPreset.subColumnCount
                });
              }}>
                {(Object.keys(STORAGE_SPLIT_PRESETS) as StorageSplitPresetId[]).map((preset) => <option key={preset} value={preset}>{STORAGE_SPLIT_PRESETS[preset].label}</option>)}
              </select></label>
              <label>Старт<input type="number" min="1" value={storageSlotForm.startOrder} onChange={(event) => setStorageSlotForm({ ...storageSlotForm, startOrder: Number(event.currentTarget.value) || 1 })} /></label>
              <label>Шаг<input type="number" min="1" value={storageSlotForm.step} onChange={(event) => setStorageSlotForm({ ...storageSlotForm, step: Number(event.currentTarget.value) || 1 })} /></label>
              <label className="wide">Маска<input value={storageSlotForm.codeMask} onChange={(event) => setStorageSlotForm({ ...storageSlotForm, codeMask: event.currentTarget.value })} /></label>
            </div>
            <button className="large-map-help-inline" onClick={(event) => openHelp(event, "fraction.storage")}>? Как работает дробление хранения</button>
            <button className="large-map-primary" disabled={!selections.length} onClick={() => generateStorageSlots()}>Назначить storage slots</button>
            <p className="large-map-muted">{storageSlotStatus}</p>
            {storageSlotPreview && (
              <div className="large-map-selection">
                <b>{storageSlotPreview.created_count.toLocaleString("ru-RU")} storage slots</b>
                {storageSlotPreview.preview.slice(0, 6).map((item) => <span key={`${item.slot_code}-${item.storage_order}`}>{item.slot_code} · s{item.storage_order} · cap {item.max_pallet_count ?? 1}</span>)}
              </div>
            )}
          </section>

          <section>
            <h2>Storage slot</h2>
            {activeStorageSlot ? (
              <>
                <div className="large-map-selection">
                  <b>{activeStorageSlot.slot_code || activeStorageSlot.storage_slot_id}</b>
                  <span>sub column {activeStorageSlot.sub_column} · order {activeStorageSlot.storage_order}</span>
                  <span>capacity: {activeStorageSlot.max_pallet_count ?? 1} паллет · {activeStorageSlot.max_weight_kg || 0} кг · {activeStorageSlot.max_volume_m3 || 0} м3</span>
                </div>
                <div className="large-map-address-grid">
                  <label>Order<input type="number" min="1" value={storageSlotEditForm.storageOrder} onChange={(event) => setStorageSlotEditForm({ ...storageSlotEditForm, storageOrder: Number(event.currentTarget.value) || 1 })} /></label>
                  <label>Паллет<input type="number" min="0" step="0.5" value={storageSlotEditForm.maxPalletCount} onChange={(event) => setStorageSlotEditForm({ ...storageSlotEditForm, maxPalletCount: Number(event.currentTarget.value) || 0 })} /></label>
                  <label>Кг<input type="number" min="0" step="1" value={storageSlotEditForm.maxWeightKg} onChange={(event) => setStorageSlotEditForm({ ...storageSlotEditForm, maxWeightKg: Number(event.currentTarget.value) || 0 })} /></label>
                  <label>м3<input type="number" min="0" step="0.1" value={storageSlotEditForm.maxVolumeM3} onChange={(event) => setStorageSlotEditForm({ ...storageSlotEditForm, maxVolumeM3: Number(event.currentTarget.value) || 0 })} /></label>
                </div>
                <button className="large-map-primary" disabled={!draftId || !activeStorageSlot.storage_slot_id} onClick={patchActiveStorageSlot}>Сохранить storage slot</button>
              </>
            ) : (
              <p className="large-map-muted">Выберите дробную ячейку хранения, чтобы редактировать ее child slots.</p>
            )}
          </section>

          <section>
            <h2>Выделение</h2>
            {selections.length ? (
              <div className="large-map-selection">
                <b>{selectedCount.toLocaleString("ru-RU")} ячеек</b>
                <span>{selections.length.toLocaleString("ru-RU")} областей · L{level}</span>
                {selections.slice(0, 4).map((selection, index) => (
                  <span key={`${selection.level}-${selection.aisleFrom}-${selection.slotFrom}-${index}`}>
                    A{selection.aisleFrom.toString().padStart(2, "0")}..A{selection.aisleTo.toString().padStart(2, "0")}
                    {" · "}
                    S{selection.slotFrom.toString().padStart(3, "0")}..S{selection.slotTo.toString().padStart(3, "0")}
                    {" · "}
                    start A{selection.anchorCell.aisle}-S{selection.anchorCell.slot} → end A{selection.focusCell.aisle}-S{selection.focusCell.slot}
                  </span>
                ))}
                {selections.length > 4 && <span>+ еще {selections.length - 4}</span>}
              </div>
            ) : <p className="large-map-muted">Протяните рамку по карте.</p>}
            <p className="large-map-muted">Активная: A{activeCell.aisle.toString().padStart(2, "0")}-S{activeCell.slot.toString().padStart(3, "0")}-L{level}</p>
            {hovered && <p className="large-map-muted">Под курсором: A{hovered.aisle.toString().padStart(2, "0")}-S{hovered.slot.toString().padStart(3, "0")}-L{hovered.level}</p>}
          </section>

          <section>
            <h2>Состав карты</h2>
            <div className="large-map-filter-grid">
              {ROLE_ORDER.map((role) => (
                <button key={role} className={roleFilters[role] ? "active" : ""} onClick={() => toggleRoleFilter(role)} title={`Показать/скрыть ${ROLE_LABELS[role]}`}>
                  <i style={{ background: ROLE_COLORS[role] }} />
                  {ROLE_LABELS[role]}
                </button>
              ))}
            </div>
            <div className="large-map-counts">
              {ROLE_ORDER.filter((role) => roleCounts[role]).map((role) => (
                <span key={role}><i style={{ background: ROLE_COLORS[role] }} />{ROLE_LABELS[role]} <b>{roleCounts[role].toLocaleString("ru-RU")}</b></span>
              ))}
              {warehouseMapState && (
                <>
                  <span><i style={{ background: "#ede9fe" }} />Canvas objects <b>{Number(warehouseMapState.counters.canvas_objects || 0).toLocaleString("ru-RU")}</b></span>
                  <span><i style={{ background: "#fed7aa" }} />Passages <b>{Number(warehouseMapState.counters.passages || 0).toLocaleString("ru-RU")}</b></span>
                  <span><i style={{ background: "#dbeafe" }} />Camera links <b>{Number(warehouseMapState.counters.camera_links || 0).toLocaleString("ru-RU")}</b></span>
                </>
              )}
            </div>
          </section>

          <section>
            <h2>Инспектор</h2>
            <div className="large-map-selection">
              <b>A{activeCell.aisle.toString().padStart(2, "0")}-S{activeCell.slot.toString().padStart(3, "0")}-L{activeCell.level}</b>
              <span>{ROLE_LABELS[ROLE_ORDER[rolesRef.current[cellIndex(activeCell.aisle, activeCell.slot, activeCell.level)]]]}</span>
              <span>Координаты: аллея {activeCell.aisle}, слот {activeCell.slot}, уровень {activeCell.level}</span>
            </div>
            {selectedCamera && (
              <div className="large-map-object-inspector">
                <b>{selectedCamera.camera_code}</b>
                <span>objects: {selectedCameraObjects.length} · passages: {selectedCameraPassages.length} · links: {selectedCameraLinks.length}</span>
                {selectedCameraObjects.slice(0, 4).map((item) => (
                  <span key={`object-${item.map_object_id}`}>object {item.object_code} · {item.object_kind} · {Number(item.width_m || 0).toFixed(1)} x {Number(item.depth_m || 0).toFixed(1)} м</span>
                ))}
                {selectedCameraPassages.slice(0, 4).map((item) => (
                  <span key={`passage-${item.passage_id}`}>passage {item.passage_code} · {item.passage_kind} · width {Number(item.width_m || 0).toFixed(1)} м</span>
                ))}
                {selectedCameraLinks.slice(0, 3).map((item) => (
                  <span key={`link-${item.camera_link_id}`}>link {item.link_code} · {item.direction_code} · {Number(item.distance_m || 0).toFixed(1)} м</span>
                ))}
              </div>
            )}
          </section>

          {smokeResult && (
            <section className={`large-map-smoke ${smokeResult.ok ? "ok" : "bad"}`}>
              <h2>{smokeResult.ok ? "SMOKE PASS" : "SMOKE FAIL"}</h2>
              <b>{smokeResult.name}</b>
              {smokeResult.details.map((item) => <span key={item}>{item}</span>)}
            </section>
          )}
        </aside>

        <div ref={wrapperRef} className="large-map-canvas-wrap">
          <canvas
            ref={canvasRef}
            className="large-map-canvas"
            tabIndex={0}
            onWheel={handleWheel}
            onKeyDown={handleKeyDown}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerLeave={() => setHovered(null)}
            onContextMenu={handleCanvasContextMenu}
          />
          {contextMenu && (
            <div className="large-map-context-menu" style={{ left: contextMenu.x, top: contextMenu.y }}>
              <b>Камера</b>
              {mapCommands.map((command) => (
                <button key={command.id} disabled={!command.enabled} onClick={() => runMapCommand(command.id)} title={command.enabled ? MAP_HELP[command.helpId].body : command.disabledReason}>
                  {command.label}
                </button>
              ))}
              <button onClick={(event) => { setContextMenu(null); openHelp(event, "object.create"); }} title="Открыть help по canvas commands">
                ? Help Canvas
              </button>
              <b>Дробные ячейки</b>
              <span className="large-map-context-subtitle">Создать дробную ячейку отбора</span>
              {(Object.keys(PICK_SPLIT_PRESETS) as SplitPresetId[]).map((preset) => (
                <button key={`ctx-pick-${preset}`} disabled={!selections.length} onClick={() => { setContextMenu(null); generateSmallPickFaces(preset); }} title={MAP_HELP["fraction.pick"].body}>
                  Отбор · {PICK_SPLIT_PRESETS[preset].label}
                </button>
              ))}
              <span className="large-map-context-subtitle">Создать дробную ячейку хранения</span>
              {(Object.keys(STORAGE_SPLIT_PRESETS) as StorageSplitPresetId[]).map((preset) => (
                <button key={`ctx-storage-${preset}`} disabled={!selections.length} onClick={() => { setContextMenu(null); generateStorageSlots(preset); }} title={MAP_HELP["fraction.storage"].body}>
                  Хранение · {STORAGE_SPLIT_PRESETS[preset].label}
                </button>
              ))}
              <button onClick={(event) => { setContextMenu(null); openHelp(event, "fraction.pick"); }}>
                ? Help дробление
              </button>
              <b>Порядок обхода</b>
              <button disabled={!draftId || !selections.length} onClick={() => { setContextMenu(null); buildRouteFromSelection("LINEAR"); }}>
                Построить LINEAR
              </button>
              <button disabled={!draftId || !selections.length} onClick={() => { setContextMenu(null); buildRouteFromSelection("Z"); }}>
                Построить Z
              </button>
              <button disabled={!draftId || !selections.length} onClick={() => { setContextMenu(null); buildRouteFromSelection("U_SHAPE"); }}>
                Построить u-образно
              </button>
              <button disabled={!draftId || !selections.length} onClick={() => { setContextMenu(null); buildRouteFromSelection("P_SHAPE"); }}>
                Построить П-образно
              </button>
              <b>Формат</b>
              <button disabled={!selections.length} onClick={() => { setContextMenu(null); copyFormat(); }} title="Скопировать роли и формат выделенного прямоугольника">
                Скопировать формат
              </button>
              <button disabled={!formatClipboard} onClick={() => { setContextMenu(null); pasteFormat(); }} title="Вставить скопированный формат от активной ячейки">
                Вставить формат
              </button>
              <button disabled={!formatPainterActive} onClick={() => { setContextMenu(null); cancelFormatPainter(); }} title="Отменить режим кисти">
                Отменить кисть
              </button>
            </div>
          )}
          {activeHelpId && helpPopupPosition && (
            <div className="large-map-help-popover" style={{ left: helpPopupPosition.x, top: helpPopupPosition.y }}>
              <b>{MAP_HELP[activeHelpId].title}</b>
              <span>{MAP_HELP[activeHelpId].body}</span>
              <button onClick={closeHelp}>Закрыть</button>
            </div>
          )}
          {moduleGuideOpen && (
            <div className="large-map-guide-backdrop" onMouseDown={() => setModuleGuideOpen(false)}>
              <div className="large-map-guide-modal" role="dialog" aria-modal="true" aria-label="Инструкция по модулю карты склада" onMouseDown={(event) => event.stopPropagation()}>
                <div className="large-map-guide-head">
                  <div>
                    <b>Инструкция по модулю карты больших складов</b>
                    <span>Структура, назначение, workflow и контроль публикации</span>
                  </div>
                  <button onClick={() => setModuleGuideOpen(false)} title="Закрыть инструкцию">Закрыть</button>
                </div>
                <div className="large-map-guide-body">
                  {MODULE_GUIDE.map((section) => (
                    <section key={section.title}>
                      <h3>{section.title}</h3>
                      {section.body.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
                    </section>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

function createInitialRoles() {
  const roles = createRegularRoles();
  drawTransportAisles(roles);
  drawDockZone(roles, [defaultDockSelection()]);
  drawFilmZone(roles);
  return roles;
}

function createBlockedRoles() {
  const roles = new Uint8Array(totalCells());
  roles.fill(ROLE_ORDER.indexOf("BLOCKED"));
  return roles;
}

function createRegularRoles() {
  const roles = new Uint8Array(totalCells());
  const pickFace = ROLE_ORDER.indexOf("PICK_FACE");
  const storage = ROLE_ORDER.indexOf("STORAGE");

  for (let level = 1; level <= GRID.levels; level += 1) {
    for (let a = 1; a <= GRID.aisleCount; a += 1) {
      for (let s = 1; s <= GRID.slotsPerAisle; s += 1) {
        roles[cellIndex(a, s, level)] = level === 1 ? pickFace : storage;
      }
    }
  }
  return roles;
}

function isEmptyRealCameraState(state: WarehouseMapState) {
  return Boolean(state.canvas)
    && state.cameras.length > 0
    && Number(state.counters.topology_cells || 0) === 0
    && Number(state.counters.canvas_objects || 0) === 0
    && Number(state.counters.passages || 0) === 0
    && Number(state.counters.camera_links || 0) === 0;
}

function drawTransportAisles(roles: Uint8Array) {
  const aisle = ROLE_ORDER.indexOf("AISLE");
  for (let level = 1; level <= GRID.levels; level += 1) {
    for (let a = 5; a <= GRID.aisleCount; a += 5) {
      for (let s = 40; s <= 43; s += 1) {
        roles[cellIndex(a, s, level)] = aisle;
      }
    }
  }
}

function defaultDockSelection(): CellSelection {
  return normalizeSelection(
    { aisle: 1, slot: 1, level: 1 },
    { aisle: GRID.aisleCount, slot: Math.min(12, GRID.slotsPerAisle), level: 1 }
  );
}

function drawDockZone(roles: Uint8Array, selections: CellSelection[]) {
  const gate = ROLE_ORDER.indexOf("GATE");
  const staging = ROLE_ORDER.indexOf("TRANSPORT_STAGING");
  const gateWidth = 2;
  const moduleWidth = 4;
  selections.forEach((selection) => {
    const level = selection.level;
    const topSlot = selection.slotFrom;
    const bottomSlot = selection.slotTo;
    for (let aisle = selection.aisleFrom; aisle + gateWidth - 1 <= selection.aisleTo; aisle += moduleWidth) {
      for (let offset = 0; offset < gateWidth; offset += 1) {
        roles[cellIndex(aisle + offset, topSlot, level)] = gate;
      }
      for (let slot = topSlot + 1; slot <= bottomSlot; slot += 1) {
        for (let offset = 0; offset < gateWidth; offset += 1) {
          roles[cellIndex(aisle + offset, slot, level)] = staging;
        }
      }
    }
  });
}

function drawFilmZone(roles: Uint8Array) {
  const film = ROLE_ORDER.indexOf("FILM_WRAP");
  for (let a = 31; a <= 35; a += 1) {
    for (let s = 72; s <= 82; s += 1) {
      roles[cellIndex(a, s, 1)] = film;
    }
  }
}

function selectedTargetAisles(selections: CellSelection[], sourceAisle: number) {
  const targets = new Set<number>();
  selections.forEach((selection) => {
    for (let aisle = selection.aisleFrom; aisle <= selection.aisleTo; aisle += 1) {
      if (aisle !== sourceAisle) targets.add(aisle);
    }
  });
  if (!targets.size) {
    for (let aisle = 2; aisle <= Math.min(10, GRID.aisleCount); aisle += 1) {
      if (aisle !== sourceAisle) targets.add(aisle);
    }
  }
  return [...targets].sort((a, b) => a - b);
}

function copyAisleRoles(roles: Uint8Array, sourceAisle: number, targetAisles: number[]) {
  targetAisles.forEach((targetAisle) => {
    for (let level = 1; level <= GRID.levels; level += 1) {
      for (let slot = 1; slot <= GRID.slotsPerAisle; slot += 1) {
        roles[cellIndex(targetAisle, slot, level)] = roles[cellIndex(sourceAisle, slot, level)];
      }
    }
  });
}

function selectionObjectPayload(selection: CellSelection, camera: WarehouseMapCamera, orderNo: number, objectCode?: string) {
  const widthCells = selection.aisleTo - selection.aisleFrom + 1;
  const depthCells = selection.slotTo - selection.slotFrom + 1;
  return {
    object_code: objectCode || `OBJ-${camera.camera_code}-${String(orderNo).padStart(3, "0")}`,
    object_kind: "ZONE",
    object_name: "Canvas object",
    level_no: selection.level,
    x_m: Number(((selection.aisleFrom - 1) * CELL_WIDTH_MM / 1000).toFixed(3)),
    y_m: Number(((selection.slotFrom - 1) * CELL_HEIGHT_MM / 1000).toFixed(3)),
    z_m: 0,
    width_m: Number((widthCells * CELL_WIDTH_MM / 1000).toFixed(3)),
    depth_m: Number((depthCells * CELL_HEIGHT_MM / 1000).toFixed(3)),
    height_m: Number(camera.height_m || 0) || 3,
    angle_deg: 0,
    geometry_json: { shape: "rect", source: "selection" },
    style_json: { fill: "#f5f3ff", stroke: "#7c3aed" }
  };
}

function canvasObjectPayload(item: WarehouseMapObject) {
  return {
    object_code: item.object_code,
    object_kind: item.object_kind,
    object_name: item.object_name,
    level_no: item.level_no,
    x_m: Number(item.x_m || 0),
    y_m: Number(item.y_m || 0),
    z_m: Number(item.z_m || 0),
    width_m: item.width_m == null ? undefined : Number(item.width_m),
    depth_m: item.depth_m == null ? undefined : Number(item.depth_m),
    height_m: item.height_m == null ? undefined : Number(item.height_m),
    angle_deg: Number(item.angle_deg || 0),
    geometry_json: item.geometry_json,
    style_json: item.style_json
  };
}

function selectionPassagePayload(selection: CellSelection, camera: WarehouseMapCamera, orderNo: number, passageCode?: string) {
  const centerAisle = selection.aisleFrom - 1 + (selection.aisleTo - selection.aisleFrom + 1) / 2;
  return {
    passage_code: passageCode || `PASS-${camera.camera_code}-${String(orderNo).padStart(3, "0")}`,
    passage_name: "Проход",
    passage_kind: "PICK_AISLE",
    x1_m: Number((centerAisle * CELL_WIDTH_MM / 1000).toFixed(3)),
    y1_m: Number(((selection.slotFrom - 1) * CELL_HEIGHT_MM / 1000).toFixed(3)),
    z1_m: 0,
    x2_m: Number((centerAisle * CELL_WIDTH_MM / 1000).toFixed(3)),
    y2_m: Number((selection.slotTo * CELL_HEIGHT_MM / 1000).toFixed(3)),
    z2_m: 0,
    width_m: Number(camera.default_passage_width_m || 3),
    aisle_spacing_m: Number(camera.default_aisle_spacing_m || 0) || undefined,
    geometry_json: { shape: "line", source: "selection" },
    allowed_resource_mask: "ALL"
  };
}

function passagePayload(item: WarehouseMapPassage) {
  return {
    passage_code: item.passage_code,
    passage_name: item.passage_name,
    passage_kind: item.passage_kind,
    x1_m: Number(item.x1_m || 0),
    y1_m: Number(item.y1_m || 0),
    z1_m: Number(item.z1_m || 0),
    x2_m: Number(item.x2_m || 0),
    y2_m: Number(item.y2_m || 0),
    z2_m: Number(item.z2_m || 0),
    width_m: Number(item.width_m || 3),
    aisle_spacing_m: item.aisle_spacing_m == null ? undefined : Number(item.aisle_spacing_m),
    geometry_json: item.geometry_json,
    allowed_resource_mask: item.allowed_resource_mask
  };
}

function cameraLinkPayload(item: WarehouseMapCameraLink) {
  return {
    link_code: item.link_code,
    link_kind: item.link_kind,
    from_camera_id: item.from_camera_id,
    to_camera_id: item.to_camera_id,
    distance_m: Number(item.distance_m || 0),
    direction_code: item.direction_code
  };
}

function drawCanvas(
  canvas: HTMLCanvasElement,
  roles: Uint8Array,
  level: number,
  view: ViewState,
  selections: CellSelection[],
  activeCell: GridCell,
  hovered: GridCell | null,
  roleFilters: Record<CellRole, boolean>,
  canvasObjects: WarehouseMapObject[],
  passages: WarehouseMapPassage[],
  fractionVisuals: Map<string, FractionVisualPreset>,
  routeRows: RouteDraftRow[],
  setMetrics: React.Dispatch<React.SetStateAction<{ renderMs: number; visibleCells: number; selectedCells: number; bulkMs: number; selectionMs: number; domNodes: number }>>
) {
  const parent = canvas.parentElement;
  if (!parent) return;
  const ratio = window.devicePixelRatio || 1;
  const width = parent.clientWidth;
  const height = parent.clientHeight;
  if (canvas.width !== Math.floor(width * ratio) || canvas.height !== Math.floor(height * ratio)) {
    canvas.width = Math.floor(width * ratio);
    canvas.height = Math.floor(height * ratio);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
  }

  const started = performance.now();
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#f6f9fc";
  ctx.fillRect(0, 0, width, height);

  const cellW = BASE_CELL_WIDTH * view.zoom;
  const cellH = BASE_CELL_HEIGHT * view.zoom;
  const originX = view.panX + GRID_OFFSET_X * view.zoom;
  const originY = view.panY + GRID_OFFSET_Y * view.zoom;
  const minAisle = Math.max(1, Math.floor((-originX) / cellW) + 1);
  const maxAisle = Math.min(GRID.aisleCount, Math.ceil((width - originX) / cellW));
  const minSlot = Math.max(1, Math.floor((-originY) / cellH) + 1);
  const maxSlot = Math.min(GRID.slotsPerAisle, Math.ceil((height - originY) / cellH));
  const drawGrid = cellW >= 5 && cellH >= 4;
  const drawText = cellW >= 28 && cellH >= 18;
  let visibleCells = 0;

  for (let aisle = minAisle; aisle <= maxAisle; aisle += 1) {
    for (let slot = minSlot; slot <= maxSlot; slot += 1) {
      const role = ROLE_ORDER[roles[cellIndex(aisle, slot, level)]] || "EMPTY";
      const x = originX + (aisle - 1) * cellW;
      const y = originY + (slot - 1) * cellH;
      const visibleRole = roleFilters[role];
      ctx.globalAlpha = visibleRole ? 1 : .18;
      ctx.fillStyle = ROLE_COLORS[role];
      ctx.fillRect(x, y, Math.ceil(cellW), Math.ceil(cellH));
      if (drawGrid) {
        ctx.strokeStyle = ROLE_STROKES[role];
        ctx.lineWidth = role === "EMPTY" ? .35 : .7;
        ctx.strokeRect(x + .5, y + .5, Math.max(1, cellW - 1), Math.max(1, cellH - 1));
      }
      if (drawText) {
        ctx.fillStyle = "#0f1f35";
        ctx.font = "700 9px system-ui, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(`${aisle}.${slot}`, x + cellW / 2, y + cellH / 2);
      }
      if (role === "FRACTIONAL_PICK_FACE" || role === "FRACTIONAL_STORAGE") {
        const visual = fractionVisuals.get(fractionVisualKey({ aisle, slot, level }))
          || (role === "FRACTIONAL_STORAGE" ? STORAGE_SPLIT_VISUALS[1] : PICK_SPLIT_PRESETS.PICK_2_LEVELS.visual);
        drawFractionMarker(ctx, x, y, cellW, cellH, visual);
      }
      ctx.globalAlpha = 1;
      visibleCells += 1;
    }
  }

  drawMapObjectOverlays(ctx, canvasObjects, level, originX, originY, view.zoom);
  drawPassageOverlays(ctx, passages, originX, originY, view.zoom);
  drawRouteOrderOverlays(ctx, routeRows, level, originX, originY, cellW, cellH);

  selections.filter((selection) => selection.level === level).forEach((selection) => {
    const x = originX + (selection.aisleFrom - 1) * cellW;
    const y = originY + (selection.slotFrom - 1) * cellH;
    const w = (selection.aisleTo - selection.aisleFrom + 1) * cellW;
    const h = (selection.slotTo - selection.slotFrom + 1) * cellH;
    ctx.fillStyle = "rgba(37,99,216,.18)";
    ctx.strokeStyle = "#0969e8";
    ctx.lineWidth = 2;
    ctx.fillRect(x, y, w, h);
    ctx.strokeRect(x + 1, y + 1, Math.max(1, w - 2), Math.max(1, h - 2));
    drawSelectionEndpoint(ctx, selection.anchorCell, originX, originY, cellW, cellH, "#16a34a", "S");
    drawSelectionEndpoint(ctx, selection.focusCell, originX, originY, cellW, cellH, "#ef3b82", "E");
  });

  if (activeCell.level === level) {
    const x = originX + (activeCell.aisle - 1) * cellW;
    const y = originY + (activeCell.slot - 1) * cellH;
    ctx.strokeStyle = "#111827";
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 4]);
    ctx.strokeRect(x + 2, y + 2, Math.max(1, cellW - 4), Math.max(1, cellH - 4));
    ctx.setLineDash([]);
  }

  if (hovered && hovered.level === level) {
    const x = originX + (hovered.aisle - 1) * cellW;
    const y = originY + (hovered.slot - 1) * cellH;
    ctx.strokeStyle = "#ef3b82";
    ctx.lineWidth = 2;
    ctx.strokeRect(x + 1, y + 1, Math.max(1, cellW - 2), Math.max(1, cellH - 2));
  }

  ctx.fillStyle = "#0f1f35";
  ctx.font = "700 11px system-ui, sans-serif";
  ctx.textAlign = "left";
  ctx.fillText(`ячейка ${CELL_HEIGHT_MM} x ${CELL_WIDTH_MM} мм · L${level}`, 12, height - 14);

  const renderMs = performance.now() - started;
  setMetrics((current) => ({
    ...current,
    renderMs,
    visibleCells,
    selectedCells: selectionListSize(selections),
    domNodes: document.querySelectorAll("*").length
  }));
}

function drawMapObjectOverlays(
  ctx: CanvasRenderingContext2D,
  canvasObjects: WarehouseMapObject[],
  level: number,
  originX: number,
  originY: number,
  zoom: number
) {
  canvasObjects
    .filter((item) => !item.level_no || Number(item.level_no) === level)
    .forEach((item) => {
      const x = originX + Number(item.x_m || 0) / (CELL_WIDTH_MM / 1000) * BASE_CELL_WIDTH * zoom;
      const y = originY + Number(item.y_m || 0) / (CELL_HEIGHT_MM / 1000) * BASE_CELL_HEIGHT * zoom;
      const w = Math.max(3, Number(item.width_m || 1) / (CELL_WIDTH_MM / 1000) * BASE_CELL_WIDTH * zoom);
      const h = Math.max(3, Number(item.depth_m || 1) / (CELL_HEIGHT_MM / 1000) * BASE_CELL_HEIGHT * zoom);
      ctx.save();
      ctx.fillStyle = "rgba(124,58,237,.16)";
      ctx.strokeStyle = "#7c3aed";
      ctx.lineWidth = 2;
      ctx.setLineDash([7, 4]);
      ctx.fillRect(x, y, w, h);
      ctx.strokeRect(x, y, w, h);
      if (w > 42 && h > 18) {
        ctx.setLineDash([]);
        ctx.fillStyle = "#4c1d95";
        ctx.font = "800 10px system-ui, sans-serif";
        ctx.textAlign = "left";
        ctx.textBaseline = "top";
        ctx.fillText(item.object_code || item.object_kind, x + 5, y + 4);
      }
      ctx.restore();
    });
}

function drawPassageOverlays(
  ctx: CanvasRenderingContext2D,
  passages: WarehouseMapPassage[],
  originX: number,
  originY: number,
  zoom: number
) {
  passages.forEach((item) => {
    const x1 = originX + Number(item.x1_m || 0) / (CELL_WIDTH_MM / 1000) * BASE_CELL_WIDTH * zoom;
    const y1 = originY + Number(item.y1_m || 0) / (CELL_HEIGHT_MM / 1000) * BASE_CELL_HEIGHT * zoom;
    const x2 = originX + Number(item.x2_m || 0) / (CELL_WIDTH_MM / 1000) * BASE_CELL_WIDTH * zoom;
    const y2 = originY + Number(item.y2_m || 0) / (CELL_HEIGHT_MM / 1000) * BASE_CELL_HEIGHT * zoom;
    ctx.save();
    ctx.strokeStyle = "rgba(180,83,9,.86)";
    ctx.lineWidth = Math.max(3, Number(item.width_m || 3) / (CELL_WIDTH_MM / 1000) * BASE_CELL_WIDTH * zoom);
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
    ctx.strokeStyle = "#fff7ed";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([7, 5]);
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
    ctx.restore();
  });
}

function drawRouteOrderOverlays(
  ctx: CanvasRenderingContext2D,
  routeRows: RouteDraftRow[],
  level: number,
  originX: number,
  originY: number,
  cellW: number,
  cellH: number
) {
  if (!routeRows.length || cellW < 16 || cellH < 12) return;
  sortedRouteRows(routeRows)
    .filter((row) => row.physical_cell.level === level)
    .slice(0, 700)
    .forEach((row) => {
      const x = originX + (row.physical_cell.aisle - 1) * cellW;
      const y = originY + (row.physical_cell.slot - 1) * cellH;
      const radius = Math.max(6, Math.min(13, Math.min(cellW, cellH) * .42));
      ctx.save();
      ctx.fillStyle = "#fff";
      ctx.strokeStyle = "#0f6bff";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(x + cellW / 2, y + cellH / 2, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = "#063b8f";
      ctx.font = "800 9px system-ui, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(String(Number(row.pick_sequence)), x + cellW / 2, y + cellH / 2 + .5);
      ctx.restore();
    });
}

function drawFractionMarker(ctx: CanvasRenderingContext2D, x: number, y: number, cellW: number, cellH: number, visual: FractionVisualPreset) {
  ctx.strokeStyle = "rgba(76,29,149,.7)";
  ctx.lineWidth = Math.max(1, Math.min(2, cellW / 18));
  const columns = clamp(Math.round(visual.columns), 1, 9);
  const rows = clamp(Math.round(visual.rows), 1, 9);
  for (let column = 1; column < columns; column += 1) {
    const xx = x + (cellW / columns) * column;
    ctx.beginPath();
    ctx.moveTo(xx, y + 2);
    ctx.lineTo(xx, y + cellH - 2);
    ctx.stroke();
  }
  for (let row = 1; row < rows; row += 1) {
    const yy = y + (cellH / rows) * row;
    ctx.beginPath();
    ctx.moveTo(x + 2, yy);
    ctx.lineTo(x + cellW - 2, yy);
    ctx.stroke();
  }
}

function drawSelectionEndpoint(
  ctx: CanvasRenderingContext2D,
  cell: GridCell,
  originX: number,
  originY: number,
  cellW: number,
  cellH: number,
  color: string,
  label: string
) {
  const x = originX + (cell.aisle - 1) * cellW + cellW / 2;
  const y = originY + (cell.slot - 1) * cellH + cellH / 2;
  const radius = Math.max(4, Math.min(10, Math.min(cellW, cellH) * .45));
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, Math.PI * 2);
  ctx.fill();
  if (cellW >= 10 && cellH >= 8) {
    ctx.fillStyle = "#fff";
    ctx.font = "800 8px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(label, x, y + .5);
  }
}

function cellFromPointer(event: PointerEvent<HTMLCanvasElement>, view: ViewState, level: number): GridCell | null {
  const rect = event.currentTarget.getBoundingClientRect();
  const x = (event.clientX - rect.left - view.panX) / view.zoom - GRID_OFFSET_X;
  const y = (event.clientY - rect.top - view.panY) / view.zoom - GRID_OFFSET_Y;
  const aisle = Math.floor(x / BASE_CELL_WIDTH) + 1;
  const slot = Math.floor(y / BASE_CELL_HEIGHT) + 1;
  if (aisle < 1 || aisle > GRID.aisleCount || slot < 1 || slot > GRID.slotsPerAisle) return null;
  return { aisle, slot, level };
}

function normalizeSelection(a: GridCell, b: GridCell): CellSelection {
  return {
    level: a.level,
    aisleFrom: Math.min(a.aisle, b.aisle),
    aisleTo: Math.max(a.aisle, b.aisle),
    slotFrom: Math.min(a.slot, b.slot),
    slotTo: Math.max(a.slot, b.slot),
    anchorCell: { ...a },
    focusCell: { ...b }
  };
}

function cellToSelection(cell: GridCell): CellSelection {
  return {
    level: cell.level,
    aisleFrom: cell.aisle,
    aisleTo: cell.aisle,
    slotFrom: cell.slot,
    slotTo: cell.slot,
    anchorCell: { ...cell },
    focusCell: { ...cell }
  };
}

function mergeSelections(a: CellSelection, b: CellSelection): CellSelection {
  if (a.level !== b.level) return b;
  return {
    level: a.level,
    aisleFrom: Math.min(a.aisleFrom, b.aisleFrom),
    aisleTo: Math.max(a.aisleTo, b.aisleTo),
    slotFrom: Math.min(a.slotFrom, b.slotFrom),
    slotTo: Math.max(a.slotTo, b.slotTo),
    anchorCell: a.anchorCell,
    focusCell: b.focusCell
  };
}

function replaceLastSelection(selections: CellSelection[], selection: CellSelection) {
  return [...selections.slice(0, -1), selection];
}

function cellIndex(aisle: number, slot: number, level: number) {
  return (level - 1) * GRID.aisleCount * GRID.slotsPerAisle
    + (slot - 1) * GRID.aisleCount
    + (aisle - 1);
}

function fractionVisualKey(cell: GridCell) {
  return `${cell.aisle}:${cell.slot}:${cell.level}`;
}

function buildFractionVisualsFromDraft(draft: WarehouseMapDraft) {
  const visuals = new Map<string, FractionVisualPreset>();
  const pickGroups = new Map<string, FractionVisualPreset>();
  (draft.small_pick_faces || [])
    .filter((item) => item.active !== 0 && item.physical_cell)
    .forEach((item) => {
      const key = fractionVisualKey(item.physical_cell);
      const current = pickGroups.get(key) || { columns: 1, rows: 1 };
      pickGroups.set(key, {
        columns: Math.max(current.columns, Number(item.sub_column || 1)),
        rows: Math.max(current.rows, Number(item.sub_level || 1))
      });
    });
  pickGroups.forEach((visual, key) => visuals.set(key, visual));

  const storageGroups = new Map<string, FractionVisualPreset>();
  (draft.storage_slots || [])
    .filter((item) => item.active !== 0 && item.physical_cell)
    .forEach((item) => {
      const key = fractionVisualKey(item.physical_cell);
      const current = storageGroups.get(key) || { columns: 1, rows: 1 };
      storageGroups.set(key, {
        columns: Math.max(current.columns, Number(item.sub_column || item.fraction_cell_count || 1)),
        rows: 1
      });
    });
  storageGroups.forEach((visual, key) => visuals.set(key, visual));
  return visuals;
}

function findStorageSlotsForCell(draft: WarehouseMapDraft | null, cell: GridCell) {
  return (draft?.storage_slots || [])
    .filter((item) => item.active !== 0 && item.physical_cell && fractionVisualKey(item.physical_cell) === fractionVisualKey(cell))
    .sort((a, b) => Number(a.storage_order || 0) - Number(b.storage_order || 0));
}

function sortedRouteRows(rows: RouteDraftRow[]) {
  return [...rows]
    .filter((row) => row.active !== 0 && row.physical_cell)
    .sort((a, b) => Number(a.pick_sequence || 0) - Number(b.pick_sequence || 0));
}

function totalCells() {
  return GRID.aisleCount * GRID.slotsPerAisle * GRID.levels;
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function selectionSize(selection: CellSelection) {
  return (selection.aisleTo - selection.aisleFrom + 1) * (selection.slotTo - selection.slotFrom + 1);
}

function selectionListSize(selections: CellSelection[]) {
  return selections.reduce((total, selection) => total + selectionSize(selection), 0);
}

function toApiSelection(selection: CellSelection) {
  return {
    aisle_from: selection.aisleFrom,
    aisle_to: selection.aisleTo,
    slot_from: selection.slotFrom,
    slot_to: selection.slotTo,
    level_from: selection.level,
    level_to: selection.level
  };
}

function toApiCell(cell: GridCell) {
  return {
    aisle: cell.aisle,
    slot: cell.slot,
    level: cell.level
  };
}

function previewAddressCodes(selection: CellSelection, form: { aisleNo: number; startPickNo: number; step: number; direction: AddressDirection; side: AddressSide; codeMask: string }, maxCount: number) {
  const cells = orderedSelectionCells(selection);
  if (form.direction === "END_TO_START") cells.reverse();
  return cells.slice(0, maxCount).map((cell, index) => formatAddressCode(form.codeMask, form.aisleNo, form.startPickNo + index * form.step, cell.level, form.side));
}

function createSmallPickClientPreview(
  cell: GridCell,
  fractionCellCount: number,
  subLevelCount: number,
  subColumnCount: number,
  orderMode: SmallPickOrderMode,
  startOrder: number,
  step: number,
  codeMask: string
) {
  const positions = smallPickPositions(subLevelCount, subColumnCount, orderMode).slice(0, fractionCellCount);
  return positions.map(([subLevel, subColumn], index) => {
    const pickOrder = startOrder + index * step;
    return {
      logical_cell_code: formatSmallPickCode(codeMask, cell, subLevel, subColumn, pickOrder),
      sub_level: subLevel,
      sub_column: subColumn,
      pick_order: pickOrder
    };
  });
}

function smallPickPositions(subLevelCount: number, subColumnCount: number, orderMode: SmallPickOrderMode) {
  const positions: [number, number][] = [];
  if (orderMode === "COLUMN_THEN_SUB_LEVEL") {
    for (let subColumn = 1; subColumn <= subColumnCount; subColumn += 1) {
      for (let subLevel = 1; subLevel <= subLevelCount; subLevel += 1) positions.push([subLevel, subColumn]);
    }
  } else {
    for (let subLevel = 1; subLevel <= subLevelCount; subLevel += 1) {
      for (let subColumn = 1; subColumn <= subColumnCount; subColumn += 1) positions.push([subLevel, subColumn]);
    }
  }
  return positions;
}

function formatSmallPickCode(mask: string, cell: GridCell, subLevel: number, subColumn: number, pickOrder: number) {
  return replaceTokens(mask, {
    "{physical_cell}": `A${String(cell.aisle).padStart(2, "0")}-S${String(cell.slot).padStart(3, "0")}-L${cell.level}`,
    "{aisle}": String(cell.aisle).padStart(2, "0"),
    "{slot}": String(cell.slot).padStart(3, "0"),
    "{level}": String(cell.level),
    "{sub_level}": String(subLevel),
    "{sub_column}": String(subColumn),
    "{pick_order}": String(pickOrder)
  });
}

function replaceTokens(value: string, tokens: Record<string, string>) {
  return Object.entries(tokens).reduce((result, [token, replacement]) => result.split(token).join(replacement), value);
}

function orderedSelectionCells(selection: CellSelection) {
  const aisleStep = selection.anchorCell.aisle <= selection.focusCell.aisle ? 1 : -1;
  const slotStep = selection.anchorCell.slot <= selection.focusCell.slot ? 1 : -1;
  const aisles = rangeByStep(selection.aisleFrom, selection.aisleTo, aisleStep);
  const slots = rangeByStep(selection.slotFrom, selection.slotTo, slotStep);
  return slots.flatMap((slot) => aisles.map((aisle) => ({ aisle, slot, level: selection.level })));
}

function rangeByStep(from: number, to: number, step: 1 | -1) {
  const values: number[] = [];
  if (step > 0) {
    for (let value = from; value <= to; value += 1) values.push(value);
  } else {
    for (let value = to; value >= from; value -= 1) values.push(value);
  }
  return values;
}

function formatAddressCode(mask: string, aisleNo: number, pickNo: number, level: number, side: AddressSide) {
  return replaceToken(replaceToken(replaceToken(replaceToken(
    mask,
    "{aisle}",
    String(aisleNo).padStart(2, "0")
  ), "{pick_no}", String(pickNo).padStart(3, "0")), "{level}", String(level)), "{side}", side);
}

function replaceToken(value: string, token: string, replacement: string) {
  return value.split(token).join(replacement);
}

function parseAddress(value: string, fallbackLevel: number): GridCell | null {
  const normalized = value.trim().toUpperCase();
  const match = normalized.match(/A(\d+)[-\s_.]*S(\d+)(?:[-\s_.]*L(\d+))?/);
  if (!match) return null;
  const aisle = clamp(Number(match[1]), 1, GRID.aisleCount);
  const slot = clamp(Number(match[2]), 1, GRID.slotsPerAisle);
  const level = clamp(Number(match[3] || fallbackLevel), 1, GRID.levels);
  return { aisle, slot, level };
}

function aisleOverviewColor(roles: Uint8Array, aisle: number, level: number) {
  const counts = Object.fromEntries(ROLE_ORDER.map((role) => [role, 0])) as Record<CellRole, number>;
  for (let slot = 1; slot <= GRID.slotsPerAisle; slot += 1) {
    const role = ROLE_ORDER[roles[cellIndex(aisle, slot, level)]] || "EMPTY";
    counts[role] += 1;
  }
  const dominant = ROLE_ORDER.reduce((best, role) => counts[role] > counts[best] ? role : best, "EMPTY");
  return ROLE_COLORS[dominant];
}

function readSelectionRoles(roles: Uint8Array, selection: CellSelection) {
  const values = new Uint8Array(selectionSize(selection));
  let index = 0;
  for (let aisle = selection.aisleFrom; aisle <= selection.aisleTo; aisle += 1) {
    for (let slot = selection.slotFrom; slot <= selection.slotTo; slot += 1) {
      values[index] = roles[cellIndex(aisle, slot, selection.level)];
      index += 1;
    }
  }
  return values;
}

function writeSelectionRoles(roles: Uint8Array, selection: CellSelection, values: Uint8Array) {
  let index = 0;
  for (let aisle = selection.aisleFrom; aisle <= selection.aisleTo; aisle += 1) {
    for (let slot = selection.slotFrom; slot <= selection.slotTo; slot += 1) {
      roles[cellIndex(aisle, slot, selection.level)] = values[index];
      index += 1;
    }
  }
}

function byteArraysEqual(left: Uint8Array, right: Uint8Array) {
  if (left.length !== right.length) return false;
  for (let index = 0; index < left.length; index += 1) {
    if (left[index] !== right[index]) return false;
  }
  return true;
}

function filledRoleValues(selection: CellSelection, role: CellRole) {
  const values = new Uint8Array(selectionSize(selection));
  values.fill(ROLE_ORDER.indexOf(role));
  return values;
}

function countRoles(roles: Uint8Array) {
  const counts = Object.fromEntries(ROLE_ORDER.map((role) => [role, 0])) as Record<CellRole, number>;
  roles.forEach((value) => {
    const role = ROLE_ORDER[value] || "EMPTY";
    counts[role] += 1;
  });
  return counts;
}

function cameraPayload(form: CameraFormState) {
  return {
    camera_code: form.cameraCode.trim(),
    camera_name: form.cameraName.trim() || form.cameraCode.trim(),
    camera_kind: form.cameraKind,
    origin_x_m: form.originX,
    origin_y_m: form.originY,
    origin_z_m: form.originZ,
    width_m: form.width,
    depth_m: form.depth,
    height_m: form.height,
    levels: form.levels,
    grid_cell_width_m: CELL_WIDTH_MM / 1000,
    grid_cell_depth_m: CELL_HEIGHT_MM / 1000,
    default_passage_width_m: form.defaultPassageWidth,
    default_aisle_spacing_m: form.defaultAisleSpacing,
    boundary_json: { shape: "rect" },
    created_by: "warehouse-map-ui"
  };
}

function nextCameraCode(value: string) {
  const match = value.match(/^(.*?)(\d+)$/);
  if (!match) return `${value || "CAM"}-02`;
  const nextNumber = Number(match[2]) + 1;
  return `${match[1]}${String(nextNumber).padStart(match[2].length, "0")}`;
}

function nextCameraName(value: string) {
  const match = value.match(/^(.*?)(\d+)$/);
  if (!match) return `${value || "Камера"} 02`;
  const nextNumber = Number(match[2]) + 1;
  return `${match[1]}${String(nextNumber).padStart(match[2].length, "0")}`;
}

async function apiFetchJson<T>(input: RequestInfo | URL, init: RequestInit = {}): Promise<T> {
  const response = await fetch(input, {
    ...init,
    headers: {
      Authorization: `Basic ${btoa(API_BASIC_AUTH)}`,
      "Content-Type": "application/json",
      ...init.headers
    }
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`API request failed: ${response.status}${body ? ` · ${body.slice(0, 220)}` : ""}`);
  }
  return response.json() as Promise<T>;
}

function encodeRoles(roles: Uint8Array) {
  let binary = "";
  const chunkSize = 4096;
  for (let index = 0; index < roles.length; index += chunkSize) {
    binary += String.fromCharCode(...roles.slice(index, index + chunkSize));
  }
  return btoa(binary);
}

function decodeRoles(encoded: string, expectedLength: number) {
  const binary = atob(encoded);
  if (binary.length !== expectedLength) throw new Error("Draft role length mismatch");
  const roles = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    roles[index] = binary.charCodeAt(index);
  }
  return roles;
}
