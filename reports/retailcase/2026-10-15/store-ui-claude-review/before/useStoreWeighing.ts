import { useEffect, useRef, useState } from "react";
import { storeAppRequest, storeAppApiBase, isAuthError, StoreAppApiError } from "./api";
import { scaleDevices, weighResult, confirmedCapture, checkWeighResult, type StoreScaleDevice, type WeighRequest, type WeighRequestBody } from "./scaleRequests";
import type { StorePreview, StoreCredentials, ScaleCapture } from "./contracts";

function readSaved(key: string, preview: StorePreview): { body: WeighRequestBody; confirmedRejection: boolean } | null {
 const raw = localStorage.getItem(key);
 if (!raw) return null;
 const value = JSON.parse(raw);
 const body = (value.body ?? value) as WeighRequestBody;
 if (!body || !/^[A-Za-z0-9_.:-]{1,100}$/.test(body.request_id) || !body.device_id || body.load_operation_id !== preview.load_operation_id
  || body.store_address !== preview.store_address || body.expected_composition_signature !== preview.composition_signature) throw new Error("Сохранённый запрос весов повреждён. Новое взвешивание заблокировано; обратитесь к ответственному.");
 return { body, confirmedRejection: value.confirmedRejection === true };
}
export function useStoreWeighing(preview: StorePreview, credentials: StoreCredentials, onAuthError: () => void) {
 const key = "store-weigh:" + storeAppApiBase() + ":" + credentials.username + ":" + preview.store_address + ":" + preview.load_operation_id + ":" + preview.composition_signature;
 const current = useRef(key), [devices, setDevices] = useState<StoreScaleDevice[]>([]), [device, setDevice] = useState("");
 const [pending, setPending] = useState<WeighRequestBody | null>(null), [fact, setFact] = useState<WeighRequest | null>(null), [capture, setCapture] = useState<ScaleCapture | null>(null);
 const [rejected, setRejected] = useState(false);
 const [busy, setBusy] = useState(false), [message, setMessage] = useState(""), [corrupt, setCorrupt] = useState(false);
 function fail(error: unknown) { setMessage(String(error).replace(/^Error: /, "")); if (isAuthError(error)) onAuthError(); }
 async function refreshDevices() {
  try { const rows = await scaleDevices(preview, credentials); if (current.current !== key) return; setDevices(rows); const ready = rows.filter(row => row.readiness === "READY"); if (ready.length === 1) setDevice(ready[0].device_id); }
  catch (error) { if (current.current === key) fail(error); }
 }
 useEffect(() => {
  current.current = key; setDevices([]); setDevice(""); setPending(null); setFact(null); setCapture(null); setRejected(false); setMessage(""); setCorrupt(false); setRejected(false);
  try { const saved = readSaved(key, preview); setPending(saved?.body ?? null); setRejected(saved?.confirmedRejection ?? false); } catch (error) { setCorrupt(true); fail(error); }
  void refreshDevices();
  return () => { current.current = ""; };
 }, [key]);
 async function resolve(body: WeighRequestBody) {
  const value = await weighResult(body, credentials);
  if (current.current !== key) return;
  setFact(value);
  if (value.state === "CAPTURED" && value.capture_key) {
   const saved = await confirmedCapture(value.capture_key, body, credentials);
   if (current.current !== key) return;
   setCapture(saved); setMessage("Стабильный вес подтверждён сервером.");
  } else if (value.state !== "REQUESTED") setMessage(value.state === "EXPIRED" ? "Время запроса истекло. Проверьте весы и запросите новое измерение." : "Состав или настройки изменились. Перечитайте поставку.");
 }
 useEffect(() => {
  if (!pending || rejected || corrupt || capture || (fact && fact.state !== "REQUESTED")) return;
  let cancelled = false;
  const tick = async () => { try { await resolve(pending); } catch (error) { if (!cancelled && current.current === key) fail(error); } };
  void tick(); const timer = window.setInterval(() => void tick(), 2000);
  return () => { cancelled = true; clearInterval(timer); };
 }, [pending, rejected, fact?.state, capture, corrupt]);
 async function request() {
  if (busy || corrupt || rejected || !device) return;
  const body = pending ?? { request_id: "WEIGH:" + crypto.randomUUID(), device_id: device, load_operation_id: preview.load_operation_id, store_address: preview.store_address, expected_composition_signature: preview.composition_signature };
  setBusy(true); setMessage("");
  try {
   const raw = JSON.stringify({ body, confirmedRejection: false }); localStorage.setItem(key, raw); if (localStorage.getItem(key) !== raw) throw new Error("Запрос не сохранён. Взвешивание не начато.");
   setPending(body);
   const value = await storeAppRequest<WeighRequest>("/api/delivery/store-scales/requests", credentials, body);
   if (current.current !== key) return;
   setFact(checkWeighResult(value, body)); await resolve(body);
  } catch (error) {
   if (current.current === key) {
    if (error instanceof StoreAppApiError && error.confirmed) { localStorage.setItem(key, JSON.stringify({ body, confirmedRejection: true })); setRejected(true); }
    fail(error);
   }
  }
  finally { if (current.current === key) setBusy(false); }
 }
 function newMeasurement() {
  if (busy || (!rejected && (!fact || !["EXPIRED", "CAPTURED", "STALE"].includes(fact.state)))) return;
  const raw = localStorage.getItem(key); if (raw) localStorage.setItem(key + ":history:" + pending!.request_id, raw);
  localStorage.removeItem(key); setPending(null); setFact(null); setCapture(null); setRejected(false); setMessage("");
 }
 return { devices, device, setDevice, pending, fact, capture, busy, corrupt, rejected, message, request, newMeasurement, refreshDevices };
}
