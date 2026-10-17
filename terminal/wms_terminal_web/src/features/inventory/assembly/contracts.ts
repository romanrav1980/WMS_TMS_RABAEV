// Assembly Scale API v1 (ASSEMBLY_SCALE_API_V1.md, Codex). Field names match the frozen backend contract exactly.
// "state", not "status". No browser-computed mass: every weight here is server-reported evidence only.

export interface AssemblyCredentials { username: string; password: string }

export type PolicyState = "CONFIGURED" | "UNCONFIGURED";
export interface AssemblyLine {
  case_line_id: number; article: string; name: string; status?: string; source_cell?: string; product_codes?: string[]; remaining_quantity: string; base_uom: string; policy_state: PolicyState;
}

export interface TareCapture { capture_key: string; weight_kg: string; measured_at: string }
export type ConfirmationMode = "AUTO" | "BUTTON";
export type DeviceMode = "TEST" | "HARDWARE";
export interface AssemblyStation {
  device_id: string; post_cell: string; confirmation_mode: ConfirmationMode; device_mode: DeviceMode;
  device_policy_version: number; calibration_ref: string; tare_captures: TareCapture[];
}

export type SessionState = "OPEN" | "BLOCKED" | "FINALIZED";
export type StepState = "WAITING_BEFORE" | "ARMED" | "READY" | "APPLIED" | "DISCREPANCY" | "CANCELLED";

export interface AssemblyStep {
  step_id: string; session_id: string; operation_id: string; sequence: number; case_line_id: number; article: string; quantity: string;
  state: StepState; confirmation_mode: ConfirmationMode; content_version: number;
  before_capture_id: string | null; after_capture_id: string | null;
  before_weight_kg: string | null; after_weight_kg: string | null; delta_kg: string | null;
  min_delta_kg: string | null; expected_delta_min_kg: string | null; expected_delta_max_kg: string | null;
  consent_to_auto: boolean; button_intent: boolean; block_reason: string | null; stock_posted: boolean;
}

export interface AssemblySession {
  session_id: string; task_id: number; device_id: string; post_cell: string; operator_id: string; warehouse_id: number; scan_container: string;
  state: SessionState; confirmation_mode: ConfirmationMode; content_version: number;
  tare_capture_key: string; tare_weight_kg: string; last_weight_kg: string | null; expires_at: string | null; block_reason: string | null;
  steps: AssemblyStep[]; reconciliation?: Reconciliation | null;
}

export interface AssemblyContext {
  task_id: number; task_state: string; content_version: number; scan_container: string; warehouse_id: number;
  lines: AssemblyLine[]; stations: AssemblyStation[]; active_session: AssemblySession | null;
  resource_session_id?: number | null; assigned_resource_id?: number | null; shipment_binding_state?: string; bound_pallet_identifier?: string | null;
  prepared_shipments?: { pallet_identifier: string; shipment_id: number; fulfillment_id: number; state: string }[];
  final_composition_signature?: string | null; final_signature_domain?: string; final_signature_version?: number;
}

export interface OpenSessionBody {
  session_id: string; task_id: number; device_id: string; expected_content_version: number; tare_capture_key: string; scan_container: string;
}
export interface OpenStepBody {
  step_id: string; operation_id: string; case_line_id: number; quantity: string; scan_source_cell: string; scan_product: string;
  scan_container: string; expected_content_version: number; consent_to_auto: boolean;
}
export interface FinishBody { final_capture_key: string }

/** final_readings() returns archived RRL_WH_SCALE_CAPTURE result JSON, same shape RRL_WH_SCALE_API.capture_final builds
 *  (db/migrations/2026-10-11_ni042_final_scale/002_body.sql) — not guessed. Eligibility for finish is native-checked
 *  again server-side at /finish; this is the UI's own honest pre-filter, not a second authority. */
export interface FinalCaptureCandidate {
  capture_key: string; device_id: string; post_cell: string; device_mode: DeviceMode; purpose: "EMPTY_TARE" | "FINAL_GROSS";
  case_task_id: number; case_content_version: number; scan_container: string; basis: "GROSS"; weight_kg: string;
  device_policy_version: number; calibration_ref: string; measured_at: string; status: string; stock_posted: boolean;
  tare_capture_key?: string; tare_weight_kg?: string; net_weight_kg?: string; composition_signature?: string; signature_domain?: string; composition_signature_version?: number;
}

export const UNRESOLVED_STEP_STATES: ReadonlySet<StepState> = new Set(["WAITING_BEFORE", "ARMED", "READY"]);

export interface CaseCloseBody { operation_id: string; expected_content_version: number }
export interface CaseCloseAck {
  session_id: string; case_pick_task_id: number; operation_id: string; status: string;
  content_version: number; already_closed: boolean; physical_stock_changed: false;
}


export type ReconciliationState = "REQUESTED" | "AUTHORIZED" | "COMPLETED" | "DISCREPANCY";
export interface Reconciliation {
  reconciliation_id: string; session_id: string; step_id: string; case_task_id: number;
  state: ReconciliationState; requester_id: string; controller_id: string | null;
  expected_weight_kg: string; expected_content_version: number; operation_id?: string;
}
export interface RecoveryRequestBody { operation_id: string; step_id: string; expected_content_version: number; reason: string }
export interface RecoveryAuthorizeBody { operation_id: string; reason: string; unaccepted_goods_removed: true }




