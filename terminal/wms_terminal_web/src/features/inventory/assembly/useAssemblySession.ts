import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { closeCaseSession, finishSession, markPlaced, openSession, openStep, readSession, validSession } from "./commands";
import { requestReconciliation } from "./recoveryCommands";
import { usePolling } from "./usePolling";
import type { JournalMeta } from "./journal";
import type { AssemblyCredentials, AssemblySession, RecoveryRequestBody, FinishBody, OpenSessionBody, OpenStepBody } from "./contracts";
import { UNRESOLVED_STEP_STATES } from "./contracts";

type PendingKind = "open_session" | "open_step" | "finish" | "placed" | "case_close" | "recovery_request" | null;
type ReadState = { message: string; auth: boolean } | null;
export function useAssemblySession(credentials: AssemblyCredentials | null, taskId: number | null, initialSession: AssemblySession | null, refreshContext: () => void) {
  const [session, setSession] = useState<AssemblySession | null>(initialSession);
  const [busy, setBusy] = useState<PendingKind>(null), [stale, setStale] = useState<ReadState>(null);
  const [error, setError] = useState<{ kind: PendingKind; message: string; confirmed: boolean; uncertain: boolean } | null>(null);
  const live = useRef(true), revision = useRef(0), inFlight = useRef(false);
  useEffect(() => { live.current = true; return () => { live.current = false; revision.current += 1; }; }, []);
  const meta: JournalMeta | null = useMemo(() => credentials && taskId != null ? { server: location.origin, actor: credentials.username, task_id: taskId } : null, [credentials, taskId]);
  const lastAttempt = useRef<(() => void) | null>(null);
  const currentStep = useMemo(() => {
    const steps = session?.steps ?? [];
    return steps.length ? steps.reduce((a, b) => b.sequence > a.sequence ? b : a) : null;
  }, [session]);
  const unresolved = currentStep != null && UNRESOLVED_STEP_STATES.has(currentStep.state);
  const adoptSession = useCallback((value: AssemblySession) => {
    if (!live.current || !credentials || taskId == null) return;
    validSession(value, credentials, value.session_id, taskId);
    revision.current += 1; setSession(value); setStale(null); setError(null); refreshContext();
  }, [credentials, taskId, refreshContext]);
  const run = useCallback(async <T,>(kind: Exclude<PendingKind, null>, fn: () => Promise<T>, onOk: (v: T) => void) => {
    if (inFlight.current || stale) return;
    inFlight.current = true; const attempt = ++revision.current;
    lastAttempt.current = () => void run(kind, fn, onOk);
    setBusy(kind); setError(null);
    try {
      const result = await fn();
      if (live.current && revision.current === attempt) { revision.current += 1; onOk(result); lastAttempt.current = null; }
    } catch (err) {
      if (!live.current || revision.current !== attempt) return;
      const status = (err as { status?: number }).status ?? 0, confirmed = (err as { confirmed?: boolean }).confirmed === true;
      setError({ kind, message: err instanceof Error ? err.message : String(err), confirmed, uncertain: !confirmed });
      if (!confirmed && status !== 401 && status !== 403) setStale({ message: "Результат команды ещё не подтверждён. Перечитайте состояние перед физическими действиями.", auth: false });
      if (status === 401 || status === 403) setStale({ message: "Допуск изменён. Повторите вход и чтение задания.", auth: true });
    } finally { if (live.current) { inFlight.current = false; setBusy(null); } }
  }, [stale]);
  const startSession = useCallback((body: OpenSessionBody) => {
    if (credentials && meta) void run("open_session", () => openSession(credentials, meta, body), setSession);
  }, [credentials, meta, run]);
  const startStep = useCallback((body: OpenStepBody) => {
    if (credentials && meta && session) void run("open_step", () => openStep(credentials, meta, session.session_id, body),
      step => setSession(s => s ? { ...s, steps: [...s.steps, step] } : s));
  }, [credentials, meta, session, run]);
  const place = useCallback(() => {
    if (!credentials || !currentStep || !session || session.state !== "OPEN") return;
    void run("placed", async () => {
      await markPlaced(credentials, currentStep.step_id, session.session_id);
      return readSession(credentials, session.session_id);
    }, adoptSession);
  }, [credentials, currentStep, session, run, adoptSession]);
  const finish = useCallback((body: FinishBody) => {
    if (credentials && meta && session) void run("finish", () => finishSession(credentials, meta, session.session_id, body), setSession);
  }, [credentials, meta, session, run]);
  const closeCase = useCallback(() => {
    if (!credentials || !meta || !session || unresolved) return;
    const body = { operation_id: `ASM.CLOSE:${crypto.randomUUID()}`, expected_content_version: session.content_version };
    void run("case_close", () => closeCaseSession(credentials, meta, session.session_id, body), () => refreshContext());
  }, [credentials, meta, session, unresolved, run, refreshContext]);
  const requestRecovery = useCallback((body: RecoveryRequestBody) => {
    if (!credentials || !meta || !session) return;
    void run("recovery_request", async () => {
      await requestReconciliation(credentials, meta, session.session_id, body);
      const fresh = await readSession(credentials, session.session_id);
      if (fresh.state !== "BLOCKED") throw new Error("Остановка ещё не подтверждена текущим состоянием. Ничего не убирайте с весов.");
      return fresh;
    }, adoptSession);
  }, [credentials, meta, session, run, adoptSession]);
  const readBeforeRetry = useCallback(async () => {
    if (!credentials || !session) return;
    try { adoptSession(await readSession(credentials, session.session_id)); }
    catch (err) { if (live.current) setStale({ message: err instanceof Error ? err.message : String(err), auth: [401,403].includes((err as {status?: number}).status ?? 0) }); }
  }, [credentials, session, adoptSession]);
  const retrySame = useCallback(() => { if (!stale) lastAttempt.current?.(); }, [stale]);
  const dismissError = useCallback(() => setError(null), []);
  const afterAbandonment = useCallback(() => {
    revision.current += 1; lastAttempt.current = null; setError(null); setStale(null); refreshContext();
  }, [refreshContext]);
  usePolling(!!credentials && !!session && session.state !== "FINALIZED" && !stale?.auth, 2000, async signal => {
    if (!credentials || !session || inFlight.current) return;
    const observed = revision.current;
    try {
      const fresh = await readSession(credentials, session.session_id, signal);
      if (!signal.aborted && live.current && revision.current === observed) { setSession(fresh); setStale(null); }
    } catch (err) {
      if (!signal.aborted && live.current && revision.current === observed) setStale({ message: err instanceof Error ? err.message : String(err), auth: [401,403].includes((err as {status?: number}).status ?? 0) });
    }
  });
  return { session, currentStep, unresolved, busy, error, stale, meta, startSession, startStep, place, finish, closeCase, requestRecovery, dismissError, readBeforeRetry, retrySame, adoptSession, afterAbandonment };
}
export type AssemblySessionState = ReturnType<typeof useAssemblySession>;




