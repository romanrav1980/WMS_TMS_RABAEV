import type { PendingReceipt } from "./contracts";

const isObject = (value: unknown): value is Record<string, unknown> => !!value && typeof value === "object" && !Array.isArray(value);
const isText = (value: unknown, max: number): value is string => typeof value === "string" && value.length > 0 && value.length <= max;
const isDecimal = (value: unknown) => typeof value === "string" && /^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(value);

function validScans(value: unknown, aggregate: boolean): boolean {
 return value === undefined || (Array.isArray(value) && value.length <= (aggregate ? 1000 : 20000) && value.every((item) =>
  isObject(item) && isText(item.system_code, 40) && isText(item.profile_code, 80)
  && new TextEncoder().encode(String(item.profile_code)).length <= 80
  && isText(item.code, 4000) && new TextEncoder().encode(String(item.code)).length <= 4000
  && (!aggregate || ["BOX", "PALLET"].includes(String(item.level)))
  && (item.disposition === undefined || ["ACCEPTED", "REFUSED", "DAMAGED"].includes(String(item.disposition)))));
}

export function parseReceiptIntent(raw: string | null, storeAddress: string): PendingReceipt | null {
 if (raw === null) return null;
 const value: unknown = JSON.parse(raw);
 if (!isObject(value) || !isObject(value.body) || (value.confirmedRejection !== undefined && typeof value.confirmedRejection !== "boolean")) {
  throw new Error("INVALID_RECEIPT_INTENT");
 }
 const body = value.body;
 if (!isText(body.operation_id, 100) || !/^[A-Za-z0-9_.:-]+$/.test(body.operation_id)
  || !isText(body.load_operation_id, 100) || body.store_address !== storeAddress
  || !isText(body.scan_place, 200)
  || typeof body.expected_composition_signature !== "string" || !/^[A-F0-9]{64}$/.test(body.expected_composition_signature)
  || typeof body.before_cameras !== "boolean"
  || !validScans(body.scans, false) || !validScans(body.aggregation_scans, true)
  || (body.paper_reference !== undefined && (!isText(body.paper_reference, 200) || new TextEncoder().encode(body.paper_reference).length > 400))
  || (body.case_note !== undefined && !isText(body.case_note, 2000))) {
  throw new Error("INVALID_RECEIPT_INTENT");
 }
 if (body.observations !== undefined && (!Array.isArray(body.observations) || body.observations.length > 200
  || !body.observations.every((row: unknown) => isObject(row) && isText(row.lot_uid, 200)
   && ["accepted", "missing", "refused", "damaged", "extra"].every((key) => isDecimal((row as Record<string, unknown>)[key] ?? "0"))))) {
  throw new Error("INVALID_RECEIPT_INTENT");
 }
 if (body.unloading !== undefined && (!isObject(body.unloading) || !isText(body.unloading.start_operation_id, 100)
  || !["ROLL_CAGE", "PALLET", "MANUAL"].includes(String(body.unloading.method))
  || typeof body.unloading.rolling_difficult !== "boolean" || typeof body.unloading.loader_present !== "boolean"
  || !isText(body.unloading.evidence_reference, 100))) {
  throw new Error("INVALID_RECEIPT_INTENT");
 }
 return value as unknown as PendingReceipt;
}
