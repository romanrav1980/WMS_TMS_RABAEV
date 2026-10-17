import { useCallback, useEffect, useRef, useState } from "react";
import { assemblyRequest } from "./api";
import { validSession } from "./commands";
import type { AssemblyContext, AssemblyCredentials } from "./contracts";
function isContext(value: unknown): value is AssemblyContext {
  const v = value as AssemblyContext;
  return !!v && typeof v.task_id === "number" && typeof v.content_version === "number" && Array.isArray(v.lines) && Array.isArray(v.stations);
}
export function useAssemblyContext(credentials: AssemblyCredentials | null, taskId: number | null) {
  const [loadedCredentials, setLoadedCredentials] = useState<AssemblyCredentials | null>(null);
  const [context, setContext] = useState<AssemblyContext | null>(null);
  const [loading, setLoading] = useState(false), [error, setError] = useState("");
  const epoch = useRef(0);
  const load = useCallback((preserve: boolean) => {
    if (!credentials || taskId == null) { setContext(null); setError(""); return; }
    const attempt = ++epoch.current;
    if (!preserve) { setContext(null); setLoading(true); }
    setError("");
    assemblyRequest<unknown>(`/context?task_id=${taskId}`, credentials)
      .then(data => {
        if (epoch.current !== attempt) return;
        if (!isContext(data) || data.task_id !== taskId) throw new Error("Сервер вернул непригодный контекст этого задания.");
        if (data.active_session) validSession(data.active_session, credentials, data.active_session.session_id, taskId);
        setLoadedCredentials(credentials); setContext(data);
      })
      .catch(err => { if (epoch.current === attempt) { if (!preserve) setContext(null); setError(err instanceof Error ? err.message : String(err)); } })
      .finally(() => { if (epoch.current === attempt) setLoading(false); });
  }, [credentials, taskId]);
  const refresh = useCallback(() => load(false), [load]);
  const refreshMetadata = useCallback(() => load(true), [load]);
  useEffect(() => { refresh(); return () => { epoch.current += 1; }; }, [refresh]);
  return { context: loadedCredentials === credentials && context?.task_id === taskId ? context : null, loading, error, refresh, refreshMetadata };
}
