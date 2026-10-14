import { Html, RoundedBox } from "@react-three/drei";
import { useMemo } from "react";
import type { Trip } from "../contracts/twin";
import { tripById } from "../sim/journal";
import { useTwin } from "../store/twinStore";
import { riskBadge, tripStatus } from "../ui/format";
import { C, toneColor } from "./palette";
import { useSmoothPose } from "./smooth";

const ON_MAP = new Set(["arriving", "queued", "reversing", "docked", "departing"]);

export function Trucks() {
  const entitiesVersion = useTwin((s) => s.entitiesVersion);
  const world = useTwin((s) => s.world);
  const ids = useMemo(() => world.trips.filter((t) => t.phase !== "planned").map((t) => t.id), [world, entitiesVersion]);
  return (
    <group>
      {ids.map((id) => (
        <Truck key={id} id={id} />
      ))}
    </group>
  );
}

function Truck({ id }: { id: string }) {
  const world = useTwin((s) => s.world);
  useTwin((s) => s.hudVersion);
  const labels = useTwin((s) => s.labels);
  const selected = useTwin((s) => s.selected);
  const select = useTwin((s) => s.select);
  const ref = useSmoothPose(() => {
    const t = tripById(world, id);
    return t && ON_MAP.has(t.phase) ? t : undefined;
  });
  const trip = tripById(world, id);
  if (!trip || !ON_MAP.has(trip.phase)) return null;
  const isSel = selected?.kind === "trip" && selected.id === id;
  const status = tripStatus(trip);
  const risk = riskBadge(trip);
  return (
    <group ref={ref} onClick={(e) => { e.stopPropagation(); select({ kind: "trip", id }); }}>
      <TruckModel trip={trip} />
      {isSel && <SelectRing radius={trip.vehicle.length / 2 + 1.2} />}
      {labels !== "none" && (
        <Html position={[0, 4.6, 0]} center zIndexRange={[40, 0]}>
          <button type="button" className={`tag ${isSel ? "tag-selected" : ""}`} onClick={() => select({ kind: "trip", id })}>
            <span className="tag-dot" style={{ background: toneColor(status.tone) }} />
            <b>{trip.id}</b>
            <span>{status.label}</span>
            {risk && <span className={`tag-risk tone-${risk.tone}`}>{risk.label}</span>}
          </button>
        </Html>
      )}
    </group>
  );
}

export function SelectRing({ radius }: { radius: number }) {
  return (
    <mesh rotation-x={-Math.PI / 2} position={[0, 0.06, 0]}>
      <ringGeometry args={[radius - 0.25, radius, 48]} />
      <meshBasicMaterial color={C.select} transparent opacity={0.9} />
    </mesh>
  );
}

function TruckModel({ trip }: { trip: Trip }) {
  const L = trip.vehicle.length;
  const cabLen = 2.3;
  const trailerLen = L - cabLen - 0.25;
  const trailerH = trip.vehicle.pallets <= 4 ? 2.3 : 3;
  const cabColor = trip.direction === "out" ? C.fleetCab : C.inboundCab;
  const wheelsZ = useMemo(() => [L / 2 - 1.2, -L / 2 + 1.4, -L / 2 + 2.6].filter((_, i) => i < 2 || L > 10), [L]);
  return (
    <group>
      <RoundedBox args={[2.4, 2.5, cabLen]} radius={0.28} smoothness={3} position={[0, 1.65, L / 2 - cabLen / 2]} castShadow>
        <meshStandardMaterial color={cabColor} />
      </RoundedBox>
      <mesh position={[0, 2.25, L / 2 - 0.02]}>
        <boxGeometry args={[2.1, 0.9, 0.05]} />
        <meshStandardMaterial color="#1e293b" />
      </mesh>
      <RoundedBox args={[2.5, trailerH, trailerLen]} radius={0.12} smoothness={2} position={[0, 0.75 + trailerH / 2, -L / 2 + trailerLen / 2]} castShadow>
        <meshStandardMaterial color={C.trailer} />
      </RoundedBox>
      <mesh position={[1.26, 0.75 + trailerH * 0.45, -L / 2 + trailerLen / 2]}>
        <boxGeometry args={[0.02, 0.35, trailerLen * 0.8]} />
        <meshBasicMaterial color={trip.direction === "out" ? C.stripe : "#64748b"} />
      </mesh>
      <mesh position={[-1.26, 0.75 + trailerH * 0.45, -L / 2 + trailerLen / 2]}>
        <boxGeometry args={[0.02, 0.35, trailerLen * 0.8]} />
        <meshBasicMaterial color={trip.direction === "out" ? C.stripe : "#64748b"} />
      </mesh>
      {trip.vehicle.reefer && (
        <mesh position={[0, 0.75 + trailerH * 0.7, -L / 2 + trailerLen + 0.15]}>
          <boxGeometry args={[1.8, 1.1, 0.35]} />
          <meshStandardMaterial color="#cbd5e1" />
        </mesh>
      )}
      {wheelsZ.map((z) => (
        <group key={z} position={[0, 0.45, z]}>
          {[-1.1, 1.1].map((x) => (
            <mesh key={x} position={[x, 0, 0]} rotation-z={Math.PI / 2}>
              <cylinderGeometry args={[0.45, 0.45, 0.35, 14]} />
              <meshStandardMaterial color={C.wheel} />
            </mesh>
          ))}
        </group>
      ))}
    </group>
  );
}
