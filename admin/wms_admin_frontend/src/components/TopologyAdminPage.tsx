import { PointerEvent, useEffect, useMemo, useState } from "react";

type TopologyStatus = "DRAFT" | "VALIDATED" | "PUBLISHED" | "ARCHIVED";

type Topology = {
  topology_id: number;
  ware_id: number;
  ware_name?: string;
  topology_code: string;
  topology_name?: string;
  version_no: number;
  status: TopologyStatus;
  cell_count?: number;
  aisle_count?: number;
};

type TopologyCell = {
  topology_cell_id: number;
  topology_id: number;
  ware_id: number;
  cell_code: string;
  zone_code?: string;
  section_code?: string;
  aisle_code?: string;
  bay_no?: number;
  level_no?: number;
  side_code: "LEFT" | "RIGHT" | "CENTER";
  cell_kind: string;
  max_volume_m3?: number;
  max_weight_kg?: number;
  x: number;
  y: number;
  z: number;
  width: number;
  depth: number;
  height: number;
  active: number;
  nearest_outbound_gate_distance_m?: number;
  nearest_inbound_gate_distance_m?: number;
};

type TopologyAisle = {
  topology_aisle_id: number;
  aisle_code: string;
  aisle_name?: string;
  aisle_kind: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  width_m: number;
};

type PickRoute = {
  pick_route_id: number;
  topology_id: number;
  route_code: string;
  route_name?: string;
  route_pattern?: string;
  status?: string;
  cell_count?: number;
};

type TopologyGate = {
  topology_gate_id: number;
  topology_id: number;
  ware_id: number;
  gate_code: string;
  gate_name?: string;
  gate_kind: "RECEIVING" | "SHIPPING" | "BOTH";
  staging_zone_code?: string;
  vehicle_class?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  active: number;
};

type CellGateDistance = {
  cell_gate_distance_id: number;
  topology_id: number;
  topology_cell_id: number;
  topology_gate_id: number;
  gate_code: string;
  gate_kind: string;
  flow_kind: "INBOUND" | "OUTBOUND" | "BOTH";
  distance_m: number;
  travel_time_sec?: number;
};

type PickRouteCell = {
  pick_route_cell_id: number;
  pick_route_id: number;
  topology_cell_id?: number;
  cell_code: string;
  pick_sequence: number;
  [key: string]: unknown;
};

type TopologyMap = {
  topology: Topology;
  aisles: TopologyAisle[];
  gates: TopologyGate[];
  cells: TopologyCell[];
  distances: CellGateDistance[];
  routes: PickRoute[];
  route_cells: PickRouteCell[];
};

type MapLayerState = {
  aisles: boolean;
  cells: boolean;
  zones: boolean;
  gates: boolean;
  labels: boolean;
  route: boolean;
  distances: boolean;
};

type ValidationResult = {
  valid: boolean;
  error_count: number;
  checks: Record<string, unknown[]>;
};

type ApiState = "loading" | "demo" | "api" | "saving";
type RoutePattern = "Z" | "U_SHAPE" | "SNAKE" | "LINEAR";
type SvgSelectionRect = { x1: number; y1: number; x2: number; y2: number };
type AreaDragState = { start: SvgPoint; current: SvgPoint; additive: boolean };
type SvgPoint = { x: number; y: number };

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8088";
const API_BASIC_AUTH = import.meta.env.VITE_ADMIN_BASIC_AUTH || "admin:admin123";
const MIN_TOPOLOGY_ZOOM = 0.1;
const MAX_TOPOLOGY_ZOOM = 12;

function apiHeaders(extra?: HeadersInit): HeadersInit {
  return {
    Authorization: `Basic ${btoa(API_BASIC_AUTH)}`,
    ...extra
  };
}

function apiFetch(input: RequestInfo | URL, init: RequestInit = {}) {
  return fetch(input, {
    ...init,
    headers: apiHeaders(init.headers)
  });
}

