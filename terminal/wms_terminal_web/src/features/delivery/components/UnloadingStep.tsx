import { useEffect, useRef, useState } from "react";
import { storeAppRequest, storeAppApiBase, StoreAppApiError, isAuthError } from "../api";
import { HelpHint } from "../help/HelpHint";
import { UnloadingAbandon } from "./UnloadingAbandon";
import { validUnloadingControl, type UnloadingPending } from "../unloadingIntent";
import type { StoreCredentials, StorePreview, UnloadingDetails, UnloadingStartBody } from "../contracts";

type Pending = UnloadingPending;

function parsePending(raw: string, preview: StorePreview): Pending | null {
 const value = JSON.parse(raw) as Pending;
 const body = value?.body;
 if (!body || typeof body.operation_id !== "string" || !/^[A-Za-z0-9_.:-]{1,100}$/.test(body.operation_id)
  || body.load_operation_id !== preview.load_operation_id || body.store_address !== preview.store_address
  || typeof body.expected_composition_signature !== "string" || !body.expected_composition_signature
  || typeof body.scan_place !== "string" || !body.scan_place || body.before_cameras !== true
  || (value.confirmedRejection !== undefined && typeof value.confirmedRejection !== "boolean") || !validUnloadingControl(value)) {
  throw new Error("Сохранённая запись о начале выгрузки повреждена или относится к другому месту.");
 }
 return value;
}

function archiveDamaged(key: string) {
 const raw = localStorage.getItem(key);
 if (raw !== null) localStorage.setItem(key + ":damaged:" + crypto.randomUUID(), raw);
}

interface UnloadingProps {
 preview: StorePreview;
 credentials: StoreCredentials;
 scanPlace: string;
 beforeCameras: boolean;
 disabled: boolean;
 onDetails: (details: UnloadingDetails | undefined) => void;
 onPending: (pending: boolean) => void;
 onStarted: () => void;
 onAuthError: () => void;
}

