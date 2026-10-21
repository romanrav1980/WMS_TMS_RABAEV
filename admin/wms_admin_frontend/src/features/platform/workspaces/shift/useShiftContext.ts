import { useEffect, useMemo, useState } from "react";
import type { ResourceTimeline } from "../resources/timelineTypes";
import { useUrlWarehouse } from "../useUrlWarehouse";

/** Склад старшего смены — общий хук адреса (C0118), тот же для всех рабочих мест. */
export const useShiftWarehouse = useUrlWarehouse;
export function readUrlWave(): number | null {
  const value = Number(new URLSearchParams(location.search).get("wave_id"));
  return Number.isSafeInteger(value) && value > 0 ? value : null;
}
export function writeUrlWave(id: number | null): void {
  const url = new URL(location.href);
  if (id != null) url.searchParams.set("wave_id", String(id)); else url.searchParams.delete("wave_id");
  history.replaceState(history.state, "", url);
}
export function useShiftWave() {
  const [wave, setWave] = useState<number | null>(readUrlWave);
  useEffect(() => { const sync = () => setWave(readUrlWave()); window.addEventListener("popstate", sync); return () => window.removeEventListener("popstate", sync); }, []);
  const select = (id: number | null) => { setWave(id); writeUrlWave(id); };
  return [wave, select] as const;
}

export function useResourceKeyBySession(timeline: ResourceTimeline | null) {
  return useMemo(() => {
    const result = new Map<number, string>();
    for (const resource of timeline?.resources ?? []) {
      if (resource.last_signal?.session_id != null) result.set(resource.last_signal.session_id, resource.resource_key);
    }
    return result;
  }, [timeline]);
}
