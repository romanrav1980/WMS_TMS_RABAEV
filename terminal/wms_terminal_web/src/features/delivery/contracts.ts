export interface StoreCredentials { username: string; password: string }

export type ReceiptMode = "BARCODE" | "WEIGHT_PHOTO" | "PAPER_COUNT";

export interface StoreSummary {
 store_id: string;
 address: string;
 receipt_mode: ReceiptMode;
 policy_version: number;
}

export interface StoreSession {
 username: string;
 display_name: string;
 access_revision: number;
 stores: StoreSummary[];
 limit: number;
 has_more: boolean;
 auth_scope: string;
}

export type TimeStatus = "UNRESOLVED_SERVER_LOCAL" | "AWARE";

export interface DeliveryListItem {
 load_operation_id: string;
 trip_id: number;
 root_key: string;
 gross_weight_kg: number | null;
 departed_at: string | null;
 time_status: TimeStatus;
 receipt_operation_id?: string | null;
 receipt_state?: string | null;
}

export interface DeliveryListResponse {
 store_id: string;
 items: DeliveryListItem[];
 next_after: string | null;
 limit: number;
}

export interface UnloadingDetails { start_operation_id: string; method: "ROLL_CAGE" | "PALLET" | "MANUAL"; rolling_difficult: boolean; loader_present: boolean; evidence_reference: string }
export interface UnloadingFact { operation_id: string; started_at_instant: string; status: "STARTED" | "COMPLETED"; finished_at_instant?: string | null; actual_details?: UnloadingDetails | null }
export interface UnloadingStartBody { operation_id: string; load_operation_id: string; store_address: string; expected_composition_signature: string; scan_place: string; before_cameras: boolean }

export interface StoreUnitScan { system_code: string; profile_code: string; code: string; disposition?: "ACCEPTED" | "REFUSED" | "DAMAGED" }
export interface StoreAggregateScan extends StoreUnitScan { level: "BOX" | "PALLET" }

export interface StoreMarkProfile { system_code: string; profile_code: string; profile_version: string; scan_mode: string }
export interface StoreMarkControl {
 supported: boolean;
 reason?: string;
 physical_unit_count?: number;
 expected_scan_count?: number;
 profiles?: StoreMarkProfile[];
 units?: Array<{ key: string; lot_uid?: string; article?: string; quantity: string; base_uom: string; profiles?: StoreMarkProfile[] }>;
 ordinary_lots?: string[];
}

export interface StoreBoxMass {
 box_uid: string;
 sscc?: string | null;
 gross_weight_kg: string;
 tare_weight_kg?: string | null;
 net_weight_kg?: string | null;
 origin: "MANUAL_CONFIRMED" | "WAREHOUSE_SCALE_QC";
 device_mode?: "TEST" | "HARDWARE" | null;
 coverage_complete?: boolean;
 final_scale_capture?: string | null;
 warehouse_qc_operation?: string | null;
}

export interface StorePreview {
 receipt?: { operation_id: string; state: string; result: ReceiptResult | null } | null;
 unloading?: UnloadingFact | null;
 marked_unit_control?: StoreMarkControl;
 marked_partial_control?: boolean;
 physical_boxes?: StoreBoxMass[];
 load_operation_id: string;
 store_address: string;
 root: string;
 root_scan_identifier: string;
 root_sscc?: string | null;
 composition_signature: string;
 mode: ReceiptMode;
 shipping_gross_weight_kg: string;
 shipping_weight_tolerance_kg: string | null;
 requires_marked_recipient_flow: boolean;
 already_received: boolean;
 policy_version?: number;
 snapshot: { nodes: Array<{ uid: string; kind: string; article?: string; quantity?: string; base_uom?: string }> };
}

export interface StoreDisposition { lot_uid: string; accepted: string; missing: string; refused: string; damaged: string; extra: string }
export interface WeightEvidence { scale_capture_key: string; photo_ids: string[]; weight_act_confirmed?: boolean }

export interface ReceiptBody {
 aggregation_scans?: StoreAggregateScan[];
 unloading?: UnloadingDetails;
 scans?: StoreUnitScan[];
 operation_id: string;
 load_operation_id: string;
 store_address: string;
 scan_place: string;
 expected_composition_signature: string;
 before_cameras: boolean;
 observations?: StoreDisposition[];
 case_note?: string;
 scale_capture_key?: string;
 manual_weight_kg?: string;
 photo_ids?: string[];
 weight_act_confirmed?: boolean;
 paper_reference?: string;
}

export interface PendingReceipt { body: ReceiptBody; confirmedRejection?: boolean }

export interface ReceiptResultLine { line_no: number; lot_uid: string; article: string; base_uom: string; shipped?: string; accepted: string; missing?: string; refused?: string; damaged?: string; extra?: string }
export interface ReceiptResult {
 operation_id: string;
 load_operation_id: string;
 store_address: string;
 root: string;
 status: "ACCEPTED" | "DISCREPANCY";
 discrepancy_case_id?: string;
 accepted_lines: ReceiptResultLine[];
 government_ack_created?: boolean;
 regulatory_ack_verified?: boolean;
 weight?: ReceiptWeight;
}

/** Итог веса приёмки WEIGHT_PHOTO от сервера. MANUAL_CONFIRMED: capture_key/device_id/device_policy_version = null. Массы — строки сервера. */
export interface ReceiptWeight {
 capture_key: string | null; device_id: string | null; device_policy_version: number | null;
 measurement_origin: string; recorded_by: string | null;
 shipping_gross_kg: string; observed_gross_kg: string; tolerance_kg: string | null; delta_kg: string;
 in_tolerance: 0 | 1; act_confirmed: 0 | 1; photos?: { photo_id: string; view: string; sha256?: string }[];
}

export interface ReceiptStatusLookup {
 operation_id: string;
 state: "APPLIED" | "NOT_VISIBLE" | "UNKNOWN";
 outcome_confirmed: boolean;
 result?: ReceiptResult;
}

export interface ScaleCapture { capture_key: string; device_id: string; gross_weight_kg: string; received_at: string; sample_count: number; span_ms: number; calibration_ref: string }
export interface ReceiptPhoto { photo_id: string; sha256: string; view: string; recorded_at: string; recorded_by: string; mime_type: string }
