import { useCallback, useRef, useState } from "react";
import { assemblyAuthHeader } from "./api";
import type { AssemblyCredentials } from "./contracts";

export interface AssemblyIdentity { username: string; display_name: string; user_group: string; permissions: string[] }

function isIdentity(value: unknown): value is AssemblyIdentity {
  const v = value as AssemblyIdentity;
  return !!v && typeof v.username === "string" && !!v.username && Array.isArray(v.permissions);
}

/** Login via the existing /api/terminal/auth/me (Basic). Credentials stay in memory only, never storage. */
export function useAssemblyAuth() {
  const [credentials, setCredentials] = useState<AssemblyCredentials | null>(null);
  const [identity, setIdentity] = useState<AssemblyIdentity | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const epoch = useRef(0);

  const login = useCallback(async (username: string, password: string) => {
    if (busy) return;
    const trimmed = username.trim();
    if (!trimmed || !password) { setError("Введите имя пользователя и пароль."); return; }
    const attempt = ++epoch.current;
    setBusy(true); setError("");
    try {
      const response = await fetch("/api/terminal/auth/me", { headers: { Authorization: assemblyAuthHeader({ username: trimmed, password }) } });
      if (epoch.current !== attempt) return;
      if (!response.ok) throw new Error(response.status === 401 || response.status === 403 ? "Неверное имя пользователя или пароль." : `Сервер ответил ошибкой (HTTP ${response.status}).`);
      const data = await response.json();
      if (epoch.current !== attempt) return;
      if (!isIdentity(data)) throw new Error("Сервер вернул непригодный ответ учётной записи.");
      if (data.username.trim().toLowerCase() !== trimmed.toLowerCase()) throw new Error("Сервер подтвердил другую учётную запись. Вход отклонён.");
      setCredentials({ username: data.username, password });
      setIdentity(data);
    } catch (err) {
      if (epoch.current !== attempt) return;
      setCredentials(null); setIdentity(null);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      if (epoch.current === attempt) setBusy(false);
    }
  }, [busy]);

  const logout = useCallback(() => {
    epoch.current += 1;
    setCredentials(null); setIdentity(null); setError(""); setBusy(false);
  }, []);

  return { credentials, identity, busy, error, login, logout };
}
export type AssemblyAuthState = ReturnType<typeof useAssemblyAuth>;