export function TopologyAdminPage({ onBack }: { onBack: () => void }) {
  const [map, setMap] = useState<TopologyMap>(() => emptyTopologyMap());
  const [topologyOptions, setTopologyOptions] = useState<Topology[]>([]);
  const [apiState, setApiState] = useState<ApiState>("loading");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [rightTab, setRightTab] = useState<"general" | "params" | "stats">("general");
  const [mapMode, setMapMode] = useState<"3d" | "plan" | "list">("plan");
  const [navCollapsed, setNavCollapsed] = useState(false);
  const [leftPanelCollapsed, setLeftPanelCollapsed] = useState(false);
  const [rightPanelCollapsed, setRightPanelCollapsed] = useState(false);
  const [view, setView] = useState({ zoom: 1, panX: 0, panY: 0 });
  const [panDrag, setPanDrag] = useState<{ startX: number; startY: number; originX: number; originY: number } | null>(null);
  const [areaDrag, setAreaDrag] = useState<AreaDragState | null>(null);
  const [selectionMode, setSelectionMode] = useState(false);
  const [routeMenu, setRouteMenu] = useState<{ x: number; y: number } | null>(null);
  const [dirtyCells, setDirtyCells] = useState<Set<number>>(() => new Set());
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [layers, setLayers] = useState<MapLayerState>({
    aisles: true,
    cells: true,
    zones: true,
    gates: true,
    labels: true,
    route: true,
    distances: false
  });
  const [selectedAisles, setSelectedAisles] = useState<string[]>(["A01", "A02", "A03"]);
  const [selectedRouteCellIds, setSelectedRouteCellIds] = useState<Set<number>>(() => new Set());
  const [routePattern, setRoutePattern] = useState<RoutePattern>("Z");
  const [generator, setGenerator] = useState({
    aisle_count: 6,
    bays_per_aisle: 18,
    levels: 1,
    create_both_sides: 1
  });

  useEffect(() => {
    loadInitialTopology().then((loaded) => {
      if (loaded?.map) {
        setTopologyOptions(loaded.topologies);
        setMap(loaded.map);
        setApiState("api");
        return;
      }
      setMap(demoTopologyMap());
      setApiState("demo");
    });
  }, []);

  useEffect(() => {
    if (selectedId === null && map.cells.length) {
      setSelectedId(map.cells[0].topology_cell_id);
    }
  }, [map?.cells, selectedId]);

  const selectedCell = map.cells.find((cell) => cell.topology_cell_id === selectedId) || null;
  const activeRoute = map.routes.find((route) => route.status !== "ARCHIVED" && route.route_pattern === routePattern)
    || map.routes.find((route) => route.status !== "ARCHIVED")
    || map.routes[0]
    || null;
  const activeRouteCells = useMemo(() => {
    if (!activeRoute) return [];
    return map.route_cells
      .filter((routeCell) => routeCell.pick_route_id === activeRoute.pick_route_id)
      .sort((a, b) => Number(a.pick_sequence || 0) - Number(b.pick_sequence || 0));
  }, [activeRoute, map.route_cells]);
  const routeByCell = useMemo(() => {
    const result = new Map<number, PickRouteCell>();
    activeRouteCells.forEach((routeCell) => {
      if (routeCell.topology_cell_id) result.set(routeCell.topology_cell_id, routeCell);
    });
    return result;
  }, [activeRouteCells]);
  const stats = useMemo(() => topologyStats(map, activeRouteCells.length), [map, activeRouteCells]);
  const selectedRouteCell = selectedId ? routeByCell.get(selectedId) : undefined;
  const selectedCellIndex = selectedCell ? map.cells.findIndex((cell) => cell.topology_cell_id === selectedCell.topology_cell_id) : -1;
  const prevCell = selectedCellIndex > 0 ? map.cells[selectedCellIndex - 1] : null;
  const nextCell = selectedCellIndex >= 0 && selectedCellIndex < map.cells.length - 1 ? map.cells[selectedCellIndex + 1] : null;
  const distancesForSelected = useMemo(() => {
    if (!selectedId) return [];
    return map.distances
      .filter((distance) => distance.topology_cell_id === selectedId)
      .sort((a, b) => Number(a.distance_m || 0) - Number(b.distance_m || 0))
      .slice(0, 4);
  }, [map.distances, selectedId]);

  if (apiState === "loading" && map.cells.length === 0) {
    return (
      <div className="loading-screen">
        <b>Управление топологией склада</b>
        <span>Загружаю опубликованную топологию и порядок обхода...</span>
      </div>
    );
  }

  function toggleAisle(aisleCode: string) {
    setSelectedAisles((current) => current.includes(aisleCode)
      ? current.filter((code) => code !== aisleCode)
      : [...current, aisleCode].sort());
    setSelectedRouteCellIds(new Set());
  }

  function selectablePickFaceCells() {
    return map.cells.filter((cell) => cell.active === 1
      && cell.cell_kind.includes("PICK_FACE")
      && selectedAisles.includes(cell.aisle_code || ""));
  }

  function selectRouteCells(scope: "all" | "left" | "right" | "clear" | "invert") {
    if (scope === "clear") {
      setSelectedRouteCellIds(new Set());
      return;
    }
    const candidates = selectablePickFaceCells();
    if (scope === "invert") {
      setSelectedRouteCellIds((current) => {
        const next = new Set(current);
        candidates.forEach((cell) => {
          if (next.has(cell.topology_cell_id)) next.delete(cell.topology_cell_id);
          else next.add(cell.topology_cell_id);
        });
        return next;
      });
      return;
    }
    const side = scope === "left" ? "LEFT" : scope === "right" ? "RIGHT" : null;
    setSelectedRouteCellIds(new Set(candidates
      .filter((cell) => !side || cell.side_code === side)
      .map((cell) => cell.topology_cell_id)));
  }

  function toggleLayer(layer: keyof MapLayerState) {
    setLayers((current) => ({ ...current, [layer]: !current[layer] }));
  }

  async function handleGenerate() {
    setApiState((current) => current === "api" ? "saving" : current);
    const local = generateLocalTopology(map.topology, generator);
    try {
      const topologyId = apiState === "api" ? map.topology.topology_id : await createApiTopology();
      const response = await apiFetch(`${API_BASE}/api/admin/warehouse-topologies/${topologyId}/generate-cells`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          zone_code: "PICK",
          section_code: "S01",
          aisle_count: generator.aisle_count,
          bays_per_aisle: generator.bays_per_aisle,
          levels: generator.levels,
          create_both_sides: generator.create_both_sides,
          overwrite_existing: 1
        })
      });
      if (response.ok) {
        const loaded = await loadTopologyMap(topologyId);
        if (loaded) {
          setMap(loaded);
          setTopologyOptions((current) => current.some((item) => item.topology_id === loaded.topology.topology_id)
            ? current
            : [...current, loaded.topology]);
        }
        setApiState("api");
        return;
      }
    } catch {
      // Demo fallback keeps the page useful while the Oracle migration is not applied.
    }
    setMap(local);
    setApiState("demo");
  }

  async function handleTopologyChange(topologyId: number) {
    if (!topologyId || topologyId === map.topology.topology_id) return;
    setApiState("loading");
    const loaded = await loadTopologyMap(topologyId);
    if (loaded) {
      setMap(loaded);
      setSelectedId(null);
      setSelectedRouteCellIds(new Set());
      setSelectedAisles(loaded.aisles.filter((aisle) => aisle.aisle_kind === "PICK_AISLE").slice(0, 3).map((aisle) => aisle.aisle_code));
      setDirtyCells(new Set());
      setValidation(null);
      setView({ zoom: 1, panX: 0, panY: 0 });
      setApiState("api");
      return;
    }
    setApiState("api");
  }

  async function handleBuildRoute(pattern: RoutePattern = routePattern) {
    const selectedCellIds = Array.from(selectedRouteCellIds);
    const route = buildLocalRoute(map, selectedAisles, pattern, selectedCellIds);
    setMap(route);
    setRoutePattern(pattern);
    setRouteMenu(null);
    setApiState((current) => current === "api" ? "saving" : current);
    try {
      const response = await apiFetch(`${API_BASE}/api/admin/pick-routes/build`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topology_id: map.topology.topology_id,
          ware_id: map.topology.ware_id,
          route_code: `CASE-${pattern}-MAIN`,
          route_name: `Основной ${pattern}-обход отбора`,
          route_pattern: pattern,
          aisle_codes: selectedAisles,
          cell_ids: selectedCellIds.length ? selectedCellIds : null,
          side_order: ["LEFT", "RIGHT"],
          strict_sequence: 1
        })
      });
      if (response.ok) {
        const loaded = await loadTopologyMap(map.topology.topology_id);
        if (loaded) setMap(loaded);
        setApiState("api");
        return;
      }
    } catch {
      // Keep local preview.
    }
    setApiState("demo");
  }

  async function handleRecalculateDistances() {
    setMap(recalculateLocalGateDistances(map));
    setApiState((current) => current === "api" ? "saving" : current);
    try {
      const dockY = Math.max(...map.cells.map((cell) => cell.y), 30) + 22;
      await apiFetch(`${API_BASE}/api/admin/warehouse-topologies/${map.topology.topology_id}/generate-gates`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gate_count: 10, gate_kind: "SHIPPING", start_y: dockY, overwrite_existing: 0 })
      });
      const response = await apiFetch(`${API_BASE}/api/admin/warehouse-topologies/${map.topology.topology_id}/distances/recalculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ flow_kind: "BOTH", picker_speed_mps: 1.1, reachtruck_speed_mps: 1.8 })
      });
      if (response.ok) {
        const loaded = await loadTopologyMap(map.topology.topology_id);
        if (loaded) setMap(loaded);
        setApiState("api");
        return;
      }
    } catch {
      // Demo fallback keeps calculated local distances.
    }
    setApiState("demo");
  }

  async function handleValidate() {
    const local = validateLocalTopology(map);
    setValidation(local);
    setApiState((current) => current === "api" ? "saving" : current);
    try {
      const response = await apiFetch(`${API_BASE}/api/admin/warehouse-topologies/${map.topology.topology_id}/validate`, {
        method: "POST"
      });
      if (response.ok) {
        setValidation(await response.json());
        setApiState("api");
        return;
      }
    } catch {
      // Keep local validation.
    }
    setApiState("demo");
  }

  async function handlePublishTopology() {
    const local = validateLocalTopology(map);
    setValidation(local);
    if (!local.valid) return;
    setApiState((current) => current === "api" ? "saving" : current);
    try {
      const response = await apiFetch(`${API_BASE}/api/admin/warehouse-topologies/${map.topology.topology_id}/publish`, {
        method: "POST"
      });
      if (response.ok) {
        const loaded = await loadTopologyMap(map.topology.topology_id);
        if (loaded) setMap(loaded);
        setApiState("api");
        return;
      }
    } catch {
      // Demo publish.
    }
    setMap((current) => ({ ...current, topology: { ...current.topology, status: "PUBLISHED" } }));
    setApiState("demo");
  }

  async function handleSaveSelectedCell() {
    if (!selectedCell) return;
    setApiState((current) => current === "api" ? "saving" : current);
    try {
      const response = await apiFetch(`${API_BASE}/api/admin/topology-cells/${selectedCell.topology_cell_id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          x: selectedCell.x,
          y: selectedCell.y,
          z: selectedCell.z,
          side_code: selectedCell.side_code,
          cell_kind: selectedCell.cell_kind,
          active: selectedCell.active
        })
      });
      if (response.ok) {
        setDirtyCells((current) => {
          const next = new Set(current);
          next.delete(selectedCell.topology_cell_id);
          return next;
        });
        setApiState("api");
        return;
      }
    } catch {
      // Demo save clears dirty state.
    }
    setDirtyCells((current) => {
      const next = new Set(current);
      next.delete(selectedCell.topology_cell_id);
      return next;
    });
    setApiState("demo");
  }

  function updateSelectedCell(field: keyof TopologyCell, value: string | number) {
    if (!selectedId) return;
    setMap((current) => ({
      ...current,
      cells: current.cells.map((cell) => cell.topology_cell_id === selectedId ? { ...cell, [field]: value } : cell)
    }));
    markDirty(selectedId);
  }

  function markDirty(id: number) {
    setDirtyCells((current) => {
      const next = new Set(current);
      next.add(id);
      return next;
    });
  }

  function handleCellPointerDown(event: PointerEvent<SVGGElement>, cell: TopologyCell) {
    event.preventDefault();
    event.stopPropagation();
    setSelectedId(cell.topology_cell_id);
    setSelectedRouteCellIds((current) => {
      if (!event.ctrlKey && !event.metaKey && !event.shiftKey && !selectionMode) return current;
      const next = new Set(current);
      if (next.has(cell.topology_cell_id)) next.delete(cell.topology_cell_id);
      else next.add(cell.topology_cell_id);
      return next;
    });
  }

  function handleMapPointerMove(event: PointerEvent<SVGSVGElement>) {
    if (areaDrag) {
      const point = svgPointFromEvent(event, view);
      setAreaDrag((current) => current ? { ...current, current: point } : current);
      return;
    }
    if (panDrag) {
      setView((current) => ({
        ...current,
        panX: panDrag.originX + event.clientX - panDrag.startX,
        panY: panDrag.originY + event.clientY - panDrag.startY
      }));
    }
  }

  function handleMapPointerDown(event: PointerEvent<SVGSVGElement>) {
    if (event.button !== 0) return;
    setRouteMenu(null);
    if (selectionMode || event.altKey || event.shiftKey) {
      const point = svgPointFromEvent(event, view);
      setAreaDrag({ start: point, current: point, additive: event.shiftKey });
      return;
    }
    setPanDrag({ startX: event.clientX, startY: event.clientY, originX: view.panX, originY: view.panY });
  }

  function handleMapPointerUp() {
    if (areaDrag) {
      const bounds = mapBounds(map.cells, map.aisles);
      const rect = normalizeRect(areaDrag.start, areaDrag.current);
      const selectedCells = map.cells.filter((cell) => {
        const aisle = map.aisles.find((item) => item.aisle_code === cell.aisle_code);
        const point = projectCellPoint(cell, bounds, mapMode, aisle);
        const x = point.x;
        const y = point.y;
        return cell.active === 1 && cell.cell_kind.includes("PICK_FACE") && x >= rect.x1 && x <= rect.x2 && y >= rect.y1 && y <= rect.y2;
      });
      const selectedIds = selectedCells.map((cell) => cell.topology_cell_id);
      setSelectedRouteCellIds((current) => {
        if (!areaDrag.additive) return new Set(selectedIds);
        const next = new Set(current);
        selectedIds.forEach((id) => next.add(id));
        return next;
      });
      const aisles = Array.from(new Set(selectedCells.map((cell) => cell.aisle_code).filter(Boolean))) as string[];
      if (aisles.length) {
        setSelectedAisles((current) => areaDrag.additive
          ? Array.from(new Set([...current, ...aisles])).sort()
          : aisles.sort());
      }
      setAreaDrag(null);
    }
    setPanDrag(null);
  }

  function handleRouteContextMenu(event: PointerEvent<SVGSVGElement>) {
    event.preventDefault();
    const target = event.currentTarget.getBoundingClientRect();
    setRouteMenu({ x: event.clientX - target.left, y: event.clientY - target.top });
  }

  return (
    <div className={`topology-admin ${navCollapsed ? "nav-collapsed" : ""}`}>
      <aside className={`topology-nav ${navCollapsed ? "collapsed" : ""}`}>
        <div className="topology-nav-brand">
          <b>W</b>
          <span>Управление топологией склада</span>
          <button
            className="topology-nav-collapse"
            onClick={() => setNavCollapsed((current) => !current)}
            title={navCollapsed ? "Развернуть меню" : "Свернуть меню"}
          >
            {navCollapsed ? "›" : "‹"}
          </button>
        </div>
        <button onClick={onBack} title="Обзор"><span>⌂</span><em>Обзор</em></button>
        <small>Топология</small>
        {[
          ["▣", "Склад", "Рабочая страница управления картой склада, ячейками и порядком обхода"],
          ["╂", "Аллеи", "Будущий раздел для отдельного справочника аллей"],
          ["□", "Ячейки", "Будущий раздел для отдельного списка физических ячеек"],
          ["▰", "Ворота", "Будущий раздел для справочника ворот и зон накопления"],
          ["◇", "Зоны", "Будущий раздел для зон склада"],
          ["⚙", "Оборудование", "Будущий раздел для складского оборудования"],
          ["▤", "Типы ячеек", "Будущий раздел для типов и габаритов ячеек"]
        ].map(([icon, item, hint], index) => (
          <button key={item} className={index === 0 ? "active" : "future-control"} title={hint} aria-disabled={index === 0 ? undefined : true}><span>{icon}</span><em>{item}</em></button>
        ))}
        <small>Аналитика</small>
        <button className="future-control" title="Будущий аналитический раздел загрузки склада" aria-disabled="true"><span>↯</span><em>Загрузка</em></button>
        <button className="future-control" title="Будущий аналитический раздел по емкости склада" aria-disabled="true"><span>▥</span><em>Емкость</em></button>
        <button className="future-control" title="Будущий раздел контроля качества топологии и операций" aria-disabled="true"><span>◉</span><em>Контроль</em></button>
        <small>Настройки</small>
        <button className="future-control" title="Будущий раздел справочников топологии" aria-disabled="true"><span>☷</span><em>Справочники</em></button>
        <button className="future-control" title="Будущий раздел правил построения и проверки топологии" aria-disabled="true"><span>↔</span><em>Правила</em></button>
        <button className="future-control" title="Будущий раздел системных параметров топологии" aria-disabled="true"><span>⚙</span><em>Параметры</em></button>
        <p>Версия 1.0.0<br />© WMS</p>
      </aside>

      <main className="topology-shell">
        <header className="topology-topbar">
          <div className="topology-title">
            <h1>Управление топологией склада</h1>
            <span>{topologyStatusText(map.topology.status)}</span>
          </div>
          <label className="topology-warehouse-select" title="Выбор версии топологии склада, которую нужно открыть на карте">
            <span>Склад</span>
            <select
              value={map.topology.topology_id}
              disabled={apiState === "loading" || apiState === "saving" || !topologyOptions.length}
              onChange={(event) => {
                const topologyId = Number(event.currentTarget.value);
                handleTopologyChange(topologyId);
              }}
            >
              {(topologyOptions.length ? topologyOptions : [map.topology]).map((topology) => (
                <option key={topology.topology_id} value={topology.topology_id}>
                  {topology.ware_name || `Склад ${topology.ware_id}`} · {topology.topology_code} · v{topology.version_no}
                </option>
              ))}
            </select>
          </label>
          <div className="topology-actions">
            <button className="future-control" title="Заглушка: будущий импорт топологии из файла или внешней системы" aria-disabled="true">Импорт</button>
            <button className="future-control" title="Заглушка: будущий экспорт версии топологии в файл" aria-disabled="true">Экспорт</button>
            <button className="primary" onClick={handleGenerate} title="Сгенерировать или добавить структуру топологии по параметрам генератора">+ Добавить</button>
            <button onClick={handleValidate} title="Проверить текущую топологию перед публикацией">Проверить</button>
            <button onClick={handlePublishTopology} title="Опубликовать проверенную версию топологии для использования в WMS">Опубликовать</button>
            <span className={`topology-status ${map.topology.status.toLowerCase()}`}>{map.topology.status}</span>
            <span className="api-pill">{apiState === "api" ? "API" : apiState === "saving" ? "Сохранение" : apiState === "loading" ? "Загрузка" : "Demo"}</span>
          </div>
        </header>

        <section className={`topology-layout ${leftPanelCollapsed ? "left-collapsed" : ""} ${rightPanelCollapsed ? "right-collapsed" : ""}`}>
          <aside className={`topology-left ${leftPanelCollapsed ? "collapsed" : ""}`}>
          <button className="panel-collapse-button" onClick={() => setLeftPanelCollapsed((current) => !current)} title={leftPanelCollapsed ? "Развернуть левую панель" : "Свернуть левую панель"}>
            {leftPanelCollapsed ? "›" : "‹"}
          </button>
          <section>
            <h2>{map.topology.topology_name || map.topology.topology_code}</h2>
            <p>{map.topology.ware_name || `Склад ${map.topology.ware_id}`} · версия {map.topology.version_no}</p>
            <div className="topology-stat-grid">
              <span><b>{stats.aisles}</b>аллей</span>
              <span><b>{stats.pickFaces}</b>ячеек отбора</span>
              <span><b>{stats.dynamic}</b>dynamic</span>
              <span><b>{stats.routeCells}</b>в обходе</span>
              <span><b>{stats.gates}</b>ворот</span>
              <span><b>{dirtyCells.size}</b>изменено</span>
            </div>
          </section>

          <section>
            <h3>Слои</h3>
            <LayerToggle label="Аллеи" checked={layers.aisles} onChange={() => toggleLayer("aisles")} />
            <LayerToggle label="Ячейки" checked={layers.cells} onChange={() => toggleLayer("cells")} />
            <LayerToggle label="Зоны" checked={layers.zones} onChange={() => toggleLayer("zones")} />
            <LayerToggle label="Ворота" checked={layers.gates} onChange={() => toggleLayer("gates")} />
            <LayerToggle label="Подписи" checked={layers.labels} onChange={() => toggleLayer("labels")} />
            <LayerToggle label="Порядок обхода" checked={layers.route} onChange={() => toggleLayer("route")} />
            <LayerToggle label="Расстояния" checked={layers.distances} onChange={() => toggleLayer("distances")} />
          </section>

          <section>
            <h3>Генератор</h3>
            <NumberField label="Аллеи" value={generator.aisle_count} min={1} max={24} onChange={(value) => setGenerator((current) => ({ ...current, aisle_count: value }))} />
            <NumberField label="Ячеек на сторону" value={generator.bays_per_aisle} min={4} max={80} onChange={(value) => setGenerator((current) => ({ ...current, bays_per_aisle: value }))} />
            <NumberField label="Ярусы" value={generator.levels} min={1} max={4} onChange={(value) => setGenerator((current) => ({ ...current, levels: value }))} />
            <label className="topology-check"><input type="checkbox" checked={generator.create_both_sides === 1} onChange={(event) => {
              const createBothSides = event.currentTarget.checked ? 1 : 0;
              setGenerator((current) => ({ ...current, create_both_sides: createBothSides }));
            }} /> две стороны прохода</label>
          </section>

          <section>
            <h3>Участок обхода</h3>
            <div className="aisle-tags">
              {map.aisles.filter((aisle) => aisle.aisle_kind === "PICK_AISLE").map((aisle) => (
                <button key={aisle.aisle_code} className={selectedAisles.includes(aisle.aisle_code) ? "active" : ""} onClick={() => toggleAisle(aisle.aisle_code)} title={`Включить или исключить аллею ${aisle.aisle_code} из участка построения обхода`}>
                  {aisle.aisle_code}
                </button>
              ))}
            </div>
            <div className="route-strategy-grid">
              {(["Z", "U_SHAPE", "SNAKE", "LINEAR"] as RoutePattern[]).map((pattern) => (
                <button key={pattern} className={routePattern === pattern ? "active" : ""} onClick={() => handleBuildRoute(pattern)} title={routePatternHint(pattern)}>
                  {pattern}
                </button>
              ))}
            </div>
            <div className="selection-toolbar">
              <button className={selectionMode ? "active" : ""} onClick={() => setSelectionMode((current) => !current)} title="Включить режим выделения ячеек рамкой на карте">Рамка</button>
              <button onClick={() => selectRouteCells("all")} title="Выделить все pick-face ячейки выбранных аллей">Все</button>
              <button onClick={() => selectRouteCells("left")} title="Выделить только левые ячейки выбранных аллей">Левая</button>
              <button onClick={() => selectRouteCells("right")} title="Выделить только правые ячейки выбранных аллей">Правая</button>
              <button onClick={() => selectRouteCells("invert")} title="Инвертировать текущее выделение в выбранных аллеях">Инверт.</button>
              <button onClick={() => selectRouteCells("clear")} title="Снять текущее выделение ячеек">Сброс</button>
            </div>
            <p>В режиме “Рамка” протяните мышью по карте. Без режима карта двигается мышью; Ctrl/Shift-клик по ячейке добавляет или убирает ее из области.</p>
            <button className="wide-action" onClick={() => handleBuildRoute(routePattern)} title="Построить порядок обхода для выделенных ячеек по выбранной стратегии">Применить стратегию</button>
            <span className="selection-counter">{selectedRouteCellIds.size ? `Выделено ячеек: ${selectedRouteCellIds.size}` : "Область не выделена"}</span>
          </section>

          <section>
            <h3>Ворота и расстояния</h3>
            <p>Матрица расстояний влияет на скорость перемещения к отгрузке и от приемки к хранению.</p>
            <button className="wide-action secondary-action" onClick={handleRecalculateDistances} title="Пересчитать матрицу расстояний от ячеек до ворот приемки и отгрузки">Пересчитать до ворот</button>
          </section>
        </aside>

        <main className="topology-map-panel">
          <div className="topology-map-title">
            <div>
              <b>Карта ячеек отбора</b>
              <span>2D план · порядок обхода редактируется отдельно от ежедневных волн</span>
            </div>
            <div className="topology-view-tabs">
              <button className={mapMode === "plan" ? "active" : ""} onClick={() => setMapMode("plan")} title="Открыть 2D карту для редактирования порядка обхода">2D План</button>
              <button className={mapMode === "list" ? "active" : ""} onClick={() => setMapMode("list")} title="Открыть табличный список ячеек топологии">Список</button>
            </div>
            <div className="map-legend">
              <span><i className="cell-left" /> Левая сторона</span>
              <span><i className="cell-right" /> Правая сторона</span>
              <span><i className="cell-route" /> Порядок обхода</span>
            </div>
          </div>
          {mapMode === "list" ? (
            <TopologyCellTable cells={map.cells} selectedId={selectedId} onSelect={setSelectedId} />
          ) : (
            <>
            <div className="map-selection-tools">
              <b>Выделение</b>
              <button className={selectionMode ? "active" : ""} onClick={() => setSelectionMode((current) => !current)} title="Включить режим выделения прямоугольной областью">Рамка</button>
              <button onClick={() => selectRouteCells("all")} title="Выделить все ячейки выбранных аллей">Все</button>
              <button onClick={() => selectRouteCells("left")} title="Выделить левую сторону проходов">Левая</button>
              <button onClick={() => selectRouteCells("right")} title="Выделить правую сторону проходов">Правая</button>
              <button onClick={() => selectRouteCells("invert")} title="Инвертировать выделенные и невыделенные ячейки">Инверт.</button>
              <button onClick={() => selectRouteCells("clear")} title="Очистить выделение ячеек">Сброс</button>
              <span>{selectedRouteCellIds.size ? `${selectedRouteCellIds.size} ячеек` : "нет области"}</span>
              {selectionMode && <span className="selection-mode-hint">Протяните рамку по ячейкам отбора</span>}
            </div>
            <div className="topology-map-wrap">
              <div className="topology-map-controls">
                <button onClick={() => setView((current) => ({ ...current, zoom: clampZoom(Number((current.zoom * 1.25).toFixed(2))) }))} title="Приблизить карту">+</button>
                <button onClick={() => setView((current) => ({ ...current, zoom: clampZoom(Number((current.zoom / 1.25).toFixed(2))) }))} title="Отдалить карту">-</button>
                <label className="topology-zoom-slider" title="Масштаб карты">
                  <span>{Math.round(view.zoom * 100)}%</span>
                  <input
                    type="range"
                    min={10}
                    max={1200}
                    step={10}
                    value={Math.round(view.zoom * 100)}
                    onChange={(event) => {
                      const zoom = clampZoom(Number(event.currentTarget.value) / 100);
                      setView((current) => ({ ...current, zoom }));
                    }}
                  />
                </label>
                <button onClick={() => setView({ zoom: 1, panX: 0, panY: 0 })} title="Вернуть масштаб и положение карты по умолчанию">Сброс</button>
                <button className={selectionMode ? "active" : ""} onClick={() => setSelectionMode((current) => !current)} title="Включить или выключить выделение рамкой">□ Рамка</button>
                <button onClick={() => setView((current) => ({ ...current, panX: current.panX - 30 }))} title="Сдвинуть карту влево">←</button>
                <button onClick={() => setView((current) => ({ ...current, panX: current.panX + 30 }))} title="Сдвинуть карту вправо">→</button>
                <button onClick={() => setView((current) => ({ ...current, panY: current.panY - 30 }))} title="Сдвинуть карту вверх">↑</button>
                <button onClick={() => setView((current) => ({ ...current, panY: current.panY + 30 }))} title="Сдвинуть карту вниз">↓</button>
              </div>
              <TopologySvg
                map={map}
                routeCells={activeRouteCells}
                routeByCell={routeByCell}
                selectedId={selectedId}
                selectedRouteCellIds={selectedRouteCellIds}
                selectionRect={areaDrag ? normalizeRect(areaDrag.start, areaDrag.current) : null}
                layers={layers}
                mode={mapMode}
                view={view}
                isPanning={Boolean(panDrag)}
                isSelecting={selectionMode || Boolean(areaDrag)}
                onSelect={setSelectedId}
                onCellPointerDown={handleCellPointerDown}
                onPointerDown={handleMapPointerDown}
                onPointerMove={handleMapPointerMove}
                onPointerUp={handleMapPointerUp}
                onContextMenu={handleRouteContextMenu}
              />
              {routeMenu && (
                <div className="route-context-menu" style={{ left: routeMenu.x, top: routeMenu.y }}>
                  <b>Стратегия обхода</b>
                  <span>Массовое выделение</span>
                  <button title="Переключить карту в режим выделения ячеек рамкой" onClick={() => {
                    setSelectionMode(true);
                    setRouteMenu(null);
                  }}>Включить рамку</button>
                  <button title="Выделить все ячейки выбранных аллей" onClick={() => {
                    selectRouteCells("all");
                    setRouteMenu(null);
                  }}>Выделить все</button>
                  <button title="Выделить ячейки слева от прохода" onClick={() => {
                    selectRouteCells("left");
                    setRouteMenu(null);
                  }}>Выделить левую сторону</button>
                  <button title="Выделить ячейки справа от прохода" onClick={() => {
                    selectRouteCells("right");
                    setRouteMenu(null);
                  }}>Выделить правую сторону</button>
                  <button title="Инвертировать выделение в выбранном участке" onClick={() => {
                    selectRouteCells("invert");
                    setRouteMenu(null);
                  }}>Инвертировать</button>
                  <button title="Очистить выделение участка обхода" onClick={() => {
                    selectRouteCells("clear");
                    setRouteMenu(null);
                  }}>Снять выделение</button>
                  <span>Построить обход</span>
                  {(["Z", "U_SHAPE", "SNAKE", "LINEAR"] as RoutePattern[]).map((pattern) => (
                    <button key={pattern} title={routePatternHint(pattern)} onClick={() => handleBuildRoute(pattern)}>{pattern}</button>
                  ))}
                </div>
              )}
            </div>
            </>
          )}
        </main>

          <aside className={`topology-right ${rightPanelCollapsed ? "collapsed" : ""}`}>
          <button className="panel-collapse-button" onClick={() => setRightPanelCollapsed((current) => !current)} title={rightPanelCollapsed ? "Развернуть правую панель" : "Свернуть правую панель"}>
            {rightPanelCollapsed ? "‹" : "›"}
          </button>
          <section>
            <div className="inspector-heading"><h3>{selectedCell?.aisle_code || "Аллея A03"}</h3><button onClick={() => setSelectedId(null)} title="Закрыть выбор ячейки в инспекторе">×</button></div>
            <div className="inspector-tabs">
              <button className={rightTab === "general" ? "active" : ""} onClick={() => setRightTab("general")} title="Показать общие данные выбранной ячейки">Общее</button>
              <button className={rightTab === "params" ? "active" : ""} onClick={() => setRightTab("params")} title="Показать редактируемые параметры выбранной ячейки">Параметры</button>
              <button className={rightTab === "stats" ? "active" : ""} onClick={() => setRightTab("stats")} title="Показать статистику, соседей и расстояния выбранной ячейки">Статистика</button>
            </div>
            {selectedCell ? (
              <div className="cell-inspector">
                <b>{selectedCell.cell_code}</b>
                {rightTab === "general" && (
                  <>
                    <span>{selectedCell.aisle_code} · {selectedCell.side_code} · bay {selectedCell.bay_no}</span>
                    <span>Тип: {selectedCell.cell_kind}</span>
                    <span>Координаты: {selectedCell.x.toFixed(1)} / {selectedCell.y.toFixed(1)}</span>
                    <span>Емкость: {selectedCell.max_volume_m3 || 0} м³ · {selectedCell.max_weight_kg || 0} кг</span>
                    <span>До отгрузки: {formatDistance(selectedCell.nearest_outbound_gate_distance_m)}</span>
                    <span>От приемки: {formatDistance(selectedCell.nearest_inbound_gate_distance_m)}</span>
                    <span>Порядок обхода: {selectedRouteCell ? `#${selectedRouteCell.pick_sequence}` : "не входит"}</span>
                    <button className="save-cell-button" disabled={!dirtyCells.has(selectedCell.topology_cell_id)} onClick={handleSaveSelectedCell} title={dirtyCells.has(selectedCell.topology_cell_id) ? "Сохранить изменения выбранной ячейки" : "Нет несохраненных изменений выбранной ячейки"}>Сохранить ячейку</button>
                  </>
                )}
                {rightTab === "params" && (
                  <>
                    <span>Координаты физической ячейки фиксируются топологией. На этой странице редактируется порядок обхода и связи между ячейками.</span>
                    <label className="inspector-field"><span>Сторона</span><select value={selectedCell.side_code} onChange={(event) => {
                      const value = event.currentTarget.value;
                      updateSelectedCell("side_code", value);
                    }}><option>LEFT</option><option>RIGHT</option><option>CENTER</option></select></label>
                    <label className="inspector-field"><span>Тип</span><select value={selectedCell.cell_kind} onChange={(event) => {
                      const value = event.currentTarget.value;
                      updateSelectedCell("cell_kind", value);
                    }}><option>PICK_FACE</option><option>DYNAMIC_PICK_FACE</option><option>STORAGE</option><option>STAGING</option></select></label>
                  </>
                )}
                {rightTab === "stats" && (
                  <>
                    <div className="gate-distance-list">
                      {distancesForSelected.map((distance) => (
                        <span key={distance.cell_gate_distance_id}>
                          <b>{distance.gate_code}</b>
                          {Math.round(distance.distance_m)} м · {formatSeconds(distance.travel_time_sec)}
                        </span>
                      ))}
                    </div>
                    <span>Предыдущая: {prevCell?.cell_code || "нет"}</span>
                    <span>Следующая: {nextCell?.cell_code || "нет"}</span>
                  </>
                )}
              </div>
            ) : <p>Выберите ячейку на карте, чтобы увидеть сторону прохода, координаты и участие в маршруте.</p>}
          </section>

          <section>
            <h3>Проверка</h3>
            {validation ? (
              <div className={validation.valid ? "validation-card ok" : "validation-card bad"}>
                <b>{validation.valid ? "Ошибок нет" : `${validation.error_count} ошибок`}</b>
                {Object.entries(validation.checks).map(([key, rows]) => (
                  <span key={key}>{validationLabel(key)}: {Array.isArray(rows) ? rows.length : 0}</span>
                ))}
              </div>
            ) : <p>Запустите проверку перед публикацией топологии.</p>}
            <button className="save-cell-button" onClick={handleValidate} title="Запустить проверку целостности топологии и порядка обхода">Проверить топологию</button>
          </section>

          <section>
            <h3>Порядок обхода</h3>
            {activeRoute ? (
              <div className="route-summary">
                <b>{activeRoute.route_code}</b>
                <span>{activeRoute.route_pattern || "Z"} · {activeRoute.status || "DRAFT"}</span>
                <span>{activeRouteCells.length} ячеек в последовательности</span>
              </div>
            ) : <p>Постройте Z-обход для выбранных аллей.</p>}
            <div className="route-list">
              {activeRouteCells.slice(0, 12).map((routeCell) => (
                <span key={routeCell.pick_route_cell_id}><b>{routeCell.pick_sequence}</b>{routeCell.cell_code}</span>
              ))}
            </div>
          </section>

          <section>
            <h3>Рекомендации</h3>
            <div className="topology-recommendation warning">
              <b>ABC layout</b>
              <span>A-SKU с высокой частотой отбора стоит держать ближе к фронтальному проезду. Это рекомендация к новой версии, не ежедневное изменение.</span>
            </div>
            <div className="topology-recommendation">
              <b>Dynamic pick-face</b>
              <span>Свободные ячейки отбора лучше выделять в конце аллеи и публиковать через мастер-данные.</span>
            </div>
          </section>
          </aside>
        </section>
      </main>
    </div>
  );
}

