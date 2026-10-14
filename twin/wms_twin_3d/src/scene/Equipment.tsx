import { Html } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import { useRef } from "react";
import type * as THREE from "three";
import type { Resource } from "../contracts/twin";
import { receivingPoint } from "../sim/layout";
import { useTwin } from "../store/twinStore";
import { resourceStatus } from "../ui/format";
import { C, toneColor } from "./palette";
import { useSmoothPose } from "./smooth";
import { SelectRing } from "./Trucks";

const MAST_MAX = { reachtruck: 6.6, forklift: 3.2, picker: 0 } as const;

export function Equipment() {
  const world = useTwin((s) => s.world);
  return (
    <group>
      {world.resources.map((r) => (
        <Machine key={r.id} id={r.id} kind={r.kind} />
      ))}
      <StagedPallets />
    </group>
  );
}

function Machine({ id, kind }: { id: string; kind: Resource["kind"] }) {
  const world = useTwin((s) => s.world);
  useTwin((s) => s.hudVersion);
  const labels = useTwin((s) => s.labels);
  const selected = useTwin((s) => s.selected);
  const select = useTwin((s) => s.select);
  const get = () => world.resources.find((r) => r.id === id);
  const ref = useSmoothPose(() => get(), 12);
  const r = get();
  if (!r) return null;
  const isSel = selected?.kind === "resource" && selected.id === id;
  const status = resourceStatus(r, world);
  const showLabel = labels === "all" || (labels === "fleet" && kind !== "picker") || isSel;
  return (
    <group ref={ref} onClick={(e) => { e.stopPropagation(); select({ kind: "resource", id }); }}>
      {kind === "picker" ? <PickerModel tone={status.tone} /> : <LiftModel id={id} kind={kind} />}
      {isSel && <SelectRing radius={kind === "picker" ? 0.9 : 1.6} />}
      {showLabel && (
        <Html position={[0, kind === "reachtruck" ? 3.8 : 2.6, 0]} center zIndexRange={[30, 0]}>
          <button type="button" className={`tag tag-small ${isSel ? "tag-selected" : ""}`} onClick={() => select({ kind: "resource", id })}>
            <span className="tag-dot" style={{ background: toneColor(status.tone) }} />
            <b>{r.id}</b>
            <span>{status.label}</span>
          </button>
        </Html>
      )}
    </group>
  );
}

function PickerModel({ tone }: { tone: string }) {
  return (
    <group>
      <mesh position={[0, 0.75, 0]} castShadow>
        <capsuleGeometry args={[0.24, 0.8, 4, 10]} />
        <meshStandardMaterial color={C.picker} />
      </mesh>
      <mesh position={[0, 1.55, 0]} castShadow>
        <sphereGeometry args={[0.2, 12, 10]} />
        <meshStandardMaterial color="#fde3c8" />
      </mesh>
      <mesh position={[0, 0.35, 0.65]} castShadow>
        <boxGeometry args={[0.6, 0.5, 0.8]} />
        <meshStandardMaterial color="#94a3b8" />
      </mesh>
      <mesh rotation-x={-Math.PI / 2} position={[0, 0.05, 0]}>
        <ringGeometry args={[0.42, 0.55, 24]} />
        <meshBasicMaterial color={toneColor(tone)} />
      </mesh>
    </group>
  );
}

