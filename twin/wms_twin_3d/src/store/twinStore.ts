import { create } from "zustand";
import { createSource, type TwinSource } from "../adapters/source";
import type { Selection, TwinState, Vec2 } from "../contracts/twin";
import { cellById, gateById, tripById } from "../sim/journal";

// 1 реальная секунда = SIM_SCALE модельных секунд на скорости ×1.
export const SIM_SCALE = 8;
export const SPEEDS = [1, 2, 5, 10] as const;
export type LabelLayer = "all" | "fleet" | "none";
export type BottomTab = "ops" | "journey" | "docks" | "gate" | "events";

type TwinStore = {
  source: TwinSource;
  world: TwinState;
  version: number;
  hudVersion: number;
  layoutVersion: number;
  entitiesVersion: number;
  stockVersion: number;
  speed: number;
  paused: boolean;
  selected?: Selection;
  focusSeq: number;
  follow: boolean;
  labels: LabelLayer;
  heatmap: boolean;
  bottomTab: BottomTab;
  panelsHidden: boolean;
  tick: (realDt: number) => void;
  select: (sel?: Selection, focus?: boolean) => void;
  setSpeed: (speed: number) => void;
  togglePause: () => void;
  setFollow: (follow: boolean) => void;
  setLabels: (labels: LabelLayer) => void;
  toggleHeatmap: () => void;
  setBottomTab: (tab: BottomTab) => void;
  togglePanels: () => void;
};

const source = createSource();
let hudAccumulator = 0;

// world — изменяемая проекция источника; счётчики версий служат сигналами для перерисовки:
// version — каждый тик (сцена читает в useFrame), hudVersion — 4 раза в секунду (панели),
// entitiesVersion — появились/исчезли машины, stockVersion — изменились остатки ячеек.
export const useTwin = create<TwinStore>((set, get) => ({
  source,
  world: source.world,
  version: 0,
  hudVersion: 0,
  layoutVersion: 0,
  entitiesVersion: 0,
  stockVersion: 0,
  speed: 1,
  paused: false,
  focusSeq: 0,
  follow: false,
  labels: "fleet",
  heatmap: false,
  bottomTab: source.mode === "live" ? "ops" : "journey",
  panelsHidden: false,
  tick: (realDt) => {
    const s = get();
    if (!s.paused) s.source.advance(realDt * SIM_SCALE * s.speed);
    hudAccumulator += realDt;
    const w = s.source.world;
    const patch: Partial<TwinStore> = { version: s.version + 1 };
    if (hudAccumulator >= 0.25) {
      hudAccumulator = 0;
      patch.hudVersion = s.hudVersion + 1;
    }
    if (w.layoutVersion !== s.layoutVersion) patch.layoutVersion = w.layoutVersion;
    if (w.entitiesVersion !== s.entitiesVersion) patch.entitiesVersion = w.entitiesVersion;
    if (w.stockVersion !== s.stockVersion) patch.stockVersion = w.stockVersion;
    set(patch);
  },
  select: (sel, focus = true) => set((s) => ({ selected: sel, focusSeq: focus ? s.focusSeq + 1 : s.focusSeq, follow: sel?.kind === "trip" || sel?.kind === "resource" ? s.follow : false })),
  setSpeed: (speed) => set({ speed, paused: false }),
  togglePause: () => set((s) => ({ paused: !s.paused })),
  setFollow: (follow) => set({ follow }),
  setLabels: (labels) => set({ labels }),
  toggleHeatmap: () => set((s) => ({ heatmap: !s.heatmap })),
  setBottomTab: (bottomTab) => set({ bottomTab }),
  togglePanels: () => set((s) => ({ panelsHidden: !s.panelsHidden }))
}));

// Мировая точка выбранного объекта — для подлёта камеры.
export function focusPoint(w: TwinState, sel?: Selection): Vec2 | undefined {
  if (!sel) return undefined;
  switch (sel.kind) {
    case "trip": {
      const trip = tripById(w, sel.id);
      if (!trip) return undefined;
      if (trip.phase === "planned" || trip.phase === "transit" || trip.phase === "done") {
        const gate = gateById(w, trip.gateId);
        return gate ? { x: gate.x, z: w.layout.depth + 8 } : undefined;
      }
      return trip.pos;
    }
    case "resource":
      return w.resources.find((r) => r.id === sel.id)?.pos;
    case "gate": {
      const gate = gateById(w, sel.id);
      return gate ? { x: gate.x, z: w.layout.depth + 2 } : undefined;
    }
    case "cell": {
      const cell = cellById(w, sel.id);
      return cell ? { x: cell.x, z: cell.z } : undefined;
    }
    case "st": {
      const st = w.sts[sel.id];
      const picker = st?.pickerId && st.stage === "picking" ? w.resources.find((r) => r.id === st.pickerId) : undefined;
      if (picker) return picker.pos;
      const gate = st ? gateById(w, st.gateId) : undefined;
      return gate ? { x: gate.x, z: w.layout.stagingZ } : undefined;
    }
    case "collision": {
      const c = w.collisions.find((x) => x.key === sel.id);
      return c && c.bound !== false ? c.pos : undefined;
    }
    case "operation": {
      const op = w.operations.find((o) => o.key === sel.id);
      const cellId = [op?.to, op?.from].find((l) => l?.bound)?.cell ?? op?.lines?.find((l) => l.bound)?.cell;
      const cell = cellById(w, cellId);
      return cell ? { x: cell.x, z: cell.z } : undefined;
    }
    case "executor": {
      const ex = w.executors.find((e) => e.id === sel.id);
      if (ex?.positionBasis === "SIMULATED") return w.resources.find((r) => r.id === ex.id)?.pos;
      const cell = ex?.positionBasis === "OBSERVED_CELL" ? cellById(w, ex.lastCell) : undefined;
      return cell ? { x: cell.x, z: cell.z } : undefined;
    }
    case "site":
      return { x: w.layout.width / 2, z: w.layout.depth * 0.75 };
  }
}
