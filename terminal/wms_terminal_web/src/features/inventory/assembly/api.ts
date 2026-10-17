import type { AssemblyCredentials } from "./contracts";

// Same-origin /api via Vite proxy/static mount; no base-url override needed (narrow standalone terminal).
const PREFIX = "/api/inventory/assembly-scale";

export class AssemblyApiError extends Error {
  constructor(message: string, public status: number, public confirmed: boolean, public code?: string) { super(message); }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function authHeader(credentials: AssemblyCredentials): string {
  const bytes = new TextEncoder().encode(credentials.username + ":" + credentials.password);
  return "Basic " + btoa(Array.from(bytes, b => String.fromCharCode(b)).join(""));
}
export const assemblyAuthHeader = authHeader;

async function toApiError(response: Response, body: unknown): Promise<AssemblyApiError> {
  let data: unknown = null;
  try { data = await response.json(); } catch { /* ответ без тела/не JSON — источник не готов */ }
  const detailRaw = isRecord(data) ? data.detail : undefined;
  const detail = isRecord(detailRaw) ? detailRaw : undefined;
  const code = typeof detail?.code === "string" ? detail.code : undefined;
  const message = typeof detailRaw === "string" ? detailRaw
    : typeof detail?.message === "string" ? detail.message
    : `Весовой сервис сборки ответил ошибкой (HTTP ${response.status}).`;
  const req = isRecord(body) ? body : undefined;
  // outcome_confirmed должен прийти от сервера именно для НАШЕГО operation_id/step_id — иначе отказ не подтверждён (C-0036/C-0062).
  let confirmed = false;
  if (detail && response.status < 500 && detail.outcome_confirmed === true) {
    const idFields = ["operation_id", "step_id", "session_id"] as const;
    confirmed = idFields.some(f => typeof req?.[f] === "string" && detail[f] === req[f]);
  }
  return new AssemblyApiError(message, response.status, confirmed, code);
}

export async function assemblyRequest<T>(path: string, credentials: AssemblyCredentials, body?: unknown, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try {
    response = await fetch(PREFIX + path, {
      method: body === undefined ? "GET" : "POST",
      headers: { Authorization: authHeader(credentials), ...(body === undefined ? {} : { "Content-Type": "application/json" }) },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") throw err;
    throw new AssemblyApiError("Нет связи с сервером. Проверьте подключение и повторите.", 0, false);
  }
  if (!response.ok) throw await toApiError(response, body);
  if (response.status === 204) return undefined as T;
  try { const data = await response.json(); if (signal?.aborted) throw new DOMException("Aborted", "AbortError"); return data as T; } catch { throw new AssemblyApiError("Сервер ответил без ожидаемых данных.", response.status, false); }
}

export function isAuthError(error: unknown): boolean {
  return error instanceof AssemblyApiError && (error.status === 401 || error.status === 403);
}

/** GET on an absolute path outside the assembly-scale prefix (e.g. warehouse-scales final-captures), same Basic auth. */
export async function rawApiGet<T>(path: string, credentials: AssemblyCredentials, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try { response = await fetch(path, { cache: "no-store", headers: { Authorization: authHeader(credentials) }, signal }); }
  catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") throw err;
    throw new AssemblyApiError("Нет связи с сервером. Проверьте подключение и повторите.", 0, false);
  }
  if (!response.ok) throw await toApiError(response, undefined);
  try { const data = await response.json(); if (signal?.aborted) throw new DOMException("Aborted", "AbortError"); return data as T; } catch { throw new AssemblyApiError("Сервер ответил без ожидаемых данных.", response.status, false); }
}

export async function rawApiPost<T>(path: string, credentials: AssemblyCredentials, body: unknown, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try { response = await fetch(path, { method: "POST", headers: { Authorization: authHeader(credentials), "Content-Type": "application/json", "X-Scale-Protocol-Version": "1.0" }, body: JSON.stringify(body), signal }); }
  catch (err) { if (err instanceof DOMException && err.name === "AbortError") throw err; throw new AssemblyApiError("Нет связи. Исходный запрос сохранён для точного повтора.", 0, false); }
  if (!response.ok) throw await toApiError(response, body);
  return await response.json() as T;
}
