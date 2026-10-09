import { apiClient } from "./client";

let authenticated = false;

export function hasTerminalAuth(): boolean { return authenticated; }
export function clearTerminalAuth(): void {
  authenticated = false;
  delete apiClient.defaults.headers.common.Authorization;
}

export async function authenticateTerminal(username: string, password: string) {
  clearTerminalAuth();
  const bytes = new TextEncoder().encode(username + ":" + password);
  const authorization = "Basic " + btoa(Array.from(bytes, value => String.fromCharCode(value)).join(""));
  const response = await apiClient.get<{ username: string; display_name: string; permissions: string[] }>(
    "/api/terminal/auth/me", { headers: { Authorization: authorization } });
  apiClient.defaults.headers.common.Authorization = authorization;
  authenticated = true;
  return response.data;
}
