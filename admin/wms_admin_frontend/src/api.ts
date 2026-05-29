const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8088";
const API_BASIC_AUTH = import.meta.env.VITE_ADMIN_BASIC_AUTH || "admin:admin123";

function apiHeaders(initHeaders?: HeadersInit): HeadersInit {
  return {
    Authorization: `Basic ${btoa(API_BASIC_AUTH)}`,
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
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body?.detail || detail;
    } catch {
      // Keep the HTTP status text when the response body is not JSON.
    }
    throw new Error(`${res.status}: ${detail}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
