import { useCallback, useEffect, useRef, useState } from "react";
import { rawApiGet, rawApiPost, isAuthError } from "./api";
import type { AssemblyCredentials } from "./contracts";
import type { JournalMeta } from "./journal";
import { readPhysical, physicalLock, persistPhysical, clearPhysical } from "./physicalJournal";
import type { PhysicalIntent } from "./physicalJournal";
import { WEIGH_PATH, validWeigh, terminalWeigh, loadDeadline } from "./physicalContracts";
import type { WeighBody, WeighState } from "./physicalContracts";

export function useWarehouseWeigh(credentials: AssemblyCredentials, meta: JournalMeta, onCaptured: () => void) {
  const [entry, setEntry] = useState<PhysicalIntent<WeighBody> | null>(null), [state, setState] = useState<WeighState | null>(null);
  const [error, setError] = useState(""), [denied, setDenied] = useState(false), [busy, setBusy] = useState(false), [revision, bump] = useState(0);
  const [deadline, setDeadline] = useState(0), [now, setNow] = useState(performance.now());
  const leaseDeadline = useRef<{claim: string | null; deadline: number}>({claim: null, deadline: 0});
  const life = useRef(true), captured = useRef(onCaptured); captured.current = onCaptured;
  const restore = useCallback(() => {
    setDeadline(0); setState(null);
    try { setEntry(readPhysical<WeighBody>("warehouse_weigh", meta)); setError(""); }
    catch (err) { setError(err instanceof Error ? err.message : String(err)); }
    bump(v => v + 1);
  }, [meta]);
  useEffect(() => { life.current = true; restore(); const storage = () => restore(); window.addEventListener("storage", storage);
    return () => { life.current = false; window.removeEventListener("storage", storage); }; }, [restore]);
  useEffect(() => { const timer = window.setInterval(() => setNow(performance.now()), 250); return () => clearInterval(timer); }, []);
  const accept = useCallback(async (value: unknown, original: PhysicalIntent<WeighBody>, started: number): Promise<void> => {
    const result = validWeigh(value, original.body);
    if (!life.current) return;
    setState(result);
    let until = loadDeadline(result, started);
    if (until > 0 && leaseDeadline.current.claim === result.claim_id && leaseDeadline.current.deadline > 0) until = Math.min(until, leaseDeadline.current.deadline);
    if (until > 0) leaseDeadline.current = { claim: result.claim_id, deadline: until };
    setDeadline(until); setError(""); setDenied(false);
    if (result.state === "CAPTURED") {
      await physicalLock("warehouse_weigh", meta, async () => {
        const saved = readPhysical<WeighBody>("warehouse_weigh", meta);
        if (saved && JSON.stringify(saved) !== JSON.stringify(original)) throw new Error("Журнал изменился в другой вкладке. Сначала перечитайте результат.");
        clearPhysical("warehouse_weigh", meta);
      }, true);
      if (life.current) { setEntry(null); captured.current(); }
    }
  }, [meta]);
  useEffect(() => {
    if (!entry) return;
    let alive = true, timer = 0; const controller = new AbortController();
    const read = async () => {
      const started = performance.now();
      try { const result = await rawApiGet<unknown>(`${entry.url}/${encodeURIComponent(entry.body.request_id)}`, credentials, controller.signal);
        if (alive) await accept(result, entry, started);
      } catch (err) { if (alive && !controller.signal.aborted) { setDeadline(0); setError((err as {status?: number}).status === 404 ? "Результат пока не виден. Исходный запрос сохранён: можно повторить только его же." : err instanceof Error ? err.message : String(err)); setDenied(isAuthError(err)); } }
      if (alive) timer = window.setTimeout(() => void read(), 2000);
    };
    const offline = () => { setDeadline(0); setError("Связь не подтверждена. Указание загрузить платформу приостановлено."); };
    const online = () => { setDeadline(0); bump(v => v + 1); };
    window.addEventListener("offline", offline); window.addEventListener("online", online); void read();
    return () => { alive = false; clearTimeout(timer); controller.abort(); window.removeEventListener("offline", offline); window.removeEventListener("online", online); };
  }, [entry, credentials, accept, revision]);
  const send = useCallback(async (body?: WeighBody) => {
    if (busy || denied) return;
    setBusy(true); setDeadline(0);
    try {
      await physicalLock("warehouse_weigh", meta, async () => {
        let original = readPhysical<WeighBody>("warehouse_weigh", meta);
        if (body && original) {
          const previous = validWeigh(await rawApiGet(`${original.url}/${encodeURIComponent(original.body.request_id)}`, credentials), original.body);
          if (!terminalWeigh(previous)) throw new Error("Предыдущий запрос ещё не завершён. Повторите его без изменений.");
          clearPhysical("warehouse_weigh", meta); original = null;
        }
        if (!original) { if (!body) throw new Error("Нет исходного запроса для повтора."); original = { version: 1, url: WEIGH_PATH, body }; persistPhysical("warehouse_weigh", meta, original); }
        if (life.current) { setEntry(original); setState(null); setError(""); }
        const started = performance.now(), response = await rawApiPost(original.url, credentials, original.body);
        // Read poll performs the terminal journal resolution under the same task lock after this POST releases it.
        const result = validWeigh(response, original.body);
        if (life.current) { setState(result); setDeadline(loadDeadline(result, started)); }
      });
    } catch (err) { if (life.current) { setError(err instanceof Error ? err.message : String(err)); setDenied(isAuthError(err)); } }
    finally { if (life.current) setBusy(false); }
  }, [busy, denied, credentials, meta]);
  return { entry, state, error, denied, busy, blocked: busy || !!entry || !!error || denied, loadAllowed: !error && !denied && now < deadline && navigator.onLine !== false,
    remainingSeconds: Math.max(0, Math.ceil((deadline - now) / 1000)), refresh: restore, retry: () => void send(), start: (body: WeighBody) => void send(body) };
}
export type WarehouseWeighState = ReturnType<typeof useWarehouseWeigh>;
