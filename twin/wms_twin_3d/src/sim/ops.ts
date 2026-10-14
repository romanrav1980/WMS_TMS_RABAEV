import type { OpPhase, Resource, St, TwinExecutor, TwinOperation, TwinState, WTask } from "../contracts/twin";
import { clock } from "./transport";

// Операции симуляции в том же контракте warehouse-twin-operation/1, что и live-адаптер.
// Режим SIM и расчётная траектория помечены явно (§10, §14 спецификации складских заданий).
const SUBTYPE: Record<WTask["kind"], string> = { REPL: "REPLENISHMENT", PUTAWAY: "PUTAWAY", LOAD: "SIM_LOAD", UNLOAD: "SIM_UNLOAD" };

function taskPhase(t: WTask, r?: Resource): OpPhase {
  if (t.status === "done") return "COMPLETED";
  if (t.status === "created") return "PLANNED";
  if (!r) return "ASSIGNED";
  if (r.carrying) return r.leg === "toTarget" && r.status === "working" ? "TARGET_CONFIRMED" : "CARRYING";
  if (r.leg === "toSource" && r.status === "working") return "SOURCE_CONFIRMED";
  return "STARTED";
}

function stPhase(st: St, picker?: Resource): OpPhase {
  if (st.stage === "created") return "PLANNED";
  if (st.stage === "picking") return picker?.status === "waiting" ? "BLOCKED" : st.lines.some((l) => l.picked) ? "PARTIAL" : "STARTED";
  return "COMPLETED";
}

const at = (_w: TwinState, sec?: number) => (sec === undefined ? undefined : `${clock(sec)} (модельное)`);

export function simOperations(w: TwinState): TwinOperation[] {
  const observedAt = `${clock(w.simTime)} (модельное)`;
  const cellSet = new Set(w.cells.map((c) => c.id));
  const ops: TwinOperation[] = w.tasks.map((t) => {
    const r = w.resources.find((x) => x.id === t.resourceId && x.taskId === t.id);
    const fromCell = t.fromCell;
    return {
      key: `SIM_TASK:${t.id}`,
      schemaVersion: "warehouse-twin-operation/1",
      source: { entity: "SIM", id: t.id, rawStatus: t.status, mode: "SIM", observedAt },
      warehouseId: w.layout.siteId,
      kind: "MOVE",
      subtype: SUBTYPE[t.kind],
      phase: taskPhase(t, r),
      context: { stNumber: t.stId, tripId: t.tripId, sourceDoc: t.gateId ? `Ворота ${t.gateId}` : undefined },
      executor: { resourceId: t.resourceId, label: t.resourceId },
      loadUnit: { kind: "STOCK", uid: `SIM-PAL-${t.id}` },
      from: fromCell ? { cell: fromCell, bound: cellSet.has(fromCell) } : t.gateId ? { cell: t.kind === "UNLOAD" ? `Кузов ${t.tripId}` : `Зона ${t.gateId}`, bound: false } : undefined,
      to: t.toCell ? { cell: t.toCell, bound: cellSet.has(t.toCell) } : t.gateId ? { cell: t.kind === "LOAD" ? `Кузов ${t.tripId}` : `Приёмка ${t.gateId}`, bound: false } : undefined,
      quantity: { planned: "1", confirmed: t.status === "done" ? "1" : "0", unit: "PAL", mode: "PALLET", basis: "SIM" },
      blockedReason: undefined,
      times: { created: at(w, t.createdAt) },
      routeBasis: "CALCULATED"
    };
  });
  for (const st of Object.values(w.sts)) {
    if (st.stage === "delivered") continue;
    const picker = st.pickerId ? w.resources.find((r) => r.id === st.pickerId) : undefined;
    const phase = stPhase(st, picker);
    ops.push({
      key: `SIM_ST:${st.id}`,
      schemaVersion: "warehouse-twin-operation/1",
      source: { entity: "SIM", id: st.id, rawStatus: st.stage, mode: "SIM", observedAt },
      warehouseId: w.layout.siteId,
      kind: "PICK",
      subtype: "ST_PICK",
      phase,
      context: { waveCode: st.waveId, tripId: st.tripId, stNumber: st.id, customer: st.store },
      executor: { resourceId: st.pickerId, label: st.pickerId },
      loadUnit: { kind: "CASE", uid: `SIM-CASE-${st.id}` },
      to: { cell: `Выставка ${st.gateId}`, bound: false },
      quantity: { planned: String(st.lines.reduce((n, l) => n + l.qty, 0)), confirmed: String(st.lines.filter((l) => l.picked).reduce((n, l) => n + l.qty, 0)), unit: "кор.", basis: "SIM" },
      progress: { done: st.lines.filter((l) => l.picked).length, total: st.lines.length, label: "строк" },
      lines: st.lines.map((l, i) => ({ id: `${st.id}:${i}`, cell: l.cellId, sku: l.sku, planned: String(l.qty), picked: l.picked ? String(l.qty) : "0", status: l.picked ? "DONE" : "NEW", bound: cellSet.has(l.cellId) })),
      blockedReason: phase === "BLOCKED" ? picker?.waitReason : undefined,
      times: { created: at(w, st.stageAt.created), started: at(w, st.stageAt.picking), finished: at(w, st.stageAt.picked) },
      routeBasis: "CALCULATED"
    });
  }
  return ops;
}

export function simExecutors(w: TwinState): TwinExecutor[] {
  return w.resources.map((r) => ({
    id: r.id,
    kind: { picker: "CASE_PICKER", reachtruck: "REACHTRUCK", forklift: "FORKLIFT" }[r.kind],
    code: r.id,
    name: r.name,
    wareId: w.layout.siteId,
    status: r.status,
    activeTaskId: r.taskId ?? r.stId,
    positionBasis: "SIMULATED"
  }));
}
