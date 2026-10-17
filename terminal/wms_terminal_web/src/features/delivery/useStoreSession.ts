import { useCallback, useRef, useState } from "react";
import { storeAppRequest, StoreAppApiError } from "./api";
import type { StoreCredentials, StoreSession, StoreSummary } from "./contracts";

const RECEIPT_MODES = ["BARCODE", "WEIGHT_PHOTO", "PAPER_COUNT"];

function isValidStore(value: unknown): value is StoreSummary {
 const store = value as StoreSummary;
 return !!store && typeof store.store_id === "string" && !!store.store_id
  && typeof store.address === "string" && !!store.address
  && RECEIPT_MODES.includes(store.receipt_mode)
  && typeof store.policy_version === "number";
}

function isValidSession(value: unknown): value is StoreSession {
 const session = value as StoreSession;
 return !!session && session.auth_scope === "STORE_RECEIPT"
  && typeof session.username === "string" && !!session.username
  && typeof session.access_revision === "number"
  && Array.isArray(session.stores) && session.stores.length <= session.limit
  && session.stores.every(isValidStore);
}

export function useStoreSession() {
 const [credentials, setCredentials] = useState<StoreCredentials | null>(null);
 const [session, setSession] = useState<StoreSession | null>(null);
 const [busy, setBusy] = useState(false);
 const [error, setError] = useState("");
 const epoch = useRef(0);

 const login = useCallback(async (username: string, password: string) => {
  if (busy) return;
  const trimmed = username.trim();
  if (!trimmed || !password) { setError("Введите имя пользователя и пароль."); return; }
  const attempt = ++epoch.current;
  setBusy(true); setError("");
  const candidate: StoreCredentials = { username: trimmed, password };
  try {
   const data = await storeAppRequest<unknown>("/api/store-app/session", candidate);
   if (!isValidSession(data)) throw new Error("Сервер вернул непригодный ответ сессии магазина.");
   if (data.username.trim().toLowerCase() !== trimmed.toLowerCase()) {
    throw new Error("Сервер подтвердил другую учётную запись. Вход отклонён.");
   }
   if (epoch.current !== attempt) return;
   // Каноническая форма логина с сервера — иначе ADMIN/admin ведут разные локальные журналы одной учётки.
   setCredentials({ username: data.username, password });
   setSession(data);
  } catch (err) {
   if (epoch.current !== attempt) return;
   setCredentials(null);
   setSession(null);
   setError(err instanceof StoreAppApiError ? err.message : String(err));
  } finally {
   if (epoch.current === attempt) setBusy(false);
  }
 }, [busy]);

 const logout = useCallback(() => {
  epoch.current += 1;
  setCredentials(null);
  setSession(null);
  setError("");
  setBusy(false);
 }, []);

 return { credentials, session, busy, error, login, logout };
}

export type StoreSessionState = ReturnType<typeof useStoreSession>;
