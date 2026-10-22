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

const AWAITING_SHIPMENT = new Set(["WAIT_CONTROL", "CONTROL_IN_PROGRESS", "CONTROLLED", "READY_TO_SHIP"]);
/** Фактическая стадия сборки волны по её CASE-заданиям (closed states как в case_close_state.py), не по схеме.
 *  Неизвестный статус или нет заданий — null: стадия не угадывается. */
export function caseStage(statuses: string[]): "PICKING" | "AWAITING_SHIPMENT" | "SHIPPED" | null {
  const live = statuses.filter(s => s !== "CANCELLED");
  if (!live.length) return null;
  if (live.some(isOpenCase)) return "PICKING";
  if (live.every(s => s === "SHIPPED")) return "SHIPPED";
  return live.every(s => s === "SHIPPED" || AWAITING_SHIPMENT.has(s)) ? "AWAITING_SHIPMENT" : null;
}
/** Пополнение ещё актуально: завершённое и отменённое (его wait_reason — причина отмены) не ждёт и не считается. */
export const isOpenReplenishment = (status: string) => status !== "DONE" && status !== "CANCELLED";
