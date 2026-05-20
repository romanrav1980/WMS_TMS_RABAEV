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

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8088";
const API_BASIC_AUTH = import.meta.env.VITE_ADMIN_BASIC_AUTH || "admin:admin123";

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
  const [map, setMap] = useState<TopologyMap>(() => demoTopologyMap());
  const [apiState, setApiState] = useState<"demo" | "api" | "saving">("demo");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [rightTab, setRightTab] = useState<"general" | "params" | "stats">("general");
  const [mapMode, setMapMode] = useState<"3d" | "plan" | "list">("3d");
  const [view, setView] = useState({ zoom: 1, panX: 0, panY: 0 });
  const [drag, setDrag] = useState<{ id: number; startX: number; startY: number; originX: number; originY: number; bounds: MapBounds } | null>(null);
  const [panDrag, setPanDrag] = useState<{ startX: number; startY: number; originX: number; originY: number } | null>(null);
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
  const [generator, setGenerator] = useState({
    aisle_count: 6,
    bays_per_aisle: 18,
    levels: 1,
    create_both_sides: 1
  });

  useEffect(() => {
    loadInitialTopology().then((loaded) => {
      if (loaded) {
        setMap(loaded);
        setApiState("api");
      }
    });
  }, []);

  useEffect(() => {
    if (selectedId === null && map.cells.length) {
      setSelectedId(map.cells[0].topology_cell_id);
    }
  }, [map.cells, selectedId]);

  const selectedCell = map.cells.find((cell) => cell.topology_cell_id === selectedId) || null;
  const activeRoute = map.routes[0] || null;
  const routeByCell = useMemo(() => {
    const result = new Map<number, PickRouteCell>();
    map.route_cells.forEach((routeCell) => {
      if (routeCell.topology_cell_id) result.set(routeCell.topology_cell_id, routeCell);
    });
    return result;
  }, [map.route_cells]);
  const stats = useMemo(() => topologyStats(map), [map]);
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

  function toggleAisle(aisleCode: string) {
    setSelectedAisles((current) => current.includes(aisleCode)
      ? current.filter((code) => code !== aisleCode)
      : [...current, aisleCode].sort());
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
        if (loaded) setMap(loaded);
        setApiState("api");
        return;
      }
    } catch {
      // Demo fallback keeps the page useful while the Oracle migration is not applied.
    }
    setMap(local);
    setApiState("demo");
  }

  async function handleBuildRoute() {
    const route = buildLocalZRoute(map, selectedAisles);
    setMap(route);
    setApiState((current) => current === "api" ? "saving" : current);
    try {
      const response = await apiFetch(`${API_BASE}/api/admin/pick-routes/build`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topology_id: map.topology.topology_id,
          ware_id: map.topology.ware_id,
          route_code: "CASE-Z-MAIN",
          route_name: "Основной Z-обход отбора",
          route_pattern: "Z",
          aisle_codes: selectedAisles,
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
      await apiFetch(`${API_BASE}/api/admin/warehouse-topologies/${map.topology.topology_id}/generate-gates`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gate_count: 10, gate_kind: "SHIPPING", overwrite_existing: 0 })
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

  function moveSelected(dx: number, dy: number) {
    if (!selectedId) return;
    updateCellPosition(selectedId, dx, dy, true);
  }

  function updateSelectedCell(field: keyof TopologyCell, value: string | number) {
    if (!selectedId) return;
    setMap((current) => ({
      ...current,
      cells: current.cells.map((cell) => cell.topology_cell_id === selectedId ? { ...cell, [field]: value } : cell)
    }));
    markDirty(selectedId);
  }

  function updateCellPosition(id: number, dx: number, dy: number, relative: boolean) {
    setMap((current) => ({
      ...current,
      cells: current.cells.map((cell) => cell.topology_cell_id === id
        ? {
          ...cell,
          x: Number((relative ? cell.x + dx : dx).toFixed(2)),
          y: Number((relative ? cell.y + dy : dy).toFixed(2))
        }
        : cell)
    }));
    markDirty(id);
  }

  function markDirty(id: number) {
    setDirtyCells((current) => {
      const next = new Set(current);
      next.add(id);
      return next;
    });
  }

  function handleCellPointerDown(event: PointerEvent<SVGGElement>, cell: TopologyCell, bounds: MapBounds) {
    event.preventDefault();
    event.stopPropagation();
    setSelectedId(cell.topology_cell_id);
    setDrag({ id: cell.topology_cell_id, startX: event.clientX, startY: event.clientY, originX: cell.x, originY: cell.y, bounds });
  }

  function handleMapPointerMove(event: PointerEvent<SVGSVGElement>) {
    if (drag) {
      const scaleX = 760 / Math.max(1, drag.bounds.maxX - drag.bounds.minX) * view.zoom;
      const scaleY = 520 / Math.max(1, drag.bounds.maxY - drag.bounds.minY) * view.zoom;
      const nextX = drag.originX + (event.clientX - drag.startX) / scaleX;
      const nextY = drag.originY + (event.clientY - drag.startY) / scaleY;
      updateCellPosition(drag.id, nextX, nextY, false);
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
    setPanDrag({ startX: event.clientX, startY: event.clientY, originX: view.panX, originY: view.panY });
  }

  function handleMapPointerUp() {
    setDrag(null);
    setPanDrag(null);
  }

  return (
    <div className="topology-admin">
      <aside className="topology-nav">
        <div className="topology-nav-brand"><b>W</b><span>Управление топологией склада</span></div>
        <button onClick={onBack}>⌂ Обзор</button>
        <small>Топология</small>
        {["Склад", "Аллеи", "Ячейки", "Ворота", "Зоны", "Оборудование", "Типы ячеек"].map((item, index) => (
          <button key={item} className={index === 0 ? "active" : ""}>{item}</button>
        ))}
        <small>Аналитика</small>
        <button>Загрузка</button>
        <button>Емкость</button>
        <button>Контроль</button>
        <small>Настройки</small>
        <button>Справочники</button>
        <button>Правила</button>
        <button>Параметры</button>
        <em>Версия 1.0.0<br />© WMS</em>
      </aside>

      <main className="topology-shell">
        <header className="topology-topbar">
          <div className="topology-title">
            <h1>Управление топологией склада</h1>
            <span>{topologyStatusText(map.topology.status)}</span>
          </div>
          <label className="topology-warehouse-select">
            <span>Склад</span>
            <select value={map.topology.ware_id} disabled>
              <option value={map.topology.ware_id}>{map.topology.ware_name || "Основной склад"}</option>
            </select>
          </label>
          <div className="topology-actions">
            <button>Импорт</button>
            <button>Экспорт</button>
            <button className="primary" onClick={handleGenerate}>+ Добавить</button>
            <button onClick={handleValidate}>Проверить</button>
            <button onClick={handlePublishTopology}>Опубликовать</button>
            <span className={`topology-status ${map.topology.status.toLowerCase()}`}>{map.topology.status}</span>
            <span className="api-pill">{apiState === "api" ? "API" : apiState === "saving" ? "Сохранение" : "Demo"}</span>
          </div>
        </header>

        <section className="topology-layout">
          <aside className="topology-left">
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
            <label className="topology-check"><input type="checkbox" checked={generator.create_both_sides === 1} onChange={(event) => setGenerator((current) => ({ ...current, create_both_sides: event.target.checked ? 1 : 0 }))} /> две стороны прохода</label>
          </section>

          <section>
            <h3>Участок обхода</h3>
            <div className="aisle-tags">
              {map.aisles.filter((aisle) => aisle.aisle_kind === "PICK_AISLE").map((aisle) => (
                <button key={aisle.aisle_code} className={selectedAisles.includes(aisle.aisle_code) ? "active" : ""} onClick={() => toggleAisle(aisle.aisle_code)}>
                  {aisle.aisle_code}
                </button>
              ))}
            </div>
            <button className="wide-action" onClick={handleBuildRoute}>Построить Z-обход</button>
          </section>

          <section>
            <h3>Ворота и расстояния</h3>
            <p>Матрица расстояний влияет на скорость перемещения к отгрузке и от приемки к хранению.</p>
            <button className="wide-action secondary-action" onClick={handleRecalculateDistances}>Пересчитать до ворот</button>
          </section>
        </aside>

        <main className="topology-map-panel">
          <div className="topology-map-title">
            <div>
              <b>Карта ячеек отбора</b>
              <span>3D вид · топология редактируется отдельно от ежедневных волн</span>
            </div>
            <div className="topology-view-tabs">
              <button className={mapMode === "3d" ? "active" : ""} onClick={() => setMapMode("3d")}>3D Вид</button>
              <button className={mapMode === "plan" ? "active" : ""} onClick={() => setMapMode("plan")}>2D План</button>
              <button className={mapMode === "list" ? "active" : ""} onClick={() => setMapMode("list")}>Список</button>
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
            <div className="topology-map-wrap">
              <div className="topology-map-controls">
                <button onClick={() => setView((current) => ({ ...current, zoom: Math.min(2.2, Number((current.zoom + 0.15).toFixed(2))) }))}>+</button>
                <button onClick={() => setView((current) => ({ ...current, zoom: Math.max(0.65, Number((current.zoom - 0.15).toFixed(2))) }))}>-</button>
                <button onClick={() => setView({ zoom: 1, panX: 0, panY: 0 })}>Сброс</button>
                <button onClick={() => setView((current) => ({ ...current, panX: current.panX - 30 }))}>←</button>
                <button onClick={() => setView((current) => ({ ...current, panX: current.panX + 30 }))}>→</button>
                <button onClick={() => setView((current) => ({ ...current, panY: current.panY - 30 }))}>↑</button>
                <button onClick={() => setView((current) => ({ ...current, panY: current.panY + 30 }))}>↓</button>
              </div>
              <TopologySvg
                map={map}
                routeByCell={routeByCell}
                selectedId={selectedId}
                layers={layers}
                mode={mapMode}
                view={view}
                isPanning={Boolean(panDrag)}
                onSelect={setSelectedId}
                onCellPointerDown={handleCellPointerDown}
                onPointerDown={handleMapPointerDown}
                onPointerMove={handleMapPointerMove}
                onPointerUp={handleMapPointerUp}
              />
            </div>
          )}
        </main>

          <aside className="topology-right">
          <section>
            <div className="inspector-heading"><h3>{selectedCell?.aisle_code || "Аллея A03"}</h3><button onClick={() => setSelectedId(null)}>×</button></div>
            <div className="inspector-tabs">
              <button className={rightTab === "general" ? "active" : ""} onClick={() => setRightTab("general")}>Общее</button>
              <button className={rightTab === "params" ? "active" : ""} onClick={() => setRightTab("params")}>Параметры</button>
              <button className={rightTab === "stats" ? "active" : ""} onClick={() => setRightTab("stats")}>Статистика</button>
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
                    <button className="save-cell-button" disabled={!dirtyCells.has(selectedCell.topology_cell_id)} onClick={handleSaveSelectedCell}>Сохранить ячейку</button>
                  </>
                )}
                {rightTab === "params" && (
                  <>
                    <InspectorField label="X" value={selectedCell.x} onChange={(value) => updateSelectedCell("x", Number(value))} />
                    <InspectorField label="Y" value={selectedCell.y} onChange={(value) => updateSelectedCell("y", Number(value))} />
                    <label className="inspector-field"><span>Сторона</span><select value={selectedCell.side_code} onChange={(event) => updateSelectedCell("side_code", event.target.value)}><option>LEFT</option><option>RIGHT</option><option>CENTER</option></select></label>
                    <label className="inspector-field"><span>Тип</span><select value={selectedCell.cell_kind} onChange={(event) => updateSelectedCell("cell_kind", event.target.value)}><option>PICK_FACE</option><option>DYNAMIC_PICK_FACE</option><option>STORAGE</option><option>STAGING</option></select></label>
                    <div className="nudge-grid">
                      <button onClick={() => moveSelected(0, -0.4)}>↑</button>
                      <button onClick={() => moveSelected(-0.4, 0)}>←</button>
                      <button onClick={() => moveSelected(0.4, 0)}>→</button>
                      <button onClick={() => moveSelected(0, 0.4)}>↓</button>
                    </div>
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
            <button className="save-cell-button" onClick={handleValidate}>Проверить топологию</button>
          </section>

          <section>
            <h3>Порядок обхода</h3>
            {activeRoute ? (
              <div className="route-summary">
                <b>{activeRoute.route_code}</b>
                <span>{activeRoute.route_pattern || "Z"} · {activeRoute.status || "DRAFT"}</span>
                <span>{map.route_cells.length} ячеек в последовательности</span>
              </div>
            ) : <p>Постройте Z-обход для выбранных аллей.</p>}
            <div className="route-list">
              {map.route_cells.slice(0, 12).map((routeCell) => (
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
    <label className="number-field">
      <span>{label}</span>
      <input type="number" min={min} max={max} value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </label>
  );
}

function LayerToggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: () => void }) {
  return <label className="topology-check"><input type="checkbox" checked={checked} onChange={onChange} /> {label}</label>;
}

function InspectorField({ label, value, onChange }: { label: string; value: number; onChange: (value: string) => void }) {
  return <label className="inspector-field"><span>{label}</span><input type="number" value={value} step="0.1" onChange={(event) => onChange(event.target.value)} /></label>;
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

function TopologySvg({ map, routeByCell, selectedId, layers, mode, view, isPanning, onSelect, onCellPointerDown, onPointerDown, onPointerMove, onPointerUp }: {
  map: TopologyMap;
  routeByCell: Map<number, PickRouteCell>;
  selectedId: number | null;
  layers: MapLayerState;
  mode: "3d" | "plan" | "list";
  view: { zoom: number; panX: number; panY: number };
  isPanning: boolean;
  onSelect: (id: number) => void;
  onCellPointerDown: (event: PointerEvent<SVGGElement>, cell: TopologyCell, bounds: MapBounds) => void;
  onPointerDown: (event: PointerEvent<SVGSVGElement>) => void;
  onPointerMove: (event: PointerEvent<SVGSVGElement>) => void;
  onPointerUp: () => void;
}) {
  const bounds = mapBounds(map.cells, map.aisles);
  const routeCells = map.route_cells
    .map((routeCell) => {
      const cell = map.cells.find((item) => item.topology_cell_id === routeCell.topology_cell_id);
      return cell ? { routeCell, cell } : null;
    })
    .filter(Boolean) as Array<{ routeCell: PickRouteCell; cell: TopologyCell }>;
  const path = routeCells.map(({ cell }, index) => `${index === 0 ? "M" : "L"} ${sx(cell.x, bounds)} ${sy(cell.y, bounds)}`).join(" ");

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
      style={{ cursor: isPanning ? "grabbing" : "grab" }}
    >
      <defs>
        <pattern id="topology-grid" width="32" height="32" patternUnits="userSpaceOnUse">
          <path d="M 32 0 L 0 0 0 32" fill="none" stroke="#dbe6f3" strokeWidth="1" />
        </pattern>
        <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="6" stdDeviation="5" floodColor="#1f2f48" floodOpacity=".18" />
        </filter>
      </defs>
      <rect width="1000" height="650" fill="#f8fbff" />
      <g transform={`translate(${view.panX} ${view.panY}) scale(${view.zoom})`}>
        {layers.zones && (
          <>
            <rect x="44" y="54" width="858" height="480" rx="4" fill="#eef5fb" stroke="#b6c5d5" />
            {mode === "3d" && <path d="M44 54 L164 18 L938 88 L902 534 Z" fill="#f4f8fc" stroke="#d1dbe7" opacity=".72" />}
            {mode === "3d" && <path d="M44 534 L902 534 L938 88 L164 18" fill="none" stroke="#94a3b8" strokeWidth="2" opacity=".55" />}
          </>
        )}

        {layers.gates && map.gates.slice(0, 10).map((gate) => (
          <g key={gate.topology_gate_id}>
            <rect x={sx(gate.x, bounds) - 22} y="490" width="48" height="36" rx="3" fill={gate.gate_kind === "RECEIVING" ? "#0f766e" : "#27364a"} stroke="#0f172a" />
            <rect x={sx(gate.x, bounds) - 8} y="526" width="8" height="15" fill="#fbbf24" />
            {layers.labels && <text x={sx(gate.x, bounds) + 2} y="484" className="gate-label">{gate.gate_code}</text>}
          </g>
        ))}

        {layers.aisles && map.aisles.map((aisle) => {
          const x1 = sx(aisle.x1, bounds);
          const y1 = sy(aisle.y1, bounds);
          const x2 = sx(aisle.x2, bounds);
          const y2 = sy(aisle.y2, bounds);
          return (
            <g key={aisle.topology_aisle_id}>
              <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={Number(aisle.aisle_code.replace(/\D/g, "")) <= 5 ? "#86efac" : "#93c5fd"} strokeWidth={aisle.aisle_kind === "PICK_AISLE" ? 44 : 28} strokeLinecap="round" opacity=".38" />
              <line x1={x1 - 14} y1={y1} x2={x2 - 14} y2={y2} stroke="#1d4ed8" strokeWidth="3" opacity=".65" />
              <line x1={x1 + 14} y1={y1} x2={x2 + 14} y2={y2} stroke="#1d4ed8" strokeWidth="3" opacity=".65" />
              <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#2563d8" strokeWidth="2.4" strokeDasharray="9 8" strokeLinecap="round" opacity=".72" />
              {layers.labels && <text x={x1 - 22} y={y1 - 12} className="aisle-label">{aisle.aisle_code}</text>}
              {layers.labels && <text x={x2 + 22} y={y2 + 18} className="aisle-label">{aisle.aisle_code}</text>}
            </g>
          );
        })}

        {layers.route && path && <path d={path} fill="none" stroke="#ef3b82" strokeWidth="4" strokeDasharray="10 8" strokeLinecap="round" strokeLinejoin="round" opacity=".72" />}

        {layers.distances && selectedId && drawDistanceLines(map, selectedId, bounds)}

        {layers.cells && map.cells.filter((cell) => cell.active === 1).map((cell) => {
          const x = sx(cell.x, bounds);
          const y = sy(cell.y, bounds);
          const routeCell = routeByCell.get(cell.topology_cell_id);
          const selected = selectedId === cell.topology_cell_id;
          return (
            <g
              key={cell.topology_cell_id}
              className="topology-cell-node"
              onClick={() => onSelect(cell.topology_cell_id)}
              onPointerDown={(event) => onCellPointerDown(event, cell, bounds)}
              filter={selected ? "url(#soft-shadow)" : undefined}
            >
              <rect
                x={x - 10}
                y={y - 8}
                width="20"
                height="16"
                rx="3"
                fill="#d9b879"
                stroke={selected ? "#f59e0b" : "#37506d"}
                strokeWidth={selected ? 3 : 1}
              />
              <rect
                x={x - 10}
                y={y - 8}
                width="20"
                height="5"
                rx="2"
                fill={cell.side_code === "LEFT" ? "#58b76b" : cell.side_code === "RIGHT" ? "#4d86d9" : "#94a3b8"}
                strokeWidth="0"
              />
              {layers.labels && routeCell && routeCell.pick_sequence % 6 === 1 && (
                <>
                  <circle cx={x + 13} cy={y - 13} r="9" fill="#fff" stroke="#ef3b82" strokeWidth="2" />
                  <text x={x + 13} y={y - 10} className="route-sequence">{routeCell.pick_sequence}</text>
                </>
              )}
            </g>
          );
        })}

        {layers.gates && <g className="topology-dock-zone">
          <rect x="812" y="74" width="108" height="390" rx="8" fill="#e0f2fe" stroke="#38bdf8" strokeDasharray="8 6" />
          {layers.labels && <text x="866" y="62">Зона накопления / ворота</text>}
        </g>}
      </g>
    </svg>
  );
}

function topologyStats(map: TopologyMap) {
  return {
    aisles: map.aisles.filter((aisle) => aisle.aisle_kind === "PICK_AISLE").length,
    pickFaces: map.cells.filter((cell) => cell.cell_kind === "PICK_FACE" && cell.active === 1).length,
    dynamic: map.cells.filter((cell) => cell.cell_kind === "DYNAMIC_PICK_FACE" && cell.active === 1).length,
    routeCells: map.route_cells.length,
    gates: map.gates.filter((gate) => gate.active === 1).length
  };
}

async function loadInitialTopology(): Promise<TopologyMap | null> {
  try {
    const response = await apiFetch(`${API_BASE}/api/admin/warehouse-topologies`, { cache: "no-store" });
    if (!response.ok) return null;
    const topologies = await response.json() as Topology[];
    const topology = topologies.find((item) => item.status === "PUBLISHED") || topologies[0];
    if (!topology) return null;
    return loadTopologyMap(topology.topology_id);
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
  return buildLocalZRoute(generateLocalTopology(topology, {
    aisle_count: 6,
    bays_per_aisle: 18,
    levels: 1,
    create_both_sides: 1
  }), ["A01", "A02", "A03"]);
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

function buildLocalZRoute(map: TopologyMap, aisleCodes: string[]): TopologyMap {
  const sideRank: Record<string, number> = { LEFT: 0, RIGHT: 1, CENTER: 9 };
  const selected = map.cells
    .filter((cell) => cell.active === 1 && cell.cell_kind.includes("PICK_FACE") && aisleCodes.includes(cell.aisle_code || ""))
    .sort((a, b) => String(a.aisle_code).localeCompare(String(b.aisle_code))
      || Number(a.bay_no || 0) - Number(b.bay_no || 0)
      || sideRank[a.side_code] - sideRank[b.side_code]);
  const routeCells = selected.map((cell, index) => ({
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
      route_code: "CASE-Z-MAIN",
      route_name: "Основной Z-обход отбора",
      route_pattern: "Z",
      status: "DRAFT",
      cell_count: routeCells.length
    }],
    route_cells: routeCells
  };
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
    y: 34,
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

function drawDistanceLines(map: TopologyMap, selectedId: number, bounds: MapBounds) {
  const cell = map.cells.find((item) => item.topology_cell_id === selectedId);
  if (!cell) return null;
  return map.distances
    .filter((distance) => distance.topology_cell_id === selectedId)
    .sort((a, b) => a.distance_m - b.distance_m)
    .slice(0, 3)
    .map((distance) => {
      const gate = map.gates.find((item) => item.topology_gate_id === distance.topology_gate_id);
      if (!gate) return null;
      return <line key={distance.cell_gate_distance_id} x1={sx(cell.x, bounds)} y1={sy(cell.y, bounds)} x2={sx(gate.x, bounds)} y2="508" stroke="#0f766e" strokeWidth="2" strokeDasharray="6 6" opacity=".56" />;
    });
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
