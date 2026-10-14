import { useMemo } from "react";
import { useTwin } from "../store/twinStore";
import { CHARGER } from "../sim/layout";
import { sceneDims } from "./dims";
import { C } from "./palette";

const WALL_H = 7;
const DOOR_W = 4.2;
const DOOR_H = 4.6;

// Корпус склада без крыши: глухие задняя/боковые стены, остеклённый фасад с проёмами ворот, фермы перекрытия.
// Размеры и проёмы берутся из layout/ворот текущего источника.
export function Building() {
  const world = useTwin((s) => s.world);
  const select = useTwin((s) => s.select);
  const { width: W, wallZ: Z, frontZ, stagingZ } = sceneDims(world);
  const frontSegments = useMemo(() => {
    const edges = [0];
    for (const g of [...world.gates].sort((a, b) => a.x - b.x)) edges.push(g.x - DOOR_W / 2, g.x + DOOR_W / 2);
    edges.push(W);
    const segs: [number, number][] = [];
    for (let i = 0; i < edges.length; i += 2) segs.push([edges[i], edges[i + 1]]);
    return segs;
  }, [world.gates, W]);
  const trusses = useMemo(() => Array.from({ length: Math.floor(W / 8) }, (_, i) => 4 + i * 8), [W]);
  return (
    <group>
      <mesh rotation-x={-Math.PI / 2} position={[W / 2, 0.03, Z / 2]} receiveShadow onClick={(e) => { e.stopPropagation(); select({ kind: "site", id: world.layout.siteId }, false); }}>
        <planeGeometry args={[W, Z]} />
        <meshStandardMaterial color={C.floor} />
      </mesh>
      {Z - frontZ > 2 && (
        <mesh rotation-x={-Math.PI / 2} position={[W / 2, 0.04, (frontZ + Z) / 2 + 0.6]} receiveShadow>
          <planeGeometry args={[W - 1, Z - frontZ - 1.2]} />
          <meshStandardMaterial color={C.floorZone} />
        </mesh>
      )}
      <mesh rotation-x={-Math.PI / 2} position={[W / 2, 0.05, stagingZ + 1.4]}>
        <planeGeometry args={[W - 4, 0.12]} />
        <meshBasicMaterial color="#fbbf24" />
      </mesh>
      <Wall x={W / 2} z={-0.25} w={W + 0.5} d={0.5} />
      <Wall x={-0.25} z={Z / 2} w={0.5} d={Z} />
      <Wall x={W + 0.25} z={Z / 2} w={0.5} d={Z} />
      {frontSegments.map(([a, b]) => (
        <FrontPanel key={a} a={a} b={b} z={Z} />
      ))}
      <mesh position={[W / 2, DOOR_H + 0.35, Z]} castShadow>
        <boxGeometry args={[W, 0.7, 0.5]} />
        <meshStandardMaterial color={C.wall} />
      </mesh>
      <mesh position={[W / 2, WALL_H - 0.2, Z]}>
        <boxGeometry args={[W + 0.6, 0.4, 0.6]} />
        <meshStandardMaterial color={C.wallTrim} />
      </mesh>
      {trusses.map((x) => (
        <mesh key={x} position={[x, WALL_H - 0.1, Z / 2]}>
          <boxGeometry args={[0.25, 0.25, Z]} />
          <meshStandardMaterial color="#e2e8f0" />
        </mesh>
      ))}
      {world.mode === "sim" && <Charger />}
    </group>
  );
}

function Wall({ x, z, w, d }: { x: number; z: number; w: number; d: number }) {
  return (
    <group>
      <mesh position={[x, WALL_H / 2, z]} castShadow receiveShadow>
        <boxGeometry args={[w, WALL_H, d]} />
        <meshStandardMaterial color={C.wall} />
      </mesh>
      <mesh position={[x, WALL_H + 0.15, z]}>
        <boxGeometry args={[w + 0.1, 0.3, d + 0.1]} />
        <meshStandardMaterial color={C.wallTrim} />
      </mesh>
    </group>
  );
}

function FrontPanel({ a, b, z }: { a: number; b: number; z: number }) {
  const w = b - a;
  if (w <= 0.05) return null;
  const x = (a + b) / 2;
  return (
    <group>
      <mesh position={[x, 0.6, z]} castShadow>
        <boxGeometry args={[w, 1.2, 0.5]} />
        <meshStandardMaterial color={C.wall} />
      </mesh>
      <mesh position={[x, (1.2 + DOOR_H) / 2, z]}>
        <boxGeometry args={[w, DOOR_H - 1.2, 0.12]} />
        <meshStandardMaterial color={C.glass} transparent opacity={0.28} />
      </mesh>
      <mesh position={[x, (DOOR_H + 0.7 + WALL_H) / 2, z]}>
        <boxGeometry args={[w, WALL_H - DOOR_H - 0.7, 0.12]} />
        <meshStandardMaterial color={C.glass} transparent opacity={0.22} />
      </mesh>
    </group>
  );
}

function Charger() {
  return (
    <group position={[CHARGER.x + 1.4, 0, CHARGER.z]}>
      <mesh position={[0, 0.8, 0]} castShadow>
        <boxGeometry args={[0.7, 1.6, 0.5]} />
        <meshStandardMaterial color="#e5e7eb" />
      </mesh>
      <mesh position={[0, 1.35, 0.26]}>
        <boxGeometry args={[0.35, 0.18, 0.02]} />
        <meshBasicMaterial color={C.ok} />
      </mesh>
    </group>
  );
}
