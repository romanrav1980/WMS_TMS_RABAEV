import { useEffect, useMemo, useRef } from "react";
import type { Collision, DetailSelection, ResourceState, WarehouseLayout } from "../types";
import { cellById, eventLocation } from "../replay/reducer";
import { collisionTitle } from "../replay/reducer";

type SceneProps = {
  layout: WarehouseLayout;
  resources: ResourceState[];
  collisions: Collision[];
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

export function WarehouseScene({ layout, resources, collisions, selectedWaveId, onSelect }: SceneProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const hitRegions = useRef<Array<{ x: number; y: number; r: number; selection: DetailSelection }>>([]);
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
    context.setTransform(scale, 0, 0, scale, 0, 0);
    drawScene(context, rect.width, rect.height, layout, visibleResources, collisions, hitRegions.current);
  }, [layout, visibleResources, collisions]);

  return (
    <div className="scene-frame">
      <canvas
        ref={canvasRef}
        onClick={(event) => {
          const rect = event.currentTarget.getBoundingClientRect();
          const x = event.clientX - rect.left;
          const y = event.clientY - rect.top;
          const hit = hitRegions.current.find((region) => Math.hypot(region.x - x, region.y - y) <= region.r);
          if (hit) onSelect(hit.selection);
        }}
      />
      <div className="scene-overlays">
        {visibleResources.map((resource) => (
          <button
            key={resource.id}
            type="button"
            className={`resource-badge ${resource.statusColor}`}
            style={overlayStyle(layout, resource.x, resource.y, resource.kind === "reachtruck" ? 2.1 : 1.7)}
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
              style={overlayStyle(layout, loc.x, loc.y, 3)}
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
  hitRegions: Array<{ x: number; y: number; r: number; selection: DetailSelection }>
) {
  hitRegions.length = 0;
  const view = makeView(width, height);
  const gradient = ctx.createLinearGradient(0, 0, width, height);
  gradient.addColorStop(0, "#f8fbff");
  gradient.addColorStop(.55, "#e8eef7");
  gradient.addColorStop(1, "#d6e0eb");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);

  drawFloor(ctx, view);
  drawGates(ctx, view, layout);
  drawRacks(ctx, view, layout);
  drawHeatmap(ctx, view, layout, collisions);
  drawTrails(ctx, view, resources);
  for (const resource of resources) {
    const p = iso(view, resource.x, resource.y, resource.kind === "reachtruck" ? .9 : .55);
    if (resource.kind === "reachtruck") drawBox(ctx, view, resource.x - .7, resource.y - .35, .05, 1.4, .7, .55, statusColor(resource.statusColor), "#243042");
    else drawPerson(ctx, p.x, p.y, statusColor(resource.statusColor));
    drawHalo(ctx, p.x, p.y, statusColor(resource.statusColor), resource.kind === "reachtruck" ? 18 : 13);
    hitRegions.push({ x: p.x, y: p.y, r: 18, selection: { type: "resource", resource } });
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

function drawRacks(ctx: CanvasRenderingContext2D, view: View, layout: WarehouseLayout) {
  for (const cell of layout.cells.filter((row) => Number(row.level) === 1 && row.slot % 2 === 1)) {
    const height = cell.role === "DYNAMIC_PICK_FACE" ? 1.6 : cell.role === "DUPLICATE_A_PICK_FACE" ? 2.15 : 1.9;
    const topColor = cell.role === "DYNAMIC_PICK_FACE" ? "#7dd3fc" : cell.role === "DUPLICATE_A_PICK_FACE" ? "#c4b5fd" : colors.pallet;
    drawBox(ctx, view, Number(cell.x_m), Number(cell.y_m) - .55, 0, 1.05, 1.1, height, topColor, colors.rack);
    if (cell.slot % 10 === 1) {
      const p = iso(view, Number(cell.x_m), Number(cell.y_m) - .95, height + .3);
      ctx.fillStyle = "#174c9a";
      ctx.font = "800 9px Segoe UI";
      ctx.fillText(`S${String(cell.slot).padStart(3, "0")}`, p.x - 10, p.y);
    }
  }
}

function drawTrails(ctx: CanvasRenderingContext2D, view: View, resources: ResourceState[]) {
  for (const resource of resources) {
    if (resource.trail.length < 2) continue;
    ctx.strokeStyle = resource.kind === "reachtruck" ? "rgba(37,99,216,.55)" : "rgba(25,167,101,.48)";
    ctx.lineWidth = resource.kind === "reachtruck" ? 3 : 2;
    ctx.setLineDash(resource.kind === "reachtruck" ? [9, 7] : [5, 5]);
    ctx.beginPath();
    resource.trail.forEach((point, index) => {
      const p = iso(view, point.x, point.y, .25);
      if (index === 0) ctx.moveTo(p.x, p.y);
      else ctx.lineTo(p.x, p.y);
    });
    ctx.stroke();
    ctx.setLineDash([]);
  }
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

function drawPerson(ctx: CanvasRenderingContext2D, x: number, y: number, color: string) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(x, y - 8, 5, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillRect(x - 4, y - 4, 8, 13);
  ctx.fillStyle = "#fff";
  ctx.fillRect(x - 8, y + 4, 16, 4);
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

function overlayStyle(layout: WarehouseLayout, x: number, y: number, z: number): React.CSSProperties {
  const view = makeView(1090, 670);
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

type View = { originX: number; originY: number; sx: number; sy: number; z: number };

function makeView(width: number, _height: number): View {
  return { originX: width * .51, originY: 36, sx: 8.0, sy: 7.25, z: 8.5 };
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
