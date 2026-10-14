import { Html, Line } from "@react-three/drei";
import { useMemo } from "react";
import type { Cell, TwinOperation } from "../contracts/twin";
import { isOpenPhase } from "../adapters/tmsOperations";
import { cellById } from "../sim/journal";
import { useTwin } from "../store/twinStore";
import { phaseTone } from "../ui/opsFormat";
import { C, toneColor } from "./palette";

// Live-слой складских операций по правилам спецификации (§5, §10, §13):
//  • груз рисуется в последнем подтверждённом месте: до завершения — в источнике, после — в назначении;
//  • к назначению — пунктирный маршрут-намерение, а не фактическая траектория;
//  • исполнитель рисуется только в наблюдённой ячейке (last_cell) с возрастом наблюдения;
//  • операции без привязки к топологии на сцене не появляются — они в панели «Операции».
export function OperationsLayer() {
  const world = useTwin((s) => s.world);
  useTwin((s) => s.entitiesVersion);
  const labels = useTwin((s) => s.labels);
  const selected = useTwin((s) => s.selected);
  const ops = useMemo(() => world.operations.filter((o) => isOpenPhase(o.phase)), [world.operations]);
  // В SIM груз и технику рисует симуляция; слой показывает только маршруты-намерения открытых перемещений.
  if (world.mode !== "live") return <SimIntents />;
  return (
    <group>
      {ops.map((op) => (
        <OperationMarker key={op.key} op={op} showLabel={labels !== "none" || (selected?.kind === "operation" && selected.id === op.key)} selected={selected?.kind === "operation" && selected.id === op.key} />
      ))}
      <Executors />
    </group>
  );
}

const lift = (c: Cell) => c.y + 0.2;

function OperationMarker({ op, showLabel, selected }: { op: TwinOperation; showLabel: boolean; selected: boolean }) {
  const world = useTwin((s) => s.world);
  const select = useTwin((s) => s.select);
  const from = op.from?.bound ? cellById(world, op.from.cell) : undefined;
  const to = op.to?.bound ? cellById(world, op.to.cell) : undefined;
  const lines = (op.lines ?? []).filter((l) => l.bound).map((l) => ({ line: l, cell: cellById(world, l.cell) })).filter((x) => x.cell);
  const color = toneColor(phaseTone(op.phase));
  // Последнее подтверждённое положение груза: незавершённое перемещение — источник; источник неизвестен — назначение как план.
  const at = from ?? to;
  const planned = !from && !!to;
  if (!at && lines.length === 0) return null;
  const onClick = (e: { stopPropagation: () => void }) => {
    e.stopPropagation();
    select({ kind: "operation", id: op.key });
  };
  return (
    <group>
      {from && to && (
        <Line points={[[from.x, lift(from) + 1.2, from.z], [to.x, lift(to) + 1.2, to.z]]} color={color} lineWidth={selected ? 3 : 2} dashed dashSize={0.6} gapSize={0.4} />
      )}
      {at && op.kind === "MOVE" && (
        <group position={[at.x, lift(at), at.z]} onClick={onClick}>
          <mesh position={[0, 0.55, 0]} castShadow>
            <boxGeometry args={[1.0, 0.9, 1.0]} />
            <meshStandardMaterial color={planned ? "#ffffff" : C.cargo} transparent={planned} opacity={planned ? 0.45 : 1} />
          </mesh>
          <mesh rotation-x={-Math.PI / 2} position={[0, 0.02, 0]}>
            <ringGeometry args={[0.75, 0.95, 28]} />
            <meshBasicMaterial color={selected ? C.select : color} />
          </mesh>
        </group>
      )}
      {lines.map(({ line, cell }) => (
        <mesh key={line.id} rotation-x={-Math.PI / 2} position={[cell!.x, 0.1, cell!.z]} onClick={onClick}>
          <ringGeometry args={[0.45, 0.65, 24]} />
          <meshBasicMaterial color={line.status === "DONE" || line.status === "PICKED" ? C.ok : color} />
        </mesh>
      ))}
      {showLabel && (at ?? lines[0]?.cell) && (
        <Html position={[(at ?? lines[0].cell!).x, lift(at ?? lines[0].cell!) + 2.4, (at ?? lines[0].cell!).z]} center zIndexRange={[35, 0]}>
          <button type="button" className={`tag tag-small ${selected ? "tag-selected" : ""}`} onClick={() => select({ kind: "operation", id: op.key })}>
            <span className="tag-dot" style={{ background: color }} />
            <b>{op.key}</b>
            <span>{op.source.rawStatus}{planned ? " · план" : ""}</span>
          </button>
        </Html>
      )}
    </group>
  );
}

function ageLabel(iso?: string) {
  if (!iso) return "время неизвестно";
  const t = new Date(iso).getTime();
  if (Number.isNaN(t)) return iso;
  const min = Math.round((Date.now() - t) / 60000);
  return min < 1 ? "только что" : min < 120 ? `${min} мин назад` : `${Math.round(min / 60)} ч назад`;
}

function Executors() {
  const world = useTwin((s) => s.world);
  const select = useTwin((s) => s.select);
  const placed = world.executors.filter((e) => e.positionBasis === "OBSERVED_CELL").map((e) => ({ e, cell: cellById(world, e.lastCell) })).filter((x) => x.cell);
  return (
    <group>
      {placed.map(({ e, cell }) => (
        <group key={e.id} position={[cell!.x, 0, cell!.z]} onClick={(ev) => { ev.stopPropagation(); select({ kind: "executor", id: e.id }); }}>
          <mesh position={[0, 0.9, 0]} castShadow>
            <capsuleGeometry args={[0.3, 1.0, 4, 10]} />
            <meshStandardMaterial color={e.kind.includes("REACH") || e.kind.includes("FORK") ? C.machine : C.picker} />
          </mesh>
          <Html position={[0, 2.6, 0]} center zIndexRange={[30, 0]}>
            <button type="button" className="tag tag-small" onClick={() => select({ kind: "executor", id: e.id })}>
              <b>{e.code}</b>
              <span>{e.kind} · {ageLabel(e.lastPositionAt)}</span>
            </button>
          </Html>
        </group>
      ))}
    </group>
  );
}

function SimIntents() {
  const world = useTwin((s) => s.world);
  useTwin((s) => s.hudVersion);
  const routes = world.operations
    .filter((o) => o.kind === "MOVE" && isOpenPhase(o.phase) && o.from?.bound && o.to?.bound)
    .map((o) => ({ o, a: cellById(world, o.from!.cell), b: cellById(world, o.to!.cell) }))
    .filter((r) => r.a && r.b);
  return (
    <group>
      {routes.map(({ o, a, b }) => (
        <Line key={o.key} points={[[a!.x, a!.y + 1.4, a!.z], [b!.x, b!.y + 1.4, b!.z]]} color={toneColor(phaseTone(o.phase))} lineWidth={2} dashed dashSize={0.5} gapSize={0.35} />
      ))}
    </group>
  );
}
