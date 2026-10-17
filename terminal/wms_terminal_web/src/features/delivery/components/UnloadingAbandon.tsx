import { useEffect, useRef, useState } from "react";
import { storeAppRequest, isAuthError } from "../api";
import type { StoreCredentials } from "../contracts";
import type { UnloadingPending } from "../unloadingIntent";

export function UnloadingAbandon({ scope, pending, credentials, disabled, onSaved, onResolved, onAuthError }: {
 scope: string; pending: UnloadingPending; credentials: StoreCredentials; disabled: boolean;
 onSaved: (value: UnloadingPending) => void; onResolved: () => void; onAuthError: () => void;
}) {
 const [busy, setBusy] = useState(false), [message, setMessage] = useState("");
 const flight = useRef(false), mounted = useRef(scope); mounted.current = scope;
 useEffect(() => () => { mounted.current = ""; }, [scope]);
 async function resolve() {
  if (disabled || flight.current) return;
  const key = scope; flight.current = true; setBusy(true); setMessage("");
  try {
   const saved = pending.abandon ? pending : { ...pending, abandon: {
    operation_id: "UNLOAD.STOP:" + crypto.randomUUID(), original: pending.body,
    reason: "Receiver requests durable resolution of uncertain unloading start",
   } };
   localStorage.setItem(key, JSON.stringify(saved)); onSaved(saved);
   const result = await storeAppRequest<Record<string, unknown>>("/api/delivery/store-receipts/unloading/abandon-start", credentials, saved.abandon);
   if (result.operation_id !== saved.abandon!.operation_id || result.original_operation_id !== saved.body.operation_id
    || result.load_operation_id !== saved.body.load_operation_id || result.store_address !== saved.body.store_address
    || (result.status !== "ABANDONED" && result.status !== "RECORDED")) throw new Error("Ответ не подтверждает исходную операцию. Повторите проверку.");
   localStorage.setItem(key + ":resolved:" + saved.abandon!.operation_id, JSON.stringify({ ...saved, result }));
   localStorage.removeItem(key);
   if (mounted.current === key) onResolved();
  } catch (error) {
   if (mounted.current === key) { setMessage(String(error)); if (isAuthError(error)) onAuthError(); }
  } finally { flight.current = false; if (mounted.current === key) setBusy(false); }
 }
 return <div><button type="button" disabled={disabled || busy} onClick={() => void resolve()}
  title="Сервер проверит исходное начало: вернёт записанный факт либо запретит ещё не выполненный запрос, включая его запоздалую отправку"
  data-help-id="unloading.resolve">{pending.abandon ? "Повторить проверку и прекращение" : "Проверить и прекратить запрос"}</button>
  <p role="status">{message}</p></div>;
}
