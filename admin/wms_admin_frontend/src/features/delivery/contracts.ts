export interface UnloadingDetails {start_operation_id:string;method:"ROLL_CAGE"|"PALLET"|"MANUAL";rolling_difficult:boolean;loader_present:boolean;evidence_reference:string}
export interface UnloadingFact {operation_id:string;started_at_instant:string;status:"STARTED"|"COMPLETED";finished_at_instant?:string|null;actual_details?:UnloadingDetails|null}
export interface UnloadingStartBody {operation_id:string;load_operation_id:string;store_address:string;expected_composition_signature:string;scan_place:string;before_cameras:boolean}
export interface StoreUnitScan {system_code:string;profile_code:string;code:string;disposition?:"ACCEPTED"|"REFUSED"|"DAMAGED"}
export interface StoreAggregateScan extends StoreUnitScan {level:"BOX"|"PALLET"}
export interface ReturnAggregateScan {system_code:string;profile_code:string;level:"BOX"|"PALLET";code:string}
export interface ReturnMarkEvidence {scans:StoreUnitScan[];aggregation_scans:ReturnAggregateScan[]}
export interface StoreMarkProfile {system_code:string;profile_code:string;profile_version:string;scan_mode:string}
export interface StoreMarkControl {
 supported:boolean;reason?:string;physical_unit_count?:number;expected_scan_count?:number;
 profiles?:StoreMarkProfile[];
 units?:Array<{key:string;lot_uid?:string;article?:string;quantity:string;base_uom:string;profiles?:StoreMarkProfile[]}>;
 ordinary_lots?:string[];
}
export interface StorePlace {
 load_operation_id: string;
 root_key: string;
 receipt_state: string | null;
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
 unloading?:UnloadingFact|null;
 marked_unit_control?: StoreMarkControl;
 marked_partial_control?: boolean;
 physical_boxes?: StoreBoxMass[];
 load_operation_id: string;
 store_address: string;
 root: string;
 root_scan_identifier: string;
 composition_signature: string;
 mode: "BARCODE" | "WEIGHT_PHOTO" | "PAPER_COUNT";
 shipping_gross_weight_kg: string;
 shipping_weight_tolerance_kg: string|null;
 requires_marked_recipient_flow: boolean;
 already_received: boolean;
 snapshot: { nodes: Array<{uid: string; kind: string; article?: string; quantity?: string; base_uom?: string}> };
}
export interface StoreDisposition {
 lot_uid: string; accepted: string; missing: string; refused: string; damaged: string; extra: string;
}
export interface WeightEvidence {scale_capture_key:string;photo_ids:string[];weight_act_confirmed?:boolean}
export interface ReceiptBody {
 aggregation_scans?:StoreAggregateScan[];
 unloading?:UnloadingDetails;
 scans?: StoreUnitScan[];
 operation_id: string;
 load_operation_id: string;
 store_address: string;
 scan_place: string;
 expected_composition_signature: string;
 before_cameras: boolean;
 observations?: StoreDisposition[];
 case_note?: string;
 scale_capture_key?:string;
 photo_ids?:string[];
 weight_act_confirmed?:boolean;
}
export interface PendingReceipt { body: ReceiptBody; confirmedRejection?: boolean }
export interface ReceiptCredentials { username: string; password: string }
