import { Html } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import { useRef } from "react";
import type * as THREE from "three";
import type { Collision, Gate } from "../contracts/twin";
import { COLLISION_LABEL } from "../sim/collisions";
import { tripById } from "../sim/journal";
import { useTwin } from "../store/twinStore";
import { C } from "./palette";

export function Markers() {
  const world = useTwin((s) => s.world);
  useTwin((s) => s.hudVersion);
  const active = world.collisions.filter((c) => c.active && c.bound !== false);
  return (
    <group>
      {world.gates.map((g) => (
        <GateMarker key={g.id} gate={g} />
      ))}
      {active.map((c) => (
        <Hotspot key={c.key} c={c} />
      ))}
    </group>
  );
}

function gateTone(world: ReturnType<typeof useTwin.getState>["world"], gate: Gate) {
  if (world.mode === "live" && !gate.occupiedBy) {
    const booked = world.trips.filter((t) => t.gateId === gate.id && t.phase === "planned").length;
    return { color: booked ? C.info : C.idle, text: booked ? `бронь: ${booked}` : "нет брони" };
  }
  if (!gate.occupiedBy) return { color: C.ok, text: "свободны" };
  const trip = tripById(world, gate.occupiedBy);
  if (trip?.phase === "docked") return { color: trip.waitReason?.startsWith("Ждёт") ? C.warn : C.info, text: trip.id };
  return { color: C.info, text: `${gate.occupiedBy} · подъезд` };
}

function GateMarker({ gate }: { gate: Gate }) {
  const world = useTwin((s) => s.world);
  const labels = useTwin((s) => s.labels);
  const selected = useTwin((s) => s.selected);
  const select = useTwin((s) => s.select);
  const tone = gateTone(world, gate);
  const isSel = selected?.kind === "gate" && selected.id === gate.id;
  return (
    <group position={[gate.x, 0, world.layout.depth]} onClick={(e) => { e.stopPropagation(); select({ kind: "gate", id: gate.id }); }}>
      {[-2.15, 2.15].map((x) => (
        <mesh key={x} position={[x, 2.4, 0.4]} castShadow>
          <boxGeometry args={[0.25, 4.8, 0.7]} />
          <meshStandardMaterial color="#1f2937" />
        </mesh>
      ))}
      <mesh position={[0, 4.75, 0.4]}>
        <boxGeometry args={[4.5, 0.3, 0.7]} />
        <meshStandardMaterial color="#1f2937" />
      </mesh>
      <mesh position={[0, 0.55, 0.9]} receiveShadow>
        <boxGeometry args={[3.6, 1.1, 1.2]} />
        <meshStandardMaterial color="#9ca3af" />
      </mesh>
      <mesh position={[1.7, 5.25, 0.55]}>
        <sphereGeometry args={[0.22, 12, 10]} />
        <meshBasicMaterial color={tone.color} />
      </mesh>
      <mesh rotation-x={-Math.PI / 2} position={[0, 0.03, 4]}>
        <planeGeometry args={[4.6, 0.25]} />
        <meshBasicMaterial color={gate.kind === "inbound" ? "#a78bfa" : "#60a5fa"} />
      </mesh>
      {isSel && (
        <mesh rotation-x={-Math.PI / 2} position={[0, 0.05, 3]}>
          <ringGeometry args={[3, 3.3, 40]} />
          <meshBasicMaterial color={C.select} />
        </mesh>
      )}
      {labels !== "none" && (
        <Html position={[0, 6.4, 0.5]} center zIndexRange={[20, 0]}>
          <button type="button" className={`gate-tag ${gate.kind}`} onClick={() => select({ kind: "gate", id: gate.id })}>
            <b>{gate.id}</b>
            <span>{gate.kind === "inbound" ? "приёмка" : tone.text}</span>
          </button>
        </Html>
      )}
    </group>
  );
}

function Hotspot({ c }: { c: Collision }) {
  const ring = useRef<THREE.Mesh>(null);
  const select = useTwin((s) => s.select);
  const labels = useTwin((s) => s.labels);
  const color = c.severity === "critical" ? C.crit : C.warn;
  useFrame(({ clock }) => {
    if (!ring.current) return;
    const s = 1 + 0.35 * Math.sin(clock.elapsedTime * 4);
    ring.current.scale.set(s, s, s);
  });
  return (
    <group position={[c.pos.x, 0, c.pos.z]}>
      <mesh ref={ring} rotation-x={-Math.PI / 2} position={[0, 0.08, 0]}>
        <ringGeometry args={[1.1, 1.5, 32]} />
        <meshBasicMaterial color={color} transparent opacity={0.85} />
      </mesh>
      {labels !== "none" && (
        <Html position={[0, 3.2, 0]} center zIndexRange={[50, 0]}>
          <button type="button" className={`callout ${c.severity}`} onClick={() => select({ kind: "collision", id: c.key })}>
            <b>⚠ {COLLISION_LABEL[c.type]}</b>
            <span>{c.where}</span>
          </button>
        </Html>
      )}
    </group>
  );
}