export function UnloadingStep({ preview, credentials, scanPlace, beforeCameras, disabled: externalDisabled, onDetails, onPending, onStarted, onAuthError }: UnloadingProps) {
 const scope = "store-app-unloading:" + storeAppApiBase() + ":" + credentials.username + ":" + preview.load_operation_id + ":" + preview.store_address;
 const current = useRef(scope);
 const [pending, setPending] = useState<Pending | null>(null);
 const [loadedScope, setLoadedScope] = useState("");
 const disabled = externalDisabled || loadedScope !== scope;
 const [damaged, setDamaged] = useState(false);
 const [busy, setBusy] = useState(false);
 const [message, setMessage] = useState("");
 const [method, setMethod] = useState<UnloadingDetails["method"] | "">("");
 const [difficult, setDifficult] = useState(false);
 const [loader, setLoader] = useState(false);
 const [reference, setReference] = useState("");

 useEffect(() => {
  current.current = scope;
  setMessage(""); setMethod(""); setDifficult(false); setLoader(false); setReference(""); setDamaged(false);
  try {
   const raw = localStorage.getItem(scope);
   const saved = raw === null ? null : parsePending(raw, preview);
   setPending(saved); onPending(!!saved);
  } catch (error) {
   setPending(null); setDamaged(true); onPending(true); setMessage(String(error));
  }
  setLoadedScope(scope);
  return () => { current.current = ""; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
 }, [scope]);

 useEffect(() => {
  const start = preview.unloading;
  onDetails(start?.status === "STARTED" && method && reference.trim() && (!difficult || loader)
   ? { start_operation_id: start.operation_id, method, rolling_difficult: difficult, loader_present: loader, evidence_reference: reference }
   : undefined);
 }, [preview.unloading, method, difficult, loader, reference, onDetails]);

 async function send(intent: Pending) {
  if (busy || disabled || intent.abandon) return;
  const key = scope; setBusy(true); setMessage("");
  try {
   await storeAppRequest("/api/delivery/store-receipts/unloading/start", credentials, intent.body);
   localStorage.removeItem(key);
   if (current.current === key) { setPending(null); onPending(false); setMessage("Начало выгрузки сохранено."); onStarted(); }
  } catch (error) {
   if (current.current === key) {
    const confirmed = error instanceof StoreAppApiError && error.confirmed;
    const saved: Pending = { ...intent, confirmedRejection: confirmed };
    localStorage.setItem(key, JSON.stringify(saved)); setPending(saved); onPending(true); setMessage(String(error));
    if (isAuthError(error)) onAuthError();
   }
  } finally { if (current.current === key) setBusy(false); }
 }

 function start() {
  if (pending || damaged || preview.already_received || !scanPlace || !beforeCameras || disabled) return;
  const intent: Pending = { body: {
   operation_id: "UNLOAD.START:" + crypto.randomUUID(), load_operation_id: preview.load_operation_id,
   store_address: preview.store_address, expected_composition_signature: preview.composition_signature,
   scan_place: scanPlace, before_cameras: beforeCameras,
  } };
  try { localStorage.setItem(scope, JSON.stringify(intent)); setPending(intent); onPending(true); void send(intent); }
  catch (error) { setMessage("Не удалось сохранить операцию до отправки: " + String(error)); }
 }

 function recover() {
  if (busy || !damaged) return;
  try { archiveDamaged(scope); }
  catch { setMessage("Архив не сохранён. Восстановление заблокировано; освободите место на устройстве."); return; }
  onPending(true);
  setMessage("Копия повреждённой записи сохранена для разбора. Исходная запись и блокировка остаются: обратитесь к ответственному для проверки исходной операции. Новый запрос начала не создаётся.");
 }

 const fact = preview.unloading;
 return <section className="store-app-unloading" aria-label="Выгрузка">
  <h3>Выгрузка <HelpHint helpId="unloading.start" tip="Начало и фактические условия выгрузки сохраняются вместе с приёмкой" article="store-receiving-app" /></h3>
  {damaged && <button type="button" title="Сохранить копию повреждённой записи для разбора; исходная запись и блокировка новых операций остаются" data-help-id="unloading.damaged.archive" disabled={busy} onClick={recover}>Сохранить запись для разбора</button>}
  {!damaged && (fact ? <p>Начало: {fact.started_at_instant}. {fact.status === "COMPLETED" ? "Выгрузка завершена." : "Выгрузка начата; заполните фактические условия."}</p>
   : !preview.already_received && <button type="button" title="Отметить фактическое начало выгрузки после скана места перед камерами" data-help-id="unloading.start" disabled={disabled || busy || !!pending || !scanPlace || !beforeCameras} onClick={start}>Начать выгрузку</button>)}
  {!damaged && fact?.status === "STARTED" && <fieldset disabled={disabled || busy || !!pending}>
   <label>Способ выгрузки
    <select title="Укажите фактический способ выгрузки" data-help-id="unloading.method" value={method} onChange={(event) => { setMethod(event.target.value as typeof method); setDifficult(false); setLoader(false); }}>
     <option value="">Выберите способ</option><option value="MANUAL">Вручную</option><option value="PALLET">Паллетой</option><option value="ROLL_CAGE">Закатывание тележки</option>
    </select>
   </label>
   <label><input type="checkbox" title="Отметить затруднённое закатывание тележки; требуется участие грузчика" data-help-id="unloading.difficult" disabled={method !== "ROLL_CAGE"} checked={difficult} onChange={(event) => setDifficult(event.target.checked)} />Закатывание затруднено</label>
   <label><input type="checkbox" title="Подтвердить фактическое участие грузчика в выгрузке" data-help-id="unloading.loader" checked={loader} onChange={(event) => setLoader(event.target.checked)} />Работал грузчик</label>
   <label>Основание подтверждения<input title="Укажите документ или основание подтверждения условий выгрузки" data-help-id="unloading.evidence" maxLength={100} value={reference} onChange={(event) => setReference(event.target.value)} /></label>
   {difficult && !loader && <p role="alert">Для затруднённого закатывания подтвердите участие грузчика.</p>}
  </fieldset>}
  {!damaged && pending && <><button type="button" title="Повторить точную сохранённую операцию начала выгрузки" data-help-id="unloading.retry" disabled={disabled || busy || !!pending.abandon} onClick={() => void send(pending)}>Повторить сохранённое начало</button>
   <UnloadingAbandon scope={scope} pending={pending} credentials={credentials} disabled={disabled || busy} onSaved={setPending}
    onResolved={() => { setPending(null); onPending(false); onStarted(); }} onAuthError={onAuthError} /></>}
  <p role="status" className="store-app-message">{message}</p>
 </section>;
}
