import type { StoreCredentials } from "./contracts";
import { humanStoreMessage } from "./messages";

export function storeAppApiBase(): string {
 const override = import.meta.env.VITE_STORE_API_BASE_URL;
 if (typeof override === "string" && override) return override.replace(/\/+$/, "");
 return typeof location !== "undefined" ? location.origin : "";
}

export class StoreAppApiError extends Error {
 constructor(message: string, public status: number, public confirmed: boolean, public code?: string) { super(message); }
 toString(): string { return this.message; }
}

function isRecord(value: unknown): value is Record<string, unknown> {
 return !!value && typeof value === "object" && !Array.isArray(value);
}

function authHeader(credentials: StoreCredentials): string {
 const bytes = new TextEncoder().encode(credentials.username + ":" + credentials.password);
 return "Basic " + btoa(Array.from(bytes, (byte) => String.fromCharCode(byte)).join(""));
}

async function toApiError(response: Response, body: unknown): Promise<StoreAppApiError> {
 let data: unknown = null;
 try { data = await response.json(); } catch { /* ответ без тела или не JSON — источник недоступен/не готов */ }
 const detailRaw = isRecord(data) ? data.detail : undefined;
 const detail = isRecord(detailRaw) ? detailRaw : undefined;
 const code = typeof detail?.code === "string" ? detail.code : undefined;
 const fallback = response.status === 401 ? "Войдите в приложение заново."
  : response.status === 403 ? "Нет доступа к этому действию. Обратитесь к руководителю."
  : response.status >= 500 ? "Сервис временно недоступен. Результат действия пока не подтверждён."
  : "Действие не подтверждено. Проверьте состояние и введённые данные.";
 const rawMessage = typeof detailRaw === "string" ? detailRaw
  : typeof detail?.message === "string" ? detail.message
  : code || fallback;
 const requestBody = isRecord(body) ? body : undefined;
 // Принцип C-0036/C-0062: не структурированный ответ не доказывает подтверждённый бизнес-отказ.
 let confirmed = false;
 if (detail && response.status < 500 && detail.outcome_confirmed === true
  && requestBody && typeof requestBody.operation_id === "string" && detail.operation_id === requestBody.operation_id) {
  confirmed = true;
 }
 if (detail && response.status < 500 && detail.outcome_confirmed === true
  && requestBody && typeof requestBody.request_id === "string" && detail.request_id === requestBody.request_id) confirmed = true;
 return new StoreAppApiError(humanStoreMessage(rawMessage, fallback), response.status, confirmed, code);
}

export function isAuthError(error: unknown): boolean {
 return error instanceof StoreAppApiError && (error.status === 401 || error.status === 403);
}

export async function storeAppRequest<T>(path: string, credentials: StoreCredentials, body?: unknown): Promise<T> {
 const base = storeAppApiBase();
 let response: Response;
 try {
  response = await fetch(base + path, {
   method: body === undefined ? "GET" : "POST",
   headers: { Authorization: authHeader(credentials), ...(path.startsWith("/api/delivery/store-scales/") ? { "X-Scale-Protocol-Version": "1.0" } : {}), ...(body === undefined ? {} : { "Content-Type": "application/json" }) },
   body: body === undefined ? undefined : JSON.stringify(body),
  });
 } catch {
  throw new StoreAppApiError("Нет связи с сервером. Проверьте подключение и повторите.", 0, false);
 }
 if (!response.ok) throw await toApiError(response, body);
 if (response.status === 204) return undefined as T;
 try {
  return (await response.json()) as T;
 } catch {
  throw new StoreAppApiError("Не удалось прочитать ответ сервера. Результат действия пока не подтверждён.", response.status, false);
 }
}

export function authHeaderValue(credentials: StoreCredentials): string {
 return authHeader(credentials);
}
