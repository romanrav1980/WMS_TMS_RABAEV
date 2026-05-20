import { useEffect, useMemo, useState } from "react";

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
  cells: TopologyCell[];
  routes: PickRoute[];
  route_cells: PickRouteCell[];
};

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export function TopologyAdminPage({ onBack }: { onBack: () => void }) {
  const [map, setMap] = useState<TopologyMap>(() => demoTopologyMap());
  const [apiState, setApiState] = useState<"demo" | "api" | "saving">("demo");
  const [selectedId, setSelectedId] = useState<number | null>(null);
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

  function toggleAisle(aisleCode: string) {
    setSelectedAisles((current) => current.includes(aisleCode)
      ? current.filter((code) => code !== aisleCode)
      : [...current, aisleCode].sort());
  }

  async function handleGenerate() {
    setApiState((current) => current === "api" ? "saving" : current);
    const local = generateLocalTopology(map.topology, generator);
    try {
      const response = await fetch(`${API_BASE}/api/admin/warehouse-topologies/${map.topology.topology_id}/generate-cells`, {
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
        const loaded = await loadTopologyMap(map.topology.topology_id);
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
      const response = await fetch(`${API_BASE}/api/admin/pick-routes/build`, {
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

  function moveSelected(dx: number, dy: number) {
    if (!selectedId) return;
    setMap((current) => ({
      ...current,
      cells: current.cells.map((cell) => cell.topology_cell_id === selectedId
        ? { ...cell, x: Number((cell.x + dx).toFixed(2)), y: Number((cell.y + dy).toFixed(2)) }
        : cell)
    }));
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
            <span>{map.topology.status === "PUBLISHED" ? "Опубликованная мастер-версия" : "Черновик мастер-данных"}</span>
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
            </div>
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
        </aside>

        <main className="topology-map-panel">
          <div className="topology-map-title">
            <div>
              <b>Карта ячеек отбора</b>
              <span>3D вид · топология редактируется отдельно от ежедневных волн</span>
            </div>
            <div className="map-legend">
              <span><i className="cell-left" /> Левая сторона</span>
              <span><i className="cell-right" /> Правая сторона</span>
              <span><i className="cell-route" /> Порядок обхода</span>
            </div>
          </div>
          <TopologySvg map={map} routeByCell={routeByCell} selectedId={selectedId} onSelect={setSelectedId} />
        </main>

          <aside className="topology-right">
          <section>
            <div className="inspector-heading"><h3>{selectedCell?.aisle_code || "Аллея A03"}</h3><button onClick={() => setSelectedId(null)}>×</button></div>
            <div className="inspector-tabs"><button className="active">Общее</button><button>Параметры</button><button>Статистика</button></div>
            {selectedCell ? (
              <div className="cell-inspector">
                <b>{selectedCell.cell_code}</b>
                <span>{selectedCell.aisle_code} · {selectedCell.side_code} · bay {selectedCell.bay_no}</span>
                <span>Тип: {selectedCell.cell_kind}</span>
                <span>Координаты: {selectedCell.x.toFixed(1)} / {selectedCell.y.toFixed(1)}</span>
                <span>Емкость: {selectedCell.max_volume_m3 || 0} м³ · {selectedCell.max_weight_kg || 0} кг</span>
                <div className="nudge-grid">
                  <button onClick={() => moveSelected(0, -0.4)}>↑</button>
                  <button onClick={() => moveSelected(-0.4, 0)}>←</button>
                  <button onClick={() => moveSelected(0.4, 0)}>→</button>
                  <button onClick={() => moveSelected(0, 0.4)}>↓</button>
                </div>
              </div>
            ) : <p>Выберите ячейку на карте, чтобы увидеть сторону прохода, координаты и участие в маршруте.</p>}
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

function TopologySvg({ map, routeByCell, selectedId, onSelect }: {
  map: TopologyMap;
  routeByCell: Map<number, PickRouteCell>;
  selectedId: number | null;
  onSelect: (id: number) => void;
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
    <svg className="topology-svg" viewBox="0 0 1000 650" role="img" aria-label="Карта топологии склада">
      <defs>
        <pattern id="topology-grid" width="32" height="32" patternUnits="userSpaceOnUse">
          <path d="M 32 0 L 0 0 0 32" fill="none" stroke="#dbe6f3" strokeWidth="1" />
        </pattern>
        <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="6" stdDeviation="5" floodColor="#1f2f48" floodOpacity=".18" />
        </filter>
      </defs>
      <rect width="1000" height="650" fill="#f8fbff" />
      <rect x="44" y="54" width="858" height="480" rx="4" fill="#eef5fb" stroke="#b6c5d5" />
      <path d="M44 54 L164 18 L938 88 L902 534 Z" fill="#f4f8fc" stroke="#d1dbe7" opacity=".72" />
      <path d="M44 534 L902 534 L938 88 L164 18" fill="none" stroke="#94a3b8" strokeWidth="2" opacity=".55" />
      <rect x="66" y="468" width="78" height="44" fill="#dbe7f2" stroke="#94a3b8" />
      <text x="105" y="494" className="gate-label">G01</text>
      {[1, 2, 3, 4, 5, 6, 7, 8].map((gate) => (
        <g key={gate}>
          <rect x={70 + gate * 82} y="490" width="48" height="36" rx="3" fill="#27364a" stroke="#0f172a" />
          <rect x={84 + gate * 82} y="526" width="8" height="15" fill="#fbbf24" />
          <text x={94 + gate * 82} y="484" className="gate-label">G{String(gate + 1).padStart(2, "0")}</text>
        </g>
      ))}

      {map.aisles.map((aisle) => {
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
            <text x={x1 - 22} y={y1 - 12} className="aisle-label">{aisle.aisle_code}</text>
            <text x={x2 + 22} y={y2 + 18} className="aisle-label">{aisle.aisle_code}</text>
          </g>
        );
      })}

      {path && <path d={path} fill="none" stroke="#ef3b82" strokeWidth="4" strokeDasharray="10 8" strokeLinecap="round" strokeLinejoin="round" opacity=".72" />}

      {map.cells.filter((cell) => cell.active === 1).map((cell) => {
        const x = sx(cell.x, bounds);
        const y = sy(cell.y, bounds);
        const routeCell = routeByCell.get(cell.topology_cell_id);
        const selected = selectedId === cell.topology_cell_id;
        return (
          <g key={cell.topology_cell_id} className="topology-cell-node" onClick={() => onSelect(cell.topology_cell_id)} filter={selected ? "url(#soft-shadow)" : undefined}>
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
              stroke={selected ? "#f59e0b" : "#102033"}
              strokeWidth="0"
            />
            {routeCell && routeCell.pick_sequence % 6 === 1 && (
              <>
                <circle cx={x + 13} cy={y - 13} r="9" fill="#fff" stroke="#ef3b82" strokeWidth="2" />
                <text x={x + 13} y={y - 10} className="route-sequence">{routeCell.pick_sequence}</text>
              </>
            )}
          </g>
        );
      })}

      <g className="topology-dock-zone">
        <rect x="812" y="74" width="108" height="390" rx="8" fill="#e0f2fe" stroke="#38bdf8" strokeDasharray="8 6" />
        <text x="866" y="62">Зона накопления / ворота</text>
        {[0, 1, 2, 3].map((index) => (
          <g key={index}>
            <rect x="840" y={104 + index * 82} width="54" height="34" rx="3" fill="#fff" stroke="#64748b" />
            <text x="867" y={126}>G{String(index + 1).padStart(2, "0")}</text>
          </g>
        ))}
      </g>
    </svg>
  );
}

function topologyStats(map: TopologyMap) {
  return {
    aisles: map.aisles.filter((aisle) => aisle.aisle_kind === "PICK_AISLE").length,
    pickFaces: map.cells.filter((cell) => cell.cell_kind === "PICK_FACE" && cell.active === 1).length,
    dynamic: map.cells.filter((cell) => cell.cell_kind === "DYNAMIC_PICK_FACE" && cell.active === 1).length,
    routeCells: map.route_cells.length
  };
}

async function loadInitialTopology(): Promise<TopologyMap | null> {
  try {
    const response = await fetch(`${API_BASE}/api/admin/warehouse-topologies`, { cache: "no-store" });
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
  const response = await fetch(`${API_BASE}/api/admin/warehouse-topologies/${topologyId}/map`, { cache: "no-store" });
  if (!response.ok) return null;
  return normalizeMap(await response.json());
}

function normalizeMap(raw: TopologyMap): TopologyMap {
  return {
    topology: normalizeKeys(raw.topology) as Topology,
    aisles: (raw.aisles || []).map((item) => normalizeKeys(item) as TopologyAisle),
    cells: (raw.cells || []).map((item) => normalizeKeys(item) as TopologyCell),
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
  return { topology: { ...topology, cell_count: cells.length, aisle_count: aisles.length }, aisles, cells, routes: [], route_cells: [] };
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

function mapBounds(cells: TopologyCell[], aisles: TopologyAisle[]) {
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
