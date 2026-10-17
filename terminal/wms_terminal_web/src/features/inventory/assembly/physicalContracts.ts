import type { AssemblyContext } from "./contracts";
export type WeighPurpose = "EMPTY_TARE" | "FINAL_GROSS";
export interface WeighBody { request_id: string; device_id: string; purpose: WeighPurpose; case_task_id: number; expected_content_version: number; scan_container: string; zero_progress_required: true; resource_session_id?: number; tare_capture_key?: string; expected_composition_signature?: string }
export interface WeighState { request_id: string; device_id: string; purpose: WeighPurpose; case_task_id: number; state: "REQUESTED" | "CLAIMED" | "CAPTURED" | "EXPIRED" | "STALE"; current_context: "CURRENT" | "STALE"; capture_key: string | null; claim_id: string | null; stock_posted: false; zero_progress_required: true; measurement_stage: string; load_allowed: boolean; claim_expires_at: string | null; server_now: string; zero_source_sha256: string | null; zero_confirmed_at: string | null; reason?: string | null }
export interface BindBody { pallet_identifier: string; scan_container: string; expected_content_version: number }
export const WEIGH_PATH = "/api/inventory/warehouse-scales/requests";
export const bindPath = (task: number): string => `/api/case-pick/tasks/${task}/bind-shipment`;
export const keyPattern = /^[A-F0-9]{64}$/;
export function validWeigh(value: unknown, body: WeighBody): WeighState {
  const v = value as WeighState;
  if (!v || v.request_id !== body.request_id || v.device_id !== body.device_id || v.purpose !== body.purpose || v.case_task_id !== body.case_task_id || v.stock_posted !== false || v.zero_progress_required !== true || typeof v.load_allowed !== "boolean" || typeof v.server_now !== "string" || !Number.isFinite(Date.parse(v.server_now))
    || !["REQUESTED","CLAIMED","CAPTURED","EXPIRED","STALE"].includes(v.state) || !["CURRENT","STALE"].includes(v.current_context)
    || (v.state === "CAPTURED" && (typeof v.capture_key !== "string" || !keyPattern.test(v.capture_key) || typeof v.claim_id !== "string" || !v.claim_id))) throw new Error("Ответ весов не подтверждает исходный запрос. Журнал сохранён.");
  return v;
}
export function terminalWeigh(value: WeighState): boolean { return value.state === "CAPTURED" || value.state === "EXPIRED" || value.state === "STALE" && value.current_context === "STALE" && value.reason === "CURRENT_SOURCE_ASSIGNMENT_OR_POLICY_CHANGED"; }
export function loadDeadline(value: WeighState, started: number): number {
  if (value.state !== "CLAIMED" || value.current_context !== "CURRENT" || value.measurement_stage !== "ZERO_CONFIRMED" || value.load_allowed !== true || !value.claim_id
    || !value.zero_source_sha256 || !keyPattern.test(value.zero_source_sha256) || !value.zero_confirmed_at || !value.claim_expires_at) return 0;
  const ttl = Date.parse(value.claim_expires_at) - Date.parse(value.server_now);
  return Number.isFinite(ttl) && ttl > 0 && ttl <= 30000 ? started + ttl : 0; // Conservative: subtract the entire response round trip; no PC clock/timezone.
}
export function boundContext(value: AssemblyContext, task: number, body: BindBody): boolean {
  return value.task_id === task && value.content_version === body.expected_content_version && value.shipment_binding_state === "BOUND" && value.bound_pallet_identifier === body.pallet_identifier && value.scan_container === body.scan_container;
}
