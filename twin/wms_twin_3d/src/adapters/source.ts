import type { SourceMode, TwinState } from "../contracts/twin";
import { createSimulator } from "../sim/engine";
import { createTmsLiveSource } from "./tmsLive";

// Источник состояния двойника. Сцена и панели не знают, откуда пришли данные:
// мок-симуляция и live-адаптер ТМС отдают один и тот же TwinState.
export type TwinSource = {
  mode: SourceMode;
  world: TwinState;
  // Продвинуть источник на simSeconds модельного времени (live-адаптер время не двигает).
  advance: (simSeconds: number) => void;
  status: () => { ok: boolean; message: string };
  dispose: () => void;
};

export function createSimSource(seed?: number): TwinSource {
  const sim = createSimulator(seed);
  return {
    mode: "sim",
    world: sim.world,
    advance: sim.advance,
    status: () => ({ ok: true, message: "Симуляция · мок-данные по шагам процессов WMS/TMS" }),
    dispose: () => undefined
  };
}

export function createSource(): TwinSource {
  const params = new URLSearchParams(window.location.search);
  if (params.get("source") === "live") return createTmsLiveSource();
  return createSimSource(Number(params.get("seed")) || undefined);
}
