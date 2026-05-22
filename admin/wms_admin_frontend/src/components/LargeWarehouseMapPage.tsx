import { PointerEvent, useEffect, useMemo, useRef, useState } from "react";

type CellRole = "EMPTY" | "PICK_FACE" | "STORAGE" | "TRANSPORT_STAGING" | "FILM_WRAP" | "GATE" | "AISLE" | "BLOCKED" | "FRACTIONAL_PICK_FACE";

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
  updated_at?: string;
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
  counters: Record<string, number>;
  warnings: { code: string; message: string }[];
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

type MapContextMenu = {
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

type SmallPickOrderMode = "SUB_LEVEL_THEN_COLUMN" | "COLUMN_THEN_SUB_LEVEL";

type FormatClipboard = {
  source: CellSelection;
  values: Uint8Array;
  width: number;
  height: number;
  copiedAt: string;
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

const ROLE_ORDER: CellRole[] = ["PICK_FACE", "STORAGE", "TRANSPORT_STAGING", "FILM_WRAP", "GATE", "AISLE", "BLOCKED", "EMPTY", "FRACTIONAL_PICK_FACE"];

const ROLE_LABELS: Record<CellRole, string> = {
  EMPTY: "Пусто",
  PICK_FACE: "Ячейки отбора",
  FRACTIONAL_PICK_FACE: "Дробные ячейки отбора",
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
  STORAGE: "#2563eb",
  TRANSPORT_STAGING: "#b45309",
  FILM_WRAP: "#db2777",
  GATE: "#dc2626",
  AISLE: "#94a3b8",
  BLOCKED: "#334155"
};

export function LargeWarehouseMapPage({ onBack }: { onBack: () => void }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const wrapperRef = useRef<HTMLDivElement | null>(null);
  const rolesRef = useRef<Uint8Array>(createInitialRoles());
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
  const [addressStatus, setAddressStatus] = useState("Адресация не применялась");
  const [addressPreview, setAddressPreview] = useState<AddressPreview | null>(null);
  const [smallPickStatus, setSmallPickStatus] = useState("Дробные ячейки не назначались");
  const [smallPickPreview, setSmallPickPreview] = useState<SmallPickPreview | null>(null);
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
    fractionCellCount: 6,
    subLevelCount: 2,
    subColumnCount: 3,
    orderMode: "SUB_LEVEL_THEN_COLUMN" as SmallPickOrderMode,
    startOrder: 1,
    step: 1,
    side: "" as AddressSide,
    codeMask: "{physical_cell}-F{sub_level}{sub_column}"
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
    const observer = new ResizeObserver(() => drawCanvas(canvas, rolesRef.current, level, view, selections, activeCell, hovered, roleFilters, overlayObjects, overlayPassages, setMetrics));
    observer.observe(wrapper);
    drawCanvas(canvas, rolesRef.current, level, view, selections, activeCell, hovered, roleFilters, overlayObjects, overlayPassages, setMetrics);
    return () => observer.disconnect();
  }, [level, view, selections, activeCell, hovered, roleFilters, version, warehouseMapState, selectedCameraId]);

  useEffect(() => {
    setActiveCell((current) => ({ ...current, level }));
    setSelections((current) => current.map((selection) => ({ ...selection, level })));
  }, [level]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search.replace(/;/g, "&"));
    const smoke = params.get("smoke") || (window.location.href.includes("smoke=sprint12") ? "sprint12" : null);
    if (smoke !== "sprint2-multiarea" && smoke !== "sprint3" && smoke !== "sprint5" && smoke !== "sprint6" && smoke !== "sprint7" && smoke !== "sprint8" && smoke !== "sprint9" && smoke !== "sprint12" && smoke !== "sprint13-format" && smoke !== "sprint13-objects") return;
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

  function commandRegistry() {
    const hasWarehouse = selectedWareId !== null;
    const hasCamera = Boolean(selectedCamera);
    return [
      {
        id: "camera.create" as MapCommandId,
        group: "Камера",
        label: "Создать камеру",
        enabled: hasWarehouse,
        disabledReason: hasWarehouse ? "" : "Сначала выберите склад",
        run: createCameraFromForm
      },
      {
        id: "camera.clone" as MapCommandId,
        group: "Камера",
        label: "Клонировать камеру",
        enabled: hasCamera,
        disabledReason: hasCamera ? "" : "Нет выбранной камеры",
        run: cloneSelectedCamera
      },
      {
        id: "camera.archive" as MapCommandId,
        group: "Камера",
        label: "Архивировать камеру",
        enabled: hasCamera,
        disabledReason: hasCamera ? "" : "Нет выбранной камеры",
        run: archiveSelectedCamera
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
      setDraftStatus(`Сохранено API draft ${apiDraft.draft_id.slice(0, 8)} · ${apiDraft.updated_at ? new Date(apiDraft.updated_at).toLocaleTimeString("ru-RU") : ""}`);
    } catch {
      setDirty(false);
      setDraftStatus(`API недоступен, сохранено локально ${new Date(payload.savedAt).toLocaleTimeString("ru-RU")}`);
    }
  }

  async function loadDraft() {
    if (draftId) {
      try {
        const apiDraft = await apiFetchJson<WarehouseMapDraft>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}`, { cache: "no-store" });
        applyDraftRoles(apiDraft.roles_base64);
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
        body: JSON.stringify({ roles_base64: rolesBase64 })
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
    undoStackRef.current = [];
    redoStackRef.current = [];
    setDirty(false);
    setSelections([]);
    setHistoryVersion((value) => value + 1);
    setVersion((value) => value + 1);
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

  async function generateSmallPickFaces() {
    const selection = selections[0];
    if (!selection) {
      setSmallPickStatus("Нет выделения для дробной ячейки");
      return;
    }
    if (!draftId) {
      setSmallPickStatus("Сначала сохраните draft через API");
      return;
    }
    if (smallPickForm.subLevelCount * smallPickForm.subColumnCount < smallPickForm.fractionCellCount) {
      setSmallPickStatus("Сетка меньше количества дробных мест");
      return;
    }
    try {
      const result = await apiFetchJson<SmallPickPreview>(`${API_BASE}/api/admin/warehouse-map-drafts/${draftId}/small-pick-faces/generate`, {
        method: "POST",
        body: JSON.stringify({
          physical_cell: toApiCell(selection.anchorCell),
          fraction_cell_count: smallPickForm.fractionCellCount,
          sub_level_count: smallPickForm.subLevelCount,
          sub_column_count: smallPickForm.subColumnCount,
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
      setSmallPickPreview(result);
      setSmallPickStatus(`Создано логических ячеек: ${result.created_count}`);
      setDirty(true);
      setVersion((value) => value + 1);
    } catch {
      setSmallPickStatus("Не удалось создать дробную ячейку через API");
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

  return (
    <main className="large-map-page">
      <header className="large-map-topbar">
        <button className="large-map-back" onClick={onBack}>←</button>
        <div>
          <h1>Рисование карты больших складов</h1>
          <p>Canvas 2D MVP · {GRID.aisleCount} аллей × {GRID.slotsPerAisle} слотов × {GRID.levels} уровней · {totalCells().toLocaleString("ru-RU")} ячеек</p>
        </div>
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
            <h2>Реальный склад</h2>
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
                <span>Камер: {warehouseMapState.counters.cameras || 0} · objects: {warehouseMapState.counters.canvas_objects || 0}</span>
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
                <button key={command.id} disabled={!command.enabled} onClick={() => runMapCommand(command.id)} title={command.enabled ? command.label : command.disabledReason}>
                  {command.label}
                </button>
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
            <h2>Роли</h2>
            <div className="large-map-roles">
              {ROLE_ORDER.map((role) => (
                <button key={role} className={activeRole === role ? "active" : ""} onClick={() => setActiveRole(role)} title={ROLE_LABELS[role]}>
                  <i style={{ background: ROLE_COLORS[role], borderColor: ROLE_STROKES[role] }} />
                  {ROLE_LABELS[role]}
                </button>
              ))}
            </div>
            <button className="large-map-primary" disabled={!selections.length} onClick={() => assignRole()}>
              Назначить выделению
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
              <button disabled={!selections.length} onClick={copyFormat} title="Скопировать роли и формат первого выделенного прямоугольника без адресов, остатков и ID">
                Скопировать формат
              </button>
              <button disabled={!formatClipboard} onClick={pasteFormat} title="Вставить скопированный формат от активной ячейки или начала выделения">
                Вставить формат
              </button>
              <button disabled={!formatPainterActive} onClick={cancelFormatPainter} title="Отменить режим копирования формата, сохранив буфер">
                Отменить кисть
              </button>
            </div>
            <p className={`large-map-muted ${formatPainterActive ? "large-map-format-active" : ""}`}>{formatStatus}</p>
          </section>

          <section>
            <h2>Навигация</h2>
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
            <h2>Шаблоны</h2>
            <div className="large-map-template-grid">
              <button onClick={applyRegularTemplate} title="Сбросить карту в регулярный склад: L1 отбор, L2-L6 хранение">Регулярный склад</button>
              <button onClick={applyAisleTemplate} title="Нарисовать регулярные транспортные проходы">Проходы</button>
              <button onClick={applyDockTemplate} title="Нарисовать ворота и транспортное накопление на L1">Ворота + накопление</button>
              <button onClick={applyFilmTemplate} title="Нарисовать зону размещения на пленку на L1">На пленку</button>
              <button onClick={copyAisleTemplate} title="Скопировать активную аллею на выделенные аллеи; без выделения A01 копируется на A02-A10">Копировать аллею</button>
            </div>
          </section>

          <section>
            <h2>Draft</h2>
            <div className="large-map-tools">
              <button onClick={saveDraft}>Сохранить</button>
              <button onClick={loadDraft}>Загрузить</button>
            </div>
            {draftId && <p className="large-map-muted">API draft: {draftId.slice(0, 8)}</p>}
            <p className="large-map-muted">{draftStatus}</p>
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
            <div className="large-map-address-grid">
              <label>Мест<select value={smallPickForm.fractionCellCount} onChange={(event) => setSmallPickForm({ ...smallPickForm, fractionCellCount: Number(event.currentTarget.value) })}>
                {[2, 3, 4, 5, 6, 7, 8, 9].map((value) => <option key={value} value={value}>FRACTION_{value}</option>)}
              </select></label>
              <label>Сетка<input type="text" value={`${smallPickForm.subLevelCount} x ${smallPickForm.subColumnCount}`} onChange={(event) => {
                const [subLevelCount, subColumnCount] = event.currentTarget.value.split("x").map((value) => Number(value.trim()) || 1);
                setSmallPickForm({ ...smallPickForm, subLevelCount: clamp(subLevelCount, 1, 9), subColumnCount: clamp(subColumnCount, 1, 9) });
              }} /></label>
              <label>Старт<input type="number" min="1" value={smallPickForm.startOrder} onChange={(event) => setSmallPickForm({ ...smallPickForm, startOrder: Number(event.currentTarget.value) || 1 })} /></label>
              <label>Шаг<input type="number" min="1" value={smallPickForm.step} onChange={(event) => setSmallPickForm({ ...smallPickForm, step: Number(event.currentTarget.value) || 1 })} /></label>
              <label>Сторона<select value={smallPickForm.side} onChange={(event) => setSmallPickForm({ ...smallPickForm, side: event.currentTarget.value as AddressSide })}><option value="">Пусто</option><option value="LEFT">LEFT</option><option value="RIGHT">RIGHT</option></select></label>
              <label>Порядок<select value={smallPickForm.orderMode} onChange={(event) => setSmallPickForm({ ...smallPickForm, orderMode: event.currentTarget.value as SmallPickOrderMode })}><option value="SUB_LEVEL_THEN_COLUMN">Подуровень → столбик</option><option value="COLUMN_THEN_SUB_LEVEL">Столбик → подуровень</option></select></label>
              <label className="wide">Маска<input value={smallPickForm.codeMask} onChange={(event) => setSmallPickForm({ ...smallPickForm, codeMask: event.currentTarget.value })} /></label>
            </div>
            <button className="large-map-primary" disabled={!selections.length || smallPickForm.subLevelCount * smallPickForm.subColumnCount < smallPickForm.fractionCellCount} onClick={generateSmallPickFaces}>Создать дробную ячейку</button>
            <p className="large-map-muted">{smallPickStatus}</p>
            {smallPickPreview && (
              <div className="large-map-selection">
                <b>{smallPickPreview.created_count.toLocaleString("ru-RU")} подъячеек</b>
                {smallPickPreview.preview.slice(0, 9).map((item) => <span key={`${item.logical_cell_code}-${item.pick_order}`}>{item.logical_cell_code} · p{item.pick_order}</span>)}
              </div>
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
            </div>
          </section>

          <section>
            <h2>Инспектор</h2>
            <div className="large-map-selection">
              <b>A{activeCell.aisle.toString().padStart(2, "0")}-S{activeCell.slot.toString().padStart(3, "0")}-L{activeCell.level}</b>
              <span>{ROLE_LABELS[ROLE_ORDER[rolesRef.current[cellIndex(activeCell.aisle, activeCell.slot, activeCell.level)]]]}</span>
              <span>Координаты: аллея {activeCell.aisle}, слот {activeCell.slot}, уровень {activeCell.level}</span>
            </div>
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
                <button key={command.id} disabled={!command.enabled} onClick={() => runMapCommand(command.id)} title={command.enabled ? command.label : command.disabledReason}>
                  {command.label}
                </button>
              ))}
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

function drawCanvas(
  canvas: HTMLCanvasElement,
  roles: Uint8Array,
  level: number,
  view: ViewState,
  selections: CellSelection[],
  activeCell: GridCell,
  hovered: GridCell | null,
  roleFilters: Record<CellRole, boolean>,
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
      if (role === "FRACTIONAL_PICK_FACE") {
        drawFractionMarker(ctx, x, y, cellW, cellH);
      }
      ctx.globalAlpha = 1;
      visibleCells += 1;
    }
  }

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

function drawFractionMarker(ctx: CanvasRenderingContext2D, x: number, y: number, cellW: number, cellH: number) {
  ctx.strokeStyle = "rgba(76,29,149,.7)";
  ctx.lineWidth = Math.max(1, Math.min(2, cellW / 18));
  const columns = cellW >= 18 ? 3 : 2;
  const rows = cellH >= 14 ? 3 : 2;
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