function NumberField({ label, value, min, max, onChange }: {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="number-field" title={`${label}: значение от ${min} до ${max}`}>
      <span>{label}</span>
      <input type="number" min={min} max={max} value={value} onChange={(event) => {
        const nextValue = Number(event.currentTarget.value);
        onChange(nextValue);
      }} />
    </label>
  );
}

function LayerToggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: () => void }) {
  return <label className="topology-check" title={`Показать или скрыть слой "${label}" на карте`}><input type="checkbox" checked={checked} onChange={onChange} /> {label}</label>;
}

function InspectorField({ label, value, onChange }: { label: string; value: number; onChange: (value: string) => void }) {
  return <label className="inspector-field" title={`Редактировать поле "${label}" выбранной ячейки`}><span>{label}</span><input type="number" value={value} step="0.1" onChange={(event) => {
    const nextValue = event.currentTarget.value;
    onChange(nextValue);
  }} /></label>;
}

function routePatternHint(pattern: RoutePattern) {
  const hints: Record<RoutePattern, string> = {
    Z: "Построить Z-порядок: соседние проходы обходятся от ближайшего торца",
    U_SHAPE: "Построить П-образный порядок обхода участка",
    SNAKE: "Построить змейку с чередованием направления по аллеям",
    LINEAR: "Построить линейный порядок без чередования Z"
  };
  return hints[pattern];
}

