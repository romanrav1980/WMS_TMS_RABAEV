import type { TwinState } from "../contracts/twin";

// Размеры площадки берутся из layout: одна сцена рисует и демо-склад, и топологию ТМС.
export type SceneDims = {
  width: number;
  wallZ: number;
  stagingZ: number;
  frontZ: number;
  roadZ: number;
  exitZ: number;
  shoulderZ: number;
  center: { x: number; z: number };
};

export function sceneDims(w: TwinState): SceneDims {
  const width = w.layout.width;
  const wallZ = w.layout.depth;
  const rackEnd = w.cells.reduce((m, c) => Math.max(m, c.z + (c.sizeZ ?? 1.35) / 2), 0);
  const roadZ = wallZ + 32;
  return {
    width,
    wallZ,
    stagingZ: w.layout.stagingZ,
    frontZ: rackEnd + 1.8,
    roadZ,
    exitZ: roadZ + 3.6,
    shoulderZ: roadZ - 6,
    center: { x: width / 2, z: wallZ * 0.85 }
  };
}
