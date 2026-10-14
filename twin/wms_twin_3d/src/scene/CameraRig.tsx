import { OrbitControls } from "@react-three/drei";
import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useRef } from "react";
import * as THREE from "three";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";
import { focusPoint, useTwin } from "../store/twinStore";
import { sceneDims } from "./dims";

// Домашний ракурс зависит от размера площадки: цель — центр перед фасадом, дистанция — по ширине.
function home() {
  const d = sceneDims(useTwin.getState().world);
  const scale = Math.max(1, d.width / 62);
  return { target: new THREE.Vector3(d.center.x, 0, d.center.z), offset: new THREE.Vector3(58, 74, 82).multiplyScalar(scale) };
}

type CameraCommand = "zoomIn" | "zoomOut" | "rotateLeft" | "rotateRight" | "reset";
const pending: CameraCommand[] = [];
export const cameraCommand = (cmd: CameraCommand) => { pending.push(cmd); };

// Подлёт камеры к выбранному объекту: цель и камера смещаются на одну дельту, ракурс сохраняется.
export function CameraRig() {
  const controls = useRef<OrbitControlsImpl>(null);
  const goal = useRef<THREE.Vector3 | null>(null);
  const goalDist = useRef<number | null>(null);
  const focusSeq = useTwin((s) => s.focusSeq);
  const { camera } = useThree();

  const initial = useRef(home());
  useEffect(() => {
    const h = initial.current;
    camera.position.copy(h.target).add(h.offset);
    camera.lookAt(h.target);
  }, [camera]);

  useEffect(() => {
    const s = useTwin.getState();
    const p = focusPoint(s.world, s.selected);
    if (!p || focusSeq === 0) return;
    goal.current = new THREE.Vector3(p.x, 0, p.z);
    goalDist.current = s.selected?.kind === "site" ? null : 62;
  }, [focusSeq]);

  useFrame((_, delta) => {
    const c = controls.current;
    if (!c) return;
    if (applyCommands(c, camera)) {
      goal.current = null;
      goalDist.current = null;
    }
    const s = useTwin.getState();
    if (s.follow && s.selected) {
      const p = focusPoint(s.world, s.selected);
      if (p) goal.current = new THREE.Vector3(p.x, 0, p.z);
    }
    if (goal.current) {
      const k = 1 - Math.exp(-delta * 3.5);
      const step = goal.current.clone().sub(c.target).multiplyScalar(k);
      c.target.add(step);
      camera.position.add(step);
      if (goalDist.current) {
        const off = camera.position.clone().sub(c.target);
        const len = off.length();
        off.setLength(len + (goalDist.current - len) * k);
        camera.position.copy(c.target).add(off);
      }
      if (c.target.distanceTo(goal.current) < 0.05 && !s.follow) {
        goal.current = null;
        goalDist.current = null;
      }
    }
    c.update();
  });

  return (
    <OrbitControls
      ref={controls}
      makeDefault
      target={initial.current.target.toArray() as [number, number, number]}
      enableDamping
      dampingFactor={0.12}
      minDistance={12}
      maxDistance={420}
      maxPolarAngle={1.25}
      screenSpacePanning={false}
    />
  );
}

// Возвращает true, если среди команд был сброс вида — тогда текущий подлёт отменяется.
function applyCommands(c: OrbitControlsImpl, camera: THREE.Camera): boolean {
  let reset = false;
  while (pending.length) {
    const cmd = pending.shift()!;
    applyCommand(c, camera, cmd);
    if (cmd === "reset") reset = true;
  }
  return reset;
}

function applyCommand(c: OrbitControlsImpl, camera: THREE.Camera, cmd: CameraCommand) {
  const off = camera.position.clone().sub(c.target);
  if (cmd === "zoomIn") off.multiplyScalar(0.75);
  if (cmd === "zoomOut") off.multiplyScalar(1.33);
  if (cmd === "rotateLeft" || cmd === "rotateRight") off.applyAxisAngle(new THREE.Vector3(0, 1, 0), cmd === "rotateLeft" ? Math.PI / 4 : -Math.PI / 4);
  if (cmd === "reset") {
    const h = home();
    c.target.copy(h.target);
    off.copy(h.offset);
    useTwin.getState().select(undefined, false);
  }
  camera.position.copy(c.target).add(off);
}
