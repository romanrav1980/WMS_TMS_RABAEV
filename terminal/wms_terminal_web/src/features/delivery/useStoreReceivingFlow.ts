import { useEffect, useRef, useState } from "react";
import { receiptScopeKey, writeReceiptDraft } from "./receiptDraft";
import { runOpen, runSend, runCheckStatus, runRestart } from "./receiptFlowActions";
import type {
 StoreCredentials, StorePreview, PendingReceipt, ReceiptBody, ReceiptResult,
 StoreDisposition, StoreUnitScan, StoreAggregateScan, UnloadingDetails,
} from "./contracts";

export interface ConfirmInput {
 scanPlace: string;
 beforeCameras: boolean;
 observations?: StoreDisposition[];
 caseNote?: string;
 scans?: StoreUnitScan[];
 aggregationScans?: StoreAggregateScan[];
 unloading?: UnloadingDetails;
 scaleCaptureKey?: string;
 /** Ручной вес брутто, кг (строка). Вместе со scaleCaptureKey не передаётся. */
 manualWeightKg?: string;
 photoIds?: string[];
 weightActConfirmed?: boolean;
 paperReference?: string;
}

function buildReceiptBody(preview: StorePreview, input: ConfirmInput): ReceiptBody {
 return {
  operation_id: "STORE.RECEIPT:" + crypto.randomUUID(),
  load_operation_id: preview.load_operation_id,
  store_address: preview.store_address,
  scan_place: input.scanPlace,
  expected_composition_signature: preview.composition_signature,
  before_cameras: input.beforeCameras,
  ...(input.unloading ? { unloading: input.unloading } : {}),
  ...(input.observations?.length ? { observations: input.observations } : {}),
  ...(input.caseNote ? { case_note: input.caseNote } : {}),
  ...(input.scaleCaptureKey && !input.manualWeightKg ? { scale_capture_key: input.scaleCaptureKey } : {}),
  // Без ручного веса тело прежнее (поле не добавляется, null/пустая строка не отправляются).
  ...(input.manualWeightKg && !input.scaleCaptureKey ? { manual_weight_kg: input.manualWeightKg } : {}),
  ...(input.photoIds?.length ? { photo_ids: input.photoIds } : {}),
  ...(input.weightActConfirmed ? { weight_act_confirmed: true } : {}),
  ...(input.scans?.length ? { scans: input.scans } : {}),
  ...(input.aggregationScans?.length ? { aggregation_scans: input.aggregationScans } : {}),
  ...(input.paperReference ? { paper_reference: input.paperReference } : {}),
 };
}

export function useStoreReceivingFlow(storeId: string, credentials: StoreCredentials, onAuthError: () => void) {
 const [preview, setPreview] = useState<StorePreview | null>(null);
 const [pending, setPending] = useState<PendingReceipt | null>(null);
 const [busy, setBusy] = useState(false);
 const [message, setMessage] = useState("");
 const [corrupt, setCorrupt] = useState(false);
 const [stalePreview, setStalePreview] = useState(false);
 const [lastReceipt, setLastReceipt] = useState<ReceiptResult | null>(null);
 const inFlight = useRef(false);
 const current = useRef("");

 async function open(id: string) {
  if (busy || inFlight.current) return;
  const scope = receiptScopeKey(storeId, credentials.username, id);
  current.current = scope;
  setPreview(null); setPending(null); setMessage(""); setStalePreview(false); setLastReceipt(null); setCorrupt(false);
  setBusy(true);
  const result = await runOpen(scope, storeId, id, credentials);
  if (current.current !== scope) return;
  setMessage(result.message);
  if (result.preview) setPreview(result.preview);
  if (result.result) setLastReceipt(result.result);
  if (result.pending !== undefined) setPending(result.pending);
  if (result.corrupt) setCorrupt(true);
  if (result.authError) onAuthError();
  setBusy(false);
 }

 async function send(intent: PendingReceipt, scope: string) {
  if (busy || inFlight.current || current.current !== scope || corrupt) return;
  inFlight.current = true; setBusy(true);
  const result = await runSend(scope, intent, credentials);
  if (current.current !== scope) { inFlight.current = false; return; }
  if (result.corrupt) setCorrupt(true);
  if (result.ok && result.result) { setLastReceipt(result.result); setPending(null); setPreview(null); }
  else if (result.pendingToSave) setPending(result.pendingToSave);
  setMessage(result.message);
  if (result.authError) onAuthError();
  inFlight.current = false; setBusy(false);
 }

 async function confirm(input: ConfirmInput) {
  if (busy || inFlight.current || pending || !preview || stalePreview || corrupt) return;
  const scope = current.current;
  const intent: PendingReceipt = { body: buildReceiptBody(preview, input) };
  try { writeReceiptDraft(scope, intent); setPending(intent); await send(intent, scope); }
  catch (error) { setMessage(String(error)); }
 }

 async function checkStatus() {
  if (busy || inFlight.current || !pending || pending.confirmedRejection || !preview) return;
  const scope = current.current; setBusy(true);
  const result = await runCheckStatus(storeId, scope, pending, credentials);
  if (current.current !== scope) return;
  if (result.ok && result.result) { setLastReceipt(result.result); setPending(null); setPreview(null); }
  setMessage(result.message);
  if (result.authError) onAuthError();
  setBusy(false);
 }

 async function restart() {
  if (busy || inFlight.current || !pending?.confirmedRejection || !preview) return;
  const scope = current.current; setBusy(true);
  const result = await runRestart(storeId, scope, preview, pending, credentials);
  if (current.current !== scope) return;
  if (result.ok) { setPending(null); setStalePreview(!!result.changed); if (result.preview) setPreview(result.preview); }
  setMessage(result.message);
  if (result.authError) onAuthError();
  setBusy(false);
 }

 useEffect(() => {
  return () => { current.current = ""; };
 }, []);

 useEffect(() => {
  function onOnline() {
   if (pending && !pending.confirmedRejection && !corrupt) {
    setMessage("Соединение восстановлено. Нажмите «Повторить сохранённую операцию», чтобы отправить её.");
   }
  }
  window.addEventListener("online", onOnline);
  return () => window.removeEventListener("online", onOnline);
 }, [pending, corrupt]);

 return {
  preview, pending, busy, message, corrupt, stalePreview, lastReceipt,
  open, confirm, restart, checkStatus,
  retry: () => (pending && current.current ? send(pending, current.current) : Promise.resolve(undefined)),
 };
}
