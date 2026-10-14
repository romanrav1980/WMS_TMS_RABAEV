import type { Cell, EventLevel, TwinEvent, TwinState } from "../contracts/twin";

const EVENT_LIMIT = 300;

export function nextId(w: TwinState, prefix: string): string {
  w.counters.seq += 1;
  return `${prefix}${w.counters.seq}`;
}

export function logEvent(
  w: TwinState,
  what: string,
  entity: string,
  level: EventLevel = "info",
  extra: Pick<TwinEvent, "where" | "why" | "who"> = {}
) {
  w.events.unshift({ id: w.counters.eventSeq++, at: w.simTime, what, entity, level, source: "sim", ...extra });
  if (w.events.length > EVENT_LIMIT) w.events.length = EVENT_LIMIT;
}

export function cellById(w: TwinState, id?: string): Cell | undefined {
  if (!id) return undefined;
  const index = w.cellIndex[id];
  return index === undefined ? undefined : w.cells[index];
}

export function gateById(w: TwinState, id?: string) {
  return w.gates.find((g) => g.id === id);
}

export function tripById(w: TwinState, id?: string) {
  return w.trips.find((t) => t.id === id);
}
