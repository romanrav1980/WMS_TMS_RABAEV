/** Same open CASE states as inventory/domain/case_close_state.py; no inferred progress or permission. */
export const isOpenCase = (status: string) => new Set([
  "NEW", "ASSIGNED", "IN_PROGRESS", "PARTIAL", "WAIT_REPLENISHMENT", "PICKED",
]).has(status);

/** Actual native shortage decision states, not transport/task status names. */
export const isPendingShort = (status: string) => status === "CREATED" || status === "PENDING_APPROVAL";

/** Read completeness is independent of a successful source returning zero blockers. */
export function preparationComplete(detail: {
  readiness: { data: unknown; error: string }; pick: { data: unknown; error: string };
  time: { data: unknown; error: string }; replenishment: { data: unknown; error: string };
} | undefined): boolean {
  return !!detail && [detail.readiness, detail.pick, detail.time, detail.replenishment]
    .every(source => source.data != null && !source.error);
}
export const isClosedWave = (status: string) => status === "DONE" || status === "CANCELLED";
