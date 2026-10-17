import { storeAppApiBase, authHeaderValue, StoreAppApiError } from "./api";
import { humanStoreMessage } from "./messages";
import type { StoreCredentials, ReceiptPhoto } from "./contracts";

const photoBase = () => storeAppApiBase() + "/api/delivery/store-photos";

async function checked(response: Response, path: string): Promise<Response> {
 if (!response.ok) {
  let data: unknown = null;
  try { data = await response.json(); } catch { /* источник недоступен/не готов */ }
  const detail = data && typeof data === "object" ? (data as Record<string, unknown>).detail : undefined;
  const message = typeof detail === "string" ? detail
   : detail && typeof detail === "object" ? JSON.stringify(detail)
   : "Источник " + path + " недоступен (HTTP " + response.status + ").";
  throw new StoreAppApiError(humanStoreMessage(message), response.status, false);
 }
 return response;
}

export async function listReceiptPhotos(loadOperationId: string, storeAddress: string, credentials: StoreCredentials): Promise<ReceiptPhoto[]> {
 const query = new URLSearchParams({ load_operation_id: loadOperationId, store_address: storeAddress });
 const response = await checked(await fetch(photoBase() + "/list?" + query, { headers: { Authorization: authHeaderValue(credentials) } }), "/api/delivery/store-photos/list");
 return response.json() as Promise<ReceiptPhoto[]>;
}

export async function uploadReceiptPhoto(loadOperationId: string, storeAddress: string, view: string, file: File, credentials: StoreCredentials): Promise<void> {
 const query = new URLSearchParams({ load_operation_id: loadOperationId, store_address: storeAddress, view });
 await checked(await fetch(photoBase() + "/upload?" + query, {
  method: "POST",
  headers: { Authorization: authHeaderValue(credentials), "Content-Type": file.type },
  body: file,
 }), "/api/delivery/store-photos/upload");
}
