let credentials: {username: string; password: string} | null = null;
export function setSessionCredentials(value: {username: string; password: string} | null): void { credentials = value; }
export function adminBasicAuth(): string {
  if (!credentials) throw new Error("Войдите своей учётной записью.");
  return credentials.username + ":" + credentials.password;
}
export function adminAuthorization(): string {
  const bytes = new TextEncoder().encode(adminBasicAuth());
  return "Basic " + btoa(String.fromCharCode(...bytes));
}

export function currentSessionCredentials(): {username: string; password: string} {
  if (!credentials) throw new Error("Войдите своей учётной записью.");
  return {...credentials};
}

export const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8088";
export const RAW_ADMIN_BASE = String(import.meta.env.VITE_RAW_ADMIN_BASE || `${API_BASE.replace(/\/$/, "")}/wms-admin`).replace(/\/$/, "");

export function apiOperationScope(): string {
  return API_BASE+":"+adminBasicAuth().split(":",1)[0];
}
export class ApiRequestError extends Error {
  constructor(public readonly status:number,public readonly detail:unknown){
    super(`${status}: ${typeof detail==="string"?detail:JSON.stringify(detail)}`);
  }
  get confirmedRejection():boolean {
    return this.status===409&&typeof this.detail==="object"&&this.detail!==null
      &&"outcome_confirmed" in this.detail&&this.detail.outcome_confirmed===true;
  }
}

function apiHeaders(initHeaders?: HeadersInit): HeadersInit {
  return {
    Authorization: adminAuthorization(),
    "Content-Type": "application/json",
    ...(initHeaders || {}),
  };
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: apiHeaders(init.headers),
  });

  if (!res.ok) {
    let detail:unknown = res.statusText;
    try {
      const body = await res.json();
      detail = body?.detail || detail;
    } catch {
      // Keep the HTTP status text when the response body is not JSON.
    }
    throw new ApiRequestError(res.status,detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
