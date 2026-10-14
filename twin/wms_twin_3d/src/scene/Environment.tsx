import { useLayoutEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { createRng } from "../sim/rng";
import { useTwin } from "../store/twinStore";
import { type SceneDims, sceneDims } from "./dims";
import { C } from "./palette";

// Земля, дорога, двор с разметкой, газоны, деревья и забор вокруг площадки — по размерам layout.
export function Environment() {
  const world = useTwin((s) => s.world);
  const d = sceneDims(world);
  const gateXs = useMemo(() => world.gates.map((g) => g.x).sort((a, b) => a - b), [world.gates]);
  return (
    <group>
      <mesh rotation-x={-Math.PI / 2} position={[d.width / 2, -0.02, d.wallZ]} receiveShadow>
        <planeGeometry args={[d.width + 460, d.wallZ + 300]} />
        <meshStandardMaterial color={C.ground} />
      </mesh>
      <mesh rotation-x={-Math.PI / 2} position={[d.width / 2, 0, (d.wallZ + d.roadZ - 4) / 2 + 0.6]} receiveShadow>
        <planeGeometry args={[d.width + 52, d.roadZ - d.wallZ - 6]} />
        <meshStandardMaterial color={C.apron} />
      </mesh>
      <Road d={d} />
      <Lawns d={d} />
      <Trees d={d} />
      <Fence d={d} />
      <DockLines d={d} gateXs={gateXs} />
    </group>
  );
}

function Road({ d }: { d: SceneDims }) {
  const dashes = useMemo(() => Array.from({ length: Math.ceil((d.width + 340) / 10) }, (_, i) => -150 + i * 10), [d.width]);
  const z = (d.roadZ + d.exitZ) / 2;
  return (
    <group>
      <mesh rotation-x={-Math.PI / 2} position={[d.width / 2, 0.01, z]} receiveShadow>
        <planeGeometry args={[d.width + 380, 9.5]} />
        <meshStandardMaterial color={C.road} />
      </mesh>
      {dashes.map((x) => (
        <mesh key={x} rotation-x={-Math.PI / 2} position={[x, 0.02, z]}>
          <planeGeometry args={[4, 0.18]} />
          <meshBasicMaterial color={C.roadLine} />
        </mesh>
      ))}
      <mesh rotation-x={-Math.PI / 2} position={[-70, 0.012, d.shoulderZ]} receiveShadow>
        <planeGeometry args={[110, 5.5]} />
        <meshStandardMaterial color="#a3abb7" />
      </mesh>
    </group>
  );
}

function Lawns({ d }: { d: SceneDims }) {
  const lawns: [number, number, number, number][] = [
    [d.width / 2, -14, d.width + 70, 20],
    [-22, d.wallZ / 2, 34, d.wallZ + 8],
    [d.width + 26, d.wallZ / 2, 40, d.wallZ + 8],
    [d.width / 2, d.roadZ + 20, d.width + 240, 24]
  ];
  return (
    <group>
      {lawns.map(([x, z, w, h]) => (
        <mesh key={`${x}:${z}`} rotation-x={-Math.PI / 2} position={[x, 0.005, z]} receiveShadow>
          <planeGeometry args={[w, h]} />
          <meshStandardMaterial color={C.lawn} />
        </mesh>
      ))}
    </group>
  );
}

function Trees({ d }: { d: SceneDims }) {
  const crowns = useRef<THREE.InstancedMesh>(null);
  const trunks = useRef<THREE.InstancedMesh>(null);
  const spots = useMemo(() => {
    const rng = createRng(7);
    const pts: { x: number; z: number; s: number; c: string }[] = [];
    const add = (x: number, z: number) => pts.push({ x, z, s: 0.8 + rng.next() * 0.6, c: rng.pick([C.treeA, C.treeA, C.treeB, C.treeC]) });
    for (let x = -14; x < d.width + 16; x += 6.5) add(x + rng.next() * 2, -10 - rng.next() * 6);
    for (let z = 0; z < d.wallZ; z += 7) {
      add(-12 - rng.next() * 6, z);
      add(d.width + 14 + rng.next() * 8, z);
    }
    for (let x = -120; x < d.width + 140; x += 9) add(x + rng.next() * 3, d.roadZ + 14 + rng.next() * 8);
    return pts;
  }, [d.width, d.wallZ, d.roadZ]);
  useLayoutEffect(() => {
    const m = new THREE.Matrix4();
    const color = new THREE.Color();
    spots.forEach((p, i) => {
      m.compose(new THREE.Vector3(p.x, 2.2 * p.s, p.z), new THREE.Quaternion(), new THREE.Vector3(p.s, p.s, p.s));
      crowns.current?.setMatrixAt(i, m);
      crowns.current?.setColorAt(i, color.set(p.c));
      m.compose(new THREE.Vector3(p.x, 0.6 * p.s, p.z), new THREE.Quaternion(), new THREE.Vector3(p.s, p.s, p.s));
      trunks.current?.setMatrixAt(i, m);
    });
    if (crowns.current) {
      crowns.current.instanceMatrix.needsUpdate = true;
      if (crowns.current.instanceColor) crowns.current.instanceColor.needsUpdate = true;
    }
    if (trunks.current) trunks.current.instanceMatrix.needsUpdate = true;
  }, [spots]);
  return (
    <group>
      <instancedMesh key={spots.length} ref={crowns} args={[undefined, undefined, spots.length]} castShadow>
        <icosahedronGeometry args={[1.5, 0]} />
        <meshStandardMaterial flatShading />
      </instancedMesh>
      <instancedMesh key={`t${spots.length}`} ref={trunks} args={[undefined, undefined, spots.length]}>
        <cylinderGeometry args={[0.18, 0.24, 1.2, 6]} />
        <meshStandardMaterial color={C.trunk} />
      </instancedMesh>
    </group>
  );
}

function Fence({ d }: { d: SceneDims }) {
  const posts = useMemo(() => {
    const pts: [number, number][] = [];
    for (let x = -16; x <= d.width + 22; x += 3) pts.push([x, -4]);
    for (let z = -4; z <= d.roadZ - 7; z += 3) {
      pts.push([-16, z]);
      pts.push([d.width + 22, z]);
    }
    return pts;
  }, [d.width, d.roadZ]);
  return (
    <group>
      {posts.map(([x, z]) => (
        <mesh key={`${x}:${z}`} position={[x, 0.7, z]}>
          <boxGeometry args={[0.08, 1.4, 0.08]} />
          <meshStandardMaterial color="#9aa3b2" />
        </mesh>
      ))}
    </group>
  );
}

// Жёлтые линии разметки между воротами на площадке перед фасадом.
function DockLines({ d, gateXs }: { d: SceneDims; gateXs: number[] }) {
  const lines = useMemo(() => {
    if (gateXs.length === 0) return [];
    const mids = gateXs.slice(1).map((x, i) => (x + gateXs[i]) / 2);
    const pitch = gateXs.length > 1 ? gateXs[1] - gateXs[0] : 6.5;
    return [gateXs[0] - pitch / 2, ...mids, gateXs[gateXs.length - 1] + pitch / 2];
  }, [gateXs]);
  return (
    <group>
      {lines.map((x) => (
        <mesh key={x} rotation-x={-Math.PI / 2} position={[x, 0.02, d.wallZ + 9]}>
          <planeGeometry args={[0.16, 18]} />
          <meshBasicMaterial color="#fbbf24" />
        </mesh>
      ))}
    </group>
  );
}
