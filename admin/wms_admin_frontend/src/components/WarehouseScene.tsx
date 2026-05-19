import { useEffect, useMemo, useRef, useState } from "react";
import type { Collision, DetailSelection, PickFaceFill, ResourceState, WarehouseLayout } from "../types";
import { cellById, eventLocation } from "../replay/reducer";
import { collisionTitle } from "../replay/reducer";

type SceneProps = {
  layout: WarehouseLayout;
  resources: ResourceState[];
  collisions: Collision[];
  pickFaceFill: Record<string, PickFaceFill>;
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

export function WarehouseScene({ layout, resources, collisions, pickFaceFill, minute, selectedWaveId, onSelect }: SceneProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const hitRegions = useRef<Array<{ x: number; y: number; r: number; selection: DetailSelection }>>([]);
  const dragState = useRef<{ active: boolean; x: number; y: number; moved: boolean }>({ active: false, x: 0, y: 0, moved: false });
  const [navigation, setNavigation] = useState({ zoom: 1, panX: 0, panY: 0 });
  const [frameSize, setFrameSize] = useState({ width: 1090, height: 670 });
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
    drawScene(context, rect.width, rect.height, layout, visibleResources, collisions, pickFaceFill, hitRegions.current, navigation, minute);
  }, [layout, visibleResources, collisions, pickFaceFill, navigation, minute]);

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
          if (!drag.active) return;
          const dx = event.clientX - drag.x;
          const dy = event.clientY - drag.y;
          if (Math.abs(dx) + Math.abs(dy) > 2) drag.moved = true;
          drag.x = event.clientX;
          drag.y = event.clientY;
          setNavigation((current) => ({ ...current, panX: current.panX + dx, panY: current.panY + dy }));
        }}
        onMouseUp={() => { dragState.current.active = false; }}
        onMouseLeave={() => { dragState.current.active = false; }}
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
            className={`resource-badge ${resource.statusColor}`}
            style={overlayStyle(resource.x, resource.y, resource.kind === "reachtruck" ? 2.1 : 1.7, frameSize, navigation)}
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