// Ричтрак и вилочный погрузчик: шасси, мачта и каретка с вилами, высота каретки — из модели (fork 0..1).
function LiftModel({ id, kind }: { id: string; kind: "reachtruck" | "forklift" }) {
  const carriage = useRef<THREE.Group>(null);
  const load = useRef<THREE.Mesh>(null);
  const world = useTwin((s) => s.world);
  useFrame((_, delta) => {
    const r = world.resources.find((x) => x.id === id);
    if (!r || !carriage.current) return;
    const target = 0.15 + r.fork * MAST_MAX[kind];
    carriage.current.position.y += (target - carriage.current.position.y) * (1 - Math.exp(-delta * 4));
    if (load.current) load.current.visible = r.carrying;
  });
  const mastH = kind === "reachtruck" ? 4.2 : 2.6;
  return (
    <group>
      <mesh position={[0, 0.65, -0.3]} castShadow>
        <boxGeometry args={[1.25, 1.0, 1.8]} />
        <meshStandardMaterial color={C.machine} />
      </mesh>
      <mesh position={[0, 1.5, -0.55]} castShadow>
        <boxGeometry args={[1.1, 0.12, 1.0]} />
        <meshStandardMaterial color={C.machineDark} />
      </mesh>
      {[-0.45, 0.45].map((x) => (
        <mesh key={x} position={[x, 1.1, -0.95]}>
          <boxGeometry args={[0.06, 0.9, 0.06]} />
          <meshStandardMaterial color={C.machineDark} />
        </mesh>
      ))}
      {[-0.4, 0.4].map((x) => (
        <mesh key={x} position={[x, mastH / 2, 0.68]} castShadow>
          <boxGeometry args={[0.1, mastH, 0.12]} />
          <meshStandardMaterial color={C.machineDark} />
        </mesh>
      ))}
      <group ref={carriage} position={[0, 0.15, 0.8]}>
        {[-0.3, 0.3].map((x) => (
          <mesh key={x} position={[x, 0, 0.55]}>
            <boxGeometry args={[0.12, 0.06, 1.1]} />
            <meshStandardMaterial color="#4b5563" />
          </mesh>
        ))}
        <mesh ref={load} position={[0, 0.5, 0.6]} castShadow visible={false}>
          <boxGeometry args={[1.0, 0.9, 1.1]} />
          <meshStandardMaterial color={C.cargo} />
        </mesh>
      </group>
      {[-0.55, 0.55].map((x) => (
        <mesh key={x} position={[x, 0.22, 0.35]} rotation-z={Math.PI / 2}>
          <cylinderGeometry args={[0.22, 0.22, 0.18, 12]} />
          <meshStandardMaterial color={C.wheel} />
        </mesh>
      ))}
    </group>
  );
}

// Паллеты СТ, выставленные у ворот своего рейса, и принятые паллеты в зоне приёмки.
function StagedPallets() {
  const world = useTwin((s) => s.world);
  useTwin((s) => s.hudVersion);
  const select = useTwin((s) => s.select);
  const items: { key: string; x: number; z: number; stId?: string; inbound?: boolean }[] = [];
  for (const gate of world.gates) {
    const sts = Object.values(world.sts).filter((s) => s.gateId === gate.id && (s.stage === "staged" || s.stage === "loading" || s.stage === "qc"));
    let i = 0;
    for (const st of sts) {
      for (let p = st.palletsLoaded; p < st.pallets; p += 1) {
        const col = i % 3;
        const row = Math.floor(i / 3);
        items.push({ key: `${st.id}:${p}`, x: gate.x - 1.4 + col * 1.4, z: world.layout.stagingZ - 1.6 - row * 1.4, stId: st.id });
        i += 1;
      }
    }
    const rec = world.mode === "sim" ? receivingPoint(gate) : { x: gate.x - 1.6, z: world.layout.stagingZ + 2.4 };
    for (let p = 0; p < Math.min(gate.received, 9); p += 1) {
      items.push({ key: `${gate.id}:rec:${p}`, x: rec.x - (p % 3) * 1.4, z: rec.z - 3.2 - Math.floor(p / 3) * 1.4, inbound: true });
    }
  }
  return (
    <group>
      {items.map((it) => (
        <group key={it.key} position={[it.x, 0, it.z]} onClick={(e) => { if (!it.stId) return; e.stopPropagation(); select({ kind: "st", id: it.stId }); }}>
          <mesh position={[0, 0.08, 0]}>
            <boxGeometry args={[1.2, 0.15, 1.0]} />
            <meshStandardMaterial color={C.pallet} />
          </mesh>
          <mesh position={[0, 0.65, 0]} castShadow>
            <boxGeometry args={[1.1, 1.0, 0.95]} />
            <meshStandardMaterial color={it.inbound ? "#e9d5b5" : world.sts[it.stId ?? ""]?.stage === "qc" ? "#c7d2fe" : C.cargo} />
          </mesh>
        </group>
      ))}
    </group>
  );
}
