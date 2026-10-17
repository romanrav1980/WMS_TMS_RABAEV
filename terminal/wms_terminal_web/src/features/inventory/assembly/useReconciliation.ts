import { useCallback, useEffect, useRef, useState } from "react";
import { authorizeReconciliation, readReconciliation } from "./recoveryCommands";
import { readSaved } from "./savedCommands";
import { usePolling } from "./usePolling";
import type { AssemblyCredentials, Reconciliation, RecoveryAuthorizeBody } from "./contracts";
export function useReconciliation(credentials: AssemblyCredentials, id: string, fallback: Reconciliation | null) {
  const [record, setRecord] = useState<Reconciliation | null>(fallback), [error, setError] = useState("");
  const [busy, setBusy] = useState(false), [stale, setStale] = useState(true);
  const [authFailed, setAuthFailed] = useState(false);
  const live = useRef(true), epoch = useRef(0), working = useRef(false);
  const load = useCallback(async () => {
    const observed = ++epoch.current;
    try {
      const value = await readReconciliation(credentials, id);
      if (live.current && epoch.current === observed) { setRecord(value); setError(""); setStale(false); setAuthFailed(false); }
    } catch (err) {
      if (live.current && epoch.current === observed) { setError(err instanceof Error ? err.message : String(err)); setStale(true); setAuthFailed([401,403].includes((err as { status?: number }).status ?? 0)); }
    }
  }, [credentials, id]);
  useEffect(() => { live.current = true; void load(); return () => { live.current = false; epoch.current += 1; }; }, [load]);
  const authorize = useCallback(async (body: RecoveryAuthorizeBody, exactRetry = false) => {
    if (!record || working.current || authFailed) return;
    const prior = readSaved("recovery_authorize", { server: location.origin, actor: credentials.username, task_id: record.case_task_id });
    const exact = exactRetry && prior?.target_reconciliation === id && JSON.stringify(prior.body) === JSON.stringify(body);
    if (stale && !exact) return;
    const observed = ++epoch.current; working.current = true; setBusy(true); setError("");
    try {
      await authorizeReconciliation(credentials, { server: location.origin, actor: credentials.username, task_id: record.case_task_id }, record, body);
      if (live.current && epoch.current === observed) await load();
    } catch (err) { if (live.current && epoch.current === observed) setError(err instanceof Error ? err.message : String(err)); }
    finally { if (live.current) { working.current = false; setBusy(false); } }
  }, [record, stale, authFailed, credentials, id, load]);
  usePolling(!!record && ["REQUESTED","AUTHORIZED"].includes(record.state), 2000, async signal => {
    if (working.current) return;
    const observed = epoch.current;
    try {
      const fresh = await readReconciliation(credentials, id, signal);
      if (live.current && !signal.aborted && epoch.current === observed) { setRecord(fresh); setStale(false); setAuthFailed(false); setError(""); }
    } catch (err) {
      if (live.current && !signal.aborted && epoch.current === observed) { setError(err instanceof Error ? err.message : String(err)); setStale(true); setAuthFailed([401,403].includes((err as { status?: number }).status ?? 0)); }
    }
  });
  return { record, error, busy, stale, authFailed, refresh: load, authorize };
}


