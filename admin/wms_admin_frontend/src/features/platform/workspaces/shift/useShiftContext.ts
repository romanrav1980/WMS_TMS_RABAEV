import { useMemo, useState } from "react";
import type { ResourceTimeline } from "../resources/timelineTypes";
import { useUrlWarehouse } from "../useUrlWarehouse";

/** Склад старшего смены — общий хук адреса (C0118), тот же для всех рабочих мест. */
export const useShiftWarehouse = useUrlWarehouse;

export function useResourceKeyBySession(timeline: ResourceTimeline | null) {
  return useMemo(() => {
    const result = new Map<number, string>();
    for (const resource of timeline?.resources ?? []) {
      if (resource.last_signal?.session_id != null) result.set(resource.last_signal.session_id, resource.resource_key);
    }
    return result;
  }, [timeline]);
}
