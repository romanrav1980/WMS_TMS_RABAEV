import { useEffect, useMemo, useRef, useState } from "react";
import type { Collision, DetailSelection, DockPallet, PickFaceFill, ReplenishmentTask, ResourceState, WarehouseLayout } from "../types";
import { cellById, eventLocation } from "../replay/reducer";
import { collisionTitle } from "../replay/reducer";

type SceneProps = {
  layout: WarehouseLayout;
  resources: ResourceState[];
  collisions: Collision[];
  pickFaceFill: Record<string, PickFaceFill>;
  dockPallets: Record<string, DockPallet[]>;
  tasks: ReplenishmentTask[];
  minute: number;
  selectedWaveId?: string;
  onSelect: (selection: DetailSelection) => void;
};

const colors = {
  green: "#19a765",
  blue: "#2563d8",
  amber: "#f59e0b",
  red: "#ee3e37",
  gray: "#94a3b8",
  rack: "#2f4159",
  pallet: "#d6a35e",
  floor: "#e8eef5"
};

export function WarehouseScene({ layout, resources, collisions, pickFaceFill, dockPallets, tasks, minute, selectedWaveId, onSelect }: SceneProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const hitRegions = useRef<Array<{ x: number; y: number; r: number; selection: DetailSelection }>>([]);
  const dragState = useRef<{ active: boolean; x: number; y: number; moved: boolean }>({ active: false, x: 0, y: 0, moved: false });
  const [navigation, setNavigation] = useState({ zoom: 1, panX: 0, panY: 0 });
  const [frameSize, setFrameSize] = useState({ width: 1090, height: 670 });
  const [hoverPickFace, setHoverPickFace] = useState<{ x: number; y: number; cellId: string; fill?: PickFaceFill } | null>(null);
  const visibleResources = useMemo(
    () => resources.filter((resource) => !selectedWaveId || resource.waveId === selectedWaveId || !resource.waveId),
    [resources, selectedWaveId]
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    const rect = canvas.getBoundingClientRect();
    const scale = window.devicePixelRatio || 1;
    canvas.width = Math.floor(rect.width * scale);
    canvas.height = Math.floor(rect.height * scale);
    setFrameSize({ width: rect.width, height: rect.height });
    context.setTransform(scale, 0, 0, scale, 0, 0);
    drawScene(context, rect.width, rect.height, layout, visibleResources, collisions, pickFaceFill, dockPallets, hitRegions.current, navigation, minute);
  }, [layout, visibleResources, collisions, pickFaceFill, dockPallets, navigation, minute]);

  const zoomBy = (delta: number) => {
    setNavigation((current) => ({ ...current, zoom: clamp(current.zoom + delta, .65, 2.4) }));
  };

  return (
    <div className="scene-frame">
      <canvas
        ref={canvasRef}
        onMouseDown={(event) => {
          dragState.current = { active: true, x: event.clientX, y: event.clientY, moved: false };
        }}
        onMouseMove={(event) => {
          const drag = dragState.current;
          const rect = event.currentTarget.getBoundingClientRect();
          const x = event.clientX - rect.left;
          const y = event.clientY - rect.top;
          if (drag.active) {
            const dx = event.clientX - drag.x;
            const dy = event.clientY - drag.y;
            if (Math.abs(dx) + Math.abs(dy) > 2) drag.moved = true;
            drag.x = event.clientX;
            drag.y = event.clientY;
            setNavigation((current) => ({ ...current, panX: current.panX + dx, panY: current.panY + dy }));
            return;
          }
          const hit = hitRegions.current.find((region) => region.selection?.type === "pickFace" && Math.hypot(region.x - x, region.y - y) <= region.r);
          setHoverPickFace(hit?.selection?.type === "pickFace" ? { x, y, cellId: hit.selection.cellId, fill: hit.selection.fill } : null);
        }}
        onMouseUp={() => { dragState.current.active = false; }}
        onMouseLeave={() => { dragState.current.active = false; setHoverPickFace(null); }}
        onWheel={(event) => {
          event.preventDefault();
          zoomBy(event.deltaY < 0 ? .12 : -.12);
        }}
        onClick={(event) => {
          if (dragState.current.moved) {
            dragState.current.moved = false;
            return;
          }
          const rect = event.currentTarget.getBoundingClientRect();
          const x = event.clientX - rect.left;
          const y = event.clientY - rect.top;
          const hit = hitRegions.current.find((region) => Math.hypot(region.x - x, region.y - y) <= region.r);
          if (hit) onSelect(hit.selection);
        }}
      />
      {hoverPickFace && <PickFaceTooltip hover={hoverPickFace} tasks={tasks.filter((task) => task.targetCell === hoverPickFace.cellId)} />}
      <div className="scene-nav-controls" aria-label="Навигация по карте склада">
        <button type="button" title="Приблизить" onClick={() => zoomBy(.15)}>+</button>
        <button type="button" title="Отдалить" onClick={() => zoomBy(-.15)}>-</button>
        <button type="button" title="Сбросить вид" onClick={() => setNavigation({ zoom: 1, panX: 0, panY: 0 })}>Сброс</button>
      </div>
      <div className="scene-overlays">
        {visibleResources.map((resource) => (
          <button
            key={resource.id}
            type="button"
            className={`resource-badge ${resource.kind === "reachtruck" ? "machine" : ""} ${resource.statusColor}`}
            style={overlayStyle(resource.x, resource.y, resource.kind === "reachtruck" ? 3.1 : 1.7, frameSize, navigation)}
            onClick={() => onSelect({ type: "resource", resource })}
          >
            {resource.kind === "reachtruck" ? resource.id : `${resource.id} ${resource.speedRatio}%`}
            <span>{resource.status}</span>
          </button>
        ))}
        {collisions.slice(-5).map((collision) => {
          const loc = collisionLocation(layout, collision);
          return (
            <button
              key={collision.id}
              type="button"
              className={`callout ${collision.severity === "critical" ? "" : "warning"}`}
              style={overlayStyle(loc.x, loc.y, 3, frameSize, navigation)}
              onClick={() => onSelect({ type: "collision", collision })}
            >
              <b>{collisionTitle(collision.type)}</b>
              <span>{collision.locationLabel} · задержка {collision.lostMinutes} мин</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function PickFaceTooltip({ hover, tasks }: { hover: { x: number; y: number; cellId: string; fill?: PickFaceFill }; tasks: ReplenishmentTask[] }) {
  const ratio = Math.round((hover.fill?.ratio || 0) * 100);
  const openTasks = tasks.filter((task) => task.status !== "DONE");
  const hardTasks = openTasks.filter((task) => ["RELEASED", "IN_PROGRESS"].includes(task.status));
  return (
    <div className="pickface-tooltip" style={{ left: hover.x + 16, top: hover.y + 16 }}>
      <b>{hover.cellId} · заполнение {ratio}%</b>
      <span>Остаток: {Math.round(hover.fill?.qty || 0)} / {Math.round(hover.fill?.capacity || 0)} коробок</span>
      <span>Задачи пополнения: {openTasks.length || "нет"}</span>
      <span>Hard / водитель РТК: {hardTasks.length ? hardTasks.map((task) => `${task.id} ${task.status}`).join(", ") : "нет выпущенной задачи"}</span>
      {openTasks.slice(0, 3).map((task) => (
        <span key={task.id}>{task.id}: {task.reason} · {task.status} · просрочка {task.overdueMinutes} мин</span>
      ))}
      {!openTasks.length && <span>Обоснование: пополнение ещё не выпущено или адрес ждёт release-policy.</span>}
    </div>
  );
}

function drawScene(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  layout: WarehouseLayout,
  resources: ResourceState[],
  collisions: Collision[],
  pickFaceFill: Record<string, PickFaceFill>,
  dockPallets: Record<string, DockPallet[]>,
  hitRegions: Array<{ x: number; y: number; r: number; selection: DetailSelection }>,
  navigation: ViewNavigation,
  minute: number
) {
  hitRegions.length = 0;
  const view = makeView(width, height, navigation);
  const gradient = ctx.createLinearGradient(0, 0, width, height);
  gradient.addColorStop(0, "#f8fbff");
  gradient.addColorStop(.55, "#e8eef7");
  gradient.addColorStop(1, "#d6e0eb");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);

  drawFloor(ctx, view);
  drawDockStaging(ctx, view, layout, dockPallets);
  drawGates(ctx, view, layout);
  drawRacks(ctx, view, layout, pickFaceFill, hitRegions);
  drawHeatmap(ctx, view, layout, collisions);
  drawTrails(ctx, view, resources, minute);
  for (const resource of resources) {
    const p = iso(view, resource.x, resource.y, resource.kind === "reachtruck" ? .9 : .55);
    if (resource.kind === "reachtruck") drawReachtruckIcon(ctx, p.x, p.y, resourceHeading(view, resource), statusColor(resource.statusColor));
    else drawPickerIcon(ctx, p.x, p.y, statusColor(resource.statusColor));
    drawHalo(ctx, p.x, p.y, statusColor(resource.statusColor), resource.kind === "reachtruck" ? 24 : 13);
    hitRegions.push({ x: p.x, y: p.y, r: resource.kind === "reachtruck" ? 32 : 18, selection: { type: "resource", resource } });
  }
  for (const collision of collisions) {
    const loc = collisionLocation(layout, collision);
    const p = iso(view, loc.x, loc.y, 1);
    ctx.fillStyle = collision.severity === "critical" ? colors.red : colors.amber;
    ctx.beginPath();
    ctx.arc(p.x, p.y, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#fff";
    ctx.font = "900 11px Segoe UI";
    ctx.textAlign = "center";
    ctx.fillText("!", p.x, p.y + 4);
    ctx.textAlign = "left";
    hitRegions.push({ x: p.x, y: p.y, r: 16, selection: { type: "collision", collision } });
  }
}

function drawFloor(ctx: CanvasRenderingContext2D, view: View) {
  polygon(ctx, [iso(view, -10, -9), iso(view, 104, -9), iso(view, 104, 106), iso(view, -10, 106)], colors.floor, "#c9d5e2", 1);
  const crossAisles = [
    { x: 0, label: "ФРОНТАЛЬНЫЙ ПРОЕЗД", short: "FRONT" },
    { x: 45, label: "ПОЖАРНЫЙ ПРОХОД", short: "FIRE" },
    { x: 90, label: "ЗАДНИЙ ОБХОД", short: "REAR" },
  ];
  for (const cross of crossAisles) {
    polygon(ctx, [iso(view, cross.x - 1.15, -6), iso(view, cross.x + 1.15, -6), iso(view, cross.x + 1.15, 102), iso(view, cross.x - 1.15, 102)], "rgba(37,99,216,.12)", "rgba(37,99,216,.35)", 1.1);
    drawFloorLabel(ctx, view, cross.x, -7.3, cross.label, cross.short, "#1d4ed8");
    drawFloorLabel(ctx, view, cross.x, 101.3, cross.label, cross.short, "#1d4ed8");
  }
  for (let aisle = 1; aisle <= 25; aisle += 1) {
    const y = (aisle - 1) * 4;
    polygon(ctx, [iso(view, -3, y - .95), iso(view, 94, y - .95), iso(view, 94, y + .95), iso(view, -3, y + .95)], aisle % 2 ? "#f6f9fc" : "#edf3f9", "#cfdae7", .6);
    const label = iso(view, -7, y);
    ctx.fillStyle = colors.blue;
    ctx.font = "900 11px Segoe UI";
    ctx.fillText(`A${String(aisle).padStart(2, "0")}`, label.x, label.y);
  }
}

function drawGates(ctx: CanvasRenderingContext2D, view: View, layout: WarehouseLayout) {
  for (const gate of layout.gates.filter((_, index) => index % 2 === 0)) {
    const y = Number(gate.y_m || (gate.aisle - 1) * 4);
    drawBox(ctx, view, -8.2, y - 1.05, 0, 2.8, 2.1, .42, "#dbeafe", "#7fa7d6");
    drawBox(ctx, view, -9.05, y - .86, .42, .34, 1.7, 2.4, "#f8fafc", "#cbd5e1");
    const p = iso(view, -8.5, y - .9, 3.1);
    drawSign(ctx, p.x, p.y, gate.gate_id, "#2563d8", "#fff");
  }
}

function drawDockStaging(ctx: CanvasRenderingContext2D, view: View, layout: WarehouseLayout, dockPallets: Record<string, DockPallet[]>) {
  for (const gate of layout.gates.filter((_, index) => index % 2 === 0)) {
    const y = Number(gate.y_m || (gate.aisle - 1) * 4);
    const pallets = dockPallets[gate.gate_id] || [];
    const loading = pallets.find((pallet) => pallet.status === "LOADING");
    polygon(ctx, [iso(view, -7.2, y - 1.72), iso(view, 13.2, y - 1.72), iso(view, 13.2, y + 1.72), iso(view, -7.2, y + 1.72)], "rgba(34,197,94,.12)", "rgba(34,197,94,.45)", 1.1);
    const label = iso(view, -5.9, y - 1.88, .08);
    ctx.fillStyle = "rgba(21,128,61,.9)";
    ctx.font = "900 8px Segoe UI";
    ctx.fillText(`НАКОПЛЕНИЕ ${gate.gate_id}: ${pallets.length}/33`, label.x - 22, label.y);
    if (loading) drawDockTruck(ctx, view, -10.4, y, loading, pallets.length);
    pallets.slice(0, 33).forEach((pallet, index) => {
      const row = index % 2;
      const col = Math.floor(index / 2);
      const x = -6.5 + col * 1.12;
      const py = y - .92 + row * 1.22;
      drawDockPallet(ctx, view, x, py, pallet);
    });
    if (!pallets.length) {
      drawEmptyDockSlots(ctx, view, y);
    }
  }
}

function drawDockTruck(ctx: CanvasRenderingContext2D, view: View, x: number, y: number, pallet: DockPallet, palletCount: number) {
  const isTrailer = palletCount >= 33;
  const color = gateTruckColor(pallet.gateId);
  const bodyLength = isTrailer ? 4.4 : 2.65;
  drawBox(ctx, view, x, y - 1.2, .12, bodyLength, 2.38, isTrailer ? 1.36 : 1.2, color.body, color.side);
  drawBox(ctx, view, x + bodyLength - .27, y - .86, .16, .92, 1.72, .98, color.cab, "#1e293b");
  drawBox(ctx, view, x + bodyLength - .03, y - .52, .84, .42, .72, .26, "#bfdbfe", "#1e3a8a");
  drawTruckWheel(ctx, view, x + .55, y + .96);
  drawTruckWheel(ctx, view, x + bodyLength - .75, y + .96);
  drawTruckWheel(ctx, view, x + bodyLength + .12, y + .66);
  if (isTrailer) drawTruckWheel(ctx, view, x + 2.15, y + .96);
  const dockLine = iso(view, x + bodyLength + .55, y, .38);
  const gateLine = iso(view, -8.5, y, .38);
  ctx.save();
  ctx.strokeStyle = "rgba(37,99,235,.42)";
  ctx.lineWidth = 2;
  ctx.setLineDash([5, 5]);
  ctx.beginPath();
  ctx.moveTo(dockLine.x, dockLine.y);
  ctx.lineTo(gateLine.x, gateLine.y);
  ctx.stroke();
  ctx.restore();
  const p = iso(view, x + 1.3, y - 1.38, 1.68);
  ctx.save();
  ctx.fillStyle = "rgba(15,23,42,.78)";
  ctx.font = "900 8px Segoe UI";
  ctx.fillText(`${isTrailer ? "ФУРА" : "10Т"} ${pallet.gateId}`, p.x - 20, p.y - 4);
  ctx.restore();
}

function gateTruckColor(gateId: string) {
  const gateNumber = Number(String(gateId).replace(/\D/g, "")) || 0;
  return gateNumber % 2 === 0
    ? { body: "#facc15", side: "#a16207", cab: "#ef4444" }
    : { body: "#ef4444", side: "#7f1d1d", cab: "#facc15" };
}

function drawTruckWheel(ctx: CanvasRenderingContext2D, view: View, x: number, y: number) {
  const p = iso(view, x, y, .2);
  ctx.save();
  ctx.fillStyle = "#0f172a";
  ctx.beginPath();
  ctx.ellipse(p.x, p.y + 3, 5.5, 3.2, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#94a3b8";
  ctx.beginPath();
  ctx.ellipse(p.x, p.y + 3, 2.4, 1.4, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawDockPallet(ctx: CanvasRenderingContext2D, view: View, x: number, y: number, pallet: DockPallet) {
  if (pallet.stagedBy === "REACHTRUCK") {
    drawBox(ctx, view, x, y, .05, .85, .72, .82, "#b7791f", "#334155");
    return;
  }
  drawBox(ctx, view, x, y, .05, .85, .72, .28, "#d6a35e", "#475569");
  for (let layer = 0; layer < 3; layer += 1) {
    for (let box = 0; box < 2; box += 1) {
      drawBox(ctx, view, x + box * .38, y + .08, .34 + layer * .22, .34, .52, .18, "#e8b86f", "#8b5e34");
    }
  }
}

function drawEmptyDockSlots(ctx: CanvasRenderingContext2D, view: View, y: number) {
  for (let col = 0; col < 16; col += 1) {
    for (let row = 0; row < 2; row += 1) {
      polygon(ctx, [
        iso(view, -6.5 + col * 1.12, y - .92 + row * 1.22),
        iso(view, -5.65 + col * 1.12, y - .92 + row * 1.22),
        iso(view, -5.65 + col * 1.12, y - .2 + row * 1.22),
        iso(view, -6.5 + col * 1.12, y - .2 + row * 1.22),
      ], "rgba(255,255,255,.16)", "rgba(34,197,94,.18)", .4);
    }
  }
}

function drawFloorLabel(ctx: CanvasRenderingContext2D, view: View, x: number, y: number, label: string, short: string, color: string) {
  const p = iso(view, x, y, .12);
  ctx.save();
  ctx.translate(p.x, p.y);
  ctx.rotate(-0.24);
  ctx.fillStyle = "rgba(255,255,255,.88)";
  roundedRect(ctx, -54, -14, 108, 22, 5);
  ctx.fill();
  ctx.strokeStyle = "rgba(37,99,216,.25)";
  ctx.lineWidth = 1;
  ctx.stroke();
  ctx.fillStyle = color;
  ctx.font = "900 10px Segoe UI";
  ctx.textAlign = "center";
  ctx.fillText(label, 0, -1);
  ctx.fillStyle = "rgba(100,116,139,.85)";
  ctx.font = "800 7px Segoe UI";
  ctx.fillText(short, 0, 8);
  ctx.restore();
}

function drawSign(ctx: CanvasRenderingContext2D, x: number, y: number, text: string, background: string, color: string) {
  ctx.save();
  ctx.translate(x, y);
  ctx.fillStyle = background;
  roundedRect(ctx, -16, -12, 32, 19, 5);
  ctx.fill();
  ctx.strokeStyle = "rgba(255,255,255,.9)";
  ctx.lineWidth = 1.4;
  ctx.stroke();
  ctx.fillStyle = color;
  ctx.font = "900 10px Segoe UI";
  ctx.textAlign = "center";
  ctx.fillText(text, 0, 1);
  ctx.restore();
}

function drawRacks(ctx: CanvasRenderingContext2D, view: View, layout: WarehouseLayout, pickFaceFill: Record<string, PickFaceFill>, hitRegions: Array<{ x: number; y: number; r: number; selection: DetailSelection }>) {
  for (const cell of layout.cells.filter((row) => Number(row.level) === 1)) {
    const fill = pickFaceFill[cell.cell_id];
    const ratio = fill ? fill.ratio : cell.role === "DYNAMIC_PICK_FACE" ? 0 : .55;
    const height = .28 + ratio * 2.45;
    const topColor = cell.role === "DYNAMIC_PICK_FACE" && !fill ? "#7dd3fc" : fillColor(ratio);
    const sideColor = ratio < .18 ? "#5b1e1e" : ratio < .45 ? "#5f4120" : "#1d3f34";
    drawBox(ctx, view, Number(cell.x_m), Number(cell.y_m) - .45, 0, .82, .88, height, topColor, sideColor);
    if (ratio < .85) {
      const hit = iso(view, Number(cell.x_m) + .42, Number(cell.y_m), height + .2);
      hitRegions.push({ x: hit.x, y: hit.y, r: 14, selection: { type: "pickFace", cellId: cell.cell_id, fill } });
    }
    if (cell.slot % 10 === 1) {
      const p = iso(view, Number(cell.x_m), Number(cell.y_m) - .95, height + .3);
      ctx.fillStyle = "#174c9a";
      ctx.font = "800 9px Segoe UI";
      ctx.fillText(`S${String(cell.slot).padStart(3, "0")}`, p.x - 10, p.y);
    }
  }
}

function drawTrails(ctx: CanvasRenderingContext2D, view: View, resources: ResourceState[], minute: number) {
  for (const resource of resources) {
    if (resource.trail.length < 2) continue;
    const baseColor = resource.kind === "reachtruck" ? colors.blue : colors.green;
    const lineWidth = resource.kind === "reachtruck" ? 3.2 : 2.4;
    const dash = resource.kind === "reachtruck" ? [11, 8] : [6, 7];
    for (let index = 1; index < resource.trail.length; index += 1) {
      const previous = resource.trail[index - 1];
      const current = resource.trail[index];
      drawRouteIntent(ctx, view, previous, current);
      const route = routeWaypoints(previous, current).map((point) => iso(view, point.x, point.y, .28));
      const age = resource.trail.length - index;
      const alpha = Math.max(.22, 1 - age * .055);
      for (let routeIndex = 1; routeIndex < route.length; routeIndex += 1) {
        const from = route[routeIndex - 1];
        const to = route[routeIndex];
        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.strokeStyle = "rgba(255,255,255,.82)";
        ctx.lineWidth = lineWidth + 3;
        ctx.lineCap = "round";
        ctx.setLineDash(dash);
        ctx.lineDashOffset = -((minute * (resource.kind === "reachtruck" ? 2.6 : 1.8)) % 18);
        ctx.beginPath();
        ctx.moveTo(from.x, from.y);
        ctx.lineTo(to.x, to.y);
        ctx.stroke();
        ctx.strokeStyle = withAlpha(baseColor, resource.kind === "reachtruck" ? .86 : .78);
        ctx.lineWidth = lineWidth;
        ctx.lineCap = "round";
        ctx.setLineDash(dash);
        ctx.lineDashOffset = -((minute * (resource.kind === "reachtruck" ? 2.6 : 1.8)) % 18);
        ctx.beginPath();
        ctx.moveTo(from.x, from.y);
        ctx.lineTo(to.x, to.y);
        ctx.stroke();
        drawMovingArrow(ctx, from, to, baseColor, alpha, minute + index * 3 + routeIndex * 5, resource.kind === "reachtruck" ? 8 : 6);
        ctx.restore();
      }
    }
  }
}

function drawRouteIntent(ctx: CanvasRenderingContext2D, view: View, from: { x: number; y: number }, to: { x: number; y: number }) {
  const start = iso(view, from.x, from.y, .12);
  const end = iso(view, to.x, to.y, .12);
  const distance = routeDistance(from, to);
  ctx.save();
  ctx.globalAlpha = .38;
  ctx.strokeStyle = distanceColor(distance);
  ctx.lineWidth = 1.2;
  ctx.setLineDash([2, 8]);
  ctx.beginPath();
  ctx.moveTo(start.x, start.y);
  ctx.lineTo(end.x, end.y);
  ctx.stroke();
  ctx.restore();
}

function drawHeatmap(ctx: CanvasRenderingContext2D, view: View, layout: WarehouseLayout, collisions: Collision[]) {
  for (const collision of collisions) {
    const loc = collisionLocation(layout, collision);
    const p = iso(view, loc.x, loc.y, .2);
    const radius = collision.severity === "critical" ? 44 : 32;
    const gradient = ctx.createRadialGradient(p.x, p.y, 2, p.x, p.y, radius);
    gradient.addColorStop(0, collision.severity === "critical" ? "rgba(238,62,55,.62)" : "rgba(245,158,11,.58)");
    gradient.addColorStop(1, "rgba(245,158,11,0)");
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawPickerIcon(ctx: CanvasRenderingContext2D, x: number, y: number, color: string) {
  ctx.save();
  ctx.translate(x, y);
  ctx.shadowColor = "rgba(15,23,42,.22)";
  ctx.shadowBlur = 9;
  ctx.shadowOffsetY = 5;
  ctx.fillStyle = "#fff";
  ctx.beginPath();
  ctx.arc(0, -9, 13, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowColor = "transparent";
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(0, -10, 9, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#fbbf24";
  ctx.beginPath();
  ctx.arc(0, -14, 8, Math.PI, 0);
  ctx.fill();
  ctx.fillRect(-8, -14, 16, 3);
  ctx.fillStyle = "#fff";
  ctx.beginPath();
  ctx.arc(0, -9, 3.2, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#0f172a";
  ctx.fillRect(-5.5, -1, 11, 13);
  ctx.fillStyle = color;
  ctx.fillRect(-9, 3, 18, 4);
  ctx.restore();
}

function drawReachtruckIcon(ctx: CanvasRenderingContext2D, x: number, y: number, angle: number, color: string) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  ctx.scale(1.2, 1.2);
  ctx.fillStyle = "rgba(15,23,42,.22)";
  ctx.beginPath();
  ctx.ellipse(-1, 14, 27, 8, 0, 0, Math.PI * 2);
  ctx.fill();

  // Isometric reachtruck sprite: separate top/side/front planes instead of a flat badge.
  poly(ctx, [[-24, -3], [-8, -12], [13, -3], [-3, 8]], "#f6c453", "#8a5b12", 1.1);
  poly(ctx, [[-3, 8], [13, -3], [13, 8], [-3, 18]], "#d58a21", "#8a5b12", 1.1);
  poly(ctx, [[-24, -3], [-3, 8], [-3, 18], [-24, 7]], "#b8741a", "#7c4a12", 1.1);

  poly(ctx, [[-18, -17], [-8, -22], [3, -15], [-8, -9]], "#164f92", "#0f2f55", 1.1);
  poly(ctx, [[-8, -9], [3, -15], [4, -4], [-8, 3]], "#0b315b", "#0f2f55", 1.1);
  poly(ctx, [[-18, -17], [-8, -9], [-8, 3], [-18, -3]], "#0f3f75", "#0f2f55", 1.1);
  poly(ctx, [[-14, -16], [-8, -19], [-2, -15], [-8, -12]], "#dbeafe", "#7aa7d9", .8);

  ctx.strokeStyle = "#0f172a";
  ctx.lineWidth = 3;
  ctx.lineCap = "round";
  ctx.beginPath();
  ctx.moveTo(13, -24);
  ctx.lineTo(13, 13);
  ctx.moveTo(19, -21);
  ctx.lineTo(19, 11);
  ctx.stroke();
  ctx.strokeStyle = "#475569";
  ctx.lineWidth = 1.3;
  for (const yRail of [-14, -4, 6]) {
    ctx.beginPath();
    ctx.moveTo(13, yRail);
    ctx.lineTo(19, yRail - 1.5);
    ctx.stroke();
  }

  ctx.strokeStyle = "#1e293b";
  ctx.lineWidth = 2.6;
  ctx.beginPath();
  ctx.moveTo(18, 7);
  ctx.lineTo(37, 3);
  ctx.moveTo(18, 13);
  ctx.lineTo(37, 9);
  ctx.stroke();

  drawIsoWheel(ctx, -18, 9, 5.2);
  drawIsoWheel(ctx, 2, 17, 5.2);
  drawIsoWheel(ctx, 8, 6, 4.2);

  ctx.fillStyle = withAlpha(color, .86);
  ctx.beginPath();
  ctx.arc(-24, 2, 3.7, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawIsoWheel(ctx: CanvasRenderingContext2D, x: number, y: number, radius: number) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(-.22);
  ctx.fillStyle = "#0f172a";
  ctx.beginPath();
  ctx.ellipse(0, 0, radius, radius * .68, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#64748b";
  ctx.beginPath();
  ctx.ellipse(0, 0, radius * .43, radius * .27, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function poly(ctx: CanvasRenderingContext2D, points: Array<[number, number]>, fill: string, stroke: string, lineWidth: number) {
  ctx.beginPath();
  points.forEach(([x, y], index) => {
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.closePath();
  ctx.fillStyle = fill;
  ctx.fill();
  ctx.strokeStyle = stroke;
  ctx.lineWidth = lineWidth;
  ctx.stroke();
}

function drawHalo(ctx: CanvasRenderingContext2D, x: number, y: number, color: string, radius: number) {
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.globalAlpha = .55;
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, Math.PI * 2);
  ctx.stroke();
  ctx.globalAlpha = 1;
}

function drawMovingArrow(ctx: CanvasRenderingContext2D, from: { x: number; y: number }, to: { x: number; y: number }, color: string, alpha: number, phaseMinute: number, size: number) {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const length = Math.hypot(dx, dy);
  if (length < 8) return;
  const t = ((phaseMinute % 18) / 18);
  const x = from.x + dx * t;
  const y = from.y + dy * t;
  const angle = Math.atan2(dy, dx);
  ctx.save();
  ctx.globalAlpha = Math.min(.9, alpha + .15);
  ctx.translate(x, y);
  ctx.rotate(angle);
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(size, 0);
  ctx.lineTo(-size * .65, -size * .5);
  ctx.lineTo(-size * .28, 0);
  ctx.lineTo(-size * .65, size * .5);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

function resourceHeading(view: View, resource: ResourceState): number {
  const trail = resource.trail;
  if (trail.length >= 2) {
    const route = routeWaypoints(trail[trail.length - 2], trail[trail.length - 1]);
    const fromPoint = route[Math.max(0, route.length - 2)];
    const toPoint = route[route.length - 1];
    const from = iso(view, fromPoint.x, fromPoint.y, .25);
    const to = iso(view, toPoint.x, toPoint.y, .25);
    return Math.atan2(to.y - from.y, to.x - from.x);
  }
  return -Math.PI / 8;
}

function routeWaypoints(from: { x: number; y: number }, to: { x: number; y: number }): Array<{ x: number; y: number }> {
  if (Math.abs(from.y - to.y) < 1.2) return [from, to];
  const crossAisles = [0, 45, 90];
  const viaX = crossAisles.reduce((best, candidate) => {
    const bestDistance = Math.abs(from.x - best) + Math.abs(to.x - best);
    const candidateDistance = Math.abs(from.x - candidate) + Math.abs(to.x - candidate);
    return candidateDistance < bestDistance ? candidate : best;
  }, crossAisles[0]);
  return compactRoute([
    from,
    { x: viaX, y: from.y },
    { x: viaX, y: to.y },
    to
  ]);
}

function compactRoute(points: Array<{ x: number; y: number }>): Array<{ x: number; y: number }> {
  return points.filter((point, index) => {
    const previous = points[index - 1];
    return !previous || Math.abs(previous.x - point.x) > .05 || Math.abs(previous.y - point.y) > .05;
  });
}

function routeDistance(from: { x: number; y: number }, to: { x: number; y: number }): number {
  const route = routeWaypoints(from, to);
  return route.slice(1).reduce((sum, point, index) => {
    const previous = route[index];
    return sum + Math.abs(point.x - previous.x) + Math.abs(point.y - previous.y);
  }, 0);
}

function distanceColor(distance: number): string {
  if (distance < 18) return "rgba(25,167,101,.72)";
  if (distance < 48) return "rgba(245,158,11,.72)";
  return "rgba(238,62,55,.72)";
}

function fillColor(ratio: number): string {
  if (ratio < .18) return "#ef4444";
  if (ratio < .42) return "#f59e0b";
  if (ratio < .72) return "#84cc16";
  return "#22c55e";
}

function roundedRect(ctx: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, radius: number) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}

function withAlpha(color: string, alpha: number): string {
  const value = color.replace("#", "");
  const r = parseInt(value.slice(0, 2), 16);
  const g = parseInt(value.slice(2, 4), 16);
  const b = parseInt(value.slice(4, 6), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function drawBox(ctx: CanvasRenderingContext2D, view: View, x: number, y: number, z: number, dx: number, dy: number, dz: number, topColor: string, sideColor: string) {
  const p1 = iso(view, x, y, z + dz);
  const p2 = iso(view, x + dx, y, z + dz);
  const p3 = iso(view, x + dx, y + dy, z + dz);
  const p4 = iso(view, x, y + dy, z + dz);
  const b2 = iso(view, x + dx, y, z);
  const b3 = iso(view, x + dx, y + dy, z);
  const b4 = iso(view, x, y + dy, z);
  polygon(ctx, [p1, p2, p3, p4], topColor, "rgba(31,47,72,.35)", .45);
  polygon(ctx, [p2, b2, b3, p3], sideColor, "rgba(31,47,72,.25)", .4);
  polygon(ctx, [p3, b3, b4, p4], "#1d2b3d", "rgba(31,47,72,.25)", .4);
}

function overlayStyle(x: number, y: number, z: number, frameSize: { width: number; height: number }, navigation: ViewNavigation): React.CSSProperties {
  const view = makeView(frameSize.width, frameSize.height, navigation);
  const p = iso(view, x, y, z);
  return { left: `${p.x}px`, top: `${p.y}px` };
}

function collisionLocation(layout: WarehouseLayout, collision: Collision): { x: number; y: number } {
  const raw = collision.raw;
  const cell = cellById(layout, raw.cell || raw.target_cell || raw.source_cell || collision.locationLabel);
  if (cell) return { x: Number(cell.x_m), y: Number(cell.y_m) };
  const eventLoc = eventLocation(layout, raw);
  if (eventLoc) return eventLoc;
  return { x: 30 + (collision.minute % 30), y: 8 };
}

function polygon(ctx: CanvasRenderingContext2D, points: Array<{ x: number; y: number }>, fill: string, stroke: string, lineWidth: number) {
  ctx.beginPath();
  points.forEach((point, index) => {
    if (index === 0) ctx.moveTo(point.x, point.y);
    else ctx.lineTo(point.x, point.y);
  });
  ctx.closePath();
  ctx.fillStyle = fill;
  ctx.fill();
  ctx.strokeStyle = stroke;
  ctx.lineWidth = lineWidth;
  ctx.stroke();
}

type ViewNavigation = { zoom: number; panX: number; panY: number };
type View = { originX: number; originY: number; sx: number; sy: number; z: number };

function makeView(width: number, _height: number, navigation: ViewNavigation = { zoom: 1, panX: 0, panY: 0 }): View {
  return {
    originX: width * .55 + navigation.panX,
    originY: 26 + navigation.panY,
    sx: 7.15 * navigation.zoom,
    sy: 7.85 * navigation.zoom,
    z: 9.6 * navigation.zoom
  };
}

function iso(view: View, x: number, y: number, z = 0): { x: number; y: number } {
  return {
    x: view.originX + (x - y * 1.45) * view.sx,
    y: view.originY + (x * .50 + y * 1.02) * view.sy - z * view.z
  };
}

function statusColor(name: ResourceState["statusColor"]): string {
  return colors[name] || colors.blue;
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}
