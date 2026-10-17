import { useEffect, useRef, useState } from "react";
import { storeAppApiBase, storeAppRequest, isAuthError } from "../api";
import type { StoreCredentials } from "../contracts";

type Arrival = { operation_id: string; load_operation_id: string; store_address: string; arrived_at: string; reason: string };
type Timing = { arrival: { operation_id: string; arrived_at: string; on_time_state: string } | null };

function stored(key: string, load: string, store: string): Arrival | null {
 const raw = localStorage.getItem(key); if (raw === null) return null;
 const value = JSON.parse(raw) as Arrival;
 if (!value || typeof value.operation_id !== "string" || !/^[A-Za-z0-9_.:-]{1,100}$/.test(value.operation_id)
  || value.load_operation_id !== load || value.store_address !== store || typeof value.reason !== "string" || value.reason.length < 8
  || typeof value.arrived_at !== "string" || !/^\d{4}-\d{2}-\d{2}T.*(?:Z|[+-]\d{2}:\d{2})$/.test(value.arrived_at)
  || !Number.isFinite(Date.parse(value.arrived_at)) || Object.keys(value).sort().join(",") !== "arrived_at,load_operation_id,operation_id,reason,store_address")
  throw new Error("Запись прибытия повреждена. Сохраните её для ответственного; новая команда заблокирована.");
 return value;
}

export function ArrivalPanel({ load, store, credentials, disabled, onAuthError }: {
 load: string; store: string; credentials: StoreCredentials; disabled: boolean; onAuthError: () => void;
}) {
 const key = "store-arrival:" + storeAppApiBase() + ":" + credentials.username + ":" + load + ":" + store;
 const current = useRef(key), flight = useRef<string | null>(null);
 const [pending, setPending] = useState<Arrival | null>(null), [timing, setTiming] = useState<Timing | null>(null);
 const [busy, setBusy] = useState(false), [damaged, setDamaged] = useState(false), [message, setMessage] = useState("");
 const [loadedKey, setLoadedKey] = useState("");
 useEffect(() => {
  current.current = key; setPending(null); setTiming(null); setDamaged(false); setBusy(false); setMessage("");
  try { setPending(stored(key, load, store)); } catch (error) { setDamaged(true); setMessage(String(error)); }
  setLoadedKey(key);
  void storeAppRequest<Timing>("/api/delivery/timing/place?" + new URLSearchParams({ load_operation_id: load, store_address: store }), credentials)
   .then(value => { if (current.current === key) setTiming(value); })
   .catch(error => { if (current.current === key) { setMessage(String(error)); if (isAuthError(error)) onAuthError(); } });
  return () => { current.current = ""; };
 }, [key]);
 async function confirm() {
  if (disabled || loadedKey !== key || damaged || flight.current === key || timing?.arrival && !pending) return;
  const scope = key; flight.current = scope; setBusy(true); setMessage("");
  try {
   const intent = pending ?? { operation_id: "ARRIVAL:" + crypto.randomUUID(), load_operation_id: load, store_address: store,
    arrived_at: new Date().toISOString(), reason: "Store receiver confirms vehicle arrival at the current time" };
   localStorage.setItem(scope, JSON.stringify(intent)); setPending(intent);
   const result = await storeAppRequest<NonNullable<Timing["arrival"]>>("/api/delivery/timing/arrival", credentials, intent);
   if (result.operation_id !== intent.operation_id || !Number.isFinite(Date.parse(result.arrived_at))) throw new Error("Ответ прибытия не подтверждён. Повторите сохранённую команду.");
   localStorage.setItem(scope + ":confirmed:" + intent.operation_id, JSON.stringify({ intent, result })); localStorage.removeItem(scope);
   if (current.current === scope) { setPending(null); setTiming({ arrival: result }); }
  } catch (error) { if (current.current === scope) { setMessage(String(error)); if (isAuthError(error)) onAuthError(); } }
  finally { if (flight.current === scope) flight.current = null; if (current.current === scope) setBusy(false); }
 }
 return <section aria-label="Прибытие машины"><div className="store-app-hint">Прибытие машины <a href={storeAppApiBase() + "/help/delivery-timing.html"} target="_blank" rel="noreferrer" data-help-id="delivery.arrival" title="Как фиксировать прибытие и восстановить запрос после обрыва связи">Справка</a></div>
  {timing?.arrival && <p>Прибыла: {new Date(timing.arrival.arrived_at).toLocaleString("ru-RU", { dateStyle: "short", timeStyle: "short" })}</p>}
  {(!timing?.arrival || pending) && <button type="button" disabled={disabled || loadedKey !== key || busy || damaged} onClick={() => void confirm()}
   title={pending ? "Повторить сохранённый факт с прежними временем и operation_id" : "Подтвердить, что машина прибыла сейчас; время будет сохранено отдельно от разгрузки"}
   data-help-id="delivery.arrival.confirm">{pending ? "Повторить отметку прибытия" : "Машина прибыла сейчас"}</button>}
  {message && <p role="status" className="store-app-message">{message}</p>}
 </section>;
}
