import { useFrame } from "@react-three/fiber";
import { useRef } from "react";
import type * as THREE from "three";
import type { Vec2 } from "../contracts/twin";

// Модель шагает с частотой 10 Гц, кадр рисуется на 60 Гц: сцена догоняет позицию экспоненциальным сглаживанием.
export function useSmoothPose(read: () => { pos: Vec2; heading: number } | undefined, rate = 10) {
  const ref = useRef<THREE.Group>(null);
  const init = useRef(false);
  useFrame((_, delta) => {
    const g = ref.current;
    const pose = read();
    if (!g || !pose) return;
    if (!init.current) {
      g.position.set(pose.pos.x, 0, pose.pos.z);
      g.rotation.y = pose.heading;
      init.current = true;
      return;
    }
    const k = 1 - Math.exp(-delta * rate);
    const jump = Math.hypot(g.position.x - pose.pos.x, g.position.z - pose.pos.z) > 25;
    g.position.x = jump ? pose.pos.x : g.position.x + (pose.pos.x - g.position.x) * k;
    g.position.z = jump ? pose.pos.z : g.position.z + (pose.pos.z - g.position.z) * k;
    let d = pose.heading - g.rotation.y;
    d = Math.atan2(Math.sin(d), Math.cos(d));
    g.rotation.y += d * Math.min(1, k * 1.2);
  });
  return ref;
}
