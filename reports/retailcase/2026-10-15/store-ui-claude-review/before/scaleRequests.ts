import { storeAppRequest } from "./api";
import type { StoreCredentials, StorePreview, ScaleCapture } from "./contracts";
export interface StoreScaleDevice {
 device_id: string; device_policy_version: number; active: boolean; capacity_kg: string; resolution_kg: string;
 calibration_ref: string; calibrated_until: string; readiness: "READY" | "INACTIVE" | "CALIBRATION_EXPIRED" | "SENDER_UNAVAILABLE" | "RECEIPT_NOT_ELIGIBLE"; connectivity: "UNKNOWN";
}
export interface WeighRequestBody { request_id: string; device_id: string; load_operation_id: string; store_address: string; expected_composition_signature: string }
export interface WeighRequest extends WeighRequestBody { state: "REQUESTED" | "EXPIRED" | "CAPTURED" | "STALE"; capture_key: string | null; expires_at: string; reason: string | null }
export async function scaleDevices(preview: StorePreview, credentials: StoreCredentials) {
 const params = new URLSearchParams({ load_operation_id: preview.load_operation_id, store_address: preview.store_address });
 const data = await storeAppRequest<{ items: StoreScaleDevice[] }>("/api/delivery/store-scales/devices?" + params, credentials);
 if (!Array.isArray(data.items) || data.items.some(row => !row.device_id || !["READY", "INACTIVE", "CALIBRATION_EXPIRED", "SENDER_UNAVAILABLE", "RECEIPT_NOT_ELIGIBLE"].includes(row.readiness))) throw new Error("Сервер не подтвердил настройки весов.");
 return data.items;
}
export function checkWeighResult(data: WeighRequest, body: WeighRequestBody): WeighRequest {
 if (["request_id", "device_id", "load_operation_id", "store_address", "expected_composition_signature"].some(key => data[key as keyof WeighRequest] !== body[key as keyof WeighRequestBody])
  || !["REQUESTED", "EXPIRED", "CAPTURED", "STALE"].includes(data.state)) throw new Error("Ответ шлюза не совпадает с запросом взвешивания.");
 return data;
}
export async function weighResult(body: WeighRequestBody, credentials: StoreCredentials) {
 const data = await storeAppRequest<WeighRequest>("/api/delivery/store-scales/requests/" + encodeURIComponent(body.request_id), credentials);
 return checkWeighResult(data, body);
}
export async function confirmedCapture(key: string, body: WeighRequestBody, credentials: StoreCredentials) {
 const result = await storeAppRequest<ScaleCapture & { load_operation_id: string; store_address: string; capture_id: string }>("/api/delivery/store-scales/captures/" + encodeURIComponent(key), credentials);
 if (result.capture_key !== key || result.device_id !== body.device_id || result.capture_id !== body.request_id || result.load_operation_id !== body.load_operation_id || result.store_address !== body.store_address) throw new Error("Измерение относится к другому запросу или месту.");
 return result;
}
