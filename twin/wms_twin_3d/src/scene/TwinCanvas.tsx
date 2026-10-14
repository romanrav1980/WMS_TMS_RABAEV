import { Canvas, useThree } from "@react-three/fiber";
import { useLayoutEffect, useRef } from "react";
import type * as THREE from "three";
import { sceneDims } from "./dims";
import { useTwin } from "../store/twinStore";
import { Building } from "./Building";
import { CameraRig } from "./CameraRig";
import { Environment } from "./Environment";
import { Equipment } from "./Equipment";
import { Markers } from "./Markers";
import { OperationsLayer } from "./OperationsLayer";
import { Racks } from "./Racks";
import { Trucks } from "./Trucks";

export function TwinCanvas() {
  const select = useTwin((s) => s.select);
  return (
    <Canvas
      className="twin-canvas"
      shadows
      dpr={[1, 2]}
      camera={{ fov: 32, near: 1, far: 900 }}
      onPointerMissed={() => select(undefined, false)}
    >
      <color attach="background" args={["#eef2f7"]} />
      <fog attach="fog" args={["#eef2f7", 260, 520]} />
      <hemisphereLight args={["#ffffff", "#c8d2e0", 0.9]} />
      <Sun />
      <Environment />
      <Building />
      <Racks />
      <Markers />
      <OperationsLayer />
      <Equipment />
      <Trucks />
      <CameraRig />
    </Canvas>
  );
}

function Sun() {
  const light = useRef<THREE.DirectionalLight>(null);
  const scene = useThree((s) => s.scene);
  const world = useTwin((s) => s.world);
  const d = sceneDims(world);
  const span = Math.max(120, d.width + 60, d.wallZ + 60);
  useLayoutEffect(() => {
    const l = light.current;
    if (!l) return;
    l.target.position.set(d.width / 2, 0, d.wallZ / 2 + 10);
    scene.add(l.target);
    return () => { scene.remove(l.target); };
  }, [scene, d.width, d.wallZ]);
  return (
    <directionalLight
      ref={light}
      position={[d.width / 2 + 70, 110, d.wallZ + 60]}
      intensity={1.6}
      castShadow
      shadow-mapSize={[2048, 2048]}
      shadow-camera-left={-span}
      shadow-camera-right={span}
      shadow-camera-top={span}
      shadow-camera-bottom={-span}
      shadow-camera-near={10}
      shadow-camera-far={400}
      shadow-bias={-0.0004}
    />
  );
}