function drawScene(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  layout: WarehouseLayout,
  resources: ResourceState[],
  collisions: Collision[],
  pickFaceFill: Record<string, PickFaceFill>,
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
  drawGates(ctx, view, layout);
  drawRacks(ctx, view, layout, pickFaceFill);
  drawHeatmap(ctx, view, layout, collisions);
  drawTrails(ctx, view, resources, minute);
  for (const resource of resources) {
    const p = iso(view, resource.x, resource.y, resource.kind === "reachtruck" ? .9 : .55);
    if (resource.kind === "reachtruck") drawReachtruckIcon(ctx, p.x, p.y, resourceHeading(view, resource), statusColor(resource.statusColor));
    else drawPickerIcon(ctx, p.x, p.y, statusColor(resource.statusColor));
    drawHalo(ctx, p.x, p.y, statusColor(resource.statusColor), resource.kind === "reachtruck" ? 18 : 13);
    hitRegions.push({ x: p.x, y: p.y, r: resource.kind === "reachtruck" ? 24 : 18, selection: { type: "resource", resource } });
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
  polygon(ctx, [iso(view, -8, -7), iso(view, 101, -7), iso(view, 101, 105), iso(view, -8, 105)], colors.floor, "#c9d5e2", 1);
  for (const crossX of [0, 45, 90]) {
    const label = crossX === 0 ? "фронтальный проезд" : crossX === 45 ? "пожарный проход" : "задний обход";
    polygon(ctx, [iso(view, crossX - .8, -5), iso(view, crossX + .8, -5), iso(view, crossX + .8, 101), iso(view, crossX - .8, 101)], "rgba(37,99,216,.08)", "rgba(37,99,216,.22)", .7);
    const p = iso(view, crossX - 1.5, -4.7, .05);
    ctx.fillStyle = "rgba(23,76,154,.72)";
    ctx.font = "800 9px Segoe UI";
    ctx.fillText(label, p.x, p.y);
  }
  for (let aisle = 1; aisle <= 25; aisle += 1) {
    const y = (aisle - 1) * 4;
    polygon(ctx, [iso(view, -2, y - .95), iso(view, 92, y - .95), iso(view, 92, y + .95), iso(view, -2, y + .95)], aisle % 2 ? "#f6f9fc" : "#edf3f9", "#cfdae7", .6);
    const label = iso(view, -7, y);
    ctx.fillStyle = colors.blue;
    ctx.font = "700 10px Segoe UI";
    ctx.fillText(`A${String(aisle).padStart(2, "0")}`, label.x, label.y);
  }
}

function drawGates(ctx: CanvasRenderingContext2D, view: View, layout: WarehouseLayout) {
  for (const gate of layout.gates) {
    const y = Number(gate.y_m || (gate.aisle - 1) * 4);
    drawBox(ctx, view, -5.8, y - .75, 0, 4.2, 1.5, .35, "#eff6ff", "#c7daf5");
    const p = iso(view, -5.8, y);
    ctx.fillStyle = colors.blue;
    ctx.font = "800 9px Segoe UI";
    ctx.fillText(gate.gate_id, p.x - 8, p.y - 7);
  }
}

function drawRacks(ctx: CanvasRenderingContext2D, view: View, layout: WarehouseLayout, pickFaceFill: Record<string, PickFaceFill>) {
  for (const cell of layout.cells.filter((row) => Number(row.level) === 1)) {
    const fill = pickFaceFill[cell.cell_id];
    const ratio = fill ? fill.ratio : cell.role === "DYNAMIC_PICK_FACE" ? 0 : .55;
    const height = .28 + ratio * 2.45;
    const topColor = cell.role === "DYNAMIC_PICK_FACE" && !fill ? "#7dd3fc" : fillColor(ratio);
    const sideColor = ratio < .18 ? "#5b1e1e" : ratio < .45 ? "#5f4120" : "#1d3f34";
    drawBox(ctx, view, Number(cell.x_m), Number(cell.y_m) - .45, 0, .82, .88, height, topColor, sideColor);
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
  ctx.shadowColor = "rgba(15,23,42,.24)";
  ctx.shadowBlur = 10;
  ctx.shadowOffsetY = 5;
  ctx.fillStyle = "#f59e0b";
  roundedRect(ctx, -18, -9, 28, 16, 4);
  ctx.fill();
  ctx.shadowColor = "transparent";
  ctx.fillStyle = "#1f2937";
  ctx.fillRect(8, -13, 5, 24);
  ctx.fillStyle = color;
  roundedRect(ctx, -13, -13, 15, 9, 3);
  ctx.fill();
  ctx.fillStyle = "#dbeafe";
  ctx.fillRect(-9, -11, 7, 5);
  ctx.strokeStyle = "#1f2937";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(13, -8);
  ctx.lineTo(25, -8);
  ctx.moveTo(13, 7);
  ctx.lineTo(25, 7);
  ctx.stroke();
  ctx.fillStyle = "#111827";
  ctx.beginPath();
  ctx.arc(-10, 9, 4, 0, Math.PI * 2);
  ctx.arc(5, 9, 4, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
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
    originX: width * .51 + navigation.panX,
    originY: 36 + navigation.panY,
    sx: 8.0 * navigation.zoom,
    sy: 7.25 * navigation.zoom,
    z: 8.5 * navigation.zoom
  };
}

function iso(view: View, x: number, y: number, z = 0): { x: number; y: number } {
  return {
    x: view.originX + (x - y * 1.85) * view.sx,
    y: view.originY + (x * .42 + y * 1.03) * view.sy - z * view.z
  };
}

function statusColor(name: ResourceState["statusColor"]): string {
  return colors[name] || colors.blue;
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}
