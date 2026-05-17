import { apiClient } from "./client";
import type {
  DbPingResponse,
  LegacyBlock,
  LegacyExecuteResponse,
  LotCheckPayload,
  PlaceCheckPayload
} from "../types";

export async function getHealth(): Promise<{ status: string }> {
  const response = await apiClient.get("/health");
  return response.data;
}

export async function getDbPing(): Promise<DbPingResponse> {
  const response = await apiClient.get("/db/ping");
  return response.data;
}

export async function getTerminalUser(userId: string): Promise<LegacyBlock[]> {
  const response = await apiClient.get(`/api/terminal/users/${encodeURIComponent(userId)}`);
  return response.data;
}

export async function getProductByBarcode(barcode: string): Promise<LegacyBlock[]> {
  const response = await apiClient.get(`/api/products/by-barcode/${encodeURIComponent(barcode)}`);
  return response.data;
}

export async function getLotItems(usscc: string): Promise<LegacyExecuteResponse> {
  const response = await apiClient.get(`/api/lots/${encodeURIComponent(usscc)}/items`);
  return response.data;
}

export async function getPlaceItems(placeId: string): Promise<LegacyExecuteResponse> {
  const response = await apiClient.get(`/api/places/${encodeURIComponent(placeId)}/items`);
  return response.data;
}

export async function executeLegacyPayload(payload: string): Promise<LegacyExecuteResponse> {
  const response = await apiClient.post("/api/legacy/tserver/execute", { payload });
  return response.data;
}

export async function confirmLotCheck(usscc: string, payload: LotCheckPayload): Promise<{ status: string }> {
  const response = await apiClient.post(`/api/terminal/lots/${encodeURIComponent(usscc)}/check`, payload);
  return response.data;
}

export async function confirmPlaceCheck(payload: PlaceCheckPayload): Promise<{ status: string }> {
  const response = await apiClient.post("/api/terminal/place-checks", payload);
  return response.data;
}

export async function getProductionBatchStatus(batchId: string): Promise<Record<string, unknown>> {
  const response = await apiClient.get(`/api/production-batches/${encodeURIComponent(batchId)}/status`);
  return response.data;
}
