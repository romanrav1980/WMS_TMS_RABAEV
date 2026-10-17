import { useRef, useState, useEffect } from "react";
import { ScanField } from "../../platform";
import { storeAppRequest, isAuthError } from "../api";
import type { StoreCredentials } from "../contracts";
export function DeliveryScanner({ storeId, credentials, onOpen, onClose, onAuthError }: {
 storeId: string; credentials: StoreCredentials; onOpen: (load: string, code: string) => void; onClose: () => void; onAuthError: () => void;
}) {
 const [code, setCode] = useState(""), [message, setMessage] = useState(""), [busy, setBusy] = useState(false), active = useRef(true);
 useEffect(() => { active.current = true; return () => { active.current = false; }; }, []);
 async function resolve(value: string) {
  if (!value || busy) return;
  setBusy(true); setMessage("");
  try {
   const params = new URLSearchParams({ store_id: storeId, code: value });
   const data = await storeAppRequest<{ load_operation_id: string; store_id: string; scanned_code: string }>("/api/store-app/deliveries/lookup?" + params, credentials);
   if (!active.current) return;
   if (data.store_id !== storeId || data.scanned_code !== value || !data.load_operation_id) throw new Error("Сервер не подтвердил поставку по этому коду.");
   onOpen(data.load_operation_id, value);
  } catch (error) { if (active.current) { setMessage(String(error).replace(/^Error: /, "")); if (isAuthError(error)) onAuthError(); } }
  finally { if (active.current) setBusy(false); }
 }
 return <div className="store-app-help-overlay"><section className="store-app-help-panel" role="dialog" aria-label="Найти поставку по коду" aria-modal="true">
  <header className="store-app-header"><h2>Сканировать поставку</h2><button type="button" title="Закрыть сканирование и вернуться к списку" data-help-id="lookup.close" onClick={onClose}>Закрыть</button></header>
  <ScanField label="Идентификатор паллеты или места" value={code} onChange={setCode} onSubmit={resolve} disabled={busy} autoFocus />
  <button type="button" className="store-app-primary" title="Найти этот код на сервере среди разрешённых поставок выбранного магазина" data-help-id="lookup.open" disabled={busy || !code} onClick={() => void resolve(code)}>{busy ? "Ищем…" : "Открыть поставку"}</button>
  {message && <p className="store-app-message" role="status">{message}</p>}
 </section></div>;
}