function TopologyCellTable({ cells, selectedId, onSelect }: { cells: TopologyCell[]; selectedId: number | null; onSelect: (id: number) => void }) {
  return (
    <div className="topology-table-wrap">
      <table className="topology-table">
        <thead><tr><th>Ячейка</th><th>Аллея</th><th>Сторона</th><th>Тип</th><th>X</th><th>Y</th><th>До ворот</th></tr></thead>
        <tbody>
          {cells.slice(0, 260).map((cell) => (
            <tr key={cell.topology_cell_id} className={selectedId === cell.topology_cell_id ? "selected" : ""} onClick={() => onSelect(cell.topology_cell_id)}>
              <td>{cell.cell_code}</td>
              <td>{cell.aisle_code}</td>
              <td>{cell.side_code}</td>
              <td>{cell.cell_kind}</td>
              <td>{cell.x.toFixed(1)}</td>
              <td>{cell.y.toFixed(1)}</td>
              <td>{formatDistance(cell.nearest_outbound_gate_distance_m)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

type MapBounds = { minX: number; maxX: number; minY: number; maxY: number };

function TopologySvg({ map, routeCells: activeRouteCells, routeByCell, selectedId, selectedRouteCellIds, selectionRect, layers, mode, view, isPanning, isSelecting, onSelect, onCellPointerDown, onPointerDown, onPointerMove, onPointerUp, onContextMenu }: {
  map: TopologyMap;
  routeCells: PickRouteCell[];
  routeByCell: Map<number, PickRouteCell>;
  selectedId: number | null;
  selectedRouteCellIds: Set<number>;
  selectionRect: SvgSelectionRect | null;
  layers: MapLayerState;
  mode: "3d" | "plan" | "list";
  view: { zoom: number; panX: number; panY: number };
  isPanning: boolean;
  isSelecting: boolean;
  onSelect: (id: number) => void;
  onCellPointerDown: (event: PointerEvent<SVGGElement>, cell: TopologyCell) => void;
  onPointerDown: (event: PointerEvent<SVGSVGElement>) => void;
  onPointerMove: (event: PointerEvent<SVGSVGElement>) => void;
  onPointerUp: () => void;
  onContextMenu: (event: PointerEvent<SVGSVGElement>) => void;
}) {
  const bounds = mapBounds(map.cells, map.aisles);
  const routeCells = activeRouteCells
    .map((routeCell) => {
      const cell = map.cells.find((item) => item.topology_cell_id === routeCell.topology_cell_id);
      return cell ? { routeCell, cell } : null;
    })
    .filter(Boolean) as Array<{ routeCell: PickRouteCell; cell: TopologyCell }>;
  const routeSegments = buildRouteSegments(routeCells, bounds, mode, map.aisles);
  const invZoom = 1 / view.zoom;
  const cellVisual = getCellVisualSize(map.cells, bounds, mode);

  return (
    <svg
      className={`topology-svg ${mode === "plan" ? "plan-mode" : ""}`}
      viewBox="0 0 1000 650"
      preserveAspectRatio="xMidYMin meet"
      role="img"
      aria-label="Карта топологии склада"
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerLeave={onPointerUp}
      onContextMenu={onContextMenu}
      style={{ cursor: isSelecting ? "crosshair" : isPanning ? "grabbing" : "grab" }}
    >
      <defs>
        <pattern id="topology-grid" width="32" height="32" patternUnits="userSpaceOnUse">
          <path d="M 32 0 L 0 0 0 32" fill="none" stroke="#dbe6f3" strokeWidth="1" />
        </pattern>
        <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="6" stdDeviation="5" floodColor="#1f2f48" floodOpacity=".18" />
        </filter>
        <marker id="route-arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef3b82" />
        </marker>
        <marker id="passage-arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#8b5a2b" />
        </marker>
      </defs>
      <rect width="1000" height="650" fill="#f8fbff" />
      <g transform={`translate(${view.panX} ${view.panY}) scale(${view.zoom})`}>
        {layers.zones && (
          <>
            {mode === "plan" && <rect x="44" y="54" width="858" height="480" rx="3" fill="#eef5fb" stroke="#b6c5d5" />}
            {mode === "3d" && (
              <>
                <path d="M92 112 L820 44 L936 486 L178 574 Z" fill="#f2f7fb" stroke="#b6c5d5" strokeWidth="1.4" />
                <path d="M178 574 L936 486 L936 526 L178 616 Z" fill="#d9e4ee" stroke="#b6c5d5" />
                <path d="M820 44 L936 486 L936 526 L836 86 Z" fill="#e9eef5" stroke="#c5d1dd" />
                <path d="M92 112 L820 44 L836 86 L108 154 Z" fill="#ffffff" stroke="#d1dbe7" opacity=".72" />
              </>
            )}
          </>
        )}

        {layers.gates && map.gates.slice(0, 10).map((gate) => (
          <g key={gate.topology_gate_id}>
            {(() => {
              const point = projectPoint(gate.x, gate.y, bounds, mode);
              const gateY = mode === "3d" ? point.y + 26 : 568;
              return (
                <>
                  <rect x={point.x - 20} y={gateY} width="42" height="30" rx="2" fill={gate.gate_kind === "RECEIVING" ? "#0f766e" : "#27364a"} stroke="#0f172a" />
                  <rect x={point.x - 7} y={gateY + 30} width="7" height="12" fill="#fbbf24" />
                  {drawTruckIcon(point.x + 33, gateY + 3, gate.topology_gate_id)}
                  {layers.labels && <text x={point.x + invZoom} y={gateY - 5 * invZoom} className="gate-label" style={scaledTextStyle(13, 4, view.zoom)}>{gate.gate_code}</text>}
                </>
              );
            })()}
          </g>
        ))}

        {layers.gates && drawDockStagingZone(map, bounds, mode, layers.labels, view.zoom)}

        {layers.aisles && map.aisles.map((aisle) => {
          const start = projectAislePoint(aisle, aisle.y1, bounds, mode);
          const end = projectAislePoint(aisle, aisle.y2, bounds, mode);
          const x1 = start.x;
          const y1 = start.y;
          const x2 = end.x;
          const y2 = end.y;
          return (
            <g key={aisle.topology_aisle_id}>
              <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={Number(aisle.aisle_code.replace(/\D/g, "")) <= 5 ? "#86efac" : "#93c5fd"} strokeWidth={aisle.aisle_kind === "PICK_AISLE" ? mode === "3d" ? 34 : 40 : 28} strokeLinecap="round" opacity=".34" />
              <line x1={x1 - 20} y1={y1} x2={x2 - 20} y2={y2} stroke="#1d4ed8" strokeWidth="3" opacity=".65" />
              <line x1={x1 + 20} y1={y1} x2={x2 + 20} y2={y2} stroke="#1d4ed8" strokeWidth="3" opacity=".65" />
              <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#2563d8" strokeWidth="2.4" strokeDasharray="9 8" strokeLinecap="round" opacity=".72" />
            </g>
          );
        })}

        {layers.gates && drawAisleGateLinks(map, bounds)}

        {layers.distances && selectedId && drawDistanceLines(map, selectedId, bounds, mode)}

        {layers.route && (
          <g className="route-link-layer">
            {routeSegments.map((segment) => (
              <line
                key={`${segment.rowId}-${segment.fromCellId}-${segment.toCellId}`}
                className="route-link-line"
                x1={segment.x1}
                y1={segment.y1}
                x2={segment.x2}
                y2={segment.y2}
                markerEnd="url(#route-arrow)"
              >
                <title>{segment.title}</title>
              </line>
            ))}
          </g>
        )}

        {layers.cells && map.cells.filter((cell) => cell.active === 1).map((cell) => {
          const aisle = map.aisles.find((item) => item.aisle_code === cell.aisle_code);
          const point = projectCellPoint(cell, bounds, mode, aisle);
          const x = point.x;
          const y = point.y;
          const routeCell = routeByCell.get(cell.topology_cell_id);
          const selected = selectedId === cell.topology_cell_id;
          const inRouteSelection = selectedRouteCellIds.has(cell.topology_cell_id);
          return (
            <g
              key={cell.topology_cell_id}
              className="topology-cell-node"
              onClick={() => onSelect(cell.topology_cell_id)}
              onPointerDown={(event) => onCellPointerDown(event, cell)}
              filter={selected ? "url(#soft-shadow)" : undefined}
            >
              <title>{cellTooltip(cell, routeCell)}</title>
              <rect
                x={x - cellVisual.width / 2}
                y={y - cellVisual.height / 2}
                width={cellVisual.width}
                height={cellVisual.height}
                rx="0"
                fill="none"
                stroke="#ffffff"
                strokeWidth={cellVisual.separatorWidth}
                className="pick-face-cell-separator"
              />
              <rect
                x={x - cellVisual.width / 2}
                y={y - cellVisual.height / 2}
                width={cellVisual.width}
                height={cellVisual.height}
                rx="0"
                fill={cellFill(cell)}
                stroke={selected ? "#f59e0b" : inRouteSelection ? "#7c3aed" : "#37506d"}
                strokeWidth={selected || inRouteSelection ? 2.2 : 1.15}
                className="pick-face-cell-rect"
              />
              {mode === "3d" && <path d={`M ${x - cellVisual.width / 2} ${y + cellVisual.height / 2} L ${x - cellVisual.width / 2 + 8} ${y + cellVisual.height / 2 + 7} L ${x + cellVisual.width / 2 + 8} ${y + cellVisual.height / 2 + 7} L ${x + cellVisual.width / 2} ${y + cellVisual.height / 2} Z`} fill="#8b6f3e" opacity=".5" />}
            </g>
          );
        })}

        {layers.aisles && drawPassageOverlay(map, bounds, mode, layers.labels, view.zoom)}

        {selectionRect && (
          <rect
            x={selectionRect.x1}
            y={selectionRect.y1}
            width={Math.max(1, selectionRect.x2 - selectionRect.x1)}
            height={Math.max(1, selectionRect.y2 - selectionRect.y1)}
            fill="rgba(37,99,216,.12)"
            stroke="#2563eb"
            strokeWidth="2"
            strokeDasharray="8 6"
          />
        )}
      </g>
      {layers.labels && drawFixedLabelOverlay(map, routeByCell, bounds, mode, view)}
    </svg>
  );
}

function topologyStats(map: TopologyMap, activeRouteCellCount = map.route_cells.length) {
  return {
    aisles: map.aisles.filter((aisle) => aisle.aisle_kind === "PICK_AISLE").length,
    pickFaces: map.cells.filter((cell) => cell.cell_kind === "PICK_FACE" && cell.active === 1).length,
    dynamic: map.cells.filter((cell) => cell.cell_kind === "DYNAMIC_PICK_FACE" && cell.active === 1).length,
    routeCells: activeRouteCellCount,
    gates: map.gates.filter((gate) => gate.active === 1).length
  };
}

function clampZoom(value: number) {
  return Math.min(MAX_TOPOLOGY_ZOOM, Math.max(MIN_TOPOLOGY_ZOOM, Number(value.toFixed(2))));
}

function scaledTextStyle(fontPx: number, strokePx: number, zoom: number) {
  return {
    fontSize: `${fontPx / zoom}px`,
    strokeWidth: strokePx ? `${strokePx / zoom}px` : undefined
  };
}

function getCellVisualSize(cells: TopologyCell[], bounds: MapBounds, mode: "3d" | "plan" | "list") {
  const projectedSteps: number[] = [];
  const groups = new Map<string, TopologyCell[]>();
  cells.filter((cell) => cell.active === 1).forEach((cell) => {
    const key = `${cell.aisle_code || ""}:${cell.side_code || ""}:${cell.level_no || 1}`;
    groups.set(key, [...(groups.get(key) || []), cell]);
  });
  groups.forEach((groupCells) => {
    const ys = groupCells
      .map((cell) => projectPoint(cell.x, cell.y, bounds, mode).y)
      .sort((a, b) => a - b);
    for (let index = 1; index < ys.length; index += 1) {
      const delta = Math.abs(ys[index] - ys[index - 1]);
      if (delta > 0.5) projectedSteps.push(delta);
    }
  });
  const step = median(projectedSteps) || 14;
  const height = Math.max(4.8, Math.min(18, step * 0.72));
  const width = mode === "3d" ? 13 : 16;
  return {
    width,
    height,
    capHeight: 0,
    radius: 0,
    separatorWidth: 4.5
  };
}

function cellFill(cell: TopologyCell) {
  if (cell.cell_kind === "DYNAMIC_PICK_FACE") return "#fef08a";
  if (cell.side_code === "LEFT") return "#a7f3d0";
  if (cell.side_code === "RIGHT") return "#bfdbfe";
  return "#e2e8f0";
}

function median(values: number[]) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

async function loadInitialTopology(): Promise<{ topologies: Topology[]; map: TopologyMap } | null> {
  try {
    const response = await apiFetch(`${API_BASE}/api/admin/warehouse-topologies`, { cache: "no-store" });
    if (!response.ok) return null;
    const topologies = ((await response.json()) as Topology[]).map((item) => normalizeKeys(item) as Topology);
    const topology = topologies.find((item) => item.status === "PUBLISHED") || topologies[0];
    if (!topology) return null;
    const map = await loadTopologyMap(topology.topology_id);
    return map ? { topologies, map } : null;
  } catch {
    return null;
  }
}

async function loadTopologyMap(topologyId: number): Promise<TopologyMap | null> {
  const response = await apiFetch(`${API_BASE}/api/admin/warehouse-topologies/${topologyId}/map`, { cache: "no-store" });
  if (!response.ok) return null;
  return normalizeMap(await response.json());
}

async function createApiTopology(): Promise<number> {
  const response = await apiFetch(`${API_BASE}/api/admin/warehouse-topologies`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ware_id: 1,
      topology_code: `MAIN-${new Date().toISOString().slice(0, 10)}`,
      topology_name: "Основная топология отбора",
      version_no: 1,
      comment_text: "Создано из админки топологии склада"
    })
  });
  if (!response.ok) {
    throw new Error(`Topology create failed: ${response.status}`);
  }
  const created = await response.json() as { topology_id: number };
  return created.topology_id;
}

function normalizeMap(raw: TopologyMap): TopologyMap {
  return {
    topology: normalizeKeys(raw.topology) as Topology,
    aisles: (raw.aisles || []).map((item) => normalizeKeys(item) as TopologyAisle),
    gates: (raw.gates || []).map((item) => normalizeKeys(item) as TopologyGate),
    cells: (raw.cells || []).map((item) => normalizeKeys(item) as TopologyCell),
    distances: (raw.distances || []).map((item) => normalizeKeys(item) as CellGateDistance),
    routes: (raw.routes || []).map((item) => normalizeKeys(item) as PickRoute),
    route_cells: (raw.route_cells || []).map((item) => normalizeKeys(item) as PickRouteCell)
  };
}

function normalizeKeys(value: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(Object.entries(value).map(([key, item]) => [key.toLowerCase(), item]));
}

function emptyTopologyMap(): TopologyMap {
  return {
    topology: {
      topology_id: 0,
      ware_id: 1,
      ware_name: "Основной склад",
      topology_code: "LOADING",
      topology_name: "Загрузка топологии",
      version_no: 1,
      status: "DRAFT"
    },
    aisles: [],
    gates: [],
    cells: [],
    distances: [],
    routes: [],
    route_cells: []
  };
}

function demoTopologyMap(): TopologyMap {
  const topology: Topology = {
    topology_id: 1,
    ware_id: 1,
    ware_name: "Центральный склад",
    topology_code: "MAIN-2026-05",
    topology_name: "Основная топология отбора",
    version_no: 1,
    status: "DRAFT"
  };
  return buildLocalRoute(generateLocalTopology(topology, {
    aisle_count: 6,
    bays_per_aisle: 18,
    levels: 1,
    create_both_sides: 1
  }), ["A01", "A02", "A03"], "Z", []);
}

function generateLocalTopology(topology: Topology, options: {
  aisle_count: number;
  bays_per_aisle: number;
  levels: number;
  create_both_sides: number;
}): TopologyMap {
  const aisles: TopologyAisle[] = [];
  const cells: TopologyCell[] = [];
  const sides = options.create_both_sides ? ["LEFT", "RIGHT"] as const : ["LEFT"] as const;
  let cellId = 1;
  for (let aisleIndex = 0; aisleIndex < options.aisle_count; aisleIndex += 1) {
    const aisleCode = `A${String(aisleIndex + 1).padStart(2, "0")}`;
    const x = 8 + aisleIndex * 5;
    aisles.push({
      topology_aisle_id: aisleIndex + 1,
      aisle_code: aisleCode,
      aisle_name: `Аллея ${aisleCode}`,
      aisle_kind: "PICK_AISLE",
      x1: x,
      y1: 6,
      x2: x,
      y2: 6 + options.bays_per_aisle * 1.4,
      width_m: 3
    });
    for (let bay = 1; bay <= options.bays_per_aisle; bay += 1) {
      for (let level = 1; level <= options.levels; level += 1) {
        for (const side of sides) {
          const sideShift = side === "LEFT" ? -1.2 : 1.2;
          cells.push({
            topology_cell_id: cellId,
            topology_id: topology.topology_id,
            ware_id: topology.ware_id,
            cell_code: `${aisleCode}-B${String(bay).padStart(3, "0")}-L${level}-${side[0]}`,
            zone_code: "PICK",
            section_code: "S01",
            aisle_code: aisleCode,
            bay_no: bay,
            level_no: level,
            side_code: side,
            cell_kind: bay > options.bays_per_aisle - 2 ? "DYNAMIC_PICK_FACE" : "PICK_FACE",
            max_volume_m3: 1.5,
            max_weight_kg: 900,
            x: x + sideShift,
            y: 6 + bay * 1.4,
            z: 0,
            width: 1.1,
            depth: 1.1,
            height: 1.4,
            active: 1
          });
          cellId += 1;
        }
      }
    }
  }
  const gates = buildDemoGates(topology);
  return recalculateLocalGateDistances({ topology: { ...topology, cell_count: cells.length, aisle_count: aisles.length }, aisles, gates, cells, distances: [], routes: [], route_cells: [] });
}

function buildLocalRoute(map: TopologyMap, aisleCodes: string[], pattern: RoutePattern, selectedCellIds: number[]): TopologyMap {
  const sideRank: Record<string, number> = { LEFT: 0, RIGHT: 1, CENTER: 9 };
  const selectedSet = new Set(selectedCellIds);
  const aisleOrder = new Map(aisleCodes.map((code, index) => [code, index]));
  const selected = map.cells
    .filter((cell) => cell.active === 1
      && cell.cell_kind.includes("PICK_FACE")
      && aisleCodes.includes(cell.aisle_code || "")
      && (!selectedSet.size || selectedSet.has(cell.topology_cell_id)))
    .sort((a, b) => String(a.aisle_code).localeCompare(String(b.aisle_code))
      || Number(a.bay_no || 0) - Number(b.bay_no || 0)
      || sideRank[a.side_code] - sideRank[b.side_code]);
  const ordered = orderRouteCells(selected, aisleOrder, pattern, sideRank);
  const routeCells = ordered.map((cell, index) => ({
    pick_route_cell_id: index + 1,
    pick_route_id: 1,
    topology_cell_id: cell.topology_cell_id,
    cell_code: cell.cell_code,
    pick_sequence: index + 1
  }));
  return {
    ...map,
    routes: [{
      pick_route_id: 1,
      topology_id: map.topology.topology_id,
      route_code: `CASE-${pattern}-MAIN`,
      route_name: `Основной ${pattern}-обход отбора`,
      route_pattern: pattern,
      status: "DRAFT",
      cell_count: routeCells.length
    }],
    route_cells: routeCells
  };
}

function orderRouteCells(
  cells: TopologyCell[],
  aisleOrder: Map<string, number>,
  pattern: RoutePattern,
  sideRank: Record<string, number>
) {
  const groups = Array.from(groupByAisle(cells).entries())
    .sort((a, b) => (aisleOrder.get(a[0]) ?? 999) - (aisleOrder.get(b[0]) ?? 999));
  const ordered: TopologyCell[] = [];
  groups.forEach(([, aisleCells], index) => {
    const reverse = pattern === "Z" || pattern === "SNAKE" ? index % 2 === 1 : pattern === "U_SHAPE";
    const sideFirst = pattern === "LINEAR" || pattern === "U_SHAPE";
    ordered.push(...aisleCells.sort((a, b) => {
      const bayDiff = Number(a.bay_no || 0) - Number(b.bay_no || 0);
      const levelDiff = Number(a.level_no || 0) - Number(b.level_no || 0);
      const sideDiff = sideRank[a.side_code] - sideRank[b.side_code];
      if (sideFirst) return sideDiff || (reverse ? -bayDiff : bayDiff) || levelDiff;
      return (reverse ? -bayDiff : bayDiff) || sideDiff || levelDiff;
    }));
  });
  return ordered;
}

function groupByAisle(cells: TopologyCell[]) {
  const groups = new Map<string, TopologyCell[]>();
  cells.forEach((cell) => {
    const aisle = cell.aisle_code || "";
    groups.set(aisle, [...(groups.get(aisle) || []), cell]);
  });
  return groups;
}

function buildDemoGates(topology: Topology): TopologyGate[] {
  return Array.from({ length: 10 }, (_, index) => ({
    topology_gate_id: index + 1,
    topology_id: topology.topology_id,
    ware_id: topology.ware_id,
    gate_code: `G${String(index + 1).padStart(2, "0")}`,
    gate_name: `Ворота G${String(index + 1).padStart(2, "0")}`,
    gate_kind: index < 2 ? "RECEIVING" : "SHIPPING",
    staging_zone_code: "DOCK",
    x: 4 + index * 4.2,
    y: 58,
    width: 2.8,
    height: 3.2,
    active: 1
  }));
}

function recalculateLocalGateDistances(map: TopologyMap): TopologyMap {
  const distances: CellGateDistance[] = [];
  let id = 1;
  const cells = map.cells.map((cell) => {
    const cellDistances = map.gates.map((gate) => {
      const distance = Math.abs(cell.x - gate.x) + Math.abs(cell.y - gate.y);
      const speed = cell.cell_kind === "STORAGE" ? 1.8 : 1.1;
      const item: CellGateDistance = {
        cell_gate_distance_id: id++,
        topology_id: map.topology.topology_id,
        topology_cell_id: cell.topology_cell_id,
        topology_gate_id: gate.topology_gate_id,
        gate_code: gate.gate_code,
        gate_kind: gate.gate_kind,
        flow_kind: "BOTH",
        distance_m: Number(distance.toFixed(1)),
        travel_time_sec: Number((distance / speed).toFixed(1))
      };
      distances.push(item);
      return item;
    });
    const outbound = cellDistances.filter((distance) => distance.gate_kind !== "RECEIVING").sort((a, b) => a.distance_m - b.distance_m)[0];
    const inbound = cellDistances.filter((distance) => distance.gate_kind !== "SHIPPING").sort((a, b) => a.distance_m - b.distance_m)[0];
    return {
      ...cell,
      nearest_outbound_gate_distance_m: outbound?.distance_m,
      nearest_inbound_gate_distance_m: inbound?.distance_m
    };
  });
  return { ...map, cells, distances };
}

function formatDistance(value?: number) {
  return typeof value === "number" ? `${Math.round(value)} м` : "не рассчитано";
}

function formatSeconds(value?: number) {
  if (typeof value !== "number") return "нет времени";
  if (value < 60) return `${Math.round(value)} сек`;
  return `${Math.floor(value / 60)} мин ${Math.round(value % 60)} сек`;
}

function validateLocalTopology(map: TopologyMap): ValidationResult {
  const duplicateMap = new Map<string, number>();
  map.cells.filter((cell) => cell.active === 1).forEach((cell) => {
    duplicateMap.set(cell.cell_code, (duplicateMap.get(cell.cell_code) || 0) + 1);
  });
  const duplicate_cells = Array.from(duplicateMap.entries()).filter(([, count]) => count > 1);
  const pick_faces_without_aisle = map.cells.filter((cell) => cell.active === 1 && cell.cell_kind.includes("PICK_FACE") && !cell.aisle_code);
  const pick_faces_without_side = map.cells.filter((cell) => cell.active === 1 && cell.cell_kind.includes("PICK_FACE") && !["LEFT", "RIGHT"].includes(cell.side_code));
  const gates_missing = map.gates.filter((gate) => gate.active === 1).length ? [] : [{ gate: "missing" }];
  const distances_missing = map.distances.length ? [] : [{ distance: "missing" }];
  const checks = { duplicate_cells, pick_faces_without_aisle, pick_faces_without_side, gates_missing, distances_missing };
  const error_count = Object.values(checks).reduce((sum, rows) => sum + rows.length, 0);
  return { valid: error_count === 0, error_count, checks };
}

function validationLabel(key: string) {
  const labels: Record<string, string> = {
    duplicate_cells: "Дубли ячеек",
    pick_faces_without_aisle: "Pick-face без аллеи",
    pick_faces_without_side: "Pick-face без стороны",
    multiple_active_pick_routes: "Несколько активных обходов",
    duplicate_route_sequence: "Дубли порядка обхода",
    duplicate_route_cell: "Повтор ячейки в обходе",
    pick_faces_on_inactive_route: "Pick-face на архивном обходе",
    gates_missing: "Нет ворот",
    distances_missing: "Нет расстояний"
  };
  return labels[key] || key;
}

function topologyStatusText(status: TopologyStatus) {
  const labels: Record<TopologyStatus, string> = {
    DRAFT: "Черновик мастер-данных",
    VALIDATED: "Проверенная версия мастер-данных",
    PUBLISHED: "Опубликованная мастер-версия",
    ARCHIVED: "Архивная версия"
  };
  return labels[status] || status;
}

function drawDistanceLines(map: TopologyMap, selectedId: number, bounds: MapBounds, mode: "3d" | "plan" | "list") {
  const cell = map.cells.find((item) => item.topology_cell_id === selectedId);
  if (!cell) return null;
  return map.distances
    .filter((distance) => distance.topology_cell_id === selectedId)
    .sort((a, b) => a.distance_m - b.distance_m)
    .slice(0, 3)
    .map((distance) => {
      const gate = map.gates.find((item) => item.topology_gate_id === distance.topology_gate_id);
      if (!gate) return null;
      const aisle = map.aisles.find((item) => item.aisle_code === cell.aisle_code);
      const from = projectCellPoint(cell, bounds, mode, aisle);
      const to = projectPoint(gate.x, gate.y, bounds, mode);
      return <line key={distance.cell_gate_distance_id} x1={from.x} y1={from.y} x2={to.x} y2={mode === "3d" ? to.y + 30 : 586} stroke="#0f766e" strokeWidth="2" strokeDasharray="6 6" opacity=".56" />;
  });
}

function drawDockStagingZone(map: TopologyMap, bounds: MapBounds, mode: "3d" | "plan" | "list", showLabels: boolean, zoom: number) {
  const shippingGates = map.gates.filter((gate) => gate.active === 1 && gate.gate_kind !== "RECEIVING").slice(0, 10);
  if (!shippingGates.length) return null;
  const invZoom = 1 / zoom;
  const points = shippingGates.map((gate) => projectPoint(gate.x, gate.y, bounds, mode));
  const rackRight = Math.max(...map.cells.filter((cell) => cell.active === 1).map((cell) => projectPoint(cell.x, cell.y, bounds, mode).x));
  const minX = mode === "plan" ? Math.min(870, rackRight + 36) : Math.min(878, Math.max(...points.map((point) => point.x)) + 26);
  const y = mode === "plan" ? 178 : Math.max(190, Math.min(...points.map((point) => point.y)) - 112);
  const slotColumns = 2;
  const slotRows = 16;
  const slotWidth = 20;
  const slotHeight = 10;
  const gap = 3;
  const width = slotColumns * slotWidth + (slotColumns + 1) * gap;
  const height = slotRows * slotHeight + (slotRows + 1) * gap;
  const centerGate = shippingGates[Math.max(0, Math.floor(shippingGates.length / 2) - 1)];
  const centerPoint = centerGate ? projectPoint(centerGate.x, centerGate.y, bounds, mode) : { x: 500, y: 568 };
  const receivingColumns = 5;
  const receivingRows = 4;
  const receivingSlotWidth = 13;
  const receivingSlotHeight = 9;
  const receivingGap = 3;
  const receivingWidth = receivingColumns * receivingSlotWidth + (receivingColumns + 1) * receivingGap;
  const receivingHeight = receivingRows * receivingSlotHeight + (receivingRows + 1) * receivingGap;
  const receivingX = centerPoint.x - receivingWidth / 2;
  const receivingY = mode === "plan" ? 494 : centerPoint.y - 76;
  return (
    <>
      <g className="topology-receiving-zone">
        <title>Зона приемки у центрального докового разрыва: 20 паллетомест для входящих паллет перед размещением на хранение.</title>
        <rect x={receivingX} y={receivingY} width={receivingWidth} height={receivingHeight} rx="2" className="receiving-staging-base" />
        {Array.from({ length: receivingColumns * receivingRows }, (_, index) => {
          const column = index % receivingColumns;
          const row = Math.floor(index / receivingColumns);
          return (
            <rect
              key={`receiving-slot-${index}`}
              x={receivingX + receivingGap + column * (receivingSlotWidth + receivingGap)}
              y={receivingY + receivingGap + row * (receivingSlotHeight + receivingGap)}
              width={receivingSlotWidth}
              height={receivingSlotHeight}
              rx="0"
              className="receiving-staging-slot"
            />
          );
        })}
        {showLabels && (
          <text x={receivingX + receivingWidth / 2} y={receivingY - 7 * invZoom} className="receiving-staging-label" style={scaledTextStyle(10, 3, zoom)}>
            Приемка 20 п/м
          </text>
        )}
      </g>
      <g className="topology-dock-zone">
        <title>Зона накопления транспортных паллет перед воротами отгрузки. Паллеты выставляются сюда перед загрузкой автомобиля.</title>
        <rect x={minX} y={y} width={width} height={height} rx="2" className="dock-staging-base" />
        {Array.from({ length: slotColumns * slotRows }, (_, index) => {
          const column = index % slotColumns;
          const row = Math.floor(index / slotColumns);
          return (
            <rect
              key={`dock-slot-${index}`}
              x={minX + gap + column * (slotWidth + gap)}
              y={y + gap + row * (slotHeight + gap)}
              width={slotWidth}
              height={slotHeight}
              rx="0"
              className={index < 9 ? "dock-staging-slot occupied" : "dock-staging-slot"}
            />
          );
        })}
        {showLabels && (
          <text x={minX + width / 2} y={y - 8 * invZoom} className="staging-label" style={scaledTextStyle(10, 3, zoom)}>
            Накопление ТП
          </text>
        )}
      </g>
    </>
  );
}

function drawFixedLabelOverlay(
  map: TopologyMap,
  routeByCell: Map<number, PickRouteCell>,
  bounds: MapBounds,
  mode: "3d" | "plan" | "list",
  view: { zoom: number; panX: number; panY: number }
) {
  const activeCells = map.cells.filter((cell) => cell.active === 1);
  const denseMap = activeCells.length > 300;
  const showCellCodes = !denseMap && view.zoom <= 2.8;
  const showCellRouteCodes = view.zoom >= 3.5;
  const routeBadgeStep = view.zoom >= 4 ? 6 : view.zoom >= 2 ? 12 : 30;
  const routeBadgeRadius = view.zoom >= 4 ? 10 : 7;
  return (
    <g className="fixed-map-label-layer">
      {activeCells.map((cell) => {
        const aisle = map.aisles.find((item) => item.aisle_code === cell.aisle_code);
        const point = toViewportPoint(projectCellPoint(cell, bounds, mode, aisle), view);
        const routeCell = routeByCell.get(cell.topology_cell_id);
        return (
          <g key={`fixed-label-${cell.topology_cell_id}`}>
            {routeCell && routeCell.pick_sequence % routeBadgeStep === 1 && (
              <>
                <circle cx={point.x + 13} cy={point.y - 13} r={routeBadgeRadius} className="fixed-route-badge" />
                <text x={point.x + 13} y={point.y - 9} className="route-sequence">{routeCell.pick_sequence}</text>
              </>
            )}
            {showCellRouteCodes && routeCell && (
              <text x={point.x} y={point.y + 3} className="ya-order-label">{pickFaceRouteLabel(cell, routeCell)}</text>
            )}
            {showCellCodes && <text x={point.x} y={point.y + 19} className="cell-code-label">{shortCellLabel(cell)}</text>}
          </g>
        );
      })}
      {map.aisles.map((aisle) => {
        if (denseMap && view.zoom < 1.8) return null;
        const start = toViewportPoint(projectAislePoint(aisle, aisle.y1, bounds, mode), view);
        const end = toViewportPoint(projectAislePoint(aisle, aisle.y2, bounds, mode), view);
        return (
          <g key={`fixed-aisle-label-${aisle.topology_aisle_id}`}>
            <text x={start.x - 22} y={start.y - 12} className="aisle-label">{aisle.aisle_code}</text>
            <text x={end.x + 22} y={end.y + 18} className="aisle-label">{aisle.aisle_code}</text>
          </g>
        );
      })}
    </g>
  );
}

function cellTooltip(cell: TopologyCell, routeCell?: PickRouteCell) {
  const routeFields = routeCell
    ? Object.entries(routeCell)
      .map(([key, value]) => `${key}: ${String(value ?? "")}`)
      .join("\n")
    : "не входит в активный порядок обхода";
  return [
    `ЯО: ${cell.cell_code}`,
    `topology_cell_id: ${cell.topology_cell_id}`,
    `topology_id: ${cell.topology_id}`,
    `ware_id: ${cell.ware_id}`,
    `зона: ${cell.zone_code || ""}`,
    `секция: ${cell.section_code || ""}`,
    `аллея: ${cell.aisle_code || ""}`,
    `ряд/bay: ${cell.bay_no || ""}`,
    `ярус: ${cell.level_no || ""}`,
    `сторона: ${cell.side_code}`,
    `тип: ${cell.cell_kind}`,
    `координаты: X=${cell.x}, Y=${cell.y}, Z=${cell.z}`,
    `габариты: ${cell.width} x ${cell.depth} x ${cell.height}`,
    `емкость: ${cell.max_volume_m3 || 0} м3 / ${cell.max_weight_kg || 0} кг`,
    `до отгрузки: ${formatDistance(cell.nearest_outbound_gate_distance_m)}`,
    `от приемки: ${formatDistance(cell.nearest_inbound_gate_distance_m)}`,
    "",
    "Порядок сбора:",
    routeFields
  ].join("\n");
}

function pickFaceRouteLabel(cell: TopologyCell, routeCell: PickRouteCell) {
  return `${cell.bay_no || 0}-${routeCell.pick_sequence}`;
}

function toViewportPoint(point: SvgPoint, view: { zoom: number; panX: number; panY: number }): SvgPoint {
  return {
    x: view.panX + point.x * view.zoom,
    y: view.panY + point.y * view.zoom
  };
}

function drawPassageOverlay(map: TopologyMap, bounds: MapBounds, mode: "3d" | "plan" | "list", showLabels: boolean, zoom: number) {
  const pickAisles = map.aisles.filter((aisle) => aisle.aisle_kind === "PICK_AISLE");
  const activeCells = map.cells.filter((cell) => cell.active === 1);
  const denseMap = activeCells.length > 300;
  const showAisleLabels = showLabels && (!denseMap || zoom >= 1.8);
  const sectionRects = groupedSectionRects(activeCells, bounds, mode);
  const invZoom = 1 / zoom;
  return (
    <g className="topology-passage-layer">
      {sectionRects.map((rect) => (
        <g key={rect.sectionCode} className="section-boundary">
          <rect x={rect.x} y={rect.y} width={rect.width} height={rect.height} rx="2" />
          {showLabels && <text x={rect.x + rect.width / 2} y={rect.y + rect.height + 22 * invZoom} style={scaledTextStyle(13, 4, zoom)}>{rect.sectionCode}</text>}
        </g>
      ))}
      {pickAisles.map((aisle, index) => {
        const start = projectAislePoint(aisle, aisle.y1, bounds, mode);
        const end = projectAislePoint(aisle, aisle.y2, bounds, mode);
        const directionDown = index % 2 === 0;
        const from = directionDown ? start : end;
        const to = directionDown ? end : start;
        const aisleNo = Number(aisle.aisle_code.replace(/\D/g, ""));
        return (
          <g key={`passage-${aisle.topology_aisle_id}`} className="passage-corridor">
            <line x1={start.x} y1={start.y} x2={end.x} y2={end.y} className="passage-fill" />
            <line x1={start.x - 13} y1={start.y} x2={end.x - 13} y2={end.y} className="passage-edge" />
            <line x1={start.x + 13} y1={start.y} x2={end.x + 13} y2={end.y} className="passage-edge" />
            <line x1={from.x} y1={from.y + (directionDown ? 22 : -22)} x2={to.x} y2={to.y + (directionDown ? -22 : 22)} className="passage-direction" markerEnd="url(#passage-arrow)" />
            {showAisleLabels && (
              <>
                <text x={start.x} y={start.y - 20 * invZoom} className="passage-label" style={scaledTextStyle(16, 5, zoom)}>{aisle.aisle_code}</text>
                <text x={end.x} y={end.y + 28 * invZoom} className="passage-label" style={scaledTextStyle(16, 5, zoom)}>{aisle.aisle_code}</text>
                {aisleNo % 3 === 1 && <text x={start.x + 18 * invZoom} y={(start.y + end.y) / 2} className="passage-width-label" style={scaledTextStyle(10, 3, zoom)}>проход 3 м</text>}
              </>
            )}
          </g>
        );
      })}
      {drawCrossPassages(pickAisles, bounds, mode, zoom, showAisleLabels)}
    </g>
  );
}

function groupedSectionRects(cells: TopologyCell[], bounds: MapBounds, mode: "3d" | "plan" | "list") {
  const groups = new Map<string, TopologyCell[]>();
  cells.forEach((cell) => {
    const key = cell.section_code || "Секция";
    groups.set(key, [...(groups.get(key) || []), cell]);
  });
  return Array.from(groups.entries()).map(([sectionCode, sectionCells]) => {
    const points = sectionCells.map((cell) => projectPoint(cell.x, cell.y, bounds, mode));
    const xs = points.map((point) => point.x);
    const ys = points.map((point) => point.y);
    const padX = mode === "plan" ? 42 : 34;
    const padY = mode === "plan" ? 28 : 26;
    const minX = Math.min(...xs) - padX;
    const maxX = Math.max(...xs) + padX;
    const minY = Math.min(...ys) - padY;
    const maxY = Math.max(...ys) + padY;
    return { sectionCode, x: minX, y: minY, width: maxX - minX, height: maxY - minY };
  });
}

function drawCrossPassages(aisles: TopologyAisle[], bounds: MapBounds, mode: "3d" | "plan" | "list", zoom: number, showLabels: boolean) {
  if (aisles.length < 2) return null;
  const invZoom = 1 / zoom;
  const sorted = [...aisles].sort((a, b) => a.x1 - b.x1);
  const first = sorted[0];
  const last = sorted[sorted.length - 1];
  const topStart = projectAislePoint(first, first.y1, bounds, mode);
  const topEnd = projectAislePoint(last, last.y1, bounds, mode);
  const bottomStart = projectAislePoint(first, first.y2, bounds, mode);
  const bottomEnd = projectAislePoint(last, last.y2, bounds, mode);
  return (
    <g className="cross-passage">
      <line x1={topStart.x} y1={topStart.y - 22} x2={topEnd.x} y2={topEnd.y - 22} markerEnd="url(#passage-arrow)" />
      <line x1={bottomEnd.x} y1={bottomEnd.y + 22} x2={bottomStart.x} y2={bottomStart.y + 22} markerEnd="url(#passage-arrow)" />
      {showLabels && (
        <>
          <text x={(topStart.x + topEnd.x) / 2} y={topStart.y - 34 * invZoom} style={scaledTextStyle(13, 4, zoom)}>фронтальный проход</text>
          <text x={(bottomStart.x + bottomEnd.x) / 2} y={bottomStart.y + 42 * invZoom} style={scaledTextStyle(13, 4, zoom)}>тыловой проход</text>
        </>
      )}
    </g>
  );
}

function drawAisleGateLinks(map: TopologyMap, bounds: MapBounds) {
  const shippingGates = map.gates.filter((gate) => gate.active === 1 && gate.gate_kind !== "RECEIVING");
  if (!shippingGates.length) return null;
  return map.aisles.filter((aisle) => aisle.aisle_kind === "PICK_AISLE").flatMap((aisle) => {
    const ends = [
      { code: "верхний торец", x: aisle.x1, y: aisle.y1 },
      { code: "нижний торец", x: aisle.x2, y: aisle.y2 }
    ];
    return ends.map((end) => {
      const nearestGate = shippingGates
        .map((gate) => ({ gate, distance: Math.abs(end.x - gate.x) + Math.abs(end.y - gate.y) + 20 }))
        .sort((a, b) => a.distance - b.distance)[0];
      if (!nearestGate) return null;
      const x1 = sx(end.x, bounds);
      const y1 = sy(end.y, bounds);
      const x2 = sx(nearestGate.gate.x, bounds);
      const y2 = 586;
      return (
        <g key={`${aisle.aisle_code}-${end.code}-${nearestGate.gate.gate_code}`} className="gate-link">
          <path d={`M ${x1} ${y1} L ${x1} ${Math.min(560, y2 - 36)} L ${x2} ${Math.min(560, y2 - 36)} L ${x2} ${y2}`} fill="none" />
          <text x={(x1 + x2) / 2} y={Math.min(552, y2 - 44)}>{Math.round(nearestGate.distance)} м</text>
        </g>
      );
    });
  });
}

function buildRouteSegments(
  rows: Array<{ routeCell: PickRouteCell; cell: TopologyCell }>,
  bounds: MapBounds,
  mode: "3d" | "plan" | "list",
  aisles: TopologyAisle[]
) {
  return rows.slice(1).map(({ routeCell, cell }, index) => {
    const previous = rows[index];
    const fromAisle = aisles.find((item) => item.aisle_code === previous.cell.aisle_code);
    const toAisle = aisles.find((item) => item.aisle_code === cell.aisle_code);
    const from = projectCellPoint(previous.cell, bounds, mode, fromAisle);
    const to = projectCellPoint(cell, bounds, mode, toAisle);
    const routeFields = Object.entries(routeCell)
      .map(([key, value]) => `${key}=${String(value ?? "")}`)
      .join("\n");
    return {
      rowId: routeCell.pick_route_cell_id,
      fromCellId: previous.cell.topology_cell_id,
      toCellId: cell.topology_cell_id,
      x1: from.x,
      y1: from.y,
      x2: to.x,
      y2: to.y,
      title: [
        "Таблица: RRL_PICK_ROUTE_CELL",
        routeFields,
        "Вычисленный переход UI, не поля таблицы:",
        `sequence: ${previous.routeCell.pick_sequence} -> ${routeCell.pick_sequence}`,
        `from.topology_cell_id=${previous.cell.topology_cell_id}`,
        `from.cell_code=${previous.cell.cell_code}`,
        `to.topology_cell_id=${cell.topology_cell_id}`,
        `to.cell_code=${cell.cell_code}`,
        `from.pick_route_cell_id=${previous.routeCell.pick_route_cell_id}`,
        `to.pick_route_cell_id=${routeCell.pick_route_cell_id}`
      ].join("\n")
    };
  });
}

function projectCellPoint(cell: TopologyCell, bounds: MapBounds, mode: "3d" | "plan" | "list", aisle?: TopologyAisle) {
  const travel = projectTravelPoint(cell, bounds, mode, aisle);
  const side = cell.side_code === "LEFT" ? -1 : cell.side_code === "RIGHT" ? 1 : 0;
  const offset = mode === "3d" ? 30 : 34;
  return {
    x: travel.x + side * offset,
    y: travel.y
  };
}

function projectTravelPoint(cell: TopologyCell, bounds: MapBounds, mode: "3d" | "plan" | "list", aisle?: TopologyAisle) {
  const centerX = aisle ? aisle.x1 : cell.side_code === "LEFT" ? cell.x + 1.2 : cell.side_code === "RIGHT" ? cell.x - 1.2 : cell.x;
  return projectPoint(centerX, cell.y, bounds, mode);
}

function projectAislePoint(aisle: TopologyAisle, y: number, bounds: MapBounds, mode: "3d" | "plan" | "list") {
  return projectPoint(aisle.x1, y, bounds, mode);
}

function projectPoint(x: number, y: number, bounds: MapBounds, mode: "3d" | "plan" | "list") {
  const flatX = sx(x, bounds);
  const flatY = sy(y, bounds);
  if (mode !== "3d") return { x: flatX, y: flatY };
  const centerX = 500;
  const baseY = 326;
  return {
    x: centerX + (flatX - centerX) * .82 + (flatY - baseY) * .32,
    y: 116 + (flatY - 70) * .72 - (flatX - centerX) * .08
  };
}

function drawTruckIcon(x: number, y: number, index: number) {
  const red = index % 3 === 0;
  const cab = red ? "#dc2626" : "#facc15";
  const trailer = red ? "#f87171" : "#fde68a";
  return (
    <g transform={`translate(${x} ${y})`} className="dock-truck-icon">
      <path d="M0 8 L30 8 L36 15 L36 25 L0 25 Z" fill={trailer} stroke="#334155" />
      <path d="M30 12 L42 12 L48 18 L48 25 L36 25 L36 15 Z" fill={cab} stroke="#334155" />
      <path d="M35 14 L42 18 L35 18 Z" fill="#dbeafe" stroke="#334155" />
      <circle cx="9" cy="27" r="4" fill="#111827" />
      <circle cx="37" cy="27" r="4" fill="#111827" />
      <circle cx="9" cy="27" r="1.5" fill="#e5e7eb" />
      <circle cx="37" cy="27" r="1.5" fill="#e5e7eb" />
    </g>
  );
}

function shortCellLabel(cell: TopologyCell) {
  const side = cell.side_code === "LEFT" ? "L" : cell.side_code === "RIGHT" ? "R" : "C";
  return `${String(cell.bay_no || 0).padStart(2, "0")}${side}`;
}

function svgPointFromEvent(event: PointerEvent<SVGSVGElement>, view: { zoom: number; panX: number; panY: number }): SvgPoint {
  const svg = event.currentTarget;
  const matrix = svg.getScreenCTM();
  if (matrix) {
    const point = svg.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    const svgPoint = point.matrixTransform(matrix.inverse());
    return {
      x: (svgPoint.x - view.panX) / view.zoom,
      y: (svgPoint.y - view.panY) / view.zoom
    };
  }
  const rect = svg.getBoundingClientRect();
  const scale = 1000 / Math.max(1, rect.width);
  return {
    x: ((event.clientX - rect.left) * scale - view.panX) / view.zoom,
    y: ((event.clientY - rect.top) * scale - view.panY) / view.zoom
  };
}

function normalizeRect(a: SvgPoint, b: SvgPoint): SvgSelectionRect {
  return {
    x1: Math.min(a.x, b.x),
    y1: Math.min(a.y, b.y),
    x2: Math.max(a.x, b.x),
    y2: Math.max(a.y, b.y)
  };
}

function mapBounds(cells: TopologyCell[], aisles: TopologyAisle[]): MapBounds {
  const xs = [...cells.map((cell) => cell.x), ...aisles.flatMap((aisle) => [aisle.x1, aisle.x2])];
  const ys = [...cells.map((cell) => cell.y), ...aisles.flatMap((aisle) => [aisle.y1, aisle.y2])];
  return {
    minX: Math.min(...xs) - 4,
    maxX: Math.max(...xs) + 10,
    minY: Math.min(...ys) - 4,
    maxY: Math.max(...ys) + 4
  };
}

function sx(x: number, bounds: { minX: number; maxX: number }) {
  return 70 + (x - bounds.minX) / Math.max(1, bounds.maxX - bounds.minX) * 760;
}

function sy(y: number, bounds: { minY: number; maxY: number }) {
  return 70 + (y - bounds.minY) / Math.max(1, bounds.maxY - bounds.minY) * 520;
}
