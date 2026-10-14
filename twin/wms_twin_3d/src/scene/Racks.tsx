import { useLayoutEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import type { ThreeEvent } from "@react-three/fiber";
import type { Cell } from "../contracts/twin";
import { useTwin } from "../store/twinStore";
import { LEVEL_H, RACK_DEPTH, SLOT_LEN } from "../sim/layout";
import { C } from "./palette";

const tmp = new THREE.Matrix4();
const q = new THREE.Quaternion();
const color = new THREE.Color();
const sx = (c: Cell) => c.sizeX ?? RACK_DEPTH;
const sz = (c: Cell) => c.sizeZ ?? SLOT_LEN;

// Стеллажи и груз рендерятся через InstancedMesh: тысячи ячеек — несколько draw call.
// Каркас строится из самих ячеек, поэтому одинаково работает для демо-склада и топологии ТМС.
export function Racks() {
  return (
    <group>
      <RackFrames />
      <Cargo />
      <SelectedCell />
    </group>
  );
}

function RackFrames() {
  const posts = useRef<THREE.InstancedMesh>(null);
  const beams = useRef<THREE.InstancedMesh>(null);
  const world = useTwin((s) => s.world);
  const columns = useMemo(() => {
    const map = new Map<string, { cell: Cell; top: number }>();
    for (const c of world.cells) {
      const key = `${c.x.toFixed(2)}:${c.z.toFixed(2)}`;
      const prev = map.get(key);
      if (!prev || c.level > prev.top) map.set(key, { cell: c, top: c.level });
    }
    return [...map.values()];
  }, [world.cells]);
  useLayoutEffect(() => {
    let p = 0;
    for (const { cell, top } of columns) {
      const h = top * LEVEL_H + 0.4;
      for (const dx of [-sx(cell) / 2, sx(cell) / 2]) {
        for (const dz of [-sz(cell) / 2, sz(cell) / 2]) {
          tmp.compose(new THREE.Vector3(cell.x + dx, h / 2, cell.z + dz), q, new THREE.Vector3(1, h, 1));
          posts.current?.setMatrixAt(p++, tmp);
        }
      }
    }
    world.cells.forEach((cell, i) => {
      tmp.compose(new THREE.Vector3(cell.x, cell.y + 0.05, cell.z), q, new THREE.Vector3(sx(cell) + 0.06, 1, sz(cell)));
      beams.current?.setMatrixAt(i, tmp);
    });
    for (const mesh of [posts.current, beams.current]) {
      if (!mesh) continue;
      mesh.instanceMatrix.needsUpdate = true;
      mesh.computeBoundingSphere();
    }
  }, [columns, world.cells]);
  return (
    <group>
      <instancedMesh ref={posts} args={[undefined, undefined, Math.max(1, columns.length * 4)]} castShadow>
        <boxGeometry args={[0.09, 1, 0.09]} />
        <meshStandardMaterial color={C.rackPost} />
      </instancedMesh>
      <instancedMesh ref={beams} args={[undefined, undefined, Math.max(1, world.cells.length)]} receiveShadow>
        <boxGeometry args={[1, 0.1, 1]} />
        <meshStandardMaterial color={C.rackBeam} />
      </instancedMesh>
    </group>
  );
}

function heatColor(fill: number) {
  return color.setHSL(0.33 * fill, 0.75, 0.52);
}

function Cargo() {
  const cargo = useRef<THREE.InstancedMesh>(null);
  const empties = useRef<THREE.InstancedMesh>(null);
  const world = useTwin((s) => s.world);
  const stockVersion = useTwin((s) => s.stockVersion);
  const heatmap = useTwin((s) => s.heatmap);
  const select = useTwin((s) => s.select);
  const count = world.cells.length;
  useLayoutEffect(() => {
    const zero = new THREE.Vector3(0, 0, 0);
    for (const cell of world.cells) {
      const known = cell.stockKnown !== false;
      const visible = !known || cell.qty > 0;
      const fill = known ? cell.qty / cell.capacity : 0.5;
      const h = !known ? 0.5 : cell.role === "pick" ? 0.35 + 0.75 * fill : 1.05;
      const size = new THREE.Vector3((sx(cell) - 0.18) / (RACK_DEPTH - 0.18), h, (sz(cell) - 0.2) / (SLOT_LEN - 0.2));
      tmp.compose(new THREE.Vector3(cell.x, cell.y + 0.12 + h / 2, cell.z), q, visible ? size : zero);
      cargo.current?.setMatrixAt(cell.index, tmp);
      if (!known) cargo.current?.setColorAt(cell.index, color.set("#d7dde6"));
      else if (heatmap) cargo.current?.setColorAt(cell.index, cell.role === "pick" ? heatColor(fill) : color.set("#cbd5e1"));
      else cargo.current?.setColorAt(cell.index, color.set(cell.role === "pick" && fill <= 0.21 ? C.cargoLow : C.cargo));
      const empty = known && cell.role === "pick" && cell.qty === 0;
      tmp.compose(new THREE.Vector3(cell.x, 0.09, cell.z), q, empty ? new THREE.Vector3(sx(cell) / RACK_DEPTH, 1, sz(cell) / SLOT_LEN) : zero);
      empties.current?.setMatrixAt(cell.index, tmp);
    }
    for (const mesh of [cargo.current, empties.current]) {
      if (!mesh) continue;
      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
      mesh.computeBoundingSphere();
    }
  }, [world, stockVersion, heatmap]);
  const onClick = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    if (e.instanceId === undefined) return;
    select({ kind: "cell", id: world.cells[e.instanceId].id });
  };
  return (
    <group>
      <instancedMesh ref={cargo} args={[undefined, undefined, count]} castShadow onClick={onClick}>
        <boxGeometry args={[RACK_DEPTH - 0.18, 1, SLOT_LEN - 0.2]} />
        <meshStandardMaterial />
      </instancedMesh>
      <instancedMesh ref={empties} args={[undefined, undefined, count]} onClick={onClick}>
        <boxGeometry args={[RACK_DEPTH - 0.1, 0.06, SLOT_LEN - 0.12]} />
        <meshBasicMaterial color={C.cargoEmpty} />
      </instancedMesh>
    </group>
  );
}

function SelectedCell() {
  const selected = useTwin((s) => s.selected);
  const world = useTwin((s) => s.world);
  if (selected?.kind !== "cell") return null;
  const cell = world.cells[world.cellIndex[selected.id]];
  if (!cell) return null;
  return (
    <mesh position={[cell.x, cell.y + 0.75, cell.z]}>
      <boxGeometry args={[sx(cell) + 0.2, 1.5, sz(cell) + 0.1]} />
      <meshBasicMaterial color={C.select} wireframe />
    </mesh>
  );
}
