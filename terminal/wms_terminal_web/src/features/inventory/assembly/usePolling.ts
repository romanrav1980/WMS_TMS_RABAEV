import { useEffect, useRef } from "react";

/** Bounded fixed-interval poll. Each mount (including StrictMode's double-invoke) owns its own controller/disposed
 *  flag, so a late response from a previous effect run never lands on the current one. Not a second timeline/engine. */
export function usePolling(active: boolean, intervalMs: number, tick: (signal: AbortSignal) => Promise<void>): void {
  const tickRef = useRef(tick);
  tickRef.current = tick;
  useEffect(() => {
    if (!active) return;
    let disposed = false, timer: ReturnType<typeof setTimeout> | null = null;
    const controller = new AbortController();
    const run = () => {
      if (disposed) return;
      tickRef.current(controller.signal).catch(() => {}).finally(() => { if (!disposed) timer = setTimeout(run, intervalMs); });
    };
    run();
    return () => { disposed = true; controller.abort(); if (timer) clearTimeout(timer); };
  }, [active, intervalMs]);
}
